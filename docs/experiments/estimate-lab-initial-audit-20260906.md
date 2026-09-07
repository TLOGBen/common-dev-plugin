# Estimate Lab 初始實作稽核

來源稽核時間：2026-09-06 12:15:32–12:23（Asia/Taipei；筆記寫入及核對另計）。本次把 Estimate 當成待改善的產品，未啟動客戶評估、未替 PM 選方向或核准人天。穩定 source、generated 與現有案件均未修改。以下行號相對於 `plugins/analysis-estimation/skills/estimate/`。

## 結論

先測「精簡入口、按問題載入手冊、人類承諾的接續」是合理的最小切片；保留 schema 8、計算及輸出投影。Validator PASS 不足以判定成果有效：本輪已重現五個語意缺口全部無 errors / warnings，另重現 Gate 5 回答候選被自己的 validator 擋下。程式修補與入口簡化須分輪比較，避免混淆收益。

## 程式支持的熱點

1. **Gate 5 回答接續失敗。** `scripts/case_state.py:1256-1286` 新增回答後清空 currentDecision，只有 select-scenario 分支會調整 gates；`911-919` 卻要求 estimate-ready 保留 confirm-estimate。用既有 fixture，mock 磁碟 load / commit，只執行實際 cmd_answer 的候選建立與 validator，得到「estimate-ready 必須保留 PM 確認人天的目前決定」。`tests/test_case_state.py:426-440` 直接造 complete / decisions / gates，沒有驗這條回答路徑。

2. **不同 ID 不代表施工互斥。** `scripts/case_state.py:400-422` 只要求 catalog 至少被引用一次；`1099-1120` 要求 priced node ID 只由一項 work 承接。複製完全相同的底座 work 與 node，只改 ID、引用原 catalog：validator 無 errors / warnings，高值由 9.5 增至 14.5。不能全面禁止同 catalog 多重引用，因為例外差額與驗證可能合理共用；需要直接比較施工、成果、驗證和增量邊界。

3. **Canonical 明細與 work 的數量仍可分離。** `scripts/case_state.py:335-346` 查 catalog 自身 count，`1056-1067` 查 work 自身守恆及 pricingUnits 上限，`815-839` 查 scopeDelta 與 catalog，沒有核對 work 需處理數與相同工作集合。catalog / scopeDelta 保持 3 項，只將 work total / needsChange / pricingUnits 改為 3 / 2 / 2：validator 無 errors / warnings，高值由 9.5 降至 8.0。批次單位可少於明細數，但不能混淆需處理數與計價單位。

4. **Evidence ID 存在不等於證據可查證。** `scripts/case_state.py:1020-1024` 只查 evidence claim / method；`593-645` 相容性查引用存在。把唯一 evidence 縮成 id / claim / method 仍無 errors / warnings。`455-462` 已明說只驗存在、引用與一致性；supported 標籤不保證來源定位、完整 footprint 或 runtime probe 成立。

5. **停等旗標與因果說明仍依賴實際判讀。** `scripts/case_state.py:1128-1155` 未查 currentDecision.requiresHuman 型別／真值；`726-747` 只查外部文字存在與長度。把 Gate 5 requiresHuman 改 false，或把對外說明改成兩次 `This package does everything required.`，均無 errors / warnings。真正的 reader 應只讀生成後的五欄主表，回答範圍、主要動作、費用驅動、完成結果；原契約已在 `references/deliverables.md:38-52`。

6. **同 revision 投影有邊界。** `scripts/generate_outputs.py:503-532` 讀一次 state，逐檔 atomic replace，最後寫 manifest；單次生成源自同一記憶體 snapshot。但 generator 不限定 complete，也不鎖整組輸出，需區分 Gate 5 預覽與已核准交付，並避免多個 writer 同寫一個 output dir。跨程序混合檔案只屬靜態風險，本輪未重現。

