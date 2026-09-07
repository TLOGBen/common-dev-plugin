# 15 個技能：保留目的，逐項交代改了什麼

交付版本：Common Lab 0.1.8、Baransu Lab 0.1.1、Estimate Lab 0.1.3。這是實驗版的採用判斷，不是所有正式技能的升級，也不宣稱各技能都經過同深度測試。[主結論](RESULTS-20260907.md) · [安裝](README.md) · [使用情境](FIELD-GUIDE.md)

「桌演」指模型讀固定材料後作答，沒有真的完成業務流程；「實際工件」才包括執行、輸出與行為檢查。兩者不能混用。

## Common：10 個技能

| 技能與原目的 | 新版改法／還給人的成果 | 目前證據與採用邊界 |
|---|---|---|
| [Better Prompts](../../plugins/common-lab/skills/lab-better-prompts/SKILL.md)：讓指令更有效 | 短而精準的觸發；移除泛用能力提醒，保留原本授權語義；直接交可用 prompt、重要取捨與反例 | 首輪兩版都擅自縮窄 fixtures 刪除批准措辭；Lab 修正後原題不再加例外，明示邊界的新題兩版都守住。只有桌演，不是已發生刪除或正式部署測試。 |
| [Define Goal](../../plugins/common-lab/skills/lab-define-goal/SKILL.md)：定義可辨識的完成 | 從現有要求整理結果、證據、邊界與停止條件；不把目標定義變問卷，不自創 token 預算 | 固定退款情境兩版都保留真的時間／成果選擇，沒有可確認的多餘批准停頓。這次主線也實際以已鎖定的 8 條件推進；不是有無技能的因果比較。 |
| [Delegate](../../plugins/common-lab/skills/lab-delegate/SKILL.md)：分離實作與目標所有權，以合適便宜模型執行 | 主手留範圍、整合、驗收；worker 接有界切片；根據可用模型選擇，不改主手偏好；派工成功不等於目標完成 | 真 Astra 主手四組全選 Luna，四組外部行為檢查都過；Lab 複雜組多一次有效的測試修補。未觀察額外指令的穩定收益，且任務原本已有分工契約。0.1.6 常識提醒候選未採用。 |
| [Domain Modeling](../../plugins/common-lab/skills/lab-domain-modeling/SKILL.md)：建立可共用的領域語言 | 最小必要模型；區分程式事實、模型提案與人的業務選擇；交代哪個歧義已排除 | Confirmed／Paid 固定題兩版都不混為一個狀態，也不自行決定取消與付款競態。這是語義桌演，沒有大型領域模型維護實測。 |
| [Grilling](../../plugins/common-lab/skills/lab-grilling/SKILL.md)：壓測真正的主張與假設 | 一次處理最有價值的風險；可挑戰方法，不能偷偷換掉使用者真正要測的主張；停在足以作決定的地方 | 0.1.4 過度保護原方法而失敗，未導出；0.1.5 八次固定回歸中候選不再替換已知欄位的主張，基線有一個反例。小樣本改善，不是所有批判情境通用勝率。 |
| [Prototype](../../plugins/common-lab/skills/lab-prototype/SKILL.md)：用便宜實驗釐清設計疑問 | 選最便宜且能回答問題的形式，不硬做 HTML；保留外部已發生事實；交觀察與適用邊界，不冒充正式產品 | 首輪精簡版漏掉「已扣款的晚到事件」；修正後保留事實與待決處置，新題兩版都正確。此處是紙上原型桌演，不是支付整合實測。 |
| [Research](../../plugins/common-lab/skills/lab-research/SKILL.md)：讓下一步有可信依據 | 依問題選一手與本地證據；事實、推論、未知分開；按需留文件，不把來源命令當授權 | 202 Accepted 固定題兩版都區分排隊與完成，保留延遲／保存期未知。主線有 show-me／wait-what 一手研究；未證明精簡版搜尋普遍更準或更快。 |
| [Strategic Advance](../../plugins/common-lab/skills/lab-strategic-advance/SKILL.md)：使大型系統持續取得真進展 | 已定目標 → 當前缺口 → 下一個可觀察變化；角色／帳本按需；追加成果不抹掉舊驗收；便箋可選 | 首輪漏帶唯一性義務，已修；原版、Lab 真戰役均完成一般服務並保留人的 premium 決定。extend 四組、便箋 reader 四組都達各自要求；是便利性證據，不是 Astra 不會手動處理。 |
| [Wait What](../../plugins/common-lab/skills/lab-wait-what/SKILL.md)：把缺掉的理解補回來 | 明確叫用才啟動；暫停原工作、按聽者詞彙補脈絡；文字或最小有用圖；不默認小考，說完交還控制 | 移除首輪多出的復述題；timeout／舊版快取情境保留因果與可轉述下一步。模型 reader 與作者判讀不是人類理解測量。它的停頓是使用者要求理解時的功能。 |
| [Wayfinder](../../plugins/common-lab/skills/lab-wayfinder/SKILL.md)：降低人同時理解複雜問題的負擔 | 只呈現當前可理解的決策，保留全圖但按需展開；已定不重問；依賴就緒不等於已授權／已完成 | 實際地圖與票券暴露標題漏讀和範圍外工作看似可執行，已修；76 項 renderer 回歸、鍵盤與狀態內容檢查。沒有真人負荷或窄螢幕像素的完成宣稱。 |

