# `common` — 通用工具

回到 [文件索引](../README.md)。

<img src="../images/plugin-common.png" alt="common" width="320">

不綁定特定情境的通用開發輔助；Claude 用 `/common:<skill>`，Codex 用 `$<skill>` 呼叫。預設啟用（`defaultEnabled: true`），不需要可用 `claude plugin disable common` 關閉。

- Claude source：`plugins/common/`
- Codex 移植：`codex/plugins/common/`
- 版本：見 `plugins/common/.claude-plugin/plugin.json` 與 [CHANGELOG](../../CHANGELOG.md)

## Skills

| Skill | 簡介 |
|-------|------|
| `better-prompts` | 依 Claude 與 GPT 官方 prompting guidance 審核、改寫、起草或遷移 prompts 與 agent instructions。 |
| `delegate` | 將邊界清楚、可驗證的工作派給 native sub-agent、Codex CLI 或 Claude CLI；Codex 可原生 pin model／effort，Fast 與精確 profile 另保留 CLI fallback。 |
| `define-goal` | 把模糊意圖整理成有驗證證據、明確邊界與停止條件的可驗收目標。 |
| `strategic-advance` | 鎖定可驗收的戰略目標，以即時情報、單一主攻與可驗證的一動持續推進長期任務；內建自含 HTML 沙盤 renderer，直接 render，不另設環境 preflight 或 legacy mode。 |
| `wait-what` | 停下目前工作，從斷掉的那個連結開始，按「哪裡沒懂」挑講法重講；純文字，圖另叫 show-me；只在明確叫用時觸發。 |
| `wayfinder` | 把一個 session 裝不下的大工作畫成決策票地圖，逐票或以 drain 模式推進到路線清楚；內建自含 HTML 地圖 renderer。 |
| `token-lens` | 唯讀分析 Codex session：逐回應 token、重複讀取、巨大輸出與壓縮成本；附可篩選時間線與工項貢獻標記，協助驗證 Skill 改進假設。 |
| `show-me` | 用最小的視圖（pseudocode、call tree、diff、Mermaid、HTML）講清楚；Mermaid 同時產生並開啟 HTML 預覽。 |
| `grilling` | Matt Pocock 原版：以設計樹分輪訪談，事實模型自查、決定由人下，直到前線為空。 |
| `domain-modeling` | 釐清專案領域語言，將共識寫入 `CONTEXT.md`，必要時記錄 ADR。 |
| `research` | 派背景 agent 查證一手來源，將附引用的發現整理成 repo 內的 Markdown。 |
| `prototype` | 用可拋棄的邏輯 demo 或 UI variants 快速回答設計問題，再把驗證結果折回正式實作。 |

`grilling`、`domain-modeling`、`research`、`prototype` 是 wayfinder 的四個附屬 Skill。

## Bundled agents

| Agent | 用途 |
|-------|------|
| `luna-max-sidekick` | `delegate` 用的可重用執行 sidekick 角色（`plugins/common/agents/luna-max-sidekick.md`）。 |
| `sa-scribe` | `strategic-advance` 每次整併時派出的無狀態戰役書記（`plugins/common/agents/sa-scribe.md`）。 |

Codex 版放在 `codex/plugins/common/.codex-agents/*.toml`；Codex 不會自動註冊這個目錄，由使用它的 skill 自行載入，找不到時 fail closed（`AGENT_DEFINITION_MISSING`）。

## 與其他 plugin 的關係

- `analysis-estimation:cold-estimation` 在開場決策問題中引用 `common:show-me` 講解；Cold 與 common 的 show-me 末尾均保留 `Say what you mean` 原文。
- `common-mod` 狀態列的「看不懂」與「畫給我看」按鈕分別呼叫 `/common:wait-what` 與 `/common:show-me`。
- Lab 版疊加技能（`*-jever`）在 [common-lab](common-lab.md)；派工一律用 `common:delegate`。

## Show Me 的來源

`show-me/SKILL.md` 以 [HumanLayer 上游](https://github.com/humanlayer/skills/blob/main/plugins/show-me/skills/show-me/SKILL.md) 原文為基礎，末尾補上 `Say what you mean` 的對話收束指引；Codex 版本由 transfer 產生平台適配。HumanLayer 的完整 MIT 版權與許可聲明保留在技能目錄的 `LICENSE`，不重複放進技能正文。（舊版 README 將這段放在「Common Lab 的 Show Me 來源」標題下；show-me 已畢業到穩定版 `common`。）
