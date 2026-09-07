# CLI 輸出控制：unittest 與 probe

兩個新上下文 Astra／Sol，各四個只執行一次的合成命令：兩個 unittest、兩個 python -c probe。stdout／stderr 各含不同的 128-bit 隨機標記，標記只存在命令會讀取的 fixture，沒有出現在 prompt 或命令參數。每次命令使用不同 fixture，避免從前次讀取得知標記。local self-check 驗證兩條 stream 與 7 tests。

這是外部紀錄是否足以重建模型可見內容的有限量測控制，不計入 skill train／held-out、不改 rubric。若 final 有正確 nonce 但任何 captured tool output 都無對應內容，可支持採集缺口；全可見只代表本批未重現，不能修補歷史空白。兩次 normal read-only CLI、不變更政策、不重試。結束後不再無限追查 telemetry。
