# 05 · Bundle / Common Lab 0.1.5

主線完整閱讀 3 次 CLI 的 prompt、stdout/result、主手實際驗收與最後交接；針對 CLI 空白的 status 回應另核對 exact native session，不將序列化缺漏判成模型造證。

獨立 oracle 14 項全部通過：generator 原資料與換資料皆符合精確 JSON，主手指定的新工件正確，接受端保留唯一 D0001 且 caller 可見、無新重複投遞。artifact 為 artifacts/catalog-release-v2-verified.json；canonical payload SHA-256 c50cc8aaa4c6632a4f05d0f0a2766101a21965c6080f3856d68ed246d281dba9。

Astra 實際派 Luna 修改 generator/tests，回來後讀碼、重跑 5 個 unittest、產出新工件、核對內容與 hash、以 ensure 揭露原有正確接受事件，再讀 status。沒有把 worker 完成當成業務完成；final 正確回報兩项成果與工件。Lab Delegate/runtime/executor 有載入，Strategic 沒有，因此此例不能證明完整 Strategic 的效果。

摩擦：worker 新測試曾少一個結尾括號，遭 SyntaxError 後修正，保留原始軌跡。主手把共同 transport 的「24 CLI calls」誤讀成一般 shell/tool 次數，brief 提了 5 次限制；這是共享載體的歧義，不是 Lab 的因果效果。下輪所有組共用明確的 MODEL invocations 說明，這批不回寫。

耗時 191.722677125 秒；校準後 407,280 tokens（lead 251,671；worker 155,609），詳見相鄰 usage checkpoint；帳單費用未知。三次模型呼叫、單次合成觀察、不隨機且不盲測。語意交接經主線核對，並未測量真人理解或滿意。
