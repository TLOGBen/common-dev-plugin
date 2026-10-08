# 兩家模型陣容與分工驗證（2026-10-08）

> 證據等級標示：**【官方】** 官方文件或公告原文；**【本機】** 本機 CLI 實測；**【推論】** 我根據前兩者推出來的結論，官方沒有直接這樣說。
> 所有來源已用 `/baransu:read --save` 的流程存到 `.claude/read/material/<slug>/index.md`（見文末來源清單；這次以腳本批次跑 curl → markitdown → material/ + index.md，**沒有下載頁面圖片**）。

## 摘要結論

1. **「兩家今天都發新模型」不正確。** 今天（10/8）沒有新模型。最近的發布：Haiku 5.5 與 Sonnet 5.5 cache read 降價是 **10/7**；Sonnet 5.5 是 9/28、Opus 5.5 是 9/22、Fable 5.1 是 9/1。OpenAI：GPT-6.1 Sol 9/29、GPT-6 Sol／Luna 9/22、GPT-6 Astra 9/3。**Terra 沒有 6 代**，現行的仍是 GPT-5.6 Terra，Codex 目錄標示為「Older balanced model」。【官方】
2. **「Sonnet 5.5 cache read 降價 50%、大多數 agentic 任務約便宜 20%」屬實**：$0.20 → $0.10／MTok，出自 10/7 的 Haiku 5.5 公告；同一句話也寫在 Sonnet 5.5 what's-new 頁。【官方】
3. 提案表**保留** 4 列：lead＝Opus 5.5、Sonnet 5.5 改當中型有界實作 subagent、Haiku 5.5 負責搜尋／摘要／壓縮／分類、最小單位用 Haiku 5.5。**修正** 3 列：
   - **Fable 5.1**：官方定位是「Opus 5.5 調到較高 effort 仍不夠時才升級」，不建議當例行 reviewer；改成升級用或 advisor。
   - **Astra 6**：官方定位是「最難的端到端工作」，不是「快速抓 bug」；Codex 計價是 Sol 6.1 的 5 倍。
   - **Sol 6.1**：官方定位是「接近 Astra、Codex 複雜工作的起點」，不是雜務；雜務應給 Luna 6。
4. **Terra 5.6 沒有適合的位置【推論】**：它的價格（$2／$12，cached $0.20）在每一項都不低於 GPT-6.1 Sol（$2／$10，cached $0.10）；Codex credits 也一樣（50／5／300 對 50／2.5／250）。Codex 官方的推薦清單裡也沒有它。
5. **common:delegate 必須改的地方**：
   - Luna Max 釘死的 `gpt-5.6-luna` 已成舊代模型，現行是 `gpt-6-luna`，支援到 `max`、不支援 `ultra`。
   - Codex 多了 `ultra`；它是 subagent 編排，不是更深的推理。
   - Claude 5.5 三款在 Claude Code 的預設 effort 都是 `medium`。
   - Codex subagent 沒指定模型時會**繼承父代的模型與 effort**。本機設定是 `gpt-6-astra` + `high`，所以不指定模型就會在 Astra 上跑。

## 兩家規格表

### Anthropic（價格為 USD／MTok；Batch 一律為輸入、輸出各 5 折）【官方】

