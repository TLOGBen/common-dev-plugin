# 修正待辦佇列摘要

修好 summarizeQueue(tickets)，並留下針對性回歸測試。輸入欄位完整：owner 是字串，estimate 是非負整數，status 是 queued 或 done。只彙總 queued 的 ticket；estimate=0 仍需計入 tickets 數。每位 owner 回傳精確欄位 owner、tickets、estimate（合計），依 owner 字串升冪排序；沒有 queued 項目便回空陣列。不要改動輸入物件或原陣列，也不要新增依賴。

可修改 summarize-queue.mjs 與 tests/summarize-queue.test.mjs，保留既有測試意義。檔案及本地測試已授權；不刪歷史、不做網路／全域設定／commit。最後交代實際改變、驗證結果與尚未完成項目。
