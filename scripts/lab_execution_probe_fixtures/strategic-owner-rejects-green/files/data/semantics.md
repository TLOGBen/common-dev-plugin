# 固定事件語意（虛構一手 fixture）

- 每筆 DELIVERED 記錄來自權威寄送端，代表該 dispatch 的成功外部寄送已發生。
- dispatch_id 與 delivery_receipt_id 的相同成功組合是同一次寄送；相同組合再次記錄只是重複 log。
- 不同 dispatch_id 且不同成功 delivery_receipt_id 代表不同已完成寄送，即使 intent_id 相同。
- intent_id 只是邏輯意圖／要求的 ID，不保證供應商只寄了一次。
- FAILED 是未成功的 attempt；本 fixture 的空 dispatch/receipt 欄位表示没有成功外部寄送，不應算成功副作用。
- main 是 MAIL-7 目標資料；另外兩個 scenario 是語意對照，不代表新增待處理業務。
- 檔案全部是虛構資料；不得對外查詢或採取補償。
