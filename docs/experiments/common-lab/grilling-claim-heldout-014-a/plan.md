# Grilling：保留待驗證主張

這是新的 source-level 實驗，最多 6 次 generation calls（gpt-6-astra／high），沒有 judge calls。A 為凍結 Claude source 0.1.3；B 為只新增一段原則的 0.1.4 候選。兩臂均讀 source 根檔，不混合 generated/source frontmatter；本輪不導出。

原小任務的凍結 rubric 第 3 條是 OR，0.1.3 B 正確指出盲點已滿足該條。拿掉欄位名稱是 supplemental quality finding，不能事後改舊分數。這次 cases.json 另凍結「保留原主張／明示替代主張」判準，用原輸入重測與兩個新場景驗證。

新場景是依文件做 mock 恢復（不能偷換成記憶或診斷）和已定位 bug 修復（不能偷換成從零找 bug）。兩者都保留真正值得質疑的混淆：口頭逐步帶做、僅用已通過 smoke test 充當修復證据。允許明示不同主張的可選測試，不把不提替代方案當唯一好答案。

A/B body 唯一差異：

> When improving a method or test, preserve the claim it is meant to validate, including the information or assistance that defines the task. A different or stricter test may be useful, but explicitly distinguish what it would measure instead of silently substituting it.

版本 0.1.3／0.1.4 歸屬由各自 Claude manifest 與 source-receipt.json 記錄；runner 的 Codex plugin_versions 必須如實為 null。凍結範圍包括案例、根檔、版本證據和 runner hash，所有正式推論原始輸出、實耗用量與時間保留。主線按新凍結 criteria/guards 做未盲語意審閱，不以字數、標題數或問句數判定。
