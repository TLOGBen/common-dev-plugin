# 補齊事件投影器

完成 src/projector.py 匯出的 project_accounts(snapshots, events, requested_ids)，讓它把快照與可能亂序、重送的事件合成可相信的帳戶結果。src/normalization.py 是既有輔助模組，可以調整；不要求特定內部分層。

## 輸入契約

三個參數都是 list。snapshot 至少有 account_id（非空字串）、revision（非負整數）及 balance（整數）；account_id 不可重複。event 至少有 event_id、account_id（各為非空字串）、revision（正整數）、delta（整數，可為零或負數）。requested_ids 只含非空字串。所有整數都不接受 bool。額外欄位可存在但不影響語意。違反上述規則一律拋 ValueError；錯誤文字不指定。

先驗證全部輸入，再處理查詢。即使某帳戶未被 requested_ids 選中、事件早於快照或帳戶未知，也不能略過無效資料或衝突。

## 重送與衝突

同一 event_id 若 account_id、revision、delta 相同，視為同一事件，額外欄位差異不構成衝突；每個額外重送計入 duplicates_ignored。相同 event_id 的上述內容不同則 ValueError。不同 event_id 若占用同一 (account_id, revision)，也必須 ValueError，即使 delta 相同。所有事件均適用，包括快照之前與未知帳戶。

## 輸出契約

回傳只有 accounts、duplicates_ignored 兩個欄位的 dict。accounts 按 requested_ids 去重後的字串升序排列，每筆只有 account_id、status、revision、balance、first_missing_revision 五欄。dict 插入順序與物件 identity 不屬於契約。

- 無快照：status='missing'，revision、balance、first_missing_revision 都為 None；不可從事件憑空建立起始餘額。
- 有快照：忽略 revision <= snapshot.revision 的有效歷史事件，按 revision 由小到大套用後續 delta。不得因事件到達順序不同而改變結果。
- 後續 revision 從 snapshot.revision+1 完全連續：status='complete'，revision 是最後套用的 revision（無新事件時為快照值），balance 是快照加上各新 delta，first_missing_revision=None。
- 有缺口：只套用缺口前連續的事件；status='incomplete'，revision 是最後已連續套用值，balance=None（不可把部分餘額當完整結果），first_missing_revision 是第一個缺失 revision。缺口後事件不得先套用。很大的 revision 也應直接處理，不逐一列舉缺少的整數。

不得修改任何輸入，包含 list 順序、dict 及其額外欄位。不要依賴特定 fixture 的 ID、數字或順序。

## 完成與範圍

實作與相關測試只可改 src/、tests/；可在這兩個子樹內產生執行快取。保留既有測試的意義並補足必要反例。不新增依賴、網路、設定、部署或 commit。此為純記憶體合成資料，無真實帳務或外部系統。

既有測試：python3 -B -m unittest discover -s tests -v

主手負責完成目標與驗收，將實作交给可用的 task-fit worker，不親自改產品。收回成果後確認實際行為，最後向使用者簡明交代完成了什麼、實際證據與剩餘限制；不需要等待使用者替你決定已授權的實作細節。