| 模型（ID） | 輸入／輸出 | 5m 寫入／1h 寫入／cache read | Batch 輸入／輸出 | Context／最大輸出 | 知識截止 | Effort（預設：API／Claude Code） | 思考模式 | 前代差異 |
|---|---|---|---|---|---|---|---|---|
| Fable 5.1（`claude-fable-5-1`） | $10／$50 | $12.50／$20／**$0.25** | $5／$25 | 1M／128K | 2026-06 | low–max（high／high） | Adaptive，永遠開啟 | 對 Fable 5：輸入、輸出價格不變；cache read 從 $1 降到 $0.25（基礎輸入價的 0.025 倍）。新增 per-message effort（beta）。Breaking changes：forced tool use 會回 400；thinking block 綁定產生它的模型與對話。不支援 Fast。9/1 發布 |
| Opus 5.5（`claude-opus-5-5`） | **$4／$20** | $5／$8／**$0.20** | $2／$10 | 1M／128K（Batch beta 可到 300K） | 2026-06 | low–max（**medium**／**medium**） | Adaptive，永遠開啟（`disabled` 回 400） | 對 Opus 5（$5／$25，cache read $0.50）：輸入、輸出降 20%，cache read 降 60%。預設 effort 從 high 降為 medium，且同一級 effort 會想得更多。Fast mode 從 $10／$50 降為 **$8／$40**（僅 Claude API，research preview）。9/22 發布 |
| Sonnet 5.5（`claude-sonnet-5-5`） | $2／$10 | $2.50／$4／**$0.10** | $1／$5 | 1M／128K（Batch 300K） | 2026-06 | low–max（**high**／**medium**） | Adaptive，預設開啟；最低一檔是 `between_tools`（取代 `disabled`，只能在 high 以下使用） | 對 Sonnet 5：輸入、輸出不變；cache read 從 $0.20 降到 $0.10（10/7 生效）。effort 重新校準；最小可快取長度從 1024 降到 512；不支援 Fast。9/28 發布 |
| Haiku 5.5（`claude-haiku-5-5`） | ≤100K token 的 prompt：$0.10／$0.50；>100K：$0.50／$2.50 | ≤100K：$0.125／$0.20／**$0.01**；>100K：$0.625／$1／$0.05 | ≤100K：$0.05／$0.25；>100K：$0.25／$1.25 | 1M／128K（Batch 300K） | 2026-06 | low–max（medium／medium） | Adaptive，預設開啟；effort 在 high 以下可用 `disabled` | 對 Haiku 4.5（$1／$5，cache read $0.10）：≤100K 降 90%。context 從 200K 擴到 1M，最大輸出從 64K 到 128K。**第一個可調 effort 的 Haiku**。tokenizer 多算約 30% token。10/7 發布 |

補充【官方】：
- Effort 頁說明：`xhigh` 用於「超過 30 分鐘、token 預算以百萬計」的長程任務；`low` 的典型用途寫明是「subagents」。
- Claude Code 的 `ultracode` 是一項設定，不是 effort 級距：開啟後每個實質任務都會規劃 dynamic workflow；用 `--effort ultracode` 啟動時會同時把 effort 設成 `xhigh`。

### OpenAI（API 價格為 USD／MTok；Batch／Flex 為 Standard 的 50%；Fast＝2 倍；超過 272K 輸入時，輸入與快取 2 倍、輸出 1.5 倍）【官方】

| 模型（ID） | 輸入／輸出 | Cached input／Cache write | Codex credits（輸入／cached／輸出） | Context／最大輸出 | 知識截止 | `reasoning.effort`（API 預設） | Fast／其他 | 前代差異 |
|---|---|---|---|---|---|---|---|---|
| GPT-6 Astra（`gpt-6-astra`） | $10／$50 | $1.00／$12.50 | 250／25／1,250 | 1.05M／128K | 2026-04-30 | low–max（medium）；**無 `none`**；Codex 另有 `ultra` | Fast 2 倍；**Ultrafast** $60／$300（API）；在 Codex 內用訂閱額度是 8 倍費率 | 新的頂層型號，9/3 發布；不支援 `none`、temperature、logprobs；工具呼叫必須走 Responses API |
| GPT-6.1 Sol（`gpt-6.1-sol`） | $2／$10 | **$0.10**／$2.50 | 50／2.5／250 | 1.05M／128K | 2026-04-30 | low–max（medium）；**拿掉 `none`、`minimal`**；Codex 另有 `ultra` | Fast 支援；Ultrafast「之後推出」 | 對 GPT-6 Sol：cached 從 $0.20 降到 $0.10；拿掉 `none`；知識截止從 4/20 延到 4/30。9/29 發布 |
| GPT-5.6 Terra（`gpt-5.6-terra`） | $2／$12 | $0.20／官方頁未列金額（規則是 1.25 倍，推算約 $2.50【推論】） | 50／5／300 | 1.05M／128K | 2026-02-16 | none–max（medium） | Fast 支援 | 對應早期 GPT-5 的「mini」級；7/30 降價 20%；**沒有 GPT-6 Terra（官方未公布）** |
| GPT-6 Luna（`gpt-6-luna`） | $0.10／$0.50 | $0.01／$0.125 | 2.5／0.25／12.5 | 1.05M／128K | 2026-05-18 | none–max（medium）；Codex：最高到 Max、**不支援 Ultra** | Fast 支援 | 對 GPT-5.6 Luna（$0.20／$1.20，cached $0.02；Codex 5／0.5／30）：價格約減半或更多；知識截止從 2/16 延到 5/18。9/22 發布 |

