# CLI 工具輸出的證據邊界

2026-09-06 查閱 [OpenAI 非互動模式文件](https://learn.chatgpt.com/docs/non-interactive-mode)：`--json` 把 stdout 改為 JSONL 事件流，含命令、訊息與回合用量；此頁沒有說明 `aggregated_output` 空字串是否能證明模型當時看不到命令輸出。

另讀 [App Server 事件文件](https://learn.chatgpt.com/docs/app-server)：該協定的 commandExecution 帶可選 aggregatedOutput，stdout／stderr 另有 outputDelta。這是不同接口，不把其欄位語義直接套用為本機 CLI 缺失輸出的根因。

目前僅可確認我們保存的若干 CLI completed 事件輸出為空；沒有重新定義 exit 0 為未執行或失敗。需另以不可預猜的合成 marker 比對模型回覆與工具事件，才能測試紀錄是否足以重建回覆依據。未讀取金鑰、改動權限或組織政策。
