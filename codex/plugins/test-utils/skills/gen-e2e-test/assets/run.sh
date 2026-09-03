#!/usr/bin/env bash
# 自包含 Playwright 測試 — POSIX 入口（macOS / Linux，或 Windows Git Bash）
# 前提：在「目標站台正在跑的同一台機器」上執行（後端常只綁 localhost）。
#       Windows 使用者請改用雙擊 run-test.bat。
#
# 相依共用：優先用 ../.e2e-deps 的共用 playwright，沒有才本地裝。
# 改參數：USER_ID=xxx BASE_URL=http://... bash run.sh
set -uo pipefail
cd "$(dirname "$0")"

echo "=================================================="
echo " Playwright 自動化測試 + API 報告"
echo "=================================================="

if ! command -v node >/dev/null 2>&1; then
  echo "[錯誤] 找不到 node，請先安裝 Node.js LTS。"
  exit 1
fi

# --- 相依解析：shared (../.e2e-deps) -> local -> 安裝 ---
SHARED="$(cd .. 2>/dev/null && pwd)/.e2e-deps"
PWDEPS=""
if [ -d "$SHARED/node_modules/playwright" ]; then
  PWDEPS="$SHARED/node_modules"
elif [ -d node_modules/playwright ]; then
  PWDEPS="$(pwd)/node_modules"
else
  echo "首次執行，安裝共用 playwright（一次）..."
  if mkdir -p "$SHARED" 2>/dev/null; then
    [ -f "$SHARED/package.json" ] || cp package.json "$SHARED/package.json"
    ( cd "$SHARED" && PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install --no-audit --no-fund )
  fi
  if [ -d "$SHARED/node_modules/playwright" ]; then
    PWDEPS="$SHARED/node_modules"
  else
    echo "共用安裝失敗，改本地安裝..."
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install --no-audit --no-fund || { echo "[錯誤] npm install 失敗"; exit 1; }
    PWDEPS="$(pwd)/node_modules"
  fi
fi
export PW_DEPS="$PWDEPS"
export NODE_PATH="$PWDEPS"
echo "使用 playwright：$PWDEPS"

node test.mjs
CODE=$?
echo ""
[ $CODE -eq 0 ] && echo "✅ 完成，報告在 reports/" || echo "⚠️ 結束（exit=$CODE），詳見 reports/"
exit $CODE