補充【官方】：
- GPT-5.5 將於 **10/14** 從 ChatGPT、ChatGPT Work、Codex 退役，API 不受影響。
- Priority processing 已在 7/30 改名為 Fast mode。
- Codex 文件建議的起始 effort：Luna 從 **High** 開始、Astra 從 **Light（`low`）** 開始、Sol 6.1 用 client 預設。

## 官方用途建議

**Anthropic【官方】**
- 「大多數工作先用 Opus 5.5」。只有在 Opus 5.5 調到較高 effort、評測仍不夠時，才改用 Fable 5.1。
- Opus 5.5 公告寫它「在多數工作上表現與 Fable 5.1 同級，跑起來比 Opus 5 便宜 40%」。
- Sonnet 5.5 的定位是「well-scoped everyday tasks, fixing bugs」，是 Opus 5.5 較快、較便宜的搭檔。公告有客戶引言：由 Opus 5.5 定架構、交給 Sonnet 5.5 實作。
- Haiku 5.5 適合「summaries, compactions, database queries, and classification」，並寫明「pairs well with Opus 5.5 and Sonnet 5.5 as a subagent on coding work」。但複雜的 agentic coding 仍以 Sonnet 5.5 或 Opus 5.5 較佳。
- 混用模型有兩種策略，見 Optimizing for cost and intelligence：
  - **Orchestrator**：前沿模型掌主迴圈，把大量工作派給較便宜的 worker。只有兩種情況量測到省錢：例行工作的成本長尾，以及工作量超過一個 context window。如果工作是一條相依的鏈，「don't build an orchestrator」。
  - **Advisor**：較便宜的模型跑主迴圈，關鍵時刻請教較強的模型。實測 Opus 5.5（high）＋ Fable 5.1 advisor 只多 1.7 分，成本卻是 2.1 倍，效果約等於把 Opus 5.5 調到 `xhigh`。
  - 兩者之前，官方都要求先做 effort sweep：「Tuning effort is often a better lever than switching models」。
- **Claude Code subagent 預設**：自訂 subagent 沒寫 `model` 時會繼承主對話的模型；`/model` 切換時也會一併影響這類 subagent。
  - 要固定成較小的模型，就在定義裡寫 `model:`，或設 `CLAUDE_CODE_SUBAGENT_MODEL`；若要強制所有 subagent 都用同一個模型，再加 `_FORCE=1`。
  - 主對話用 Fable 時，Explore 會改跑 `opus` 解析到的模型。
  - `claude-code-guide` 固定使用 Haiku。
- Claude Code advisor 的配對規則：主模型是 Opus 5.5 時，advisor 可以是 Fable 或 Opus 5 以上。在部分方案上，Fable 會計入 usage credits，需要一次性同意。

**OpenAI【官方】**
- API 模型頁：「不確定就用 GPT-6 Astra」；想兼顧智慧與成本選 GPT-6.1 Sol；成本敏感、高量的工作用 GPT-6 Luna。
- Codex 模型頁：複雜 coding 與 agentic 工作「use GPT-6.1 Sol when available」；Luna 用於「focused, repeatable tasks」；Astra 用於「the hardest end-to-end work」。
- Codex subagents 頁：
  - 沒設定時，subagent 繼承父代的模型與 reasoning effort。
  - 只指定模型、沒指定 effort 時，用該模型的預設 effort。
  - 建議 `gpt-6.1-sol` 給「demanding agents」，`gpt-6-luna` 給「fast, narrowly scoped agents」。
  - reviewer 或安全類 agent 建議用 `high`。
  - 可在 `config.toml` 設定 `agents.default_subagent_model` 與 `agents.default_subagent_reasoning_effort`。
- Code review 可以用 `review_model` 另外指定模型，官方沒有推薦特定型號。
- GPT-6 Astra 指南提到：Astra 對 skills 與 `AGENTS.md` 裡的指示更敏感，衝突的指示可能讓它提早停下；它也比較常向使用者提問；可能比你期望的更少把工作委派給 subagent。

## 本機 CLI 實測【本機】

- `claude --version` → `2.1.293`。
  - `--model` 說明寫「alias for the latest model (e.g. 'fable', 'opus', or 'sonnet') or a model's full name」。
  - `--effort` 列出 `low, medium, high, xhigh, max`。
  - 官方文件另列了 `best`、`haiku`、`sonnet[1m]`、`opusplan` 等別名。在 Anthropic API 上，`haiku` 會解析到 Haiku 5.5。
