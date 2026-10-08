---
name: gen-e2e-test
description: '產生自包含、可雙擊執行的 Playwright e2e 自動化測試：由 AI 直接撰寫測試腳本驅動操作流程、 被動攔截流程期間所有 API
  呼叫，跑完自動產出 Markdown + HTML 測試報告。產物是自帶 package.json 的資料夾，可整包交給別人雙擊使用；不綁特定站台。Make sure
  to use this skill whenever the user wants to 產生測試 / 做一個自動化測試 / 寫一支 e2e 測試 / 產一份
  API 測試報告 / 要一個可點擊的測試腳本 / generate an e2e test / capture API calls into a report——即使沒講
  「Playwright」。僅適用由 AI 直接撰寫測試、不需使用者手動操作的情境：使用者要親手操作畫面錄製 （「錄製」「錄」「codegen」「side-record」）時改用
  gen-e2e-record；前端 debug / UI 驗證 / console error 排查改用 $dev-browser，非本 skill。

  '
metadata:
  version: 1.2.3
  scope: test-generation
  produces_artifact: 'true'
compatibility: Designed for Claude Code; ported to Codex.
---

# gen-e2e-test — 自包含 Playwright 測試 + API 報告產生器

> **`SKILLS_ROOT`**: Codex does not expand plugin path variables inside skills. The first time a bundled script or reference is needed, resolve the absolute path of the directory that holds this skill's folder (the parent of the folder containing this `SKILL.md`) and use it as `SKILLS_ROOT` in every path below. If it cannot be resolved, stop and ask the user; never fall back to a cwd-relative path.

把「一段操作流程」變成一個**別人也能雙擊執行**的自動化測試，並自動彙整流程期間所有 API 呼叫成一份漂亮的報告。

核心價值：使用者通常只想要「跑一下、給我報告、能交給同事」。所以產物刻意做成**自包含資料夾**（自帶 `package.json`、首次雙擊自動 `npm install`）、**純 Windows 原生**（瀏覽器跑在本機，`localhost` API 才打得通）、**`.bat` 全 ASCII**（避免中文在 cmd 被 Big5 誤解析成亂碼指令）。這些都是踩過坑換來的，照做能省下對方一堆環境地獄。

---

## 這個 skill 的靈魂：先看畫面，再動手

模型的預設慣性，是把需求或錄製檔直接翻譯成 selector、再靠跑失敗試錯收斂。請反過來：動手寫任何非顯然的 selector 前，先用瀏覽器把那一步的**真實畫面**看過——這一步才知道目標是 chip / 連結 / icon 還是純文字、面板是不是預設展開（點了反而摺疊）、aria 文字要不要 hover 才出現、那筆資料/待辦到底在不在。讀檔看不到這些，看畫面才看得到。先看再寫，比寫完再試錯便宜得多。

另一個讀檔看不到的陷阱是**「登入帳號是資料依賴」**：隨手換成權限最廣的萬用 / 管理員帳號，往往那個帳號名下根本沒有要測的那筆待辦或資料，於是流程「全綠卻測錯了」。帳號是流程的一部分，不是隨便填的環境變數——這類站台專屬的事實，去 test-template 查，不要憑印象。

---

## ⛔ 登入無法自動化時：兩段式 auth 重用（**不要判定流程失敗**）

模型最常犯的錯：站台登入有**圖形驗證碼 / OTP / 簡訊 / SSO 跳轉 / 2FA**，自動登入那步點不過、卡在 `/login`，於是直接回報「流程失敗」就收工——**還不講為什麼**。這是錯的。登入過不去 ≠ 你要測的業務流程壞了；那是**登入機制本身不該被機器自動化**（驗證碼存在就是為了擋機器），不是 selector 找不到、也不是程式 bug。

**辨識「登入是 blocker」（命中任一就走兩段式，別判失敗）**：

- 登入頁有圖形驗證碼 / 滑塊 / 點選圖片 / reCAPTCHA。
- 登入要簡訊 / Email OTP / Authenticator 動態碼。
- 登入會跳到外部 SSO（公司 IdP、Google、AD）再導回。
- 自測卡在 `/login`，且頁面上看得到上述任一元素（用 inspect / 截圖確認，**不要憑空猜「大概是 selector 壞了」就一直改登入 selector**）。

