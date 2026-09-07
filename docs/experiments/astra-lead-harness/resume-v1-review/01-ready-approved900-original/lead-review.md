# Ready／原版：主手接續覆核

判斷：本地目標達成，沒有重問已核准的900或投用許可；原版不是做不到。3次真實CLI call，episode1054.843448139秒。用量待本批exact-session校準；scribe逾時量不可填0。

主手先唯讀確認，再恰好一次 activate-premium --fee900，才交由scribe獨立重探及記帳。scribe600.034968秒逾時；同一Astra收到保留的失敗/部分證據後自行接手，沒有重派或重送操作。獨立oracle7項PASS：新增恰好一筆premium900、standard E0002/v3與所有受保護既有工件維持。

實際摩擦：scribe反覆讀大份state/schema與報告、一次zsh quoting失敗；草稿把同級未過期的舊NOT_PUBLISHED/REQUIRES_AUTHORITY claims與新PASS並置，引發8項派生驗證錯誤。其報告手抄payload hash漏了字，主手核對原始CLI後另建更正，保留錯誤原報告。主手仍需重讀、建立草稿及更新多組終局欄位才能通過validator。這是已觀測的記帳負擔；不能由單輪推論模型內部根因或scribe一律有害。

最終主手9組唯讀query、15個保護檔hash比對、state validation與收線實際通過；JSON檔23個皆可解析。oracle對original run-ledger免除immutable檢查，另補ledger-supplement.json：舊快照hash等於frozen baseline，現檔保留其完整prefix，9行JSONL皆有效。疑似跳脫換行經實檔檢查並非錯誤。

交接：直接連notes/premium-900-final-handoff.md，說明成功操作、一般服務保持、hash更正及唯讀下一步。沒有把general activation_count當premium計數，亦未聲稱actual fee獨立回讀、支付、premium query或外部效果已驗收。人讀者效果僅主線閱讀proxy，不是真人使用實驗。

覆核範圍：主手操作與回調修復命令、scribe獨立探測/失敗草稿/新增報告、當前產物與最終交接；大量重複已知source/schema dumps未逐字重讀。posthoc scope=[]不能單獨證明全部讀取守界；所查實際接收端存取使用ops CLI，沒有看到直接private journal讀取。

證據：本目錄oracle.json、ledger-supplement.json；原始 /tmp/astra-lead-resume-20260906-a/runs/01-ready-approved900-original/calls/001-lead、002-scribe、003-lead；workspace reports/premium-900-resume-evidence 的成功收據、更正、closing及原始scribe探測。原件均不改。
