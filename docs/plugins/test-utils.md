# `test-utils` — E2E 測試工具

回到 [文件索引](../README.md)。

<img src="../images/plugin-test-utils.png" alt="test-utils" width="320">

三個互補的 skill，Claude 用 `/test-utils:<skill>`、Codex 用 `$<skill>` 呼叫。預設啟用（`defaultEnabled: true`）。

- Claude source：`plugins/test-utils/`
- Codex 移植：`codex/plugins/test-utils/`
- 版本：見 `plugins/test-utils/.claude-plugin/plugin.json` 與 [CHANGELOG](../../CHANGELOG.md)

## Skills

| Skill | 做什麼 | 什麼時候用 |
|-------|--------|-----------|
| `gen-e2e-test` | 產出一個**自帶相依、可雙擊執行**的 Playwright 測試：跑完整流程、被動側錄每一個 API 呼叫，並輸出 Markdown + HTML 報告。產物是一個自帶 `package.json` 的資料夾，可直接交給同事。 | 由 AI 直接撰寫測試，不需人工錄製。 |
| `gen-e2e-record` | 開 Playwright **codegen** 讓人實際操作錄一遍，再把錄製轉成 `gen-e2e-test` 風格的測試（用真實互動產生的真實 selector）。依賴 `gen-e2e-test`。 | 流程互動多、selector 難猜時。 |
| `dev-browser` | 透過 `dev-browser` CLI 做具持久頁面狀態的 **agent 端**瀏覽器除錯：檢查 console、DOM、API response、畫面與修正後結果。 | agent 要直接互動式排查或驗證 UI，而不是產出可散佈測試時。 |

`gen-e2e-test` 負責由 AI 直接撰寫，`gen-e2e-record` 負責把使用者實際操作轉成同格式測試；`dev-browser` 則保留給 agent 的即時 UI 排查、API 驗證與修正後複驗。`common-lab:jev-browser` 是建立在 `dev-browser` 上、以 Jev 挑選元素的實驗版。

## 相依

- **`gen-e2e-test` / `gen-e2e-record`**：需要 Node.js。產出的測試首次執行時自動裝 Playwright（`npm install`）；錄製用系統 Chrome（`--channel chrome`）。
- **`dev-browser`**：需要外部 `dev-browser` CLI：
  ```bash
  npm install -g dev-browser && dev-browser install
  ```
  在 settings 允許 `Bash(dev-browser *)`；Playwright MCP 可作為備援。

## 專案端記憶庫

`gen-e2e-*` 會把站台專屬事實（登入片段、環境眉角、難搞的 selector、驗證過的流程）存進你專案的 `.claude/test-template/`，透過內附的 `query.py` 查詢。通用指引留在 skill 裡，專案事實絕不寫死進 skill。
