# WSL2 連 Windows Chrome Remote Debug — 完整設定流程

在 WSL2 環境下，`dev-browser --connect` 需要透過 portproxy 才能連到 Windows 上的 Chrome。
設定完成後可目視畫面操作，比 headless 模式更直觀可靠。

---

## 前置確認

執行 `setup-wsl2-chrome-debug.sh` 會修改 Windows `netsh portproxy` 與防火牆規則，需從具系統管理員權限的 Windows session 啟動 WSL。Windows 命令一律透過 PowerShell 7 (`pwsh.exe -NoProfile`) 執行。

```bash
# 取得 Windows host gateway（每次 WSL2 重啟可能變）
ip route show default | awk '/default/ {print $3; exit}'
# 通常是 172.21.x.1
```

若環境採 mirrored networking / DNS tunneling，或自動偵測結果無法連線，可在執行 setup script 前明確設定 `DEV_BROWSER_WINDOWS_HOST_IP`；Chrome 不在預設路徑時設定 `DEV_BROWSER_CHROME_EXE`。

---

## Step 1 — 啟動 Windows Chrome（含 debug port）

從 WSL2 執行：

```bash
"/mnt/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --remote-debugging-port=9222 \
  --user-data-dir="C:\\temp\\chrome-debug" &
```

> **⚠️ 為什麼需要 `--user-data-dir`？**
> Chrome 若已有 instance 在跑，新開的 process 會附掛到舊視窗，`--remote-debugging-port` 被忽略。
> 加上獨立的 `--user-data-dir` 強制建立全新 instance，debug port 才會生效。

驗證 port 有在 listen：

```bash
pwsh.exe -NoProfile -Command "netstat -ano | Select-String '9222.*LISTEN'"
# 應看到 TCP  127.0.0.1:9222  0.0.0.0:0  LISTENING
```

---

## Step 2 — 設 portproxy + 防火牆

Chrome 的 debug port 只綁在 Windows 的 `127.0.0.1`，WSL2 過不去。
用 `netsh portproxy` 轉發，讓 WSL2 能透過 Windows host IP 連進來。

> ⚠️ **安全**：Chrome DevTools Protocol 沒有任何身分驗證——能連到 debug port 的人就能完全操控瀏覽器（讀 cookie、開分頁、跑 JS）。所以 portproxy **只綁 WSL 對 Windows 的介面（HOST_IP），不要綁 `0.0.0.0`**，防火牆也只放行 WSL 私網段。建議直接用打包好的 `setup-wsl2-chrome-debug.sh`（已預設安全綁定）；下面的手動指令僅供理解原理。

```bash
HOST_IP=$(ip route show default | awk '/default/ {print $3; exit}')   # WSL 對 Windows 的 gateway

# 為什麼用 9333 而不直接用 9222？
# Chrome 安全政策強制只 bind 127.0.0.1，--remote-debugging-address=0.0.0.0 在新版 Chrome 無效。
# portproxy 若 listen 0.0.0.0:9222，會與 Chrome 的 127.0.0.1:9222 在 Windows 上衝突。
# 用不同 port（9333）讓兩者共存：Chrome 佔 9222，portproxy 佔 9333 轉發到 9222。
# listener 綁 HOST_IP（不是 0.0.0.0）→ 只有 WSL 連得到，不對整個 LAN 開放。
pwsh.exe -NoProfile -Command "netsh interface portproxy add v4tov4 listenaddress=${HOST_IP} listenport=9333 connectaddress=127.0.0.1 connectport=9222"

# 防火牆只放行 WSL 私網段（172.16/12）且限私有網路設定檔
pwsh.exe -NoProfile -Command "netsh advfirewall firewall add rule name='Chrome Debug Proxy 9333' dir=in action=allow protocol=TCP localport=9333 remoteip=172.16.0.0/12 profile=private"
```

確認規則已加：

```bash
pwsh.exe -NoProfile -Command "netsh interface portproxy show all"
# 應看到目前的 HOST_IP / 9333 → 127.0.0.1 / 9222
```

---

## Step 3 — 從 WSL2 驗證連通

```bash
HOST_IP=$(ip route show default | awk '/default/ {print $3; exit}')
curl -s --max-time 5 http://${HOST_IP}:9333/json/version
# 應回傳 Chrome 版本 JSON
```

---

## Step 4 — dev-browser --connect 使用

```bash
HOST_IP=$(ip route show default | awk '/default/ {print $3; exit}')

dev-browser --connect http://${HOST_IP}:9333 <<'EOF'
const page = await browser.getPage("app"); // "app" 為範例頁面名稱，換成你自己的
console.log(JSON.stringify({ url: page.url(), title: await page.title() }));
EOF
```

---

## 重啟後需要重做的步驟

| 步驟 | 原因 | 頻率 |
|------|------|------|
| 重新啟動 Chrome（Step 1）| Chrome 進程消失 | 每次重開機 |
| 重新設 portproxy（Step 2）| `netsh portproxy` 規則重開機後消失 | 每次重開機 |
| 防火牆規則 | 永久儲存，不需重設 | 只需一次 |
| Windows host IP | 可能變動，重新查 `ip route show default` | WSL2 重啟後確認 |

> **想讓 portproxy 開機自動設定**：在 Windows 工作排程器建一個開機執行的 PowerShell 腳本，
> 呼叫上面的 `netsh interface portproxy add` 指令即可。

---

## 常見問題

| 症狀 | 原因 | 解法 |
|------|------|------|
| curl exit 28（timeout）| portproxy 未設或防火牆擋 | 重新執行 Step 2 |
| curl exit 56（connection reset）| portproxy 衝突（listen 與 Chrome 同 port）| 改用 9333 轉 9222 |
| Chrome 視窗開了但 curl 沒回應 | Chrome 附掛到舊 instance，debug port 未啟動 | 加 `--user-data-dir` 重開 |
| `dev-browser --connect` 找不到頁面 | Chrome 開了但 portproxy 還沒設 | 執行 Step 2 |
