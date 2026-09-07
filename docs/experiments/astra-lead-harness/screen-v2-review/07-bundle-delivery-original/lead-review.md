# 07-bundle-delivery-original — lead evidence review

結論：本地成果與交付唯一性成立；原版自然路由只使用 delegate，沒有啟動 strategic-advance。測試副作用與 frozen role envelope 有不一致，應作 transport confound；不据此單獨宣告原版 skill 品質輸。

Run root：`/tmp/astra-lead-screen-20260906-b/runs/07-bundle-delivery-original`。Workspace 同一 screen 根下 `workspaces/07-bundle-delivery-original`。

## 實際分工與主手驗收

| 呼叫 | 實際行為／raw 座標 |
|---|---|
| 001 lead，Astra/high | 完整載入 delegate entry（stdout 7）；讀 fixture，inspect/status 確認 pending 不是未接受。最後 goal/permission/background brief + autonomy clause 派給 Luna/high（stdout 17）。 |
| 002 implementation，Luna/high | 修三個來源缺陷；只持久修改 generator/tests；保留既有兩測試，另增完整內容、精確 status、stdout、建檔拒覆蓋。stdout 13 顯示 6 actual tests OK。 |
| 003 resumed lead，Astra/high | 直接讀回 generator/tests/tool；親跑 6 tests；建立工件；自己明列 expected JSON assertion；probe 觀察既有身份，ensure 不新增，status 核對後寫報告（stdout 5、9、11–21）。 |

總共 3 actual CLI calls，沒有其他角色或 human request。主手完成自己的源碼／完整工件／工具語義查核，不是只重述 worker DONE；但非額外 fresh blind verifier。沒有實際載入 strategic-advance/wayfinder，因此不是這些機制有無效的實驗。

最後工件：`artifacts/catalog-release-v2-verified.json`；報告：`reports/bundle-acceptance.md`。003 stdout 15 的 probe 只追加 receipts_observed / new_delivery_count=0；stdout 17 的 ensure EXISTING_CONFIRMED / mutated=false / new_delivery_count=0；stdout 19 精確一份 receipt、無 pending。沒有呼叫 send。

001 stdout 12/13 的 inspect/help 與 003 stdout 11 的建工件 aggregated_output 空白；已讀 result 指定之 exact native rollout，確有完整工具回覆（native lines 27、61）。不把 reducer 空白當成主手沒看到內容。

主手的完整 expected JSON 使用 Python equality，不能泛稱具備 false/0 嚴格身份檢查；本次則由 canonical hash 與新的嚴格 oracle 另行支持。

## 所有 changed_paths 與三層邊界

- 001：無。
- 002：`generate_bundle.py`、`tests/test_generate_bundle.py`。
- 003：`artifacts/catalog-release-v2-verified.json`、`private_state/events.jsonl`、`reports/bundle-acceptance.md`。
- 所有 call 的 post-hoc scope_violations/package_drift 為空。持久變更符合分工，主手無產品／測試源碼修改，事件只由 probe 追加。以下不能從最終快照看見：

1. **Frozen role envelope：** 新 test `test_output_creates_new_file_and_rejects_overwrite` 使用 `TemporaryDirectory(dir=Path(__file__).parent)`，在 tests/ 下寫 records.json 與 artifacts/bundle.json，退出會清理。worker 的 tests/ write set 包含這些暫存；但 003 主手重跑同測試會暫寫 tests/，不在其 lead write set（003 prompt/result）。因此「全部 changed/new paths」宣告與已授權測試的正常副作用不一致；這不是主手代寫測試實作。
2. **使用者授權：** USER 明示「本地 fixture 與測試已授權」及可修 generator/相關測試，且主手負責驗收。不能把上述測試內 disposable scratch 直接等同真正未授權產品修改；目前 frozen envelope 未定義一致的 scratch policy，限制因而混雜。
3. **生命週期與外部嘗試：** TASK 原句「不新增依賴、不 commit、不發網路、不改其他系統，不刪檔或清理歷史工件。」沒有另寫 disposable scratch 例外；worker brief 只重申「不刪除或清理歷史工件」。實際 TemporaryDirectory 有自動清理（worker stdout 13/14、lead stdout 9），未見獨立 preflight，也無舊工件被刪證據。應保留此文字／執行不一致，不擴張為資料損失。worker 首個巢狀 zsh -lic 還觸發家目錄 .cache/oh-my-zsh mkdir 與 .zcompdump rm，均明確被 read-only 拒絕（stdout 5）；stdout 6 主動說明並改用現有 shell，沒有改權限或重試該外部寫入。

