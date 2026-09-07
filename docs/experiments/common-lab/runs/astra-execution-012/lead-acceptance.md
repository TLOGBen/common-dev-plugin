# 隔離實作主線驗收

驗收時間：2026-09-06 12:39（Asia/Taipei）。主線直接閱讀四組實際產物、事件語意、來源／產物 hash 與執行 trace；不是只接受 worker DONE。A 為正式版，B 為凍結 Common Lab 0.1.2。作者知悉版本，非盲評。

## 結論

四次本地任務均達成預先固定的七項語意判準及寫入邊界。這是隔離 fixture 的查核與產物任務完成，不是產品發布、真實寄送成功或真人理解測試。兩個情境各只一個配對，不能形成跨任務品質排名。

| 情境 | 正式版 A | Lab B | 可觀察成果 |
|---|---|---|---|
| Wayfinder 回答後使用者離線 | 本地任務完成 | 本地任務完成 | 23 記錄真實提供的遮蔽姓名答案；02 實讀 schema 與兩筆樣本；產生新的 HTML；產品程式未改 |
| Strategic 拒收錯誤綠燈 | 本地任務完成，業務目標拒收 | 本地任務完成，業務目標拒收 | 實跑 checker、獨立重算成功寄送與控制組、辨识舊收據不適用，寫出拒收與交接文件 |

### Wayfinder

兩組皆未重問已回答的取捨，也未因使用者離線而停止本地事實查核。schema 的穩定 ID 宣告與樣本兩筆唯一性，均未被誇大為跨批次或正式環境驗證。五項修改均在 allowlist；原 map.html、evidence 和 product 保持 byte-identical。

A 將票 24 標為 resolved 並明說「範圍外結案、未實作」，B 保留 open 並明說超出授權。原版 SKILL 明定 scope 外票應關閉，所以不能以 B 的狀態慣例倒扣 A。兩者均符合「未宣稱產品完成」的原判準。A 移除原待答焦點語意，B 清除 Current focus 23；不能把 B 新增的 pointer 格式強套給 A。

兩份 HTML 已由實際 renderer 從更新後 Markdown 生成；本次主線 acceptance 不包含額外瀏覽器像素檢查。B 的 open/out-of-scope 票在 renderer 仍可被標為「可處理」，worker 已補註它僅指依賴，不代表授權；這是值得下一輪驗證的呈現摩擦，不在本輪事後改成失敗判準。

### Strategic

主事件有兩組不同成功 dispatch/receipt，因此成功寄送為 2；相同成功 receipt 的重複 log 為 1，失敗後一次成功也為 1。checker 只算 distinct intent 而產生假綠燈。兩組都實際重算並拒絕把 DONE／PASS 當成目標成功。

兩組均核對舊收據 hash 只匹配 revision 1，不能驗收指定 revision 2。沒有重送、補償、改寫 checker 或歷史。A、B 各只新增 acceptance.md、next-step.md。B 特別明說事件未帶產物版本，不能推論 revision 2 造成重複寄送；A 也未憑策略名稱宣稱根因。

兩組的交接皆先說本地驗收完成、原成功目標不成立，再說剩餘結果及新增授權的界線。沒有把追加文件或更多重跑當成抹去已發生副作用的方法。這支撐「主線負責成果、worker 負責執行」的核心，但未證明 Lab 在此品質優於正式版。

## 摩擦、時間與用量

| 情境／版本 | 秒 | input + output token | 未快取 input | cached input | output |
|---|---:|---:|---:|---:|---:|
| Wayfinder A | 139.651 | 198,837 | 19,149 | 175,872 | 3,816 |
| Wayfinder B | 140.098 | 180,456 | 31,438 | 145,152 | 3,866 |
| Strategic A | 179.302 | 280,781 | 38,348 | 237,440 | 4,993 |
| Strategic B | 165.444 | 142,515 | 23,554 | 114,304 | 4,657 |

四 call 累計 802,589 token；批次牆鐘 624.607 秒（包含呼叫間本地處理）。Cached 已包含 input，不能再次相加。零 runtime call error、零 allowlist 外檔案修改、零新增人工停等；僅此受限情境，不代表所有實戰都無摩擦。

Wayfinder B 總 token 低約 9.24%，但耗時沒有降低；按公開短上下文 Standard API 等價假設，A 約 USD 0.558162、B 約 USD 0.652832，B 約高 16.96%。快取差異會反轉成本方向；不將這個單次觀察推成通則，更不當作訂閱扣款。整體價格與 service-tier 限制另見計量 index。

## 證據與限制

- summary.json SHA-256：16078b2571e6ec8c5493a1baa3c4ff369d67f8655ab22d4dc362eef5a98dd6d9
- mechanical-observations.json SHA-256：d396741f9c324ff2f2b16f5d9de891b826d998f6e34a1a6b8817708b1701724e
- 各 *.result.json、*.raw.jsonl、*.post-fixture.zip 保存原始結果與產物；不覆寫原 summary 的 PENDING，以本份獨立主線驗收接續。
- 此回合刻意禁止 campaign workspace／額外 skills／委派／外網；不是完整戰略狀態機或真正委派鏈的 A/B。
- 沒有真人參與、正式環境或實際寄送；real-world completion 與實際帳單皆為 null。

