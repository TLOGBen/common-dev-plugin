# Estimate Lab 0.1.2：核准承諾變更未失效
狀態：診斷已確認，尚未修復。Hunt 方法用於逐一反證與跨層核對；沒有改產品 source/tests。
## 根因
根因是 `commit` 只對新候選做當下結構驗證，未比對已核准承諾的前後差異；正式狀態僅要求最後一筆人天決定仍為 `confirm-estimate`。因此責任／選案變了，舊核准仍被視為有效。
以 immutable `experiments/estimate-lab-v0.1.2/plugins/estimate-lab/skills/lab-estimate/scripts/` 為版本定位：
- `case_state.py:1202`：commit 讀 current 只檢 revision，接著 validate(candidate) 並寫入。
- `case_state.py:920`：estimate-approved/complete 只檢 currentDecision=null、latest confirm-estimate effect；没有內容變更失效邏輯。
- `case_state.py:1252`／`1264`：merge/append 共用此 commit。
- `generate_outputs.py:510`：同一 validator 通過後生成；`34`／`499` 直接把 status 投影成人天已核准。
這與主線另查「已核准頁面仍要求 Gate5 確認」不是同一個已證明根因，本案不擴查該呈現。
## 已實跑結果
| 情境 | 真正操作 | 結果 |
|---|---|---|
| 責任範圍反例 | rev9 merge 把正式部署/UAT 從客戶改成我方 | rev10、validate/generate exit0；新責任顯示在 HTML，仍標人天已核准 |
| 選案反例 | rev9 append scenario-b；append 合成新選案紀錄；merge selectedScenarioId=b | rev12、validate/generate exit0；新方案顯示在 HTML，仍標人天已核准 |
| 直接改價反證 | merge workItems，把共用底座 high 與 development.high 各加1 | exit2；原 rev9 byte 不變，錯誤為「merge 不允許更新：workItems」 |
兩個反例的 `answer-confirm-estimate-9` 都逐欄未變，Gate1–5仍done、6current、currentDecision=null。結果 JSON 原文證據：`"approval_records_unchanged": true`、`"html_claims_approved": true`。
選案案例刻意在合成副本注入「新方案已被選定、但新估算尚未核准」的決策資料；不是實際 PM 回答，也不證明無選案紀錄能通過。範圍案例只用正常 merge，沒有新決策。兩案原 CSV 數字未變；本輪不宣稱已重現任意修改費率／數量。
## 實際影響
已接受的責任與方案可在沒有新的人天核准時被換掉，正式報告仍聲稱核准。這可能使讀者把新範圍下的舊人天當成已接受承諾。這是狀態語意的真實反例；不代表真正商務責任已發生。
## 最小防護候選（尚未實作）
1. 在共用 commit、同一 case lock 內比較 current/candidate 的承諾性欄位；責任邊界及 selectedScenarioId 真正變更須失效，不以每次 revision 變更一律重問。
2. 沿用 mapping／estimate-ready、Gate5 current／Gate6 pending、requiresHuman 的 confirm-estimate，明確重開；舊決策保留作歷史，不冒稱本次新核准。
3. 同時守住「重開後直接 merge 回 estimate-approved／complete，借用舊 confirm」的回跳；新的核准只由既有 record-answer 在有效 currentDecision 上接受。避免只降狀態一次卻仍可繞回。
4. 純呈現、outputs／交付紀錄、no-op 不應失效；不是新增 hash 簽核、平行狀態或新必填表單。
修補前先釐清現有 currentDecision 選項能否重用並安全形成明確問題；不能代填 PM 回答。若本次只做責任／選案兩個邊界，其他計價／範圍性欄位應明列未涵蓋，不宣稱全面防護。
## 證據與恢復
- [完整 commands/stdout/stderr/hashes](artifacts/result.json)
- [原始合成 rev9](artifacts/baseline-rev9.json)
- [凍結探針與邊界](SCOPING.md)、[可重跑腳本](probe.py)（固定新路徑，舊路徑存在會拒絕覆寫）
- 新合成目錄：`/tmp/estimate-approval-validity-012-a`；所有輸入、state、HTML/Markdown/CSV、lock 保留。
- 原始 rev9 及 immutable package before/after 一致。未修改真正案件、既有 fixture、source/tests，也未清理任何資料。
- baseline SHA256：`7e5a4bd33bdba95ea8a117677a768c51fd2e3f5a54ba7104cf4ff21ff994a24a`
- result SHA256：`93a5cf36ad3dee10973ad60e4bc019dfbfa9d59df8c165361c74c11668dd269c`
- 實跑：2026-09-06 14:31:54.191–14:31:55.468（臺北），1.276723秒。模型 calls 0；作者實際 token／費用 null。
## 迴歸守護
本輪依只讀範圍沒有新增產品測試。後續修補需把上述兩條持久化／產物反例與 no-op／純呈現／合法重新核准／舊核准回跳控制放進同一有界回歸。沒有 browser/pixel QA，沒有真人理解測試。