- `codex --version` → `codex-cli 0.161.0`。`codex debug models | parse-cli-json.js models` 的結果如下：

| ID | 目錄描述 | efforts | Fast |
|---|---|---|---|
| gpt-6.1-sol | Latest workhorse model for coding and everyday work. | low,medium,high,xhigh,max,ultra | yes |
| gpt-6-astra | Frontier intelligence for the most demanding work. | low,medium,high,xhigh,max,ultra | yes |
| gpt-6-sol | Previous generation workhorse model. | low…ultra | yes |
| gpt-6-luna | Fast and affordable model for easier tasks. | low,medium,high,xhigh,max（**無 ultra**） | yes |
| gpt-5.6-sol | Older generation workhorse model. | low…ultra | yes |
| gpt-5.6-terra | Older balanced model for straightforward work. | low…ultra | yes |
| gpt-5.6-luna | Older fast and efficient model. | low…max | yes |

- 這份目錄裡沒有 `none`（API 的 Luna 6 和 Terra 5.6 支援 `none`）。`gpt-5.6-luna` 仍可使用，但已標為 Older。
- `~/.codex/config.toml`：`model = "gpt-6-astra"`、`model_reasoning_effort = "high"`、`service_tier = "default"`。
- 環境陷阱：在 Git Bash 執行 `node` 會先找到另一個 nvm 墊片，它要求安裝 v22.23.2 而失敗。改從 PowerShell 執行（node v24.21.0）才成功。

## 分工建議驗證（逐列）

| 角色 | 提案 | 判定 | 理由與來源 |
|---|---|---|---|
| lead | Opus 5.5 | **保留** | 官方「most workloads start with Opus 5.5」；Claude Code `default` 也解析到 Opus 5.5。注意它在 Claude Code 的預設 effort 是 `medium`：官方說 medium 適合範圍清楚的日常工程，`high` 適合修既有程式碼的 bug、需要驗證的工作。【官方】lead 要做編排與驗收時，可考慮調到 `high`。【推論】 |
| 最難問題＋reviewer | Fable 5.1 | **修正** | 「最難問題」成立，但官方條件是 Opus 5.5 調到高 effort 仍不夠時才升級。「例行 reviewer」不建議：Fable 5.1 單價是 Opus 5.5 的 2.5 倍，在部分方案上計入 usage credits；advisor 實測多 1.7 分、成本 2.1 倍，效果約等於把 Opus 調到 `xhigh`。【官方】建議 reviewer 預設用全新 context 的 Opus 5.5（`high`）；高風險的審查再升到 Fable 5.1，或在 Claude Code 用 `/advisor fable`。【推論】 |
| 快速抓 bug／防禦式審查 | Astra 6 | **修正** | Astra 的官方定位是「hardest end-to-end work」，不是「快速」；Codex 計價是 Sol 6.1 的 5 倍（250／1,250 對 50／250 credits），Fast 模式還要再乘 2.5 倍的訂閱額度。【官方】「用 ChatGPT 額度、分散 Claude 用量」本身成立：Codex 以 ChatGPT 登入時用方案額度，與 Claude 計費分開。【官方＋推論】跨家族的第二意見有價值，但把它當日常快速審查會很快燒完額度。建議日常審查改用 Sol 6.1 `high`（官方建議 reviewer 用 high）；Astra 留給高風險的最終審查。【推論】 |
| 雜務 | Sol 6.1 | **修正** | Sol 6.1 是「near-Astra」，也是 Codex 複雜工作的推薦起點，不是雜務模型。雜務應交給 Luna 6（官方：「clear, repeatable tasks」、extraction、classification）。【官方】Sol 6.1 應該是 Codex 端的中重度 worker 或 reviewer。【推論】 |
| 中型有界實作 subagent | Sonnet 5.5（從搜尋／摘要上調） | **保留** | 官方定位「well-scoped everyday tasks, fixing bugs」；Optimizing 頁的 orchestrator 範例用的就是 Sonnet worker；客戶引言提到 Opus 定架構、Sonnet 實作。【官方】注意 Sonnet 5.5 的 API 預設 effort 是 `high`，在 Claude Code 是 `medium`；官方建議 agentic coding 中，範圍清楚的任務從 `medium` 開始，難的改 `high`。 |
| 搜尋、摘要、不需判斷的寫作、壓縮、分類 | Haiku 5.5 | **保留** | 官方點名「summaries, compactions, database queries, and classification」與「subagent」用途。【官方】注意：在 `low` effort 下，長 agent prompt 時較可能跳過搜尋、提早結束、略過檢查，所以官方建議從預設的 `medium` 開始。 |
| 最小單位 agent | Claude 端用 Haiku 5.5；Luna 只在 Codex 方便時用 | **保留（附註）** | 兩者 API 價格相同：$0.10／$0.50，cached $0.01。但 Haiku 5.5 的 prompt 超過 100K 就漲到 5 倍；Luna 6 要超過 272K 才漲 2 倍。【官方】Anthropic 公告的評測中 Haiku 5.5 優於 GPT-6 Luna，這是廠商自評。【官方，屬廠商自評】長 context 的大量掃描可考慮 Luna 6。【推論】 |
| （缺）Terra 5.6 | — | **不放入** | 屬舊代，Codex 推薦清單沒有它；價格不低於 Sol 6.1（輸出 $12 對 $10，cached $0.20 對 $0.10；credits 300 對 250）。【官方數字＋推論】唯一可能的用途是需要 `none` effort 的 API 呼叫，但 Luna 6 也支援 `none`，而且更便宜。 |

