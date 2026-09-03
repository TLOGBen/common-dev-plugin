#!/usr/bin/env bash
# Playwright 錄製器 — POSIX 入口（macOS / Linux）
# 操作流程後關閉瀏覽器，錄製存成 recording.js。
# Windows 使用者請改用雙擊 record.bat。
#
# 相依共用：優先用 ../.e2e-deps 的共用 playwright，沒有才本地裝。
# 改起始頁：URL=https://your-site/xxx bash record.sh
# 同夾或上層若有 auth.json，會自動以已登入狀態開始錄製。
set -uo pipefail
cd "$(dirname "$0")"

# 預設為佔位 URL，錄製前請以 URL 環境變數指定（範例：http://localhost:3000/login，請改成你自己的）
URL="${URL:-https://example.com/login}"

echo "=================================================="
echo " Playwright 錄製器 — 起始頁：$URL"
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

# --- auth 重用：同夾或上層有 auth.json 就自動載入已登入狀態 ---
AUTH_ARGS=""
if [ -f auth.json ]; then
  AUTH_ARGS="--load-storage=auth.json"
elif [ -f ../auth.json ]; then
  AUTH_ARGS="--load-storage=../auth.json"
fi
[ -n "$AUTH_ARGS" ] && echo "偵測到 auth.json，將以已登入狀態開始錄製。"

echo "瀏覽器與 Inspector 會開啟：操作完要測的流程後，關閉瀏覽器即完成。"
node "$PWDEPS/playwright/cli.js" codegen --target javascript --channel chrome $AUTH_ARGS -o recording.js "$URL"

[ -f recording.js ] && echo "✅ 已錄製到 recording.js，回去跟助理說「錄好了」" || echo "⚠️ 沒有 recording.js，有錄到東西嗎？"
