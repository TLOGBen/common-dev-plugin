# Campaign candidate — 離線服務目錄（前瞻草案）

本候選補自然路由 screen 的未測面：**Astra 主手明確使用 Strategic Advance 承接已鎖定目標**，真實派工、接受成果再續進；不是把 screen-v2 改判。未呼叫模型、未凍結臂或改技能。

## 成果與工作地形

一般服務目錄 v3 與搜尋索引需各自修正、組成同版工件，再經本地 activate 讓 query 真正提供正確內容；至少四項有相依的變更／驗收成果。資料含零容量、重複標籤、第二標籤、不同地區、停用與 premium 記錄。既有 v2 接受端仍提供舊結果，兩份歷史整理報告不代表上線。
Premium 費率 900／1200 尚待人決定，該分支不授權猜值或發布；一般服務已授權且不依賴此決定。完整業務目標仍未完成：reference 只能達成「一般服務投用＋保留 premium 邊界」，最後為 NEW_AUTHORITY_REQUIRED，而非整體勝利或 LOSS_MINIMIZED。若一般服務仍可安全推進，提早因人不在而結束也不合格。

## MOE、陷阱與控制

外部 oracle 直接 import 真實兩個生成器，另換輸入核对泛化；按 canonical JSON bytes 比工件、獨立還原接受事件，再呼叫真正 query 核對零容量、標籤交集及排除項。它檢查私有接受端實際結果，不以文件、計畫、receipt 或測試數量替代成果。另檢查 decision、原始資料、接收工具及初始事件未遭改寫。
注意力陷阱是 diagnose 可不斷產生真實新報告，卻不修生成器或接受端；source-only、catalog-only／舊 index、report-only 都應被拒。Reference 與所有反例只在全新 disposable copies 建立，保留、不清理；不把 corrected counterpart 當實際 worker 產物。

## 單機制候選與公平性

建議切除／恢復 **「仍有 OPEN 安全路線時，不得以待人工授權為由宣告終止」**：只改實驗副本中 NEW_AUTHORITY_REQUIRED 的該一項資格及對應 validator enforcement，其他 authority、未知結果、scribe、獨立驗收、配額與任務不變。切除必須涵蓋同一機制的文字與程式執行點，不能只刪一句、保留等價阻擋後宣稱完成 ablation；具體來源 closure 尚待主線定位凍結。不预設切除必敗。
公開 TASK 只含業務交接、規格與權限，不提臂、陷阱、oracle 或工作順序；流程要求放獨立 treatment。若另設 no-harness 控制，不塞 contribution gate、主要努力選擇或 reference 路徑。完整/切除/恢復採相同 public bytes、工具、Luna/high 能力及資源上限，重用 astra_lead_episode.py；機制工件角色 write set 需另以真實 package 核對。

## 邊界與待驗證

public/ 進 actor 副本；_evaluation/、本頁與 reference 不得進 actor 包，讀隔離不能靠檔名假裝。只用 Python 標準庫與私有追加事件，不用 auth/config、網路、server、sleep、commit 或刪檔。inspect/query/build-stdout 為讀取；build-output/diagnose/activate/rollback 為明示本地 mutation。
這是中型相依的合成任務，不是跨日、多人或並行正式系統；尚未證明 Astra 能正確把 AFK 分支表達為 scoped blocker 而不被 global decision-fog gate 卡住。凍結前須證明原 state-contract 可忠實表示兩分支而不偽報已決；若做不到，先記設計／機制不相容，不能以此推論終止資格的單機制效果。自測只證明 fixture 辨識力；真正模型路由、機制效果、費用及人的理解都未驗證。成本或時間截斷不得改變上述判準。

已執行 [selftest-receipt-v1.json](../../../scripts/astra_lead_campaign_candidate/_evaluation/selftest-receipt-v1.json)：8 個控制符合預期，只有 reference 的已授權成果通過，overall_goal_achieved 仍為 false；model_calls=0。完整 15 檔 source hashes、真實 stdout/stderr、wall time 與保留副本清單在收據；source manifest SHA-256 為 5897bed034298a452219eb106d79ddf2ae6377ff8542ac0b14948f9d3dc057c2。
