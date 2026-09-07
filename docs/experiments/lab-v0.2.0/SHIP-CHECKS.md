# Lab 本輪出貨檢查

檢查時間：2026-09-07 09:03（Asia/Taipei）。目標是 `origin/main`，不是 `company` remote，也不切換目前 App 的插件安裝。

本次一併提交先前尚未進 Git 的 Lab source、各版凍結包、測試工具、實驗證據與呈現產物。0.2.0 修訂報告與 measurement 中的「未發佈／未 commit」是當時快照，不代表本次 ship 後狀態；Git commit 與遠端分支才是發佈依據。

- fetch 後本地 main 與 origin/main 的 ahead／behind 為 0／0。
- 1,092 個 JSON 可解析，正式 marketplace 路徑檢查與 `LINKSTART_RELEASE_VALID` 通過。
- 0.2.0 三包共 60 個凍結檔案的 SHA-256，仍與先前驗證及隔離安裝收據一致。
- pending 路徑未命中 ship 的機敏檔名清單；指定來源、報告與測試目錄的常見 credential 內容模式未命中。這不是保證所有秘密都可被正則檢查發現。
- staged 全量空白檢查有警告：既有實驗快照的 CRLF、檔尾空行，以及 diff 工件保留的尾端空白。未為消除警告改寫凍結證據、變更 Git 全域規則或宣稱全量 whitespace check 通過。

依 ship allowlist，`.codex/evolve/lab-verifier` 已移到本地、Git 忽略的 `.codex/archived/lab-verifier`；1 個目錄、626 個檔案、19,410,621 bytes，來源父目錄保留。這不是刪除，必要時可將該目錄搬回原位。歸檔不含 `.codex/presentation-pilot` 等非 allowlist 產物，也沒有移動其他 plugin 或案件。

歷史實驗內指向舊 `.codex/evolve/lab-verifier` 的本機路徑，現在可透過上面的 archive 對照取回。未新增根目錄穩定 marketplace 的 Lab 入口；三包仍各用自己的實驗 marketplace。
