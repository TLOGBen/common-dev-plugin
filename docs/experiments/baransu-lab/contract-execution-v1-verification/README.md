# normalizeTag 獨立實際驗證與待審核 verifier payload

本目錄保留已執行的獨立檢查，以及尚未呼叫的兩個 fresh Sol/high verifier 輸入。合成資料搭配真實本機 Node 執行；不是真人驗收或完整原版 seal。

## 已執行

- `receipt.json` 記錄 Node v22.18.0、命令、wall time、原始 stdout/stderr 的 SHA-256、八個原工件的前後雜湊。
- A：獨立 oracle 8/8，`node --test` 4/4；B：獨立 oracle 8/8，`node --test` 5/5。四個命令均 exit 0。
- 原工件前後雜湊一致，且與 actor 完成時的雜湊一致。沒有修改 fixture、測試或既有結果檔。
- 上述結果來自非作者的主線子程序讀取與工具執行；兩個角色 verifier 尚未執行。

原始 actor runner 與此環境的摘要不可混用：A raw JSONL 第 54 行 item_29 與 B 第 26 行 item_14 都呈現一個測試檔的 tests=1/pass=1。A handoff 明確保留此範圍；B 把檔內五個案例寫成當時的 runner 計數。這是報告證據範圍的差異，不據此否定 B 的行為或把 test count 當成品質。此次獨立重跑能辨識 A 四例及 B 五例；差異的環境機制尚未診斷。

`actor-output-provenance.json` 固定 raw JSONL 的路徑、行號、item ID 與 SHA-256；各 `dispatch/<arm>/actor-last-suite.stdout.txt` 是最後一次成功 suite 工具輸出的原始文字，沒有重新編造摘要。

## 尚未執行的兩個角色呼叫

主線審核 `A-verifier.prompt.md`、`B-verifier.prompt.md`、`dispatch-plan.json` 後才呼叫。計畫只指定 `gpt-5.6-sol`／high；runtime 不可用時回報，不換模型。本次準備新增模型呼叫為 0。

A 是 installed Baransu 5.4.1 的完整 seal-agent 加必要 shared contract；B 是現有 Lab lab-verifier。原始角色檔逐位元組複製至 `frozen/`，manifest 記錄來源與 hash；這是 verifier 準備時凍結，不能冒稱 actor 開始時已凍結這些角色。

兩邊的 `dispatch/<arm>/target/` 都是全新的拋棄式副本，四個檔案與原工件 hash 相同。`baseline/` 從實作前 frozen-design.zip 取出指定三檔，`change.diff` 記錄實際 artifact 差異，沒有建立或假造 Git ref。兩份 disposable copy 的 dispatcher suite baseline 均已實跑並另存 stdout、stderr、hash、wall receipt。

A payload 恰為原版要求的五欄，採 named-artifact branch 2，完整 acceptance 作為 criteria；原版 probe admission、零 admitted probe 的 finding、五點結果、scratch custody 和精確還原要求均保留。B 依自己的 role 選證據，未加入固定五點或強制 mutation。

任何 probe 都只能改自己的 disposable source；必須先保存原位元組、分開執行唯讀 TARGET_MATCH preflight 與 mutation，恢復後 byte-compare。原 fixture、測試、acceptance、role、歷史結果均不可修改；不得 cleanup scratch。角色只回傳結果，lead 負責保存 CLI stdout 與後續判讀。

## 未執行與比較限制

- Stable marker、selection/seal-log telemetry、Stop hook、發布、dispatcher 修復與複驗均未執行。
- 原版 Git fingerprint 在非 Git fixture 中由完整 artifact bytes、前後 hash 與 materialized diff 取代；這是明列的局部適配，不宣稱驗證了原版 Git／hook 整合。
- 若 A 的原生規則要求額外工作或無 admitted probe，依原規則報告，不為符合四個主要模型呼叫的整體預算而刪掉要求。
- 完成這兩個 verifier 仍只能比较局部合約承接、實際行為與角色驗證的證據；不能宣稱完整 seal 或實驗已證明 Lab 普遍較好。

`capture-verification.py` 與 `prepare-dispatch.py` 是本輪固定路徑的一次性收據／複本準備程式，沒有模型呼叫。兩者拒絕覆寫既有證據；不要對現有目錄重跑。

