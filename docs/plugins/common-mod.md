# `common-mod` — Claude Code mod

回到 [文件索引](../README.md)。

<img src="../images/plugin-common-mod.png" alt="common-mod" width="320">

Claude Code 專屬的 mod：在 CLI 與桌面版 Code 分頁裡畫出介面元件的 function hooks，沒有 slash command。預設啟用（`defaultEnabled: true`），不需要可用 `claude plugin disable common-mod` 停用。**Codex 沒有對應版本**：mod 屬於 Claude 專屬元件，不移植到 `codex/`。

- Claude source：`plugins/common-mod/`（`hooks/bar/`、`hooks/recall/`、`hooks/side/`）
- 版本：見 `plugins/common-mod/.claude-plugin/plugin.json` 與 [CHANGELOG](../../CHANGELOG.md)
- 安裝：`/plugin install common-mod@common-dev`

## 三個 mod

### bar — 狀態列

輸入框上方的兩列狀態列：資料夾、模型與動態 ctx、5h 與 7d 用量儀表，接著是按鈕：

| 按鈕 | 做什麼 |
|------|--------|
| 側聊 | 開側聊面板（見下方 side） |
| 回想 | 開回想搜尋（見下方 recall） |
| diff | 開 diff 面板（只在終端機） |
| artifacts | 開 artifacts（只在終端機） |
| 看不懂 | 呼叫 `/common:wait-what` |
| 畫給我看 | 呼叫 `/common:show-me` |
| 下一步 | 產生下一步建議，以草稿放進輸入框 |

終端機與桌面版各自繪製：終端機用霓虹儀表與 chip；桌面版用原生按鈕與 SVG 儀表，沒有 diff 與 artifacts。「看不懂」與「畫給我看」會改用專案自己的 wait-what 與 show-me skill（若有）；專案可在 `.claude/common-mod.json` 加自己的按鈕。

### recall — 回想

在輸入框打 `#` 或按「回想」，輸入框上方會出現一條搜尋帶，可搜尋過去的 Claude Code、桌面版與 Cowork 對話。點一段會把它的 `#chat:<id>` token 放進輸入框，送出時附上那段對話作為引用內容。

設定 `recallExtraRoots`（`userConfig`）：除了 `~/.claude/projects` 之外要一起搜尋的資料夾，用分號分隔，例如 WSL 的對話紀錄資料夾。

### side — 側聊

按「側聊」在對話旁開側聊面板，像 diff 面板那樣停靠；面板從這段對話的 fork 回答，不使用工具。要換模型或動手做時，從面板開新視窗分支（可換模型、使用工具），分支裡的「帶回主線」會把總結送回主 session。
