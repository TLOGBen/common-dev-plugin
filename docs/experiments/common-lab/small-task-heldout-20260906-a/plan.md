# 小而明確任務：前瞻 A/B 設計

建立時間：2026-09-06（Asia/Taipei）。本輪準備起點 2026-09-06T05:16:27Z；真正推論時間由各 call receipt 記錄。

## 要回答的問題

當事情本來已清楚，四個技能是否交付眼前可用的成果，或讓人先補不必要的選擇、儀式、說明？這不是比字數、標題數或問句數；原版各自的輸出契約保留，實質有用的質疑與輕量追問不能只因是問句而扣分。

案例與逐項通過條件以 cases.json 為唯一凍結來源。每案只有一個使用者回合：精確連結字樣目標、已清楚的單錯字 prompt、skipped 是否刪原始列、帶位置提示的兩人找欄位試驗。最後一案刻意保留真正會破壞試驗效度的盲點，不把「沒有問問題」當作唯一好結果。

## 與既有證據的差別

已檢視 scripts/common_lab_ab_cases.json、common_lab_ab_cases_round2.json、common_lab_presentation_cases.json，以及 astra-ab-20260906、astra-presentation-011 和 reader-astra011-sol-01 的人工審閱。本輪不重跑交易逾時、DB receipt、已明講不要小考的解釋，也不重跑多項 KPI 或高風險退款設計。fable51-clarification-01 只留下訂閱存取失敗，沒有可比較的完整回答。

## 執行與隔離

- 8 次 generation calls：4 個技能 × A/B；固定 gpt-6-astra、high、每臂一次；沒有新增 judge calls。
- A：codex/plugins/common/skills，保留原版技能。B：experiments/common-lab-v0.1.3/plugins/common-lab/skills，使用不可變生成包。
- 實驗版來源封存 hash：cb290dad5817816feacbfa8197db1a9303b04c745e191c9c8b99e52990a5d1f5；整體生成輸出 hash：705e53c49e4e8f132ae8e017a51dab6b21cd4a7e78c2b806864bd009e33d853c。逐檔 hash 由 runner 重取與封存。
- 既有 scripts/common_lab_ab.py，不修改 runner；先 --plan-only 封存，再用不同的新 run-id 正式跑。
- 案例依序為 define-goal、better-prompts、wait-what、grilling；配對臂順序 A→B、B→A、A→B、B→A；workers=2，保留實際 start/end 以辨別並行而非假設全域序列。
- 每案 task-owned fixture、read-only sandbox、ephemeral、ignore-user-config。既有 wrapper 禁止真實副作用、goal/delegation、網路；因此沒有那些行為不能當作技能本身的獨立授權測試。
- 儲存原始 stdout/stderr、請求、模型實際 input/cached/output tokens、每 call 耗時、fixture 與 resource drift；USD 與本代理總用量若不可觀測即 null，不猜。

## 審閱責任與限制

主線讀原始 A/B 回答，以凍結 criteria/guards 做未盲語意審閱，再判定實際等人的原因。人工介入次數只計回答真正要求先回覆才能繼續的地方；必要的人類價值或授權停頓不是失敗。四個假想 next-reply 案例不是真人實測、產品執行、普遍模型排名或統計顯著證據。source、exporter、凍結舊版本與其他 artifacts 一律不改。

## 環境摩擦

準備期間 2026-09-06T05:24Z 左右，一次普通 exec 在 process 啟動前回傳 helper_unknown_error: setup refresh had errors；同權限、同 WSL carrier 的下一次普通讀取成功。沒有更換帳號、權限、sandbox 或模型。這是環境啟動摩擦，不計為技能或模型能力差異。
