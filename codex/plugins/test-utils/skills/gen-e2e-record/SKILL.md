---
name: gen-e2e-record
description: '錄製式測試產生器：開啟 Playwright 內建錄製器（codegen）讓使用者親手操作瀏覽器錄下一段流程， 錄完後分析錄製檔並轉成自包含、可雙擊、會攔截
  API 並產出報告的自動化測試（沿用 gen-e2e-test 的引擎與報告形態）。適用任何站台；由真人操作取得真實 selector，比憑空猜寫可靠。 Make
  sure to use this skill whenever the user wants to 錄製測試 / 錄一段操作變成測試 / 錄一個登入測試 / 邊操作邊產測試
  / 把我點的流程錄起來自動產測試 / 用 codegen / record a flow and turn it into a test——即使只說「錄」或「side-record」。
  凡測試產生需要使用者實際手動操作畫面時一律用本 skill；不需使用者操作、由 AI 直接撰寫測試則改用 gen-e2e-test。

  '
metadata:
  version: 2.1.0
  scope: test-recording
  produces_artifact: 'true'
  depends_on: gen-e2e-test
compatibility: Designed for Claude Code; ported to Codex.
---

# gen-e2e-record — 錄製操作 → 自動產生測試

> **`SKILLS_ROOT`**: Codex does not expand plugin path variables inside skills. The first time a bundled script or reference is needed, resolve the absolute path of the directory that holds this skill's folder (the parent of the folder containing this `SKILL.md`) and use it as `SKILLS_ROOT` in every path below. If it cannot be resolved, stop and ask the user; never fall back to a cwd-relative path.

讓使用者**親手在瀏覽器點一遍**要測的流程，把這段操作錄下來，再自動長成一支完整的自動化測試（自包含、可雙擊、攔截 API、出報告）。

為什麼要錄而不直接寫？因為 selector 用猜的最不可靠（尤其用動態 class 的前端框架，class 名每次 build 都可能變）。讓使用者實際操作，由 Playwright 官方錄製器 `codegen` 記下真實互動，遠比讀 code 猜畫面準。本 skill 的真正價值在「錄完之後」——把生硬的錄製檔轉成可執行測試，補上 API 攔截與報告。

> 本 skill 沿用 **gen-e2e-test**（同專案 skill）的測試引擎與報告形態。轉換時會讀其 `assets/` 範本。

---

## 核心原則：先看畫面，再動手

模型的預設慣性，是把錄製檔（`recording.js`）直接「翻譯」成測試流程、然後靠跑失敗 → 改 → 再跑的試錯來收斂。本 skill 刻意反過來：**轉換前先逐步用瀏覽器看每個錄製步驟的真實畫面、把每一步的 selector 定好、規劃完整流程，全部看懂了才開始寫測試。**

為什麼值得多花這一步？因為錄製檔只記得「點了什麼」（而且常是脆弱定位），它記不到**決定成敗的畫面現實**——而那些現實，讀檔永遠看不到：

- 面板或區塊**預設就是展開的**，你照錄製再點一次，反而把它**摺疊**起來，目標元素消失。
- 錄到看似「點某段文字」的動作，那段文字其實是一張 chip、一個連結、或一顆 icon 按鈕，不是純文字節點。
- 圖示按鈕的可讀標籤來自 **hover 才浮出的 tooltip**，沒 hover 時對應的 selector 命中 0。
- 同一個流程換成**沒有那筆待辦 / 沒有那項權限的帳號**，整列就無資料——**登入帳號本身是資料依賴**，是流程跑不跑得起來的前提。換成萬用 / 管理員帳號常會測出「綠但錯」的流程。

把「翻譯 + N 輪試錯」換成「看懂 + 一次寫對」，後面的復測就從「邊跑邊發現」降級成單純「確認連 2 次綠」。

> 一句話自問：**我有沒有親眼看過這一步的畫面，就開始寫 selector 了？** 若沒有，先看。

---

## 何時用