7. **文件與 CLI 不一致。** `references/case-state.md:38` 教 `--choice` 且漏 `--decided-by`；實際 parser 在 `scripts/case_state.py:1313-1319` 接受 `--answer` 並必填 `--decided-by`。Lab 需要用真正 CLI 流程驗接續，不能只驗手工 JSON。

Probe 全部使用 `tests/helpers.py:15-276` 的合成 fixture，在記憶體 deepcopy 後呼叫原 validator；透過 `PYTHONDONTWRITEBYTECODE=1 python3 -c ...` 避免 bytecode 寫入。9.5 / 14.5 / 8.0 沒有客戶估算意義。完整 unittest、真實 CLI 寫入與 concurrency 尚未執行。

## 修改入口前先凍結的四例

原版與 Lab 使用相同合成輸入，不在看完结果後補標準答案；下列費率由 fixture 提供，不要求模型猜價。

| 案例 | 固定輸入 | 成功結果與否證條件 |
|---|---|---|
| E1 僅指定 runtime、維護路線未承諾 | 使用者只指定 Java 17。舊框架可在該 runtime 啟動，但某私有產碼元件在候選資料層無可驗證的維護來源。 | 已給目標記錄一次，繼續查技術事實；會改變責任的保留／替換／fork 路線用白話交 PM，維持未選。擅加 Boot／Jakarta／部署、偽造 PM 答案、忽略反證或重問已回答目標即失敗。 |
| E2 工作集合、批次及例外 | 87 個 direct-touch API：84 同規則、3 特例；136 generated 產物；13 evidence-only 整合落點。明定高值費率：底座一次開發 4／測試 1；批次一次 2／1；3 例外各 0.5／0.5；整合保障一次 0／2，總計 13。 | 明細 87 完整、generated 保存重產契約、13 僅作覆蓋證據，例外只收增量、底座一次、外部責任 0。排序或多一個 catalog 引用不改總數 13。把產物數當人工乘數、同施工改 ID 重收、87 寫成 86 或例外重收一般工作即失敗。 |
| E3 回答與 revision 接續 | estimate-ready revision R；未回答時只有預覽；fixture 隨後提供明確 PM 回答，再用相同 R 重試及過期 R 操作。 | 一次合法接受回答，status / currentDecision / gates / decisions 同步，接續已授權工作；重試不重複生效，過期 R 保留 last-good；所有輸出源自接受後同 revision。卡在 confirm-estimate、自填答案、沿用舊 revision、以 CSV 存在宣稱完成或繞過出錯 CLI 都失敗。 |
| E4 只看五欄表的客戶說明 | 同金額提供因果完整文案與長度合格但空泛／錯寫範圍文案。reader 只拿實際生成 CSV，不能拿方法卡或預期答案。 | 逐列說出範圍、至少兩個動作、白話費用驅動及完成結果；指出僅三支受影響卻写「全部入口」的矛盾。修文案後數字不變。只重複標題判 PASS、從內部資料補出外表沒有的資訊或改人天来說服即失敗。 |

越權承諾、重複／漏計、revision 漂移及錯誤完成宣稱屬硬失敗，不能由平均分或低 token 抵銷。分開觀察有效 PM 決策數、重問數、合法接續率、reader 四問覆蓋、工具錯誤及可觀察 token；未暴露 token / 費用記 null。

## 最小自含資源閉包

建議候選先放未註冊的 `experiments/estimate-lab/package/`，最終命名由主線決定。17 個沿用資源 + 新 manifest / 精簡 SKILL 共 19 檔；另加合成 probe 與 fixture 作實驗證據，保留原 schema 8。

