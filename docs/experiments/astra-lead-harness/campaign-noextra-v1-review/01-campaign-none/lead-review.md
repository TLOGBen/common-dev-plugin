# 無額外 Strategic skill：主線複核

已讀兩輪 Astra 主手及真 Luna 實作的關鍵命令、派工 brief、實際產品、測試與 final；重複的既有公開 source dump 不另聲稱逐字重讀。None 未供應額外 skill package，觀察到的命令只讀任務／工作目錄，未見載入全域技能。不是完全沒有 harness：工具、權限、角色、載體 JSON、失敗交接及明確任務仍存在。

Luna 實際修改 catalog.py、search_index.py、tests/test_build.py。Astra 回來讀取並驗收，7 項測試及 54 組真接受端查詢通過；一般服務僅投用一次 E0002。獨立 oracle 16/16 PASS，含 changed-input，不靠固定資料硬編答案。指定發布工件與接受端 canonical identity 一致。Premium 人的 900/1200 決定未代填；全目標仍未完成。

Final 有可點入的實物發布檔與驗收報告，列出關鍵查詢及未完成的 premium；不是單純 PASS 印章。沒有真人閱讀測試。

摩擦：worker 在非 Git fixture 查 git status；不是產品失敗。更重要的是 tests/test_build.py:61 使用 list(item) 指定欄位插入順序，公開需求只要求欄位與 canonical JSON。主線零模型反例將每項 dict 鍵順序反轉但內容、型別、canonical bytes 不變，7 測試中 1 項誤擋；原產品本身仍正確。見 ../friction-counterexamples.json，原工作目錄雜湊不變。

3 真 calls，296.120798100 秒，431,345 已知 tokens（105,926 + 177,290 + 148,129）。最後 resume 的 carrier usage null 由精確 native invocation 增量校準，未改原紀錄；詳 ../usage-complete-v1.json。不能從一次成功推論所有大型系統均不需持久狀態。
