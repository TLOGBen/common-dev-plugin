#!/usr/bin/env bash
# WSL2 Chrome Remote Debug 一鍵設定
# 用法: bash setup-chrome-debug.sh
#       bash setup-chrome-debug.sh --no-chrome   # 只設 portproxy（Chrome 已開）
#       bash setup-chrome-debug.sh --cleanup      # 移除 portproxy 規則與防火牆

set -euo pipefail

CHROME_DEBUG_PORT=9222
PROXY_PORT=9333
CHROME_USER_DATA="${DEV_BROWSER_CHROME_USER_DATA:-C:\\temp\\chrome-debug}"
CHROME_EXE="${DEV_BROWSER_CHROME_EXE:-/mnt/c/Program Files/Google/Chrome/Application/chrome.exe}"
FIREWALL_RULE_NAME="Chrome Debug Proxy ${PROXY_PORT}"
HOST_IP="${DEV_BROWSER_WINDOWS_HOST_IP:-$(ip route show default 2>/dev/null | awk '/default/ {print $3; exit}')}"
if [[ -z "${HOST_IP}" ]]; then
  HOST_IP=$(grep nameserver /etc/resolv.conf | awk '{print $2}')
fi

# 安全預設：listener 只綁 WSL 對 Windows 的 vEthernet 介面（HOST_IP），不對整個 LAN 開放。
# Chrome DevTools Protocol 無任何身分驗證——綁 0.0.0.0 等於把瀏覽器控制權開給同網段所有人。
# 真的需要對 LAN 曝露時才加 --expose-lan（會跳警告）。
EXPOSE_LAN=0
for a in "$@"; do [[ "$a" == "--expose-lan" ]] && EXPOSE_LAN=1; done
if [[ "$EXPOSE_LAN" -eq 1 ]]; then
  LISTEN_ADDR="0.0.0.0"
  FW_SCOPE=""
else
  LISTEN_ADDR="${HOST_IP}"          # 只在 WSL vEthernet 介面上聽
  FW_SCOPE="remoteip=172.16.0.0/12 profile=private"   # 防火牆僅放行 WSL 私網段
fi

ok()   { printf "✅ %s\n" "$*"; }
warn() { printf "⚠️  %s\n" "$*"; }
err()  { printf "❌ %s\n" "$*"; }

# ── --cleanup 模式 ────────────────────────────────────────────
if [[ "${1:-}" == "--cleanup" ]]; then
  echo "清除 portproxy 與防火牆規則..."
  # 刪掉目前綁定（HOST_IP）與舊版可能殘留的 0.0.0.0 規則
  pwsh.exe -NoProfile -Command "netsh interface portproxy delete v4tov4 listenaddress=${HOST_IP} listenport=${PROXY_PORT}" 2>/dev/null || true
  pwsh.exe -NoProfile -Command "netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=${PROXY_PORT}" 2>/dev/null || true
  pwsh.exe -NoProfile -Command "netsh advfirewall firewall delete rule name='${FIREWALL_RULE_NAME}'" 2>/dev/null || true
  ok "清除完成"
  exit 0
fi

if [[ "$EXPOSE_LAN" -eq 1 ]]; then
  warn "--expose-lan：portproxy 將綁 0.0.0.0，Chrome 除錯埠會對整個區域網路開放（無驗證）。確認你信任這個網段再繼續。"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " WSL2 Chrome Remote Debug 設定"
echo " Windows host IP: ${HOST_IP}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Chrome 是否在 Windows 上 LISTENING（cmd.exe 避開 PowerShell UTF-16 亂碼問題）
chrome_is_listening() {
  cmd.exe /c "netstat -ano 2>nul | findstr :${CHROME_DEBUG_PORT} | findstr LISTENING" 2>/dev/null | grep -q "LISTENING" || return 1
}

