# Lab 0.2.0：指引優先，控制對準反覆失誤

Common Lab 10 個、Baransu Lab 4 個、Estimate Lab 1 個，全部重新檢視並修改為 **0.2.0**。這是三個可分開安裝的本地實驗包；正式版、舊實驗包與既有案件不替換，尚未遠端發佈或更新目前 App 的安裝。

這次不是全面瘦身，也不是把所有工作套進戰役流程。最重要的修正是：**讓實作中的上下文，不能單靠自我感覺決定是否繼續擴張工作。** 長程複合任務保留外部校準；小任務仍以直接、可驗收的工作為主。

## 你會實際感受到什麼

| 工作情境 | 新版應該怎麼做 | 不應該發生的摩擦 |
|---|---|---|
| 小型修字、已知且局部的 CR | 直接完成有界變更，做足以證明條件的檢查 | 強迫建立戰役、派一整組 agent、跑滿固定輪數 |
| 中型功能，目標明確但需要交棒 | Contract 落檔；適合的實作交 Delegate；Seal 依風險驗收 | 每一步重問已決定的事、重複建立相互矛盾的合約 |
| 16–24 小時以上、API／頁面／E2E／重構高度耦合 | Strategic Advance 分離目標與實作；事件及期限觸發獨立校準 | 主手把功能、風格、重構與 build 修復全部接成一個「好像可一起完成」的任務 |
| 使用者還不理解選項 | Wayfinder／Wait What 先解釋眼前差異，再交還決定 | 連續丟下一串問題；把模型可重述當作真人已理解 |

時長不是唯一門檻。短時間但高度耦合、未知副作用多的工作也可能需要戰役控制；長時間的單一有界查詢不必因此加上全套流程。

## 每個 skill 個別改了什麼

以下改動皆在 Claude Lab source，Codex 版由既有轉換器生成。既有能力未因缺乏短測試收益而被刪除；沒有證據支持改寫的 runtime 與呈現資產維持原樣。

