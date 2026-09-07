# Map: 客服名單隱私交棒

## Destination

把名單姓名呈現與現有匯出資料的事實釐清，交給後續實作；本回合不改產品。

## Notes

- 此圖沿用既有 ticket ID；02 是獨立本地研究，23 是人的取捨，24 是後續產品實作。
- 現有登入與權限不變。
- 本回合完成的是虛構 fixture 的本地查核與文件交棒；未執行真實業務活動或產品變更。
- 本回合無待回答的人類選擇，不需介入。票 24 雖已解除票 23 的依賴，仍在授權範圍外；若要推進產品實作，須另行授權。

## Decisions so far

- 沿用現有內網與登入流程。
- [票 23：名單姓名呈現](issues/23-name-presentation.md#answer) 已定案：使用者明確選擇「遮蔽姓名」，原票已結案，不再等待同一選擇。
- [票 02：現有匯出欄位事實](issues/02-export-columns.md#answer) 已完成本地查核並結案：schema 宣告穩定 `user_id` 與上游遮蔽 `display_name_masked`，兩筆 CSV 樣本欄位相符且無全名欄位。

## Not yet specified

- 正式環境的匯出行為、跨次匯出 ID 穩定性與完整資料遮蔽品質未驗證；票 02 的結論僅限虛構本地 fixture，schema 明示 `production_verified: false`。
- [票 24：產品畫面實作](issues/24-implement-view.md) 保持 open；遮蔽姓名尚未套用至產品，產品驗證與發布亦未完成。

## Out of scope

- [產品畫面實作](issues/24-implement-view.md)：不在本回合授權內，不發布產品。
- 不改 product/、歷史 evidence 或既有 map.html；新的地圖檢視輸出為 map.next.html，使用 --no-open。
