# Verifier 必要性診斷：不改技能，先量錯誤接受／錯誤拒收

固定四次新情境：Sol/high 無額外角色→Lab verifier，Astra/high Lab verifier→無額外角色。現有 lab-verifier.md 原文完整讀取，沒有新候選條款；這是診斷現有機制是否需要改，非 evolve 的結構評分／採用輪。普通 CLI 明確指定模型、不繞政策、不回退模型，240 秒每次，沒有重試。

每次相同三個全新離線唯讀 target 副本。R 使用前一批 none 真實 catalog/index/tests 與原 TASK/data（已驗證正確產品但測試誤綁 dict key order）。S 是 synthetic 明定 priority 降冪、同分 id 升冪的 top-N API，正確實作及對應順序斷言；V 是 synthetic allowlisted active 選取，產品只檢查 active 而漏掉 allowlist，既有測試未區分。三案只讓 reviewer 看原需求、source、tests，不看本設計、前輪答案、主線判讀或其他 reviewer。

所有組相同 review request：檢查產品及測試是否符合供應的契約，重大finding附位置、觸發及證據；沒有最低 finding 數，也不暗示故障種類。允許只讀命令、python3 -B 原測試／in-memory 反例，不能改 target/test/acceptance、寫檔、聯網、讀其他目錄或轉派；raw 需人工覆核，事後 hash 不替代過程安全。Reviewer fresh context 與產品作者不同，但不是盲於角色措辭；固定順序、小樣本不作模型排名。

凍結成功判準：R 區分現行產品正確與 key insertion order 非契約造成的測試誤擋；S 不將契約明定輸出順序誤稱過約束；V 指出未授權 ID 即使 active 也不應返回且目前測試漏抓。可以有其他真實且因果支持的發現。不要以抓到R一點抵銷S/V的誤判。語義結果由主線對 raw 及可執行反例核對，不讓模型自評。

如果兩版均正確，不加新必讀規則；如果現有角色缺口重現，再另凍結一個變因候選，不動本輪，保留新題做後續驗證。這次不是完整 Review／Seal lifecycle 或真人一週試用。
