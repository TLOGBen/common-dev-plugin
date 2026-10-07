# 操作輸入與定價產物

這是原本工時明細的可計算表示，不另做全庫盤點或新表單審核。定價者先讀完整無人天清單，保持原 ID、必要施工、共享歸屬與責任。把既有操作明細直接保存到新的 JSON 檔，再執行：

`python3 ${CLAUDE_PLUGIN_ROOT}/skills/cold-estimation/scripts/estimate_math.py <操作輸入.json> <尚不存在的版本目錄>`

輸出 input.json 保留原始位元及 SHA-256，result.json 是唯一數列，pricing.md 是同資料生成的內部明細。不得覆寫已產生的目錄；修正原始事實用新輸入與新版本目錄，在回覆說明受影響 ID 與事實差異。工具失敗就依錯誤修正輸入，不另手寫結果假稱已通過。工具不可用則如實說明並沿用原公式有限交付。

最小形狀（數字僅為格式示例，不是單價）：

```json
{"hours_per_day":8,"items":[
 {"id":"W1","name":"工項名稱","basis":"原清單的工程依據","references":"已承接操作 ID 與結果，無則省略","operations":[
  {"id":"W1-E1","kind":"E","description":"扣除引用後的實際施工與產出","hours":3,"count":1},
  {"id":"W1-V1","kind":"V","description":"必要驗證操作與新結果","hours":2,"count":1}
 ]}
]}
```

- 每個操作 ID 全表唯一；同一操作不可因換 ID 再收。hours 是每次工時，count 是真正重做次數，省略時為1；E/V只選一類。零修改仍保留該列必要驗證；整列無實做時用 operations:[] 與 zero_reason 說明。
- 實際修改批次沿用 operations，將 hours 寫為在 N₀ 支參考規模完成該批次的基準工時，另帶 `"batch":{"unit":"API","baseline_count":365,"actual_count":500}`；頁面或 DAO 使用 rate-card.md 的同類分母或使用者指定值。不再帶 count；工具計算 hours × actual_count / baseline_count，拒絕同時乘兩種次數。每組 E、V 分列操作 ID 並各帶相同數量依據；基準工時不可已按本案支數放大。只有實際需要隨數量換算的操作帶 batch，共用一次及獨立例外保持原輸入。不得省略或填 0 作未知支數的替代。
- 含 batch 的自然工項先加總 E／V 換算後工時、各除以 8，再以 ROUND_HALF_UP 四捨五入；不含 batch 的列仍向上取整。工具保留 batch_inputs 供覆核。框架固定 30＋10 人天照原 E 240／V 80 小時及包數 count 表示，標明經驗費率換算且不帶 batch；已含能力不另收一次。
- 使用者未拆 E／V 的固定額度或已有未拆新建單價，該列用 fixed_pd 與 basis，保留未拆、不補造 E/V；同列不再放 operations 或 additions。
- 逐件分級單價（rate-card.md「逐件分級單價」）的列用 `units` 陣列，不用 operations：每個單位帶全表唯一 id、分級名 tier、件數 count、每件 E_pd 與 V_pd、一句 description 說明「一件」是什麼；basis 寫明分級與件數來自哪一份逐件清單、單價表來自使用者或手冊預設。工具算每個單位 count × 每件人天、同列各單位加總成 E／V，不經小時。同一列可放多個分級與折價單位，例如「共用群組第 2 件起」用較低的每件人天另列一個單位；去重後不做的件數不出現在 count。預設 `unit_rounding:"exact"` 保留小數，讓逐件清單逐列加總能對回主表；使用者要整數主表時該列改 `"half_up"`，於加總後各欄四捨五入。units 列不放 fixed_pd、operations 或 additions；逐件單價未涵蓋的例外另立工項以 operations 或 additions 計。

```json
{"id":"W5","name":"API 搬移（逐件分級）","basis":"盤點/API逐支清單.csv 去重後件數；單價表由使用者指定","units":[
 {"id":"W5-U1","tier":"CRUD","count":176,"E_pd":0.5,"V_pd":0.25,"description":"單表查詢或單筆寫入，無其他業務邏輯的端點"},
 {"id":"W5-U2","tier":"中等","count":55,"E_pd":2,"V_pd":1,"description":"5–8 步業務邏輯或有對外接觸的端點"}
]}
```
- 基準按上節規則於操作加總後 E/V 分欄取整。一般加值才用 additions 陣列，例如 {"basis":"基準未涵蓋的具體剩餘操作","unit":"hours","E":[1,3],"V":[0,0]}，仍取中點並向上取整，不套 batch 倍率。必須保留真實低高；只有人天區間就 unit:"pd"，總額未拆則 unsplit:[低,高]，不補造小時。不要為了示範而新增 A。
- 必要工作尚無法定價：該列 pending:true 與 pending_reason，不同時填 operations/fixed_pd/additions。工具列待估；超20%的加值也標待處理，不截價、不把待估算0。重大異動依原規則回查已知施工後另定必要工項。
- 工具只驗算、保留輸入與產生表，不會證明普通除錯可當 A、操作 ID 不同就無重複、來源角色正確、工時合理或逐件分級正確。主線核對原始工項與操作，再接受數列；文稿只轉述接受版本的 final E/V、未拆與合計，完整施工說明仍沿用原清單。
