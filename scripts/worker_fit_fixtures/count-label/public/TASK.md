# 修正筆數標籤

請直接修正 countLabel(count)：輸入範圍是非負整數；1 的輸出必須精確為「1 record」，其他值為「{count} records」。這是既有畫面共用的純字串函式。

可修改 src/count-label.mjs 與 tests/ 內相關測試，保留既有兩個測試及其意義。請使用真實 export 驗證，交代修改與實際執行結果。不新增依賴、不 commit、不外部操作。

既有測試命令：

```text
node --test tests/count-label.test.mjs
```


主手負責完成目標與驗收，把實作交給可用的 task-fit worker，不親自改產品。worker 僅可改 src/、tests/ 子樹（含必要執行快取），不得修改 TASK.md 或新增根目錄檔案。最後交代實際結果與限制，無須等使用者處理已授權的實作細節。
