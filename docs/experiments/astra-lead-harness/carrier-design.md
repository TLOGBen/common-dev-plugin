# Astra 主手 request/resume 載具

這是傳輸適配，不是額外 skill harness、原生 subagent API 或驗收裁判。程式為 [astra_lead_episode.py](../../../scripts/astra_lead_episode.py)，離線測試為 [test_astra_lead_episode.py](../../../scripts/test_astra_lead_episode.py)。

## 這個載具做什麼

Astra 主手先自行讀取、測試、判斷，必要時以控制 JSON 提出自己的 role brief。Controller 用正常 CLI 執行 fresh Luna/high，再以實際取得的同一 session UUID resume Astra。主手可以驗收、再派工、先繼續觀察、完成交接或指出真正缺少的人類決定；載具沒有強迫第一步計畫、派工、全套 Strategic 或固定四步法。

所有臂使用同一載具、模型、權限語義與額度。主手固定 `gpt-6-astra/high`，所有下屬角色固定 `gpt-5.6-luna/high`，不自動換模型／升權限／重試。角色批次目前依序執行，不測平行吞吐。每個 worker fresh 且 `--ephemeral`；主手使用實際 UUID，從不使用 `--last`。

普通 CLI help 已在本機 **0.153.0** 確認 `exec --json`、`--output-schema`、`--ephemeral`、`--ignore-user-config`、sandbox 及 `exec resume <session_id>` 可用；`multi_agent=true` 只證明 feature 開啟，未證明子代理模型／token 可獨立計量。JSONL、結構化結果及明確 session resume 亦見 [官方非互動模式文件](https://learn.chatgpt.com/docs/non-interactive-mode)。此輪只讀 help 與離線 fake traces，沒有呼叫模型；正常登入的 model 可用性仍待首跑確認。

## 呼叫者提供的凍結輸入

`schema_version=1` 的 spec 是傳輸資料，不定義作業策略：

- `episode_id / case_id / arm / user_prompt`：識別及原始任務；`arm_context` 只載該臂目錄／規則，不塞入所有 skill 根檔。
- `workspace`：新的有界 fixture 絕對路徑；`workspace_sha256` 是所有起始檔案的相對路徑 → SHA256。
- `package_roots / package_sha256`：完整 **Codex 生成包**及逐檔 hash，位於 writable fixture 之外。必须含 `.codex-plugin/plugin.json`，不能拿 Claude source 充當正式包。主手依自然觸發讀完整選用入口與必要 refs；未啟用 Strategic 不算該機制已受測。
- `read_files`：額外唯讀 catalog／metadata 的絕對路徑 → SHA256，不授予 controller root、其他 case 或評分材料。
- `role_writes`：至少有 lead 和 implementation；角色名稱與最大相對寫入範圍由凍結者給定。尾端 `/` 表示整個子樹，否則是精確檔案。主手可寫 memo/state，不能代寫 fixture 的 product/tests；其他角色是否要用由主手決定。
- `sandbox`：父層最大權限，僅允許 read-only 或 workspace-write。**實際 request 沒有 write_paths 即使用 `-s read-only`**，有授權寫入才 workspace-write；父層 read-only 不容許任何非空 role 寫入範圍。
- `max_calls / max_wall_seconds / call_timeout_seconds`：所有角色共同消耗的界限；程式不規定本輪實驗應採多少 calls。預算耗盡記 budget_censored，不當作完成或模型失敗。
- `session_store`：選填、呼叫者明確提供的既有普通 CLI session 目錄。只依本 episode 實際 UUID 讀取唯一對應檔案，取 token_count；不讀其他 session 內容，不搜尋／複製帳號憑證。

無 spec 介面改名；既有 `sandbox: workspace-write` 相容。差異是 sandbox 現按角色／request 縮至實際需要，而非全員寫入。主手會取得可派角色與其最大路徑、共同額度，這是能力揭露，不是派工建議。

## 控制格式與交接證據

主手每次 final message 的 JSON 只有三欄：

```json
{
  "action": "dispatch",
  "requests": [
    {
      "role": "implementation",
      "brief": "主手自行撰寫的有界 brief，含必要授權與驗收脈絡",
      "write_paths": ["product.py", "tests/"]
    }
  ],
  "message": "主手自己的說明"
}
```

`dispatch` 必須有 requests，角色與路徑不得超出凍結範圍。`continue / final / human` 的 requests 為空。工具可在回傳此 JSON 之前正常使用；worker 不需控制 JSON。Controller 不將 worker 自述當作完成、不替主手補 brief，也不自動復活遭拒／未知結果的工作。

每個已完成 subordinate call 的 `prompt.txt`、`stdout.jsonl`、`stderr.txt`、`result.json`，都會以**精確絕對路徑及 SHA256**附給後續主手與角色，明列唯讀授權。這包含作者 brief 和原始 evidence，不只有摘要；同一批次較晚執行的角色也會取得較早交回的檔案。授權只累積本 episode 已交付的四種檔案，不擴至其他 controller 檔案／case／oracle。後續呼叫若改動已交付證據，其 hash drift 會被記錄並停止。

每次呼叫保留實際命令、prompt、原始 stdout/stderr、exit、起迄、牆鐘、模型／effort 請求值、workspace 前後 hashes、scope 違反及 fixture-after.zip。輸出目錄必須不存在；不合併、覆蓋、清理舊 run。有效回應中的模型名稱未被 CLI 證實時 `effective_model=null`，不把請求值冒充 backend 證明。

## 用量不是重新播放總額相加

原始每一筆 `turn.completed.usage` 由既有 `lab_reader_probe.turn_completed_usage_rows` 完整保留，包含存在時的 cache_write_input_tokens／reasoning_output_tokens；欄位缺失即未知，不補 0。

- fresh invocation 只有一筆完整 usage 時可採 CLI 本次 usage。
- resume 優先用**同一 session 的 token_count total 前後差**；沒有可驗證差值則本次採用用量為 null，原始 CLI 候選值仍保留。
- `native_session_usage_delta` 與 `raw_turn_completed_usage` 分開，`turn_usage_matches_session_delta` 對照基本三欄；不預設本機兩來源必一致。
- input 已含 cached input；reasoning 是 output 子集。total 只算 input + output，不把快取／reasoning／cumulative total 再加一次。
- 各角色分列 known subtotal 與 unknown call 數；unknown 不當成 0，也不能把部分已知小計標成完整成本。actual cost 為 null，沒有帳單就不猜。

官方目前文件／程式對 per-turn 的說明不能代替本機 resume 的實证；主線首輪須核對原始兩種 telemetry 後才採取整批加總解釋。

## 執行與停止界線

先以**不帶 `--run`**的命令驗證凍結 hashes、新目的不存在及生成包閉包入口。預設只輸出 PREFLIGHT_ONLY_NO_MODEL_CALLS，不创建 run、不呼叫模型：

```sh
python3 scripts/astra_lead_episode.py --spec /exact/frozen-spec.json --out /exact/new-run
```

只有主線凍結完成、檢查 preflight 後，才另次執行同命令加 `--run`。使用正常 WSL login CLI、`--ignore-user-config`，不改 auth／global config，不加 `--ignore-rules`，不要求放寬平台 sandbox。首輪如 model/profile／resume／權限失敗，保留真實結果；不默默換 carrier 或模型。

逾時終止本次 controller 啟動的 process group，保留 timeout_unknown，不假設副作用沒發生。協定錯誤、session UUID 不符、來源 drift、scope 違反均停止且保留工件；不自動 retry。lead_finished 只表示主手宣告交接；semantic_acceptance 與 actual_business_completion 仍為 null，須主線用獨立凍結 oracle 及真實軌跡判讀。

## 離線驗證與限制

2026-09-06 15:44:47（Asia/Taipei）觀察到 18 個 unittest 通過，測試執行 0.073 秒；假 process traces 與所有測試工件保留在 `/tmp/astra-lead-carrier-offline-mv4_gccq`。包含三階段收件驗收、後續唯讀角色接案、同 batch 動態讀授權、零寫入 sandbox、原始可選 token 欄位、resume 累計差值／未知、預算截斷、越權寫入保留、symlink、逾時、無重試及預設不呼叫模型。

這些不是 Astra/Luna 生成結果、真人測試或產品 MOE。檔案 allowlist 是明確指令加逐次 hash 檢查，**不是細粒度 OS 唯讀隔離**；workspace-write 角色在 OS 層能改同 fixture 其他檔案，事後會抓出持續差異但未必抓到寫後還原，需原始工具軌跡輔助。唯讀角色確實使用 CLI read-only；讀取範圍仍是提示約束，不可據此宣稱 oracle 的 OS 級不可讀隔離。外部 mutable 系統不在範圍。

四臂組合初篩的因果限制、MOE/MOP 及後續單變因測試，以 [REQUEST-AND-MOE](REQUEST-AND-MOE.md) 和 [runtime-addendum](runtime-addendum.md) 為準；本載具不另造評分框架。

