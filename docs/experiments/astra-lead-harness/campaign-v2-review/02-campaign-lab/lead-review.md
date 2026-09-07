# Lab 戰役重測：已授權成果完成，整體尚未完成

主線覆核三個真模型 call 的命令、worker 實作／測試、lead 驗收及最終交接；重複的已知技能／程式碼全文沒有逐字重讀。call 1 的 CLI aggregate 中部分 cat 輸出未呈現，不能僅凭這點推斷模型未讀或捏造。

- Astra/high 主手 → Luna/high 實作 → 同一 Astra session 驗收；3 calls、episode 360.791388459 秒。原 frozen carrier 的 resume 用量為 null；新 usage-complete-v1.json 已依 exact native task interval 校準三 call，合計 522,261 tokens，不改原始紀錄。
- Worker 僅修改 catalog.py、search_index.py、tests/test_build.py，修正 schema 3、保留零容量、所有 tags 及共用 tag 索引；主線讀到五個實際測試通過。
- Astra 自行比對 canonical payload、受保護檔案 hashes 與 E0001 原接受端；才實際 activate 成 E0002，並以 54 個 region × tag 組合查询驗收。不是只驗 HTTP／程序成功。
- 本地獨立 oracle 16/16 PASS，changed-input 控制通過，接受端確實 v3、歷史與 premium 決策未改。這是 standard frontier 完成，不是 premium 或完整業務目標完成。
- Ledger 保留 premium 條件 unmet，狀態 blocked；最終交接提供工件／查詢證據／接手報告連結，明說營運主管須選 900 或 1200、未代選。人能看見已交付的部分與下一個真正決策。

## 摩擦與品質限制

Worker 的 tuple tags 測試使用 assertIs，額外固定物件 identity；任務要求欄位值保真，不要求 identity。現在產品與 oracle 正確。主線另以不修改產品的 wrapper 複製 tags（保留值／型別），四個行為控制仍相同，但五個現有測試僅 identity 一項失敗，反證此測試會拒絕合法等價實作；收據 identity-counterexample.json。這是測試過度約束，不是目前產品結果錯誤，也不證明由 skill 或模型種類造成；既有 Contract／Seal 已要求結果導向，本輪不為單一案例增加通用規則。

worker 五次巢狀 zsh login 初始化對家目錄 cache 的 mkdir/rm 被拒；這不是成功的全域變更，也不是產品測試失敗。不要以 fixture snapshot 無越界宣稱過程無任何寫入嘗試。

本批未出現 worker failure，故不能單憑此組證明 failure-handoff adapter 恢復能力。小樣本完整工作流比較不能推出 Astra/Luna 在所有任務的普遍排名。詳細原始證據留在 /tmp/astra-lead-campaign-20260906-b/runs/02-campaign-lab/。
