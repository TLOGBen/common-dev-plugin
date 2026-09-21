---
name: jev-browser
description: >
  Browser debugging with TypeSafe Jev element picking, built on test-utils dev-browser: index the visible
  interactive elements, let Jev pick the target in one Choice call, and read only the candidates instead of
  the whole DOM. Invoke explicitly as /common-lab:jev-browser; use test-utils dev-browser for normal browser debugging.
allowed-tools: Bash, WebFetch, Read, Grep, Glob, Edit, AskUserQuestion
metadata:
  version: "1.1.2-lab.1"
  scope: browser-debug-and-review
  produces_artifact: "false"
  priority: primary
---

# Jev Browser — Frontend Browser Validation + Jev Element Picking

> **Lab 差異**：與 `test-utils:dev-browser` 相同，只多一個情境「找要操作的元素」（Section 3 最後一列）。要在頁面上找元素時，先跑 `element-table.js` 再跑 `jev-pick.mjs`，只讀候選，不要把整份 `snapshotForAI()` 印出來截斷。Jev 的答案是候選不是證據，操作後照樣要驗證。

> Use this for **stateful, interactive diagnosis** against a live browser. Use Playwright for repeatable automation and `gen-e2e-*` when the outcome is a distributable test artifact. ⛔ No guessing — observe facts in the browser.

> Output all reports, diagnostics, and user-facing messages in **繁體中文**.

---

## 標準 Session 三步流程

> ⛔ 不要跳過連線檢查。登入只在目標流程需要 authenticated state 時執行；公開頁、blank page、console 與純視覺排查不應被登入阻塞。

```
Step 1: 啟動 Chrome debug 連線（Section 1–2）
Step 2: 若任務需要登入，再跑 login.js 確認 authenticated state
Step 3: 執行任務（Section 3 選對應 template）
```

---

## 0. Read the live CLI contract

每個 session 先執行 `dev-browser --help`。當 live help 與 bundled reference 衝突時，以目前安裝版本的 live help 為 API 真相；若 command 不存在，回報缺少 dependency 並停止，不要猜舊 API。

---

## 1. Pre-flight — Check Port Status

> 以下 port 為範例佔位；請改成你自己專案的前端 / 後端 port。

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000   # 前端 dev server（範例）
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080   # 後端 API（範例）
```

| Output | Status |
|--------|--------|
| `200` / `3xx` | ✅ Running |
| `000` | ❌ Not started |

If not running, inform the user:
- Frontend → 啟動前端 dev server（例如 `npm run dev`）
- Backend → 啟動後端 API 服務

---

## 2. Launch dev-browser；需要 authenticated state 才登入

**Mode A — 連 Windows Chrome（推薦，可目視畫面）**

依環境二擇一：

**A1 — Native Windows（PowerShell）**：直接連 `127.0.0.1:9222`，不需 portproxy/防火牆。

```powershell
pwsh ${CLAUDE_PLUGIN_ROOT}/skills/jev-browser/scripts/setup-chrome-debug.ps1
```

| 參數 | 用途 |
|------|------|
| _(無)_ | 啟動 Chrome + 驗證連線 |
| `-NoChrome` | 跳過啟動（Chrome 已開時用），只驗證連線 |
| `-Cleanup` | 結束所有 debug Chrome 進程 |

**A2 — WSL2 連 Windows Chrome**：需 portproxy 跨 WSL2 ↔ Windows。

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/jev-browser/scripts/setup-wsl2-chrome-debug.sh
```

| 參數 | 用途 |
|------|------|
| _(無)_ | 完整設定：啟動 Chrome + portproxy + 防火牆 |
| `--no-chrome` | 只補 portproxy（Chrome 已開時用） |
| `--cleanup` | 移除 portproxy 與防火牆規則 |

> 防火牆規則永久生效；portproxy 和 Chrome 重開機後消失，需重跑腳本。
> 詳細說明見 `references/setup-wsl2-chrome.md`。

### ▶ Authenticated flow 才執行：跑 login template

目標頁面、API 或驗證條件需要 authenticated state 時才執行 `login.js`。公開頁、blank page、console error 與不需權限的 UI 驗證直接進 Section 3。

```powershell
# A1 Windows PowerShell
dev-browser --connect http://127.0.0.1:9222 run ${CLAUDE_PLUGIN_ROOT}/skills/jev-browser/scripts/case/login.js
```

```bash
# A2 WSL2
HOST_IP=$(ip route show default | awk '/default/ {print $3; exit}')
dev-browser --connect http://${HOST_IP}:9333 run ${CLAUDE_PLUGIN_ROOT}/skills/jev-browser/scripts/case/login.js
```

> **登入驗證（必檢）**：login.js 跑完後，登入成功的可觀察判準是 console 印出 token 存在的標記（例如 `localStorage.getItem('[your-token-key]')` 非空、或 login.js 輸出 `LOGIN_OK` 之類的明確標記）。
> **若 authenticated task 的判準未出現（登入靜默失敗）→ 立刻停止該 authenticated flow**；改去讀 `references/gotchas-login.md` 檢查 JWT location 與自訂下拉元件（v-combobox），修正後重跑 login.js，直到判準出現為止。