| Skill | 保護的原目的／失敗模式 | 0.2.0 的實際改動 | 控制與摩擦取捨 |
|---|---|---|---|
| [Better Prompts](../../../plugins/common-lab/skills/lab-better-prompts/SKILL.md) | Prompt 改良不能變成把承重控制刪光 | 先辨識目的、已知失敗、規模與證據，再決定保留／改寫／移除；短測試不能證明長程控制多餘 | 通常用指引；只有可指出反覆失誤的地方才加硬規則，不以字數定勝負 |
| [Define Goal](../../../plugins/common-lab/skills/lab-define-goal/SKILL.md) | 忙碌被誤認為完成，接續後目標漂移 | 區分 MOE 成果與 MOP 活動；長程、委派、跨上下文沿用一份持久成果與決策來源 | 不替小任務製造文件；已有 Contract 就重用 |
| [Delegate](../../../plugins/common-lab/skills/lab-delegate/SKILL.md) | 實作與目標責任混在一起；便宜 worker 在局部修復打轉 | 長／耦合切片加入檢查點、有限修復與部分成果交回；禁止把失敗支線擴成複合救援 | 模型依難度、能力、成本與 Host 可用性選；worker 不是自動合格的戰略校準者 |
| [Wayfinder](../../../plugins/common-lab/skills/lab-wayfinder/SKILL.md) | 人無法同時理解太多問題 | 以人的理解進度拆解；困惑時停新增選擇，先解釋當前問題；接續保留已決定內容及來源 | 安全、獨立查證可繼續；不累積問卷，也不把沉默當同意；原 map renderer 保留 |
| [Research](../../../plugins/common-lab/skills/lab-research/SKILL.md) | 反覆引用後，推論被洗成事實 | 主張綁定實際版本、模型、工作量與適用範圍；保留反證與原始定位 | 不把多個 agent 同意當作多份獨立證據；沒有強加每次全量重查 |
| [Grilling](../../../plugins/common-lab/skills/lab-grilling/SKILL.md) | 批判時偷偷改掉使用者原主張，或無限找新毛病 | 保留原主張最強版本；新反對意見須有不同失敗模式／新證據；使用者修正规模後重估受影響推論 | 不用固定審問次數製造嚴謹感 |
| [Domain Modeling](../../../plugins/common-lab/skills/lab-domain-modeling/SKILL.md) | 模型反覆解釋後，自己創造了「既定業務規則」 | 承重規則保留來源與接受狀態；矛盾明列，局部修訂 | 不將每次詞彙調整升格為整套架構治理 |
| [Prototype](../../../plugins/common-lab/skills/lab-prototype/SKILL.md) | 為了做好 demo 持續加碼，最後拿 demo 當產品證據 | 迭代不再影響設計答案就停止；交接互動、模擬範圍與未驗證部分 | 原型只回答設計問題，不承諾正式或長程可靠性 |
| [Wait What](../../../plugins/common-lab/skills/lab-wait-what/SKILL.md) | 把錯誤說得更漂亮、更容易相信 | 重述前先核對原句有無支持；有錯先修正或限定，再做白話與視覺解釋 | 保留人的理解與按需揭露；仍為明確呼叫，不自動搶走其他技能的任務 |
| [Strategic Advance](../../../plugins/common-lab/skills/lab-strategic-advance/SKILL.md) | 長程複合任務中的注意力捕獲、MOP 假進度與目標飄移 | 補回必要的 fresh calibrator；主手不兼大量實作／修復；事件／期限觸發、有界修復、原始證據封包與接續檢查 | 只對 admitted campaign 加硬控制；受影響支線暫停，不把不衝突的並行工作全停 |
| [Think](../../../plugins/baransu-lab/skills/lab-think/SKILL.md) | 以模型新舊或指令長短做存廢判決 | 依原目的、失敗模式及同規模證據裁決；使用者修正前提時只重算受影響判斷 | 不把一次討論擴張成完整工程計畫 |
| [Contract](../../../plugins/baransu-lab/skills/lab-contract/SKILL.md) | 接續後換目標，或讓較低影響的必要條件被消失 | 明定實作交棒前落檔；沿用一份驗收記錄；區分「必要／可選」與「失敗影響」 | 低影響不等於可忽略；驗證手段可採最便宜的充分證據，除非使用者已指定方法 |
| [Review](../../../plugins/baransu-lab/skills/lab-review/SKILL.md) | 自我審查、機制誤刪與沒有新證據的審查循環 | 獨立、唯讀；方法評審核對適用規模與失敗補償；需要擴大探測才讀驗證額度 reference | 第二意見不是投票真理；避免短樣本推論長跑免疫 |
| [Seal](../../../plugins/baransu-lab/skills/lab-seal/SKILL.md) | 小細節無限 mutation，而真正影響沒分輕重 | 開始前依影響定有限驗證額度；突變只回答具名不確定；耗盡／反覆無進展交回有界重排 | 缺口未補不能 PASS；隱藏的權限／資料錯誤可很嚴重，不以「人眼看不見」降級 |
| [Estimate](../../../plugins/estimate-lab/skills/lab-estimate/SKILL.md) | 跨包重複計價、舊核准套新責任、查證摘要漂移 | 保留 revision 與唯一工作集合；長程跨包按需加 fresh 唯讀 auditor；查證 sidekick 有界交回 | 小型已知 CR 不套完整長程審查；真人 PM 承諾仍由 PM 做，模型讀懂不等於人已接受 |

## 戰略推進：為什麼這次有加回機制

你的案例是：執行 16 小時、上萬行未 commit、進度 10/12，此時介入指出 code style 不符。新版要求保住既有成果，先辨別受影響支線，把原目標、實際規則、diff、build 失敗及有限的下一步交給未參與實作的上下文校準。