**正解：把測試拆成兩段，登入只做一次、用手動。**

| | 做什麼 | 工具 | 頻率 |
|---|---|---|---|
| **Part 1 擷取** | headed 開瀏覽器，**你親手登入**（驗證碼自己填）→ 存 `auth.json`（storageState＝localStorage + cookies）**＋ `auth.session.json`（sessionStorage 快照）** | `capture-auth.mjs` / 雙擊 `capture-auth.bat` | 跑一次；token 過期再跑 |
| **Part 2 測試** | 引擎偵測到 `auth.json` 自動套用、`addInitScript` 還原 `auth.session.json`、**跳過登入**，`flow` 收到 `helpers.authed=true`，直接從業務頁開始 | `test.mjs`（引擎內建） | 可重複 headless 跑 |

為什麼用 `storageState` 而非手撈 JWT 字串：一次抓全（不必先搞清楚 token 放 localStorage 還是 cookie），整碗端走最保險。

### ⚠️ storageState 不含 sessionStorage（踩過、已實證的雷）

**Playwright 的 `storageState` 只存 localStorage + cookies，不存 sessionStorage。** 很多 SPA（Vue + `vuex-persistedstate`、Pinia persist 等）會把整個 store 快照存進 **sessionStorage**；只還原 storageState 的話，冷啟時 store 是空的 → app boot 讀不到狀態而拋錯（典型 `Cannot convert undefined or null to object`）→ **整頁白畫面**，即使 token 在、`VerifyToken` 之類 API 也照跑。**reload 救不了**（缺的是 sessionStorage 快照，不是 API 沒打）。

> 典型案例：某 SPA 把整個 Vuex store 存進 `sessionStorage`（例如 `sessionStorage.vuex`，可達數十 KB）。只套 `auth.json` → 列表頁 / 總覽頁全白頁、連導覽列都不出來、`pageerror` 連環。**補存 + 還原 sessionStorage 後** → 完整 render、業務清單有資料、明細可點。

對策（**範本已內建**）：`capture-auth` 另存 `auth.session.json`；引擎 `context.addInitScript` 在每個頁面載入前把它塞回 `sessionStorage`。換站台不必改，自動生效。

**眉角**：

- `auth.json` / `auth.session.json` 內含**活憑證＝等同帳密**，範本 `.gitignore` 已含，**不可進版控 / 外流**。
- token **會過期**：API 開始回 401 → 重跑 Part 1 重抓。固有限制，不是 bug，要對使用者講清楚。
- 後端若只綁某機 localhost，Part 1 的瀏覽器一樣要跟它同機（同既有環境限制）。
- `flow()` 寫法：登入段包在 `if (!authed) { ...登入... }`；`authed` 時**先 `goto` app 殼層讓 SPA 起來再走業務頁**，別冷連深層路由。範本預設 flow 已示範。
- **成功判定要看「畫面真的 render」**（某個已知 nav / 元素存在、`document.body.innerText` 有長度），**不要只看「URL 不是 /login」** —— 白頁的 URL 也不是 /login，URL-only 判定會給你假綠。

> 一句話自問：**我判「失敗」之前，有沒有確認那是業務流程壞了，還是只是登入機制擋機器？** 若是後者，走兩段式、講原因，不要回報 fail。

---

## 何時用

- 已經手動驗過一段流程，想固化成「之後雙擊重跑 + 出報告」
- 想把測試**交給不熟環境的同事**（匯出需求）

不適用：純單元測試（用該語言的測試框架）、不需要瀏覽器的 API 壓測。

---

## 產物長相

```
tests/<name>/
├── run-test.bat        ← Windows 雙擊入口（純 ASCII，首次自動 npm install）
├── run.sh              ← macOS/Linux 入口
├── package.json        ← 自包含，依賴 playwright
├── .gitignore          ← 忽略 node_modules / reports
├── test.mjs            ← 主腳本：CONFIG + FLOW（你編輯這段）+ 攔截引擎 + 報告引擎
└── reports/            ← 輸出：....md / ....html（每次跑都新檔）
```