## 對 common:delegate 的具體修改建議（只是建議，本次沒有修改任何 skill）

1. **Luna Max 的 ID**（`plugins/common/skills/delegate/SKILL.md` 第 105、107 行，`plugins/common/agents/luna-max-sidekick.md` 第 3 行 description，Codex 版本 `codex/plugins/common/skills/delegate/SKILL.md`）：`gpt-5.6-luna` 在本機目錄已標為「Older」，官方已用 `gpt-6-luna` 取代 `gpt-5.4-mini`，價格也減半以上。有兩個選項，要由使用者決定：
   - (a) 改成釘 `gpt-6-luna` + `max`。本機目錄確認它支援 max、不支援 ultra。
   - (b) 改成「目錄中最新的 Luna」+ `max`，由 live catalog 解析。這和 SKILL 第 89 行「never hardcode a version」的原則一致。

   另外，`plugins/common/.claude-plugin/plugin.json` 的 keyword `gpt-5.6` 也一併檢查。依專案慣例，修改後要 bump version，並重新產生 Codex 版。
2. **Effort 級距**：第 101 行已寫 `xhigh`／`max`／`ultra` 需使用者明示。建議再補一句：Codex 的 `ultra` 會讓 sidekick 自己再開 subagent，屬於編排而不是更深的推理，與「有界切片」的定位衝突，sidekick 預設不要用 `ultra`。也建議註明 Claude Code 的 `ultracode` 是設定、不是 effort。【官方定義＋推論】
3. **預設 effort 必須明示**：Claude 5.5 三款在 Claude Code 預設都是 `medium`（Sonnet 5.5 的 API 預設是 `high`）；Codex subagent 沒指定就繼承父代。本機父代是 Astra `high`，所以 **delegate 每次派工都要明確指定 model 與 effort**，否則會在不知情下跑最貴的組合。【官方＋本機】
4. **Tier 升級的順序**：「一次只升一個維度」與官方「先做 effort sweep，再考慮換模型」一致。建議改寫成「先升 effort，effort 到頂再換模型」。【官方】
5. **Family-fit 表（GPT 偏原則驅動、Claude 偏步驟驅動）**：官方文件**沒有**這種家族對比，所以既無法證實，也無法否定（官方未公布）。部分官方說法與表的方向不完全一致：Astra「stronger at general instruction following」而且「more sensitive to instructions in skills」；Opus 5.5「delegates to subagents far more effectively」。建議保留，但標為「經驗啟發式、每次換代重新評估」；另外加一條：派給 GPT 6 系列時，briefing 不要留下互相衝突的指示，因為 Astra 會因此提早停下。【推論】
6. **Fast**：本機目錄顯示 7 款都支援 Fast。在 Codex 以訂閱額度計算時，Fast 是 2.5 倍、Ultrafast（僅 Astra）是 8 倍，可以在 `--fast` 段落註明成本倍數。Claude 端的 Fast 只在 Claude API 上提供，且限 Opus 系列；「Claude must not enable it」維持不變。【官方】
7. **Claude 端最便宜的 tier**：Haiku 5.5 已可調 effort、有 1M context，可列為 Claude 端的 cheapest tier。舊的 Haiku 4.5 不能當 advisor，也不支援 effort。【官方】