```text
.claude-plugin/plugin.json                     新建，獨立名稱、defaultEnabled=false
skills/lab-estimate/SKILL.md                    新建，精簡 router / human-handoff
skills/lab-estimate/requirements.lock           沿用 stdlib-only
skills/lab-estimate/scripts/case_state.py
skills/lab-estimate/scripts/generate_outputs.py
skills/lab-estimate/assets/assessment-report-template.html
skills/lab-estimate/tests/helpers.py
skills/lab-estimate/tests/test_case_state.py
skills/lab-estimate/tests/test_outputs.py
skills/lab-estimate/references/case-state.md
skills/lab-estimate/references/discovery-guide.md
skills/lab-estimate/references/dependency-behavior.md
skills/lab-estimate/references/evidence-and-success-chain.md
skills/lab-estimate/references/scenario-guide.md
skills/lab-estimate/references/estimation-guide.md
skills/lab-estimate/references/pm-decision-pauses.md
skills/lab-estimate/references/pm-report-design.md
skills/lab-estimate/references/deliverables.md
skills/lab-estimate/references/inventory-sidekick-brief.md
```

沿用來源全部位於 `plugins/analysis-estimation/skills/estimate/`。inventory-sidekick-brief 是 discovery-guide 的連結閉包，保留不代表每案都要派工。Runtime 硬依賴只有兩支腳本及一個 asset（`generate_outputs.py:19,498-500`）；其餘資源是行為和驗收閉包。新入口按問題載入，不一次要求讀完。

第一輪不需 feedback.py / test_feedback.py / feedback-learning.md、ASCII 範例、其他 RFP skills、Office runtime、客戶案件或共用 agents。feedback.py:159-181 有 tracker 發布能力，與本次合成驗證無關。Lab 不建立遠端 Issue，不以安裝 Wayfinder 當開始條件；本地摘要保留 destination／未決問題／決策語意，明記未執行正式 Wayfinder；相關手冊語意由 Lab overlay 說明，不能暗改穩定來源。

先只換 router 取得 A/B 基線，再分別驗 Gate 5 adapter 和數量交叉核對，逐一記錄實驗變因。不能把程式修補收益歸因於 prompt 精簡，也不能因保留原腳本就宣稱已解決上述缺口。

## 後續驗證命令與限制

下列須在隔離 package 建立後執行，本輪未建立 package 或宣稱 suite PASS：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s experiments/estimate-lab/package/skills/lab-estimate/tests -v
PYTHONDONTWRITEBYTECODE=1 python3 experiments/estimate-lab/package/skills/lab-estimate/scripts/case_state.py --help
PYTHONDONTWRITEBYTECODE=1 python3 experiments/estimate-lab/package/skills/lab-estimate/scripts/case_state.py record-answer --help
PYTHONDONTWRITEBYTECODE=1 python3 experiments/estimate-lab/package/skills/lab-estimate/scripts/generate_outputs.py --help
```

Test harness 在已確認的隔離 root 建立 fixture，串起 `validate → record-answer → validate → generate_outputs --json`，核對 state revision、外部兩欄人天與內部高值，並讀真正 CSV / HTML。需要加入本輪反例、Gate 5 CLI 接續及 writer 衝突測試；reader 語意不能改成關鍵字命中檢查。改寫既有輸出或清理 fixture 前仍遵守 target preflight。移植 Codex 依倉庫 transfer 流程先產到隔離目錄，核對 dropped / manual-review 與資源閉包。

本輪只新增這份筆記，未建立／註冊 marketplace、未 bump 正式版、未改生成版。曾有兩次 Windows helper setup refresh error，使用同權限 `pwsh → wsl.exe ... zsh -lic` 成功；沒有改權限、帳號或 runtime。模型 token usage / cost 為 `null`，Host 未提供本子任務可信累計值，不用工具輸出字數換算。第一次跨 shell 寫筆記時 Markdown backticks 被解讀，造成 command-not-found 並移除 inline code；已核對影響僅此 task-owned note，使用 native apply-patch 的結構化 argv 修復，未將 shell 轉義錯誤當成來源驗證結果。

記憶僅用來辨識應保留的共享底座一次、同 revision 投影與對外五欄設計；歷史客戶人天未用作 fixture 費率或答案。當前發現均由上述來源與實際記憶體 probe 支持。
