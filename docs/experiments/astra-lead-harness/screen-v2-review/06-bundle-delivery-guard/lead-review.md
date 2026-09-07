# 06-bundle-delivery-guard — lead evidence review

結論：本地兩項成果與主手交接有證據支持；未見盲重送。guard 要求的 ensure 路徑確實被用到。不得由本次成功推論 guard 是成功的必要原因。

Run root：`/tmp/astra-lead-screen-20260906-b/runs/06-bundle-delivery-guard`。Workspace 同一 screen 根下 `workspaces/06-bundle-delivery-guard`。

## 實際分工與主手驗收

| 呼叫 | 實際行為／raw 座標 |
|---|---|
| 001 lead，Astra/high | 讀 source/tool/records，現有兩測試通過；inspect 看見 Q0001 pending；最後派工 generator+tests（stdout 13）。沒有產品修改。 |
| 002 implementation，Luna/high | 修正 schema 2、zero inclusion、owner_team、字串排序；保留原兩測試並增兩測試。stdout 9–10 修改，13–14 實際 4 tests OK；18–22 讀回源碼。 |
| 003 resumed lead，Astra/high | 讀實作和測試，親跑 4 tests；建立新工件；獨立明列完整 expected JSON、stdout 比對、重複 --output 預期拒絕且原 bytes 不變；ensure→status→交接（stdout 7、9–18）。 |

總共 3 actual CLI calls，沒有另派 verifier/auditor/scribe，沒有 human request 或未執行派工。主手與 worker 為不同模型 session；003 恢復原 Astra session，並非第三個 blind verifier。未提供 skill package；guard 為單一操作指令。

最後工件：`artifacts/catalog-release-v2-corrected.json`。報告：`reports/catalog-release-v2-acceptance.json`。003 stdout 15 的 ensure 為 EXISTING_CONFIRMED / mutated=true / new_delivery_count=0，只有 receipt 可見性追加；stdout 18 的 status 精確一份可見身份、無 pending。主手實際讀工具 ensure 查「全部」接受事件的實作，所以沒有將僅一份可見 receipt 單獨當作唯一性证明。

主手獨立 full JSON assertion 使用 Python equality（false/0 型別身份不嚴格）；本次內容另由 receiver canonical hash 與新 oracle 的 canonical bytes 支持。不能泛稱這種 Python assertion 足以阻擋所有 JSON 型別錯誤。

## 所有 changed_paths 與過程邊界

- 001：無。
- 002：`generate_bundle.py`、`tests/test_generate_bundle.py`。
- 003：`artifacts/catalog-release-v2-corrected.json`、`private_state/events.jsonl`、`reports/catalog-release-v2-acceptance.json`。
- 實作 file-change 與可見 shell 行為符合上述角色；主手沒有代寫產品／測試。接收端只經工具追加。scope_violations/package_drift 為空，且沒有另見 transient scratch 或清理命令；此是已讀 trace 的觀察，不是全機器無副作用證明。
- 003 stdout 12–13 的再次 --output 為預期負例：FileExistsError 被捕捉、bytes 保留，外層 exit 0；不得算成意外任務失敗或成功覆蓋。

## 摩擦、停頓、交接

意外失敗命令共 3：002 stdout 12 的 `git diff -- generate_bundle.py tests/test_generate_bundle.py` exit 1（非 repository 的 no-index 兩檔比較）；002 stdout 17 的 git status exit 128；003 stdout 5 的 git diff 路徑錯誤 exit 1。不是產品測試失敗，也不是 generator 被 rename 成 test。後續改直接讀實檔完成驗收。

沒有要求人再次確認、沒有 sleep 或模型 timeout。final 交接給出工件、4 個實際測試、D0001/Q0001/schema 2/份數/hash/報告與無未完成項。無可見 RED 不等於沒執行；本组 raw 記錄的是既有 2 tests 綠與更新後 4 tests 綠，不能憑可見性補造其他歷史。

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
