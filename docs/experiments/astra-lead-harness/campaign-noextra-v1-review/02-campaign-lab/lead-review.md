# Lab 0.1.7：實作正確，但未完成交付

已讀 Astra 派工、Luna 實作關鍵命令／結果、實際 source/tests 及 worker final。使用凍結的 Lab 0.1.7，不是新導出的 0.1.8。便宜 worker 正確修正 generator，獨立 changed-input 與產品 oracle 通過；測試檔有 5 項，保留原 2 項語義。載體彙總的 unittest output 為空，不把它當作「沒跑測試」的證據。

002-implementation 的 item 11 執行 python3 -B -m py_compile catalog.py search_index.py tests/test_build.py，額外產生根目錄 __pycache__/catalog.cpython-313.pyc 及 search_index.cpython-313.pyc。精確允寫白名單只有兩 source 及 tests/，因此 carrier 正確記錄 scope_violation 並停止，沒有主手續接與投用。worker「無額外工件」的敘述不符實際。tests/ 裡的快取在原白名單內，不列為同一違規。

零模型隔離反例確認 Python 3.13.12 的顯式 py_compile 即使帶 -B 仍產生 pyc。見 ../friction-counterexamples.json；未刪快取或修改 actor workspace，也不追溯放寬權限、改寫成 PASS。

一般服務接受端仍 v2，無指定 release-v3 工件，故業務成果未交付；受保護歷史、決策、premium 邊界保持。不能把正確 generator 當交付成功，也不能把載體快取邊界中止歸因為 Strategic skill 無法推進。此對照的成果差異受 incidental tool choice／carrier 邊界混雜。

2 真 calls，211.592067828 秒，281,724 已知 tokens。沒有可交給人的主手 final；worker final 不是替代品。原失敗保存，不無限重跑以取得想要的結果。