它可以判斷「先最小修復」、「分開排必做風格切片」或「確實需要人選擇範圍／優先序」，但不能默默合併剩餘功能、全域排版、共用重構與 build 修復。原本 10 個已達條件，只重驗可能被此次異動影響的證據。

新增 [long-run-control.md](../../../plugins/common-lab/skills/lab-strategic-advance/references/long-run-control.md)、[lab-calibrator.md](../../../plugins/common-lab/agents/lab-calibrator.md) 與 [calibration.py](../../../plugins/common-lab/skills/lab-strategic-advance/scripts/calibration.py)。主帳本、extend、交接便箋仍是原有版本，沒有另造第二份目標真相。

檢查器能擋：過期或未來封包、原始資料變動、工作說明冒充同檔原始來源、同一宣告上下文審自己、錯封包決策、非 active 狀態及未達標的完成請求。

檢查器不能證明：語義真偽、真實 runtime 身分、別檔複製相同故事的獨立性、manifest 列出的每個檔案、修復額度的語義或所有 tool 呼叫被攔截。沒有安裝排程器或 Host enforcement。重大事件發生後，即使檔案 hash 不變，也不能假定原校準仍有效；校準者及主手仍須處理這些邊界。

給人的交接聚焦四件事：**哪些成果真的增加、還缺什麼、剛才哪條岔路停住及原因、下一個有界推進或真正需要人的選擇。** 不把內部每次校準都變成人工批准。

## 實測看到了什麼，沒有看到什麼

| 檢查 | 實際觀察 | 結論邊界 |
|---|---|---|
| 舊版／新版 fresh-context 短情境 | 舊版戰略回應由主手收斂修復並重估；新版明確要求獨立校準後續作，主手不接修復 | 看到了預期的控制差異；未實際執行 16–24 小時戰役，也未證明最終成果更好 |
| Seal、Wayfinder 相同短情境 | 兩版都拒絕無必要突變測試，也都會先協助人理解 | 這兩項不能宣稱新版勝出；新增控制是承接已知失誤，不是本輪勝率結論 |
| Estimate fresh reader | 不把 JDK 17 擴成 Boot／Jakarta；不把 120 generated 當人工次數；不沿用舊核准套新責任；小 CR 不全套 | 是情境回應，不是實際案件、PM 核准或人天結果 |
| 初版檢查器獨立 CLI probe | 81 次；75 次符合期待；6 次格式錯誤的拒絕形式不符。另實測發現工作說明可被同檔冒充 raw source | 保留失敗紀錄，據此修正，而非只保留綠燈 |
| 修正後獨立 CLI probe | 101 次，101 次符合新版 contract，0 非預期；涵蓋 direct／symlink／hardlink 來源別名 | 其中也有刻意驗證「仍可通過」的能力限制；不是 101 個語義正確證明 |
| 全新隔離安裝 | 三包皆 0.2.0；cache 與凍結包逐檔相等；Estimate 64 項 Python＋5 項事件測試通過 | Ubuntu WSL CLI 測試，不代表 Windows App 已載入或完整瀏覽器驗收 |

[行為探針](behavior-probes.md)保留情境、觀察、時間與限制。[安裝收據](install/result.json)、[原始回歸收據](validation.json)可逐步追查。安裝後的 calibration 32 項、原 ledger 16 項、extend 12 項、交接便箋 21 項，以及未改動的 Wayfinder source 76 項檢查通過；Estimate 安裝後 64＋5 項另在安裝收據。