報告含：環境、流程結果、API 統計（2xx/4xx-5xx/業務失敗）、狀態碼分布、API 總覽表、**每支 API 可展開看 Request/Response 的 Header 與 Body**、失敗明細。樣式為 Kami 風（紙色底 / 靛藍主色 / 襯線標題）。

---

## 工作流程

### Stage 0. 查站台記憶庫（動手前先做）

專案根的 `.claude/test-template/` 是站台專屬事實的記憶庫（登入片段、環境眉角、跑過的流程、難搞 selector）。動手前先確認它在不在、本站台有沒有現成可用的片段：

- 若 `.claude/test-template/` **不存在** → 先跑 `python $SKILLS_ROOT/gen-e2e-record/assets/init-test-template.py` 把骨架鋪好，再繼續。
- 若存在 → 用速查工具找本站台是否已有 `login` / `env` / `flow` / `selector` template：

  ```bash
  python .claude/test-template/query.py [關鍵字] [--site X] [--tag Y] [--kind Z]
  ```

  輸出會列出命中 template 的 id / kind / site / when / 路徑；對到的就 Read 進來照用。有現成登入 / 環境片段就直接套，不要重造。

做完這個 skill、若過程中產出了可重用的站台事實（穩定下來的登入流程、踩到的環境眉角、難搞的 selector），把它沉澱成新的 template 回寫記憶庫，下次就不必再看一遍畫面。

### Stage 1. 釐清（用 ask the user directly with numbered options, then stop; classify whether this is an authorization PAUSE before continuing，不要腦補）

至少問清楚：

| 項目 | 說明 | 預設 |
|------|------|------|
| 目標站台 base URL | 例 `http://localhost:<port>` | 問 |
| 起始路徑 / 流程步驟 | 要走的操作：開頁 → 點 → 填 → 送出 …（越具體越好） | 問 |
| 是否需登入 / 用哪個帳號 | **帳號是資料依賴**：要測的那筆待辦/資料屬於誰，就用誰；不要圖方便換成萬用/管理員帳號 | 問 |
| 後端 API host | 用來標記哪些是後端 API（例 `http://localhost:<api-port>`） | 同 base URL |
| 產物資料夾名 | `tests/<name>/` | 由流程命名 |

> **登入 / 環境片段先查 test-template**：先用 Stage 0 的 `query.py` 查本站台有沒有 `kind: login` / `kind: env` 的 template（例 `--site <站台代號> --kind login`）。有 → Read 進來直接套（含登入機制、成功判定、後端綁定限制等眉角），不必重看一次畫面。沒有 → 照下面通用原則做，做完把登入片段沉澱成新 template。

### Stage 2. 複製範本

把 `assets/` 全部複製到 `tests/<name>/`，並改名：

```
assets/test-template.mjs → test.mjs
assets/run-test.bat      → run-test.bat
assets/run.sh            → run.sh
assets/package.json      → package.json
assets/gitignore.txt     → .gitignore
```

### Stage 3. 編輯 `test.mjs` 兩個區塊（其餘不要動）

範本把「會變的」和「引擎」切開了。**只編輯這兩處**：

1. **`CONFIG`**：填 `BASE_URL` / `BACKEND` / `START_PATH` / 帳密等。
2. **`async function flow(page, { step, authed })`**：寫實際操作（`CONFIG` 是模組層變數，直接取用，不經參數傳入）。用 Playwright API（`page.goto / locator().click() / fill()`）。`step(n, msg)` 印階段進度。`flow` 回傳 `{ success, summary }`：`summary` 是 `[{label, value}]`，會顯示在報告「流程結果」。

攔截引擎與報告引擎**目標無關、原封不動沿用**——它掛 `page.on('request'/'response')` 收 xhr/fetch，並 `context.on('page')` 把攔截擴到每個新開的 popup，所以 **popup 的 API 會自動進報告（標記來源 `popup`），不用你改引擎**。

#### 先看畫面，再寫 selector（這一步是收斂關鍵）

寫每個非顯然的 selector 前，先用瀏覽器（playwright MCP / inspect）看那一步的真實畫面：確認元素到底是 chip / button / icon / tab、面板是不是預設就展開（再點一下反而摺疊）、aria 文字要不要 hover 才出現、目標資料在不在當前帳號名下。動態 class 框架（如以隨機後綴生成 class 的 UI 套件）用猜 class 最不可靠；先看再寫，能省掉後面一輪輪的試錯。

