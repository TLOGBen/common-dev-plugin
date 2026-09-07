# normalizeTag 交接

## 已完成的本機工作

- 修復 `src/normalize-tag.mjs`：只處理 string；使用 `trim()` 移除前後邊界；只將 ASCII `A-Z` 轉為小寫；內部空白與所有非 ASCII 字元原樣保留。
- trim 後為空字串時拋出 `Error`，`Error.message` 精確為 `EMPTY_TAG`。
- 在 `tests/normalize-tag.test.mjs` 保留既有兩個測試並新增行為測試，均經由真實 export 函式執行，未 mock 被驗證層。
- 保留既有 `acceptance.md` 條文與 Verbatim Constants，附加本輪非互動預設註記及查證記錄。

## 驗證結果

- 實際執行：`node --test tests/normalize-tag.test.mjs`
- 結果：測試檔案通過；指定 runner summary 為 1 pass、0 fail、0 skipped、0 cancelled（檔案內保留 4 個 `test(...)` 案例）。
- RED→GREEN：新增核心行為測試先確認失敗，再完成實作；新增空值錯誤測試先確認失敗，再完成錯誤分支；最後完整測試通過。

## 剩餘事項與人工介入

- 本次只完成合成 fixture 的局部本機程式與測試；沒有執行任何外部系統、部署、發布或商業活動，因此不存在已完成的真實業務結果可交付。
- 依本次範圍，未執行 contract 技能的 selection telemetry、正式 seal、sealed marker、Stop-hook 紀錄或發布流程；未建立 `CONTRACT.md`，以免超出指定可變更路徑。
- 如需正式採納、獨立審閱、seal 或發布，仍需人類依其治理流程審閱與核准；本檔不將駕駛者授權或本輪自動驗證視為真人審閱或商業核准。
