# Map: 客服名單隱私交棒

## Destination

把名單姓名呈現與現有匯出資料的事實釐清，交給後續實作；本回合不改產品。

## Notes

- 此圖沿用既有 ticket ID；02 是獨立本地研究，23 是人的取捨，24 是後續產品實作。
- 現有登入與權限不變。
- 本回合只更新本圖與既有票券、查核本地 evidence，並產生 `map.next.html`（`--no-open`）；保留既有 `map.html` 與歷史證據。
- 使用者已親自提供姓名呈現答案；本回合不委派、不載入其他 skills、不連網、不執行產品實作。
- 本地資料均為虛構 fixture；本圖的完成不代表真實業務事件、正式環境驗證或產品發布。

## Decisions so far

- 沿用現有內網與登入流程。
- [名單姓名呈現](issues/23-name-presentation.md) — 使用者已定案遮蔽姓名，無須重問。
- [現有匯出欄位事實](issues/02-export-columns.md) — 本地 schema 與兩筆樣本已查核，具穩定 ID 宣告與遮蔽姓名；正式環境未驗證。

## Not yet specified

- 無；本回合目的地所需的決策與本地查核均已完成。

## Out of scope

- [產品畫面實作](issues/24-implement-view.md) — 已以範圍外結案，程式仍未實作；產品修改、正式環境驗證及發布均不在本回合授權內。

## Current focus

決策與本地查核完成，無待回答選擇、無本回合可接續的執行票券。交接依據為[名單姓名呈現](issues/23-name-presentation.md)與[現有匯出欄位事實](issues/02-export-columns.md)。

本回合無須人介入；若要達成產品實際顯示遮蔽姓名的結果，需另行授權[產品畫面實作](issues/24-implement-view.md)與驗收。範圍外結案不等於產品完成。
