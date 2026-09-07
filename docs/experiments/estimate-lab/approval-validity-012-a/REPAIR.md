# 核准有效性修補驗證

這份記錄接續 [唯讀診斷](CONCLUSION.md)，不修改當時未修復的歷史結論。只修 Claude source runtime 與對應測試，未改版本、導出、安裝或發布。

## 已修補的行為

- 已核准或已完成的案件，責任邊界或採用方案真正變更時，以既有 `estimate-ready`／Gate 5／`confirm-estimate` 重開核准。
- 待確認期間同兩欄位再次變更，刷新問題中的前後差異，避免 PM 看著上一版邊界回答。
- 明確退回 `draft`／`mapping` 與其他決策不被強制拉回核准；首次待確認亦不杜撰曾經核准。
- 原金額與舊交付物暫保留，但明說須重看估算影響、舊 revision 不代表新範圍已交付。
- 重新核准必須經既有 `record-answer` 路徑；一般 merge／append 不能只恢復 approved／complete 沿用歷史確認。
- 歷史 decisions、既有正式估算驗證與原子提交保障保留。純呈現、交付紀錄、no-op 不重開。

## 測試與保留的失敗

採 Hunt 先重現，再按 TDD 先紅後綠；每一輪 CLI 執行結果與暫存 fixture 均保留。

| 輪次 | 實測結果 | 證據 |
| --- | --- | --- |
| 原基線 | 53 通過 | [baseline](artifacts/repair-baseline.json) |
| 首批反例 | 6 項中 3 失敗 | [RED](artifacts/repair-red.json) |
| 首次修補全套 | 61 通過 | [GREEN](artifacts/repair-green.json) |
| 初次窄驗證 | 6 通過 | [review](artifacts/repair-review.json) |
| 連續變更反例 | 9 項中 2 失敗 | [RED B](artifacts/repair-red-b.json) |
| 中間修補回歸 | 64 項中 1 error | [保留失敗](artifacts/repair-green-b-failed.json) |
| 最終全套 | 64 通過 | [GREEN C](artifacts/repair-green-c.json) |
| 最終窄驗證 | 9 通過 | [review B](artifacts/repair-review-b.json) |

中間 error 是新規則錯把明確退回草稿的案件拉回 ready，觸發正式估算證據要求；已縮窄條件尊重 draft／mapping，並在完整重跑後通過，不是以忽略失敗或單純重跑結案。64 項包含主線同時新增的 2 項 finding-context 測試；本子任務新增 9 項。

## 範圍與限制

自動內容失效僅覆蓋 `outcome.responsibilityBoundary` 與 `selectedScenarioId` 兩欄位。未建立所有內容 hash 審批，也未聲稱涵蓋全部範圍、費率或數量修改。直接 merge workItems 的反證仍是拒絕且原檔不變。方案切換案例使用合成決策記錄，不是實際 PM 授權、人類可用性或模型能力實驗。

最終 runtime 相對凍結 0.1.2 為 61 行新增、2 行移除。0.1.2 凍結包、原 rev9 與穩定來源未變。[完整 hash 與各轮時間](artifacts/repair-final-hashes.json) 保存精確值。

8 次自動測試累計執行 43.615262 秒，包含 RED 與中間失敗，不是作者總耗時；最終全套 8.718374 秒、窄驗證 4.566994 秒。最終窄驗證在 2026-09-06 14:52:12（Asia/Taipei）完成。未啟動模型 calls；作者實際 token／費用無可觀察資料，記為 null。