- 流程互動多、selector 不好猜（表單、下拉、多步驟），與其讀 code 不如讓使用者錄。

不適用：使用者要的是某個**已知、已沉澱成 template 的標準流程**（例如純登入），且沒有堅持要親手錄。那種直接用 `gen-e2e-test` + 站台 template 即可，不必重錄；可先告知有現成 template、確認後改走 `gen-e2e-test`。但使用者明確說要「錄」時，尊重其意圖照走本 skill。

---

## 工作流程

### Stage 0 — 查 test-template（動手前先看記憶庫）

通用原則留在本 skill；**站台專屬的事實**（怎麼登入、環境眉角、跑過的流程、難搞的 selector）放在專案的 `.claude/test-template/`。動手前先查那裡，有現成的就照用，別重新摸索。

```bash
# 沒有 test-template 目錄 → 先鋪好
python $SKILLS_ROOT/gen-e2e-record/assets/init-test-template.py

# 有了 → 查本站台是否已沉澱可用片段（kind 換成 login / env / flow / selector）
python .claude/test-template/query.py [關鍵字] --site <站台> --kind login
```

> 四類 kind 的完整 query 指令見 `references/codegen-to-flow.md` §0。

query 輸出命中 template 的 `id / kind / site / when / 路徑`，再 Read 載入照用。重點要查：

- `login`：這個站台怎麼登？穩定登入機制 + 帳號注意事項（避免拿萬用帳號測出假綠）。
- `env`：後端綁哪、瀏覽器要不要跟 app 同機、檔案編碼眉角。
- `flow`：要錄的流程是不是已經有人跑過並沉澱成骨架，可直接沿用或對照。
- `selector`：會用到的難搞元件（動態 class、icon 按鈕、popup 分頁…）有沒有現成定位法。

收尾時（Stage 7 收斂後）回填：把這次新確認的登入片段、環境眉角、跑通的流程骨架、難搞 selector，依 frontmatter schema 沉澱成新 template。重複比壞抽象便宜，但**驗證過**的流程值得留。schema 與目錄規則見 test-template README。

### Stage 1 — 釐清（ask the user directly with numbered options, then stop; classify whether this is an authorization PAUSE before continuing）

| 項目 | 說明 |
|------|------|
| 起始 URL | codegen 從哪一頁開始錄 |
| 要錄什麼流程 | 一句話描述（例「登入後到某查詢頁、按查詢、看結果」） |
| 登入帳號 | 用哪個帳號登？這流程的待辦 / 權限綁在哪個帳號上？（資料依賴，別預設萬用帳號） |
| 後端 API host | 標記後端 API 用 |
| 產物資料夾名 | `tests/<name>/` |

若站台已有 login template，登入段建議**手動登入後再開始錄業務流程**，轉換時登入段改用 template 的穩定片段（錄製器對自訂下拉 / 動態元件錄出的 selector 通常很脆）。

### Stage 2 — 佈署錄製器

把 `assets/` 複製到 `tests/<name>/`，改名 `gitignore.txt → .gitignore`，並把 `record.bat` 裡的 `set URL=` 改成起始 URL。

### Stage 3 — 請使用者錄製（互動，hard stop）

告訴使用者：

> 雙擊 **`record.bat`** → 會開一個瀏覽器與 Playwright Inspector → **在畫面上實際操作一遍你要測的流程** → 操作完**關閉瀏覽器視窗** → 錄製會存成 `recording.js`。完成後回來跟我說「錄好了」。

這一步是使用者手動操作，**不要替使用者亂點、也不要假裝錄好**。等使用者明確說完成再往下。

> **提醒使用者**：整段流程都在 **codegen 開的那個視窗**裡操作。由頁面**自動開出來的子 popup**（明細、檢視、流程圖等）codegen 跟得到；但**別自己另開一個獨立瀏覽器視窗**去點——那 codegen 錄不到，會變成測試的覆蓋黑洞（見 `references/codegen-to-flow.md` §7）。

