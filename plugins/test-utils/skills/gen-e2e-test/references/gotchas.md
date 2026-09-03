# 環境眉角 — 組裝產物前必讀

這些是實際踩出來的通用坑。範本已全部處理；自行改動時別把它們改掉。**站台專屬的具體值**（哪個 port、後端綁不綁 localhost、哪些帳號可用）不在這裡——去 `.claude/test-template/env/<站台>.md` 查（`python .claude/test-template/query.py --site <站台> --kind env`）。

## 1. `.bat` 內容必須全 ASCII（最常爆的雷）

cmd.exe 讀 `.bat` 時用**系統 ANSI codepage**（繁中 Windows = Big5/950）解析檔案內容，**不是 UTF-8**。若 `.bat` 存成 UTF-8 又含中文，中文 byte 會被 Big5 誤解析成一堆亂碼 token，cmd 把它們當指令執行 → 噴「'xxx' 不是內部或外部命令」。`chcp 65001` 也救不了，因為解析發生在 chcp 生效前。

**對策**：`.bat` 內所有文字（echo / REM / title）只用英文 ASCII。需要中文訊息一律交給 node 程式輸出（node 是 UTF-8，配 `.bat` 開頭 `chcp 65001 >nul` 在 console 正常顯示）。

> 自我檢查：`grep -nP '[^\x00-\x7F]' run-test.bat` 必須無輸出。

## 2. 瀏覽器要跑在「後端同一台」

很多後端只綁 `localhost`，不對外。若用 WSL/容器 launch 瀏覽器去測 Windows 上的站台，瀏覽器內的 `localhost:<api-port>` 指向的是 **WSL 自己的 localhost**，打不到 Windows 後端 → 所有 API connection refused，報告全紅。

**對策**：產物設計成 **Windows 原生 node + 系統 Chrome**（範本的 `run-test.bat` 正是如此），瀏覽器與後端同在 Windows，`localhost` 才一致。

**這也代表**：你（AI）在 WSL/Linux 環境**無法對這種站台實跑驗證**。驗證分兩段：
- 版型 / 語法：`node --check test.mjs` + `PREVIEW=1 node test.mjs`（不開瀏覽器，可在任何環境跑）
- 真實流程：在 app 所在主機 headless 跑（見 `verify-loop.md`），或請使用者在 Windows 雙擊 `run-test.bat`

> 某站台的後端到底綁不綁 localhost、API port 多少，是站台事實 → 查 `.claude/test-template/env/<站台>.md`。

## 2b. AI 自測 → 見 `verify-loop.md`

AI 自驅把測試跑到收斂的完整迴圈（環境表、迴圈演算法、停損、變更摘要）見同目錄 `verify-loop.md`，兩個 skill 共用，此處不重複。

## 3. Playwright 模組解析

範本 `loadPlaywright()` 先試 `require('playwright')`（自包含安裝後從本地 node_modules 解析），失敗才退回 global（`npm root -g`）。產物自帶 `package.json`，首次 `npm install` 後就有本地 playwright，最穩。

## 4. 不下載內建瀏覽器、改用系統 Chrome

`npm install playwright` 預設會下載 ~130MB chromium，公司網路常被擋。範本在安裝時設 `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1`，啟動時走「系統 Chrome → Edge → 內建 chromium」fallback。多數電腦有 Chrome，省時且避開下載失敗。沒有 Chrome 的機器再 `npm run install-browser`。

## 4b. 共用一份 node_modules（本地省重裝）

本地一直產測試資料夾時，不想每個都各裝一份 playwright。`run-test.bat` / `record.bat` / `run.sh` 的相依解析是三段：

1. **shared** — 測試資料夾的上一層 `..\.e2e-deps\node_modules`（多個測試資料夾共用一份，裝一次）
2. **local** — 自己的 `node_modules`
3. **install** — 都沒有才裝；優先裝進 shared（`tests/.e2e-deps/`），失敗才本地裝

解析到的路徑用 **`NODE_PATH`** 餵給 node，`loadPlaywright()` 的 `require('playwright')` 即可解析共用安裝。**codegen** 因為 `npx` 不吃 NODE_PATH，改用 `node "<deps>\playwright\cli.js" codegen` 直接指 CLI。

**匯出給別人**：對方解壓的資料夾沒有 `..\.e2e-deps` → 自動 fallback 到本地裝，仍可雙擊自包含。要完全離線可先在資料夾內 `npm install` 帶著 `node_modules` 一起給。

> `tests/.e2e-deps/` 是純相依快取，已 gitignore；刪掉也只是下次重裝。

## 5. headless vs headed

預設 **headed**（看得到瀏覽器），給人跑比較安心、也方便目視流程。要背景跑設 `HEADLESS=1`。

## 6. 機敏值遮蔽

報告可展開 Request/Response Header，範本對 `authorization` / `cookie` / `token` 自動遮蔽（只留前後幾碼）。報告可能被轉傳，別把遮蔽拿掉。站台若有其他自訂的機敏 header / 欄位，記在該站台的 `env` template，組裝時一併納入遮蔽。

## 7. 被動攔截只收 API

`page.on('request'/'response')` 只保留 `resourceType` 為 `xhr` / `fetch` 的請求，排除 js/css/img 等靜態資源。`HTTP 200` 不代表成功，報告額外解析 body 的 `isSuccess` / `returnCode`（多數後端慣例），標出「業務失敗」。各站台的成功判定欄位若不同，記在該站台 template。