## 來源清單

擷取檔都在 repo 的 `.claude/read/material/<slug>/index.md`。

**Anthropic**
- https://platform.claude.com/docs/en/about-claude/models/overview → `models-overview`
- https://platform.claude.com/docs/en/about-claude/pricing → `pricing`
- https://platform.claude.com/docs/en/models/fable-5-1/overview → `claude-fable-5-1latest`
- https://platform.claude.com/docs/en/models/opus-5-5/overview → `claude-opus-5-5latest`
- https://platform.claude.com/docs/en/models/sonnet-5-5/overview → `claude-sonnet-5-5latest`
- https://platform.claude.com/docs/en/models/haiku-5-5/overview → `claude-haiku-5-5latest`
- https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1 → `what-s-new-in-claude-fable-5-1`
- https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5 → `what-s-new-in-claude-opus-5-5`
- https://platform.claude.com/docs/en/models/sonnet-5-5/whats-new-sonnet-5-5 → `what-s-new-in-claude-sonnet-5-5`
- https://platform.claude.com/docs/en/models/haiku-5-5/whats-new-haiku-5-5 → `what-s-new-in-claude-haiku-5-5`
- https://platform.claude.com/docs/en/models/opus-5-5/migration-guide → `claude-opus-5-5-migration-guide`
- https://platform.claude.com/docs/en/build-with-claude/effort → `effort`
- https://platform.claude.com/docs/en/build-with-claude/fast-mode → `fast-mode-research-preview`
- https://platform.claude.com/docs/en/about-claude/models/choosing-a-model → `choosing-the-right-model`
- https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence → `optimizing-for-cost-and-intelligence`
- https://platform.claude.com/docs/en/about-claude/model-deprecations → `model-deprecations`
- https://platform.claude.com/docs/en/release-notes/overview → `claude-platform-release-notes`
- https://www.anthropic.com/claude-fable-and-mythos-5-1 → `claude-fable-5-1and-mythos-5-1`
- https://www.anthropic.com/claude-opus-5-5 → `claude-opus-5-5`
- https://www.anthropic.com/claude-sonnet-5-5 → `claude-sonnet-5-5`
- https://www.anthropic.com/claude-haiku-5-5 → `claude-haiku-5-5`
- https://www.anthropic.com/news → `newsroom`
- https://code.claude.com/docs/en/model-config → `model-configuration`
- https://code.claude.com/docs/en/sub-agents → `create-custom-subagents`
- https://code.claude.com/docs/en/advisor → `escalate-hard-decisions-with-the-advisor-tool`

**OpenAI**
- https://developers.openai.com/api/docs/models → `models`
- https://developers.openai.com/api/docs/models/gpt-6-astra → `gpt-6-astra-model-openai-api`
- https://developers.openai.com/api/docs/models/gpt-6.1-sol → `gpt-6-1-sol-model-openai-api`
- https://developers.openai.com/api/docs/models/gpt-6-sol → `gpt-6-sol-model-openai-api`
- https://developers.openai.com/api/docs/models/gpt-6-luna → `gpt-6-luna-model-openai-api`
- https://developers.openai.com/api/docs/models/gpt-5.6-terra → `gpt-5-6-terra-model-openai-api`
- https://developers.openai.com/api/docs/models/gpt-5.6-luna → `gpt-5-6-luna-model-openai-api`
- https://developers.openai.com/api/docs/pricing → `pricing_v2`
- https://developers.openai.com/api/docs/changelog → `changelog`
- https://developers.openai.com/api/docs/guides/latest-model → `using-gpt-6`
- https://developers.openai.com/api/docs/guides/model-selection → `model-selection`
- https://developers.openai.com/api/docs/guides/reasoning → `reasoning-models`
- https://developers.openai.com/codex/models → `models_v2`
- https://developers.openai.com/codex/subagents → `subagents`
- https://developers.openai.com/codex/pricing → `pricing_v3`
- https://developers.openai.com/codex/agent-configuration/speed → `speed`
- https://developers.openai.com/codex/code-review → `code-review`

**擷取失敗（已記入 index，內容為空）**
- https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-5-5 → `documentation-claude-platform`：這個 URL 不存在（0 字），已改用各模型自己的 what's-new 頁。
- https://openai.com/news/ → `news`：HTTP 403。OpenAI 的公告改用 developers.openai.com 的 changelog 與模型頁；`openai.com/index/gpt-6-astra/` 沒有取得。
