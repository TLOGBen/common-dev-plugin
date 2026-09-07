# Baransu 實作承接 v1（事前固定）

本輪先做兩次 Luna/high 原版 contract／Lab contract 的真正局部實作，各自 fresh CWD、同一份合成 acceptance。駕駛者給的是實作權限與固定需求，不是假真人核准。原版 shared/loop-contract＋contract/references/loop-pauses 明定非互動 Step 3 是 Input，可採預設並註記；不得先假設原版必然多等一回合。

主要觀察：三類現有缺陷是否修好、測試是否釘到真實行為、是否忠實承接契約、哪些要求帶來實際額外步驟／停頓，以及作者是否誇大完成。主線先以現有兩測試與獨立八例確認基線；之後再對實作產物驗證。獨立 oracle 不給 actor；它直接 import 函式，不修改工件。

Actor 只獲其 skill／必要 references、fixture 與相同 user。不提供 rubric／oracle／另一臂結果；讀取隔離是 prompt 約束，不是安全隔離。原版需要的 shared resources 全部凍結並保留，沒有刪掉 TDD 或確認規則。

本輪 user 明確排除全域 telemetry、正式 sealed marker 及 seal 執行，原版此部分記 NOT_EXECUTED_OUT_OF_SCOPE。這是 contract＋實作承接切片，不是原版完整生命週期。後續最多再安排兩個 fresh verifier，按各自真實 role；若必需修復／重驗會超過四次，分開記錄，不能為符合四次上限偷偷省略協定。

模型呼叫、time、raw JSONL、usage、來源hash、成品zip、保留fixture、實際程式行為及人工判讀各自記錄。完成呼叫不等於任務完成，讀者／驗證者為模型，不代表真人使用。
