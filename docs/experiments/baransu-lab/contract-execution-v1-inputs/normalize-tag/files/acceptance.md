# CONTRACT — normalizeTag 合成局部修復

## 目標

修復本機字串標籤正規化；只處理 string 輸入，不涉及外部系統、部署或商務承諾。
這是實驗駕駛者固定的測試需求，不是真人已審閱的合約或正式業務核准。
駕駛者明確授權依下列需求做局部實作與測試；不需新增產品方向決策。

## 前提（Premises）

- 需求：使用 JavaScript String.trim 的前後空白語義，只將 ASCII A 到 Z 轉成小寫；其他字元原樣保留。
- 既有程式與測試位於 src/normalize-tag.mjs、tests/normalize-tag.test.mjs；實際缺陷與測試覆蓋仍需由本輪讀取／執行確認。

## 可斷言條文

- [ ] A1：前後空白依 JavaScript String.trim 移除，不得把內部空格、tab 或換行縮併、移除或替換。
- [ ] A2：ASCII A 到 Z 轉成對應小寫；非 ASCII 字元（包括其大小寫及全形字元）不得改變。
- [ ] A3：trim 後為空字串時拋出 Error，其 message 必須精確等於 EMPTY_TAG，不能加前後綴。
- [ ] A4：現有兩個可執行測試仍成立，新增測試必須經過真實 export 函式，不 mock 被驗證層。
- [ ] A5：只改指定函式與相關測試；不引入依賴，不改輸入領域，不新增外部操作。
- [ ] A6：交接列出實際修改、已執行的檢查及未完成項目；不將作者自審宣稱為獨立 seal。

## 錯不起表面（Surface Inventory）

| 表面 | 格式 | 影響 | 釘死測試 |
|---|---|---|---|
| normalizeTag 回傳字串 | trim 邊界＋ASCII-only 小寫，內部與非ASCII不變 | 呼叫端標籤值 → 不得默默改掉原字元或內部空白｜上下游契約 | 本輪需補可執行行為測試 |
| 空值錯誤 | Error.message 精確 EMPTY_TAG | 呼叫端錯誤分支 → 必須能可靠辨識空標籤｜上下游契約 | 本輪需補精確錯誤斷言 |

## Verbatim Constants

```text
EMPTY_TAG
```