> 改帳號：複製到 `.agent-workspace/`，改 `USER_ID`，再 `run <複製後的路徑>`。
> 客製腳本同樣流程：複製 template 改參數，用 `run <file>` 跑。

**收工時務必清掉 debug Chrome**（避免進程殘留 + port 佔用）：
```powershell
# Windows
pwsh ${CLAUDE_PLUGIN_ROOT}/skills/jev-browser/scripts/setup-chrome-debug.ps1 -Cleanup
```
```bash
# WSL2
bash ${CLAUDE_PLUGIN_ROOT}/skills/jev-browser/scripts/setup-wsl2-chrome-debug.sh --cleanup
```

**Mode B — headless Chromium（Chrome 未開或 portproxy 未設時的備用）**

```bash
dev-browser <<'EOF'
const page = await browser.getPage("app");
await page.goto("http://localhost:3000/login", { waitUntil: "domcontentloaded" });  // /login 為範例路由，換成你自己的
console.log(await page.title());
EOF
```

> ⚠️ headless 模式下自訂下拉/登入元件容易 timeout，請改用帳號直填方式（見 `references/case-login.md`）。

---

## 3. Pick a Golden Template by Situation（連線完成後執行；登入依任務需求）

**查詢順序**：先看 Template 欄 → 有現成腳本就 `run <file>` 直接跑（改檔頭參數即可）；沒有再讀 Reference 拿說明 + 內嵌腳本。

| Situation | Template（首選） | Reference（備援 + 說明） | Summary |
|-----------|-----------------|--------------------------|---------|
| Authenticated flow + basic debug | `scripts/case/login.js` | `references/case-login.md` | Login → DOM / console error / store diagnostics |
| window.open 新分頁操作 | `scripts/case/new-tab.js` | `references/case-new-tab.md` | 攔截 window.open 取 URL；或 waitForEvent 真實開分頁 |
| API testing / data validation | _(尚未建立)_ | `references/case-api.md` | Single / batch fetch with JWT token |
| Page review / screenshot | _(尚未建立)_ | `references/case-review.md` | Interact → screenshot → DOM verification |
| 找要操作的元素（Lab：Jev） | `scripts/case/element-table.js` + `scripts/jev-pick.mjs` | `references/case-jev-pick.md` | 可操作元素編號表 → Jev 挑前 3 名 → `[data-jev-idx]` 操作 → 驗證；無 `TYPESAFE_API_KEY` 或低信心時改用 `snapshotForAI()` |

### 新增情境的標準三件套

跑完不在上表的新流程後，**主動以 `AskUserQuestion` 詢問使用者是否新增情境**。確認後一次完成：

1. **Template** — 寫 `scripts/case/<name>.js`（檔頭加反向連結 → reference）
2. **Reference** — 新增或擴充 `references/case-<name>.md`（頂端加 🔗 指向 template + 跑法 + 參數說明）
3. **SKILL Section 3** — 在上表加一列（Situation / Template 路徑 / Reference 路徑 / Summary）

> 缺任一件都不算完成：只存 .js 沒被索引等於沒存；只更新 SKILL 沒寫 Reference 等於沒文件。

---

## Quick References

- **Route index 範本**: `references/route.md`（通用路由索引範本，填入你自己專案的實際路由）
- **Gotchas**:
  - `references/gotchas-sandbox.md` — QuickJS sandbox limits (no require/fetch at top level)
  - `references/gotchas-vuetify.md` — Vuetify component quirks (v-select, overlay, animation)
  - `references/gotchas-login.md` — 自訂下拉/登入元件注意事項 (v-combobox, JWT location)

---

## Core Rules

| Rule | Reason |
|------|--------|
| Always name the page `"app"` | Keeps session alive across script runs — no re-login needed |
| All API calls need a token | `localStorage.getItem('[your-token-key]')`（`jwtToken` 只是範例 key） |
| HTTP 200 ≠ success | Always check `isSuccess` / `returnCode` / `data` in the response body |
| Re-run the script after every code change | Not verified = not fixed |
| Use `domcontentloaded` on dev servers | `load` can hang on HMR connections |
| PowerShell：現成 template 用 `run <file>`；臨時多行腳本用 here-string pipe | 目前 CLI 兩者皆支援；以 `dev-browser --help` 的 live guide 為準 |
| 收工時跑 `setup-chrome-debug.ps1 -Cleanup`（PS）/ `--cleanup`（WSL2） | debug Chrome 用獨立 profile 不會自己關，殘留會佔 9222 port |
| 跑完新情境流程後，主動以 `AskUserQuestion` 問是否新增「情境 + template」三件套 | 重複手寫腳本浪費時間；單存 .js 沒被 SKILL/Reference 索引等於沒存 |
