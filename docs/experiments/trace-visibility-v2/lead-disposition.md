# 模型有正確內容，外部工具紀錄卻空白

兩次新上下文控制已完成；Astra 28.460411 秒、Sol 30.001515 秒，64,821 已知 tokens，實際帳單未知。八個命令的十六個隨機 stream 標記全部被正確回報，但只有十四個標記出現在 captured tool events。

Astra U1/C3 的 stdout、stderr 各一個不同的 128-bit nonce 都出現在 final；對應 item_1 exit=0，aggregated_output 卻是空字串。nonce 不在 prompt、命令參數或任何非 agent_message 事件；模型可見輸入沒有採集端的 truth／hash 清單。實際觀察的八個命令均為預先指定 fixture 執行，沒有直接讀取 marker 檔、其他讀取或重試。十六個 fixture 檔案 hash 與檔案集合均未變。

這支持外部 CLI trace 不足以重建模型當時可取得的內容；不必把它推成特定內部工具實作的已知 bug，也不表示歷史上每個空輸出都其實成功。應區分「外部不可核實」與「已證明模型捏造」。一個報告仍可能有其他可獨立驗證的錯誤。

本批先做 AST 檢查，攔到主線產生腳本的換行錯誤，修復後才呼叫模型；不計作模型失敗。本控制不是 skill train／held-out，也不是人類理解試驗。前一個 cat 控制沒有重現，本批 Python probe 重現；到此停止擴張 telemetry 追查，回到 skill 目標。

## 對 verifier 演化的影響

不改舊 raw、評分、候選或 rubric。第一輪未採用仍未採用，但不能再用它的空 trace 推論候選讓模型說謊。第二輪評讀需對兩個匿名版本同等揭露這個已驗證的採集限制；這是證據有效性補充，不是為候選指定答案。若無法把執行差異和缺失紀錄分開，保留不確定，不能硬選 winner。