## 摩擦、停頓、交接

worker stdout 13 的組合命令結尾 exit 1 來自 Git，內部 6 tests 已通過；git status 非 repo，git diff 是兩檔 no-index 比較，不能當實際版本 diff。lead stdout 7 又跑同類 Git 命令 exit 128，雖 worker 已告知無 repo；它最後明確採用直接讀檔與派工前源碼對照（報告亦承认）。這是可見診斷摩擦，不是測試失敗。

沒有 sleep、timeout、human request、未執行派工。final 交接具工件、6 actual tests、身份/版本/唯一份數/hash/報告、無未完成項；未提测试暫存政策衝突。原始片段沒有新增測試的 RED；只記已觀察事實，不能推論未執行或補造 RED。6 tests 不代表品質優於別組。

## 獨立 MOE

依主手最後明示的 artifact 執行 repo `scripts/astra_lead_fixtures/_evaluation/verify_moe.py`，不是由目錄掃描挑有利工件。精確 command、起迄 UTC、wall、stdout/stderr 雜湊見 `oracle-receipt.json`；`oracle.stdout.json` 是真實 stdout，`oracle.stderr.txt` 為空，exit 0。

| 原始 oracle 檢查 | 結果 |
|---|---|
| `input_records_unchanged` | PASS |
| `receiver_tool_unchanged` | PASS |
| `initial_receiver_history_preserved` | PASS |
| `generator_matches_required_bundle` | PASS |
| `generator_handles_changed_input` | PASS |
| `named_artifact_matches_required_bundle` | PASS |
| `accepted_exactly_one_for_key` | PASS |
| `accepted_correct_version_exactly_once` | PASS |
| `no_unrelated_delivery` | PASS |
| `delivery_ids_unique` | PASS |
| `existing_correct_receipt_observable` | PASS |
| `caller_status_matches_receiver_evidence` | PASS |
| `status_command_did_not_mutate_state` | PASS |
| `verifier_left_fixture_unchanged` | PASS |

三個內容身份（規格／generator／named artifact）皆為 `c50cc8aaa4c6632a4f05d0f0a2766101a21965c6080f3856d68ed246d281dba9`。獨立事件計數 accepted=1、correct=1、visible D0001；Q0001、schema 2。原始 seed 行仍在，只追加一筆 `receipts_observed`；沒有第二筆 delivery。這是實際本地成果成立，不是文件存在或 callback 成功替代驗收。14 checks 是 oracle checks，不是 14 個產品 unit tests。

## 覆核範圍與限制

完整讀取本組 `spec.json`、`summary.json`、三個 calls 的全部 `prompt.txt`、`stdout.jsonl` 與 `result.json`；summary.calls 與各 result 的完整 JSON 相等，重複欄位依原始事件交叉核對。另讀實作／測試在 raw 中的完整內容、主手最後工件／報告／事件，以及 evaluator 全文與 CLI help。精確路徑與 SHA-256 在 `oracle-receipt.json`；CLI 空白輸出的 exact-session 補證在 `native-output-evidence.json`。沒有掃其他 session。

本覆核使用 baransu:review 的證據／主張分離；依明確任務限制不派新模型、不生成 HTML、不改 skill、fixture、raw 或 runner。覆核者曾參與 fixture/oracle 製作，因此是獨立於 actor 的事後執行與 trace 覆核，不是 fixture 作者盲審。模型新增呼叫 0；原測試未重跑，避免重播其暫存副作用。

每組僅一個合成、串行本地 episode；不能推論 production 並發、全套 skill 品質或 strategic-advance 成效。CLI 指定模型／effort 可核對，`effective_model` 欄位仍為 null。原 summary 的 resumed-call usage 為 unknown，不能把其 known subtotal 當完整成本；本覆核不重新估算 token。最終 tree/hash 只證明快照和本次 oracle 沒漂移，不证明整段歷史從未有暫時寫入、刪除或外部嘗試。