> 環境眉角（瀏覽器要不要跟 app 同機、後端綁哪）因站台而異——先查 Stage 0 的 `env` template。

> 若已有 `auth.json`（`gen-e2e-test` capture-auth 產物），`record.bat` / `record.sh` 會自動帶 `--load-storage` 跳過重登入；但站台若依賴 sessionStorage（有些 SPA 用 Vue + vuex-persistedstate、Pinia persist 等會把整個 store 快照存進 sessionStorage），`--load-storage` 不足，仍走 capture-auth + addInitScript 路線，查站台 `env` template。

### Stage 4 — 逐步視覺勘查（轉換前必經，對抗「直接動手」）

使用者說錄好後，**先別寫 flow**。先讀 `recording.js`，再**逐步看每個動作的真實畫面**，把每一步定案成一份「selector 規劃表」。能跑真站台時這一步由 AI 自驅；站台沒開則降級（見末段）。

**首選工具 `assets/walk.mjs`**（本 skill 已 bundle）：逐行重播 `recording.js`、每個動作後**截圖到 `reports/walk_<n>.png` + 印出當下 URL 與該元素的真實樣貌**；某行定位失敗時自動 dump 候選 selector。

```bash
node walk.mjs            # 重播 recording.js，逐步截圖 + dump
```

> 跑法因環境而異（同機直接 `node`；跨機如 WSL→Windows 需橋接 + 指定共用 Playwright deps）。細節查 Stage 0 的 `env` template。

兩個最關鍵提醒：**登入帳號是資料依賴**——walk 重播的就是使用者錄製當下的帳號，照它走最準，別偷換成萬用 / 管理員帳號；**popup / 新視窗裡的動作絕不能漏**，flow 要對 popup 物件操作。

> 規劃表格式與「畫面現實」清單見 `references/codegen-to-flow.md` §0「逐步視覺勘查」。

**降級（站台沒開、AI 不在 app 主機且無橋接）**：不能 walk 就**請使用者邊看畫面邊回報**每步點到的是什麼元素，或請使用者各步截圖；仍以「先確認再寫」為原則，不要憑 recording.js 盲轉。

### Stage 5 — 轉換：依規劃表寫 flow

規劃表確認後（不是從原始 `recording.js`，而是從**看過畫面定案的規劃表**）：

1. 依 `references/codegen-to-flow.md` 把規劃表的每一步寫成 `gen-e2e-test` 的 `flow(page, { step })` 函式（插入 `step()` 階段、組 summary）。
2. 從 `../gen-e2e-test/assets/` 複製測試引擎範本與 `run-test.bat` / `run.sh` / `package.json`（已有就合併），把引擎裡的 `flow()` 換成轉好的、`CONFIG` 填好起始 URL / 後端 host / 起始路徑（含勘查時定案的登入帳號）。
3. 登入段改用穩定方式——優先用 Stage 0 查到的站台 `login` template 片段，或勘查時實際看到的登入機制，只保留錄到的「登入後」動作（錄製器對自訂登入元件錄出的 selector 容易壞）。
4. **登入無法自動化（圖形驗證碼 / OTP / SSO / 2FA）**→ 不要硬寫登入、更不要因此判流程失敗。改走 `gen-e2e-test` 的**兩段式 auth 重用**：`capture-auth.bat` 手動登入存 `auth.json` + `auth.session.json`，引擎偵測到就跳過登入。完整決策與 sessionStorage 眉角見 `../gen-e2e-test/SKILL.md` §「登入無法自動化時」。

### Stage 6 — 靜態驗證

- `node --check test.mjs`、`PREVIEW=1 node test.mjs`（環境連不到站台也能驗語法 / 版型）。

### Stage 7 — AI 自驅審測迴圈（必經，不可只交付）

> **若 Stage 4 視覺勘查做足，這一步應該是「確認」而非「發現」。** 你已親眼看過每步畫面、定好 selector，所以這裡的目標是**連 2 次跑綠、確認和手動錄製對齊**，而不是邊跑邊摸索。若這裡還在大量發現新 selector 問題 → 代表 Stage 4 沒看夠，回頭補勘查，不要硬在這裡試錯。

