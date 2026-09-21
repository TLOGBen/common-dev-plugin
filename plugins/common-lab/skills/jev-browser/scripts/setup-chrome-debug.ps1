# Windows Chrome Remote Debug 一鍵設定（PowerShell 版）
# 用法:
#   pwsh .\setup-chrome-debug.ps1                  # 啟動 Chrome（debug port 9222）
#   pwsh .\setup-chrome-debug.ps1 -NoChrome        # 跳過啟動 Chrome（已開時用），只驗證連線
#   pwsh .\setup-chrome-debug.ps1 -Cleanup         # 結束 debug Chrome 進程
#
# 與 WSL2 版差異：native Windows 下 dev-browser 直接連 127.0.0.1:9222，
# 不需要 netsh portproxy 與防火牆規則。

[CmdletBinding()]
param(
    [switch]$NoChrome,
    [switch]$Cleanup
)

$ErrorActionPreference = 'Stop'

$ChromeDebugPort = 9222
$ChromeUserData  = 'C:\temp\chrome-debug'
$ChromeExe       = 'C:\Program Files\Google\Chrome\Application\chrome.exe'

function Write-Ok   { param($msg) Write-Host "[OK]   $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err  { param($msg) Write-Host "[FAIL] $msg" -ForegroundColor Red }

function Test-ChromeListening {
    try {
        $conn = Get-NetTCPConnection -LocalPort $ChromeDebugPort -State Listen -ErrorAction Stop
        return [bool]$conn
    } catch {
        return $false
    }
}

# -- Cleanup 模式：結束帶 debug 旗標的 Chrome 進程 --
if ($Cleanup) {
    Write-Host "尋找並結束 debug Chrome 進程..."
    $procs = Get-CimInstance Win32_Process -Filter "Name='chrome.exe'" |
        Where-Object { $_.CommandLine -match 'remote-debugging-port' }
    if ($procs) {
        foreach ($p in $procs) {
            Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
        }
        Write-Ok "已結束 $($procs.Count) 個 debug Chrome 進程"
    } else {
        Write-Warn "找不到 debug Chrome 進程"
    }
    exit 0
}

Write-Host "===================================================="
Write-Host " Windows Chrome Remote Debug 設定"
Write-Host " Debug Port: $ChromeDebugPort"
Write-Host " User Data : $ChromeUserData"
Write-Host "===================================================="

# -- Step 1: 啟動 Chrome --
if (-not $NoChrome) {
    Write-Host ""
    Write-Host "[1/2] 啟動 Chrome（port $ChromeDebugPort，獨立 profile）..."

    if (Test-ChromeListening) {
        Write-Ok "Chrome debug port 已在運行，略過啟動"
    } else {
        if (-not (Test-Path $ChromeExe)) {
            Write-Err "找不到 Chrome：$ChromeExe"
            Write-Host "   請手動修改腳本中的 `$ChromeExe 變數，或用 -NoChrome 跳過。"
            exit 1
        }
        if (-not (Test-Path $ChromeUserData)) {
            New-Item -ItemType Directory -Path $ChromeUserData -Force | Out-Null
        }

        Start-Process -FilePath $ChromeExe -ArgumentList @(
            "--remote-debugging-port=$ChromeDebugPort",
            "--user-data-dir=$ChromeUserData",
            "--no-first-run",
            "--no-default-browser-check"
        ) | Out-Null

        Write-Host "   等待 Chrome 啟動（最多 15 秒）..."
        $started = $false
        for ($i = 1; $i -le 15; $i++) {
            Start-Sleep -Seconds 1
            if (Test-ChromeListening) {
                Write-Ok "Chrome 已啟動（${i}s）"
                $started = $true
                break
            }
        }
        if (-not $started) {
            Write-Err "Chrome 啟動逾時"
            Write-Host "   請手動執行：& '$ChromeExe' --remote-debugging-port=$ChromeDebugPort --user-data-dir='$ChromeUserData'"
            exit 1
        }
    }
} else {
    Write-Host "[1/2] 跳過啟動 Chrome（-NoChrome）"
}

# -- Step 2: 驗證連線 --
Write-Host ""
Write-Host "[2/2] 驗證 Chrome DevTools Protocol 連線..."
Start-Sleep -Seconds 1

try {
    $resp = Invoke-RestMethod -Uri "http://127.0.0.1:$ChromeDebugPort/json/version" -TimeoutSec 5
    Write-Ok "連線成功！$($resp.Browser)"
    Write-Host ""
    Write-Host "===================================================="
    Write-Host " dev-browser 使用方式（PowerShell）："
    Write-Host ""
    Write-Host " 現成 template 用 run <file>；臨時多行腳本可依 dev-browser --help 使用 PowerShell here-string pipe。"
    Write-Host ""
    Write-Host " 跑現成 template（在 scripts/case/）："
    $LoginScript = Join-Path $PSScriptRoot 'case\login.js'
    Write-Host "   dev-browser --connect http://127.0.0.1:$ChromeDebugPort run `"$LoginScript`""
    Write-Host ""
    Write-Host " 客製：複製 template 到 .agent-workspace\ 後改參數，再用同樣 run 形式跑。"
    Write-Host "===================================================="
} catch {
    Write-Err "連線失敗：$_"
    Write-Host "   檢查項目："
    Write-Host "   1. Chrome 是否真的 LISTENING：Get-NetTCPConnection -LocalPort $ChromeDebugPort"
    Write-Host "   2. 是否有舊的 Chrome instance 攔截：用 -Cleanup 後重跑"
    exit 1
}