# ── Step 1: 啟動 Chrome ───────────────────────────────────────
if [[ "${1:-}" != "--no-chrome" ]]; then
  echo ""
  echo "[1/3] 啟動 Chrome（port ${CHROME_DEBUG_PORT}，獨立 profile）..."

  if chrome_is_listening; then
    ok "Chrome debug port 已在運行，略過啟動"
  else
    "${CHROME_EXE}" \
      --remote-debugging-port=${CHROME_DEBUG_PORT} \
      --user-data-dir="${CHROME_USER_DATA}" \
      --no-first-run \
      --no-default-browser-check \
      2>/dev/null &

    echo "   等待 Chrome 啟動（最多 15 秒）..."
    for i in {1..15}; do
      sleep 1
      if chrome_is_listening; then
        ok "Chrome 已啟動（${i}s）"
        break
      fi
      if [[ $i -eq 15 ]]; then
        err "Chrome 啟動逾時"
        echo "   請手動執行：'${CHROME_EXE}' --remote-debugging-port=${CHROME_DEBUG_PORT} --user-data-dir='${CHROME_USER_DATA}'"
        exit 1
      fi
    done
  fi
else
  echo "[1/3] 跳過啟動 Chrome（--no-chrome）"
fi

# ── Step 2: portproxy ─────────────────────────────────────────
echo ""
echo "[2/3] 設定 portproxy（${LISTEN_ADDR}:${PROXY_PORT} → 127.0.0.1:${CHROME_DEBUG_PORT}）..."

EXISTING=$(pwsh.exe -NoProfile -Command "netsh interface portproxy show all" 2>/dev/null | grep -c "${PROXY_PORT}" || echo 0)
if [[ "$EXISTING" -gt 0 ]]; then
  warn "portproxy 規則已存在，先刪除再重建"
  pwsh.exe -NoProfile -Command "netsh interface portproxy delete v4tov4 listenaddress=${HOST_IP} listenport=${PROXY_PORT}" 2>/dev/null || true
  pwsh.exe -NoProfile -Command "netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=${PROXY_PORT}" 2>/dev/null || true
fi
pwsh.exe -NoProfile -Command "netsh interface portproxy add v4tov4 listenaddress=${LISTEN_ADDR} listenport=${PROXY_PORT} connectaddress=127.0.0.1 connectport=${CHROME_DEBUG_PORT}" 2>/dev/null
ok "portproxy 已設定（listener 綁 ${LISTEN_ADDR}）"

# ── Step 3: 防火牆 ────────────────────────────────────────────
echo ""
echo "[3/3] 設定防火牆（port ${PROXY_PORT}）..."

FW_EXISTS=$(cmd.exe /c "netsh advfirewall firewall show rule name=\"${FIREWALL_RULE_NAME}\" 2>nul | findstr /c:\"Rule Name\"" 2>/dev/null | grep -c "Rule Name" || true)
FW_EXISTS="${FW_EXISTS//[^0-9]/}"  # 去掉換行符等雜訊
if [[ "${FW_EXISTS:-0}" -gt 0 ]]; then
  ok "防火牆規則已存在，略過"
else
  pwsh.exe -NoProfile -Command "netsh advfirewall firewall add rule name='${FIREWALL_RULE_NAME}' dir=in action=allow protocol=TCP localport=${PROXY_PORT} ${FW_SCOPE}" 2>/dev/null
  ok "防火牆規則已新增${FW_SCOPE:+（限 ${FW_SCOPE}）}"
fi

# ── 驗證 ──────────────────────────────────────────────────────
echo ""
echo "驗證 WSL2 → Windows Chrome 連線..."
sleep 1
RESULT=$(curl -s --max-time 5 "http://${HOST_IP}:${PROXY_PORT}/json/version" 2>/dev/null || true)

if echo "$RESULT" | grep -q '"Browser"'; then
  BROWSER=$(echo "$RESULT" | grep '"Browser"' | awk -F'"' '{print $4}')
  ok "連線成功！${BROWSER}"
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo " dev-browser 使用方式："
  echo ""
  echo "   dev-browser --connect http://${HOST_IP}:${PROXY_PORT} <<'EOF'"
  echo "   const page = await browser.getPage(\"app\");"
  echo "   console.log(page.url());"
  echo "   EOF"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
  err "連線失敗"
  echo "   請確認："
  echo "   1. Chrome port ${CHROME_DEBUG_PORT} LISTENING：curl http://127.0.0.1:${CHROME_DEBUG_PORT}/json/version"
  echo "   2. portproxy 規則：pwsh.exe -NoProfile -Command 'netsh interface portproxy show all'"
  echo "   3. Windows host IP：${HOST_IP}"
  exit 1
fi