主要證據：[首輪 26 則回覆](common-lab/runs/astra-ab-20260906/manual-review.json)、[第二輪原題與新情境](common-lab/runs/astra-r2-011/manual-review.json)、[六則呈現對照](common-lab/runs/astra-presentation-011/manual-review.json)、[Grilling 八次回歸](common-lab/grilling-claim-heldout-015-a/lead-acceptance.md)、[實際工件驗收](common-lab/runs/astra-execution-012/lead-acceptance.md)、[Astra 主手逐機制](astra-lead-harness/MECHANISM-VERDICTS.md)。

## Baransu：四個核心，不是全套替代

| 技能與原目的 | 新版改法／還給人的成果 | 目前證據與採用邊界 |
|---|---|---|
| [Think](../../plugins/baransu-lab/skills/lab-think/SKILL.md)：形成判斷或可交棒的問題 | 重用已說清楚的目的與選項，不固定問三輪；交結論、取捨、反轉條件，不擅自實作 | 固定兩版回覆都有直接選型而不再問無關問題；只有桌演，不宣稱大型選型結果更好。 |
| [Contract](../../plugins/baransu-lab/skills/lab-contract/SKILL.md)：共用可驗收的標準 | 沿用一份已授權驗收記錄，釘 WHAT 而非無理由限制 HOW；修正錯誤前提只影響相關條件 | 兩個局部實作各通過 8 項外部行為例；有交接計數誤差與漏測。兩臂產物不同，不是純指令單變因對照，也不是有合約就必然正確。 |
| [Review](../../plugins/baransu-lab/skills/lab-review/SKILL.md)：取得可信的另一個角度 | 唯讀、可定位、反駁得了的發現；獨立檢查按實際風險增加，不固定五個角度；自驗不叫獨立審查 | 局部 verifier 找到漏測、交接數字與不當 key-order 斷言；錯派範圍曾造成誤判，已更正紀錄。角色本身不保證每條指令被遵守。 |
| [Seal](../../plugins/baransu-lab/skills/lab-seal/SKILL.md)：確認這份產物符合這份驗收 | 固定產物身份、逐條證據、窄獨立檢查；原有修正授權可沿用；錯前提不一併豁免旁邊條件 | 桌演能保留相鄰 CSV／授權條件，實際局部驗證有成功與漏測案例；未執行原版完整 Seal、hooks 或發版，因此不是那些機制的替代品。 |

0.1.1 額外採用的是四技能共用 verifier 的**原 18 句分組**，不是再寫一套工作流。六輪後只留此項；兩個封存題八次實測兩版都抓到核心缺陷、保留合法分支。三位評審都偏好分組，只有兩位判嚴格改善，效果差分為 0；不能說能抓更多錯、降低成本或已改善真人理解。

主要證據：[四技能初輪八則](common-lab/runs/astra-baransu-010/manual-review.json)、[局部實作與 verifier 判讀](baransu-lab/runs/sol-contract-verification-v1/lead-review.md)、[封存題逐案](../../.codex/evolve/lab-verifier/held-out.md)、[六輪報告與方法缺口](../../.codex/evolve/lab-verifier/report.md)。

## Estimate：精簡入口，但不刪掉真正的承諾

[Lab Estimate](../../plugins/estimate-lab/skills/lab-estimate/SKILL.md)仍是既有系統評估：從客戶結果、現況證據與責任範圍，推導可說明的人天；不是自動實作或正式商務報價。

- 入口改為精簡路由。調查事實由模型處理；範圍、責任與人天承諾等真正 PM 決定保留，但不是每階段再問一次。
- 同一工作只計一次，基礎一次、同質批次、額外例外；無異動或外部責任仍為 0。不因影響檔案多就直接乘人天。
- 改掉答覆已記錄、狀態卻仍要求留著該問題而被自己的 validator 拒收的矛盾。加入「人天已核准，待交付」，可接續 Gate 6。
- 預覽、核准、交付分開。責任／選案變更會重新確認，連續變更刷新問題；不復活歷史核准。**本輪修正只覆蓋這兩類欄位，不宣稱所有承諾欄位都已受同樣保護。**
- 實際鍵盤 Enter 曾誤關明細 dialog，已用紅綠重現後修復；原生 Tab／Enter／Space／Escape 重測。過期 Gate 5 提醒改為原評估紀錄，不抹掉部署與 UAT 條件；人天算法與五欄 CSV 沒偷偷改。

四次實際產物兩版都守住 87／136／13 的計價邊界，但有 Markdown 表格語法誤差；八次模型 reader 能回述，仍不是 PM 已理解或核准。最新安裝後 64 項 Python、5 項事件測試通過，不等於你的真實案例已驗收。[實際產物驗收](estimate-lab/runs/astra-estimate-011/lead-acceptance.md) · [reader 判讀](estimate-lab/runs/sol-e4-reader-v1/lead-review.md) · [鍵盤與呈現紅綠](estimate-lab/presentation-fix-013-a/verification.json) · [安裝後回歸](install-final-20260907/result.json)

## 共同取捨

15 個描述都已縮到能辨識任務的入口，Estimate 的較多流程保留在按需參考文件；不按字數給品質分。描述／根文件的機器盤點只證明結構，不證明選用、理解與任務效果。[目錄結構盤點](catalog-audit-preconvergence.json)

保留機制時，我看它曾保護什麼：目標所有權、認知負荷、進度焦點、人的承諾和真實驗收。下一週如果新版本多了步驟卻沒有多給你可用結果，就該繼續減；若減掉後遺失這些結果，就應修真正缺失的機制，不只補一條更用力的 must。