這一步**由 AI 自驅，不用每輪等使用者**。完整演算法（自測 → 診斷 → 改 → 停損 → 收斂）見 **`../gen-e2e-test/references/verify-loop.md`**，重點：

1. **AI 自測**：在 app 主機 headless 跑測試。站台沒開 → 不硬跑，降級請使用者跑。
2. **有界自主修正**：某步失敗 → 跑 `inspect.mjs` 找穩定 selector（結構 / icon，**禁** hover-tooltip 才有的可讀文字，見 `references/codegen-to-flow.md` §5b），自動改 flow，**並把每次改動記進「變更摘要」**，再自測。
3. **停損**：停損閾值以 `../gen-e2e-test/references/verify-loop.md` 為準；觸及閾值、或偵測到「無資料 / 無權限」→ **停**，帶 `inspect` 診斷 + 已試方案回報使用者，不空轉湊綠。
4. **收斂**：流程結果成功、錄製每步都跑到、且**連跑 2 次都綠** → 收斂。
5. **交付（使用者第 2 個、也是最後一個觸點）**：給報告 + **自動修正摘要**（逐條列補了哪些 selector / 捲動 / 等待及原因），請使用者 **headed 雙擊 `run-test.bat` 確認一次**，重點審摘要裡的 selector 是否點到對的東西（擋 AI 改成錯元素的假綠）。
6. **回填 test-template**（Stage 0 收尾）：把這次跑通的流程骨架、新確認的登入 / 環境片段、難搞 selector 沉澱成新 template。

> 使用者全程只碰兩個觸點：**①Stage 3 錄製、②Stage 7 最終 headed 確認**。中間 AI 自驅。

---

## 硬性眉角

1. **`.bat` 全 ASCII** — 中文在 cmd 會被當地編碼誤解析成亂碼指令。中文訊息交給 node 印。
2. **codegen 用系統 Chrome** — `--channel chrome`，不下載整包 chromium。
3. **錄製必須使用者親自操作** — Stage 3 是 hard stop，等使用者回報完成才往下。
4. **自訂登入元件別信錄製器** — 錄出的 selector 脆，改用 Stage 0 站台 login template 的穩定片段。
5. **轉換前先看畫面** — Stage 4 視覺勘查是 hard gate：沒逐步看過畫面、沒定好每步 selector，就別開始寫 flow。漏掉＝退回「盲轉 + N 輪試錯」的舊慣性。
6. **必經復測對齊** — 轉好的測試一定要真機跑到「和手動錄製一樣會成功」、連 2 次綠才算完成。漏掉這步＝交付一支會 timeout 的測試。

## 參考檔

| 檔案 | 何時讀 |
|------|--------|
| `references/codegen-to-flow.md` | **Stage 4/5 必讀**：§0 逐步視覺勘查（walk.mjs + 規劃表）、動作對應表、登入段替換、清理規則、tooltip 雷 |
| `../gen-e2e-test/references/verify-loop.md` | **Stage 7 必讀**：AI 自驅審測迴圈（自測 / 診斷 / 停損 / 收斂 / 變更摘要的完整演算法） |
| `../gen-e2e-test/SKILL.md` | 測試引擎 / 報告 / 交付規範（本 skill 沿用其產物形態） |
| `../gen-e2e-test/references/gotchas.md` | Stage 5/6 環境眉角（`.bat` 全 ASCII、瀏覽器與後端同機等） |
| `.claude/test-template/README.md` | **Stage 0 必讀**：記憶庫切分、frontmatter schema、目錄規則、回填方式 |
| `$SKILLS_ROOT/gen-e2e-record/assets/init-test-template.py` | Stage 0：無 test-template 目錄時鋪好骨架 |
| `.claude/test-template/query.py` | Stage 0：查本站台已沉澱的 login / env / flow / selector |
