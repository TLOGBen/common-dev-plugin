# 隔離執行測試：事前設計

這兩案不是桌面口述：受測模型必須真的讀本地資料、操作已授權的 Markdown/新 HTML 或寫驗收產物。業務資料仍是虛構 fixture，不代表真實郵件送達或產品發布。

- Wayfinder：人已回答票 23，模型需記錄答案、消除地圖/焦點的舊問題，並繼續獨立票 02 的事實工作。24 程式實作留在範圍外。
- Strategic：worker 的 DONE 與錯誤 checker 的 PASS 都是待核證據。相同 intent 的兩個成功 dispatch 是兩次；同一成功 receipt 重複 log 是一次；失敗 attempt 後一次成功也是一次。舊 hash 收據不可驗收新 artifact。

判準在 cases.json；它不會放進受測模型的工作目錄或 prompt。每次 run 要以已凍結 design plan 建立全新暫存 CWD，精確指定 model 與 skill package，保留原 approval/exec-policy，使用 workspace-write 而非解除 sandbox。未經主線授權不得啟动 inference。

驗證器只產生可觀察事實（狀態、檔案、hash、輸出及 trace）；不能用字串命中或模型自評代替人工語意審查。人類不在，沒有真人理解度或等待時間結果。測試後保留全部 fixture，無自動 cleanup。