原始簡易格式檢查對 15 個生成 skill 都拒絕 `compatibility`。這是轉換器與本機 validator 的欄位差異：[Agent Skills 規格](https://agentskills.io/specification#compatibility-field)允許此欄為 1–500 字元。本輪另核對該欄，再將其餘完整 metadata 與不變正文放入新建暫存投影，交由原 validator 檢查，15 個皆通過。[分項格式驗證](metadata-validation.json)保留投影與來源 hash；沒有修改凍結包、刪掉失敗收據或宣稱原始 validator 直接全綠。

這輪未對 Astra／Fable／Sol／Luna／Opus 做同條件、重複、長時程比較；不能替模型排名。角色不硬編模型，部署時依實際可用性與任務選擇。

## 磨擦與仍待驗證的取捨

- 長程 control 增加獨立上下文、原始證據整理及續作前校準成本。這是刻意換取可恢復的方向控制；它是否在真實 24 小時 campaign 淨划算，尚待實戰。
- Seal 的「一次獨立核對＋一次集中複查」是有界變更的可調起點，不是最低配額。續輪須有新證據及有限額度；嚴重性不是無限消耗的通行證。
- Contract 必須落檔是保留的機械邊界。它防接續換目標；記錄存在不保證內容正確或使用者已接受。
- 舊版表現已合理的地方只加狹義校準，不重寫 renderer 或增加必讀手冊。人的理解也仍需要真人實戰，不能從 agent 自評打滿分。

## 試用與回到舊版

凍結 marketplace：

- [Common Lab 0.2.0](../../../experiments/common-lab-v0.2.0/.agents/plugins/marketplace.json)
- [Baransu Lab 0.2.0](../../../experiments/baransu-lab-v0.2.0/.agents/plugins/marketplace.json)
- [Estimate Lab 0.2.0](../../../experiments/estimate-lab-v0.2.0/.agents/plugins/marketplace.json)

三包可分開選。這次只在新建的暫存 home 安裝，未切換你的實際 Host。若要改用新版，先在同一 Host 用 `codex plugin list --json` 確認目前版本與 marketplace，再依該 Host 的安裝方式選入上面的本地 marketplace；不要靠重啟或畫面名稱猜版本。

舊 Common 0.1.8／Baransu 0.1.1／Estimate 0.1.3 目錄與歷史測量完整保留。A/B 一次固定一個凍結包與案例副本，核對實際載入檔案；混用 skill 就標成混合條件。Estimate 不直接接管正式案件。

## 本輪測量與完成範圍

| 項目 | 已取得的紀錄 |
|---|---|
| 時間 | 2026-09-07 07:28:55 開始觀測；至 08:05:16 快照約 36 分鐘，另有快照後的文件交接工作 |
| 主線 token 快照差量 | 6,099,877：input 6,052,834、output 47,043；input 內含 cached 5,667,968，不重複加算 |
| 實際費用 | 無可核對帳單，維持未知，不以 API 等值冒充實付 |
| 修訂完成 | 15/15 skills 已修改，3/3 新凍結包已暫存安裝並逐檔一致 |
| 成效與品質 | 機械回歸與指定短情境已查驗；真人理解、24 小時可靠性、跨模型優劣尚未證明 |

時間均為 Asia/Taipei。token 是累積紀錄的兩次快照差量，包含重複讀取上下文，不是新增文字量；第一個快照略早於第一個工作觀測，也不含截止後用量。沒有已驗證的原生子代理分攤，所以不另加子代理數字。詳見 [measurement.json](measurement.json)；先前凌晨批次的 285 次呼叫及費用沒有混算進來。

完整來源／導出差異見 [preservation report](source-change-report.json)；三包的轉換處置彙整在 [port-report.md](port-report.md)。本輪驗證導出後發現報告把 Estimate tests 的具體復原作法當作 disposition 標籤；彙整報告改用規定的 `refresh-mapping` 分類，原始 receipt 保留，套件內容未變。

## 設計依據

原 X 文的短描述與按需揭露仍保留；「模型進步」不被解讀成長程控制一律多餘。公開的一手長程 agent 經驗也描述過一次嘗試過多、接續缺少狀態與過早宣布完成；這支持針對風險設計控制，但不證明所有模型必然以相同方式失敗。[Anthropic：長程 agent harness](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

本版的工程前提是「長程工作必須按可能失焦設計，能被外部發現並恢復」，不是「已數學證明任何 LLM 跑夠久必定失敗」，也不是「加了這個 skill 就能免疫」。
