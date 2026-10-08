# `common-lab` — Common Lab（實驗性）

回到 [文件索引](../README.md)。

<img src="../images/plugin-common-lab.png" alt="common-lab" width="320">

16 個 TypeSafe Jev 實驗技能。已列入 Claude 與 Codex marketplace，需自行選擇安裝；裝後即啟用（`defaultEnabled: true`），不會取代穩定版 Common。不需要可用 `claude plugin disable common-lab` 停用。

- Claude source：`plugins/common-lab/`
- Codex 移植：`codex/plugins/common-lab/`
- 版本：見 `plugins/common-lab/.claude-plugin/plugin.json` 與 [CHANGELOG](../../CHANGELOG.md)
- 呼叫：Claude 使用 `/common-lab:<skill>`；Codex 使用 `$<skill>`
- 金鑰：需要 `TYPESAFE_API_KEY`，用 `init-jev` 設定

## Skills

### 基礎技能

| Skill | 做什麼 |
|-------|--------|
| `init-jev` | 設定 TypeSafe Jev 存取：讓 agent 的 shell 取得 `TYPESAFE_API_KEY` 而不外露金鑰，預設快取 30 天，再用一次便宜的呼叫驗證。 |
| `jev-gate` | 用 Jev（Noul）對一段文字取得快速、校準過的是／否機率。 |
| `jev-pick` | 用 Jev（Choice）從已知清單挑一個，附每個選項的機率；含停下前檢查。 |
| `jev-score` | 用 Jev（Score）依有序 rubric 評分，附每個等級的機率。 |
| `jever` | 找出目前目標中哪些只需要判斷（是非、挑選、評分）的地方可以用 Jev 取代、加速或備援，也說明哪裡不該用 Jev。 |
| `suggest-jev` | 請求路由：開工前讓 Jev 建議先載入哪個 skill、還需要哪些、流程與完成證明。 |
| `jev-browser` | 建立在 `test-utils:dev-browser` 上、以 Jev 挑選元素的瀏覽器除錯；只能明確叫用（`/common-lab:jev-browser`）。 |
| `is-truely-need-to-ask-user-jev` | 問使用者之前，先問 Jev 這個問題是否真的需要使用者，還是自己就能查到或做到。 |

### 疊加版（`*-jever`）

在正式技能的判斷點加上 Jev 讀數，作為正式判斷旁的第二意見：

| Skill | 疊加在 |
|-------|--------|
| `define-goal-jever` | `common:define-goal` |
| `strategic-advance-jever` | `common:strategic-advance` |
| `wait-what-jever` | `common:wait-what` |
| `wayfinder-jever` | `common:wayfinder` |
| `cold-estimation-jever` | `analysis-estimation:cold-estimation` |
| `contract-jever` | `baransu:contract` |
| `review-jever` | `baransu:review` |
| `think-jever` | `baransu:think` |

## 與穩定版並存

- Skill 名稱與資料夾移除 `lab-` 前綴；與正式版並存時，從技能選單選取 Common Lab 所屬項目，或使用帶套件識別的技能連結。
- 派工一律用 `common:delegate`。

## 沿革

- 實驗技能統一由 Common Lab 提供：原 Common、Baransu、Estimate Lab 合併成單一套件，以「指引優先，針對反覆失誤設置控制」保留各技能的行為與驗收邊界。舊版 README 標題寫的是 **Common Lab 0.10.0**，正文寫版本 0.19.0；目前版本以 `plugin.json` 為準。
- Estimate、define-goal、better-prompts 的 Lab 版已於 0.9.0 淘汰；strategic-advance 的 Lab 版已於 0.10.0 淘汰（請用穩定版）。
- 0.19.0 退役 ui-jever、seal-jever、show-me-jever、none-stop-jever，以及兩個 Lab delegate 變體與 executor agent；改用 `analysis-estimation:cold-estimation`、`common:define-goal`、`common:better-prompts`、`common:strategic-advance`、`common:delegate`、`baransu:ui`／`baransu:draw`、`baransu:seal` 與 `common:show-me`。
- 已畢業的技能現在在穩定版：grilling、domain-modeling、research、prototype、wait-what、wayfinder、show-me 在 `common`；think、contract、seal、review 在 baransu。
- 細節見 [CHANGELOG](../../CHANGELOG.md)。

## 實驗紀錄

`docs/experiments/` 保留為歷史測量紀錄，不能代表目前套件；舊版凍結包已移出工作樹，需要時從 Git 歷史取回；暫存安裝驗證也不代表目前 App 已載入新版。

- [0.2.0 逐技能改動、規模邊界與驗證結果](../experiments/lab-v0.2.0/README.md)
- [三個實驗包的歷史紀錄](../experiments/README.md)
- [Common 0.1.x 歷史實驗說明](../experiments/common-lab/README.md)
- [A/B 計畫與測量限制](../experiments/common-lab/RUN.md)
- [實測發現與限制（持續補充，非終報）](../experiments/common-lab/RESULTS.md)