錄製檔（若來自 gen-e2e-record）只記得「點了什麼」，記不到上面這些決定成敗的畫面現實——所以拿到錄製檔也不能直接照抄，要對著畫面校一遍。

站台的登入段、已知難搞的 selector，優先用 Stage 0 從 test-template 查到的版本，不要重猜。

**Locator 優先序**：`getByRole(name)` > `getByLabel` / `getByPlaceholder` / `getByText` > `getByTestId` > CSS（僅 role 拿不到的元件內層 input 之類才用，且加注釋說明原因）。
`first()` / `nth()` 必附注釋說明為何唯一安全；禁止用 hover 才浮出的 tooltip 文字當定位依據。

#### popup / 新視窗

點擊會開新視窗時，先 `const popup = page.waitForEvent('popup')` 再點，之後對 `popup.*` 操作（不是 `page.*`）：

```js
const popupPromise = page.waitForEvent('popup');
await detailBtn.click();
const popup = await popupPromise;
await popup.waitForLoadState('domcontentloaded');
await popup.getByRole('tab', { name: '...' }).click();   // 對 popup 操作
```

popup 的 API 引擎已自動攔（`context.on('page')` 在 context 層攔截），你只需把 popup 的 UI 動作寫對。

### Stage 4. 驗證（不要跳過）

```bash
node --check test.mjs          # 語法
PREVIEW=1 node test.mjs        # 用假資料產 reports/preview.html，確認版型不爆
```

`PREVIEW=1` 不開瀏覽器、不需目標站台，純驗報告版型。

**能跑真站台時，AI 應自驅自測收斂，不要只丟給使用者**：在 app 主機 headless 跑 `test.mjs`、失敗就執行 `node $SKILLS_ROOT/gen-e2e-record/assets/inspect.mjs` 找穩定 selector 自動修、受停損保護、收斂後附「變更摘要」請使用者 headed 確認一次。完整迴圈見 **`references/verify-loop.md`**。

⛔ **不要在 WSL 端用 WSL 自己的瀏覽器對「後端只綁 Windows localhost」的站台跑**（localhost 不通）——改用 `verify-loop.md` 的 `powershell.exe` 橋接在 Windows 端 headless 跑。站台是否有此綁定限制，去 test-template 的 `env` template 查。

### Stage 5. 交付

告訴使用者：雙擊 `run-test.bat`（首次自動裝套件，用系統 Chrome）→ `reports\` 出現 `.html`，雙擊即可看。要匯出給別人就壓縮整個資料夾（`node_modules`/`reports` 可不附，對方首次雙擊會自動裝）。

收斂後若有可重用的站台事實，回寫 test-template（見 Stage 0）。

---

## 硬性眉角（違反會讓對方環境炸掉）

讀 `references/gotchas.md` 拿完整版（通用講法；站台具體值在 test-template 的 `env` template）。最關鍵三條：

1. **`.bat` 內容全 ASCII**：cmd.exe 用系統 Big5 解析 `.bat`，中文會變亂碼被當指令。所有中文訊息交給 node 輸出（node 是 UTF-8 + `chcp 65001`）。範本已遵守，**自行新增 .bat 內容時也只能用英文**。
2. **瀏覽器跑在後端同一台**：後端常只綁 `localhost`，瀏覽器必須原生跑在那台機器，不能在 WSL launch。範本用 Windows node + 系統 Chrome 正是為此。
3. **機敏值遮蔽**：報告會展開 Header/Body，範本已對 `authorization/cookie/token` 自動遮蔽，不要拿掉。

---

## 參考檔

| 檔案 | 何時讀 |
|------|--------|
| `references/verify-loop.md` | AI 要自驅把測試跑到收斂時 |
| `references/gotchas.md` | 組裝產物前確認通用環境眉角；站台具體值再轉去 test-template |

> 站台專屬事實（登入片段、環境眉角、跑過的流程、難搞 selector）一律在 `.claude/test-template/`，用 `query.py` 查（例：登入片段 `python .claude/test-template/query.py --site <站台代號> --kind login`、環境事實 `--kind env`），不要寫死在本 skill。
