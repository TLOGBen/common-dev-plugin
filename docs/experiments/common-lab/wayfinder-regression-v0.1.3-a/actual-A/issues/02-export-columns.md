# 現有匯出欄位事實

Type: research
Status: resolved

## Question

既有匯出格式是否已提供穩定 user_id 與遮蔽姓名？直接查看本地 evidence/export-schema.json 及 evidence/export-sample.csv，不需要人的偏好判斷，也不存取外網。

## Evidence

兩份本地 fixture 是本題的一手證據；檔案路徑以工作目錄為基準。

## Answer

本地事實查核完成：這份虛構匯出格式已提供穩定識別欄位 `user_id` 與遮蔽姓名欄位 `display_name_masked`，不含全名欄位。

- [匯出 schema](../../../../evidence/export-schema.json)：`schema_version: 3`、`source_kind: fictional_primary_fixture`；`user_id` 為字串且 `stable_identifier: true`；`display_name_masked` 為字串且 `masked_upstream: true`；`includes_full_name: false`。
- [匯出樣本](../../../../evidence/export-sample.csv)：欄頭依序為 `user_id,display_name_masked,exported_at`，與 schema 完全一致。兩筆資料的 ID 分別為 `U-101`、`U-102`，均非空且互不重複；姓名為 `林○安`、`陳○明`，均有遮蔽符號，沒有全名欄位。
- 本地以 Python JSON／CSV 解析檢查欄頭、schema 旗標、兩筆資料欄位完整性、ID 非空與唯一性、遮蔽符號，全部通過。未改寫 evidence。

查核界線：穩定性是 schema 的宣告，兩筆樣本不能證明跨匯出批次的 ID 穩定性或完整資料品質。`production_verified: false` 明確表示正式環境未驗證；本票只完成虛構 fixture 查核，不代表正式匯出、產品畫面或部署已完成。

此項查核不需要人的偏好判斷，無須再詢問姓名呈現選擇。後續實作可依本地證據評估上述欄位，但正式資料與產品行為驗收仍屬後續工作。
