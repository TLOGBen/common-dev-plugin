# 現有匯出欄位事實

Type: research
Status: resolved

## Question

既有匯出格式是否已提供穩定 user_id 與遮蔽姓名？直接查看本地 evidence/export-schema.json 及 evidence/export-sample.csv，不需要人的偏好判斷，也不存取外網。

## Evidence

兩份本地 fixture 是本題的一手證據；檔案路徑以工作目錄為基準。

- `evidence/export-schema.json`：schema_version 為 3；`user_id` 為 string 且 `stable_identifier: true`；`display_name_masked` 為 string 且 `masked_upstream: true`；另有 `exported_at`。`includes_full_name: false`。
- `evidence/export-sample.csv`：表頭與 schema 的三個欄位及順序一致；兩筆資料分別為 `U-101`／`林○安`、`U-102`／`陳○明`。兩筆 ID 非空且在此樣本內不重複，姓名皆含遮蔽符號；無全名欄位。
- 本地以 Python JSON／CSV 解析核對上述欄位、宣告、筆數、非空值、樣本 ID 唯一性與遮蔽符號，檢查通過。
- schema 明示 `source_kind: fictional_primary_fixture` 與 `production_verified: false`；這些是虛構本地證據，未驗證正式環境。

## Answer

是，就本地 fixture 而言，既有匯出格式已提供宣告為穩定識別碼的 `user_id` 與上游遮蔽姓名 `display_name_masked`，CSV 樣本與宣告相符，不包含全名欄位。

穩定性依據是 schema 的明確宣告；單份兩筆樣本只能確認樣本內 ID 唯一，不能證明跨次匯出的穩定性、全部資料的遮蔽品質或正式環境行為。本票的本地查核已完成，無須使用者再次選擇姓名方案。

## Comments

結論已回寫地圖，可供後續票 24 參考；並未修改產品、連線外部服務或驗證正式環境。
