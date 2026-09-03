# 案件主檔契約

當要建立、接續、更新或解釋 `assessment-state.json` 時讀取。

## 目的

案件主檔保存目前能被證據支持的唯一案件真相。聊天、Wayfinder 地圖、報告與 CSV 從同一 revision 或穩定關聯投影，使接續、比較與重建不依賴某次對話記憶。

## 核心區域

- `outcome`：客戶成果、驗收、保留行為與責任邊界。`pmCurrentState` 保存可直接轉述的現況結論，技術證據另存 `evidence`。
- `evidence`：命題、來源定位、取得方式、強度、信心與決策影響。
- `dependencyCoverage`：實際依賴全集的來源、發現方法、元件數、盤點邊界、證據與會改變方案的 dependency ID。
- `dependencies`：會影響方案的元件；保存上游來源／維護者、內部責任、生命週期、完整 footprint、目標相容性主張、採用策略、語意斷點與 probe。
- `fogs`：仍可能改變決定的未知、影響、下一個高價值查證與狀態。`requiresHuman` 表示由 PM 承諾，`blocksReadiness` 表示正式估算是否仍被阻擋。
- `scenarios`：候選結果、成功條件、成本／風險特性、前置與未知。
- `selectedScenarioId`：PM 明確選定的方案；必須能回到帶有相同 scenario ID 的決策紀錄。
- `successChain.nodes`：所選成果成立的能力、外部責任、相依與完成證據。
- `workItems`：由成功鏈推導的互斥工作、影響數量、明確 `pricingUnits`、費率與追溯。`effortSplit.development/testing` 以每個計價單位保存低／基準／高，兩者逐層相加必須等於 `unitDays`。`pmChangeSummary` 保存 80～160 字修改重點；`changeTargets.pages/apis/files` 保存摘要落點；`detailCatalogIds` 綁定 Discovery 建立的 canonical 工作集合；`baselineRationale` 解釋基準單價與乘數。
- `detailCatalogs`：全案唯一的 canonical 工作集合。`direct-touch` 必須以 stable item ID 完整列出 `claimedCount` 項名稱／路徑、用途、處置、修改與驗證；`generated` 保存產製來源、方法、核對及輸出數，不把輸出數當人工修改次數；`evidence-only` 說明覆蓋證據及其計價角色。`origin` 標示 `discovery` 或既有案件一次性的 `legacy-migration`。
- `clientPackages`：PM 對外說明的客戶成果包；每個 work item 唯一歸入一包，包人天由工程工作加總。`name` 是對外「系統功能」，`externalSummary` 是單段、可由 PM 轉述的「功能說明」，需保留改造範圍、主要動作與完成結果；完整算法與技術證據留在內部欄位。
- `estimationReview`：主動反證需求表面範圍、施工樣態、依賴路線與計價乘數。`conclusion` 與 `checkedPatterns` 證明已檢查替代解釋；`criticalFindings` 只保存會改變範圍、方案、責任、人天或驗收的隱性發現，並連回成果包與證據。`scopeDelta` 保存人工初判數、證據確認數、落點類別及 work item，validator 會核對確認數是否等於逐名清單筆數。
- `calibration`：歷史建置報價、相似案或完成樣本的合理性對照；無資料時保留原因。
- `currentDecision`：PM 現在需要做的唯一承諾；答案可由 Agent 查明、只是進度狀態，或先前已明確回答時為空。
- `gates`：PM 進度投影，不規定 Agent 的探索順序。

Schema 8 正式要求上述 PM 確認欄位。任一 `direct-touch` 的 `claimedCount` 與完整 items 筆數不一致、work item 未綁工作集合、工作集合未被引用或 canonical ID 重複，都會阻擋 Gate 5。完整呈現契約見 [PM 確認報告設計](pm-report-design.md)。

## 更新方式

使用 `scripts/case_state.py`：

```text
python scripts/case_state.py init <case-root> --name <案件名> --goal <成果> --mode undetermined
python scripts/case_state.py append <case-root> --collection evidence --input evidence.json --expected-revision 1
python scripts/case_state.py merge <case-root> --input update.json --expected-revision 2
python scripts/case_state.py validate <case-root>
python scripts/case_state.py record-answer <case-root> --decision-id <id> --choice <PM答案> --expected-revision <revision>
```

`merge` 只合併允許的案件區域；`append` 對具 ID 的集合拒絕重複。每次寫入都要求 expected revision，先驗證候選狀態，再以 atomic replace 更新。

### PM 決策的原子接受

聊天中的 PM 決定使用 `record-answer`，以目前 `decision-id`、PM 明確答案與 `expected-revision` 寫回。案件層以固定 sidecar lock 把「讀取目前 revision、核對答案、建立候選狀態、驗證、atomic replace」包在同一個跨程序臨界區；兩個程序同時以相同 revision 寫入時，只有一個能成立，另一個會看到 revision 已前進並保留 last-good。成功後 Agent 立即接續查證與下一張票；只有到達下一個 PM 決定或完成時才停等。

### 大方向、重要決定與選案

Gate 2 先記錄成果大方向及工作分工，決策 ID 使用 `select-outcome-direction`。升版／混合案件以 dependencies 或 outcome 中的目標矩陣保存重要技術線的現況、可選終點、推薦、決定者、影響及確認狀態。使用者沒有提到的技術線維持待確認；「目前可以編譯」是可行性證據，不是保留現況的 PM 決策。正式估算必須能找到這筆 PM 決策紀錄。

需要比較的決策可在 `currentDecision.choiceDetails` 以選項文字為 key，補上 `summary`、`cost`、`risk`、`benefits`、`tradeoffs`。聊天會把它整理成可讀決策包；這些欄位只負責解釋 PM 選擇，不會替代正式 scenario 或人天資料。

`currentDecision.requiresHuman: true` 表示案件在此停等 PM 承諾。除了 schema 必填欄位，Agent 需依 [PM 決策停等指南](pm-decision-pauses.md) 準備推薦與理由、可延後項目、各選項的成果／成本／風險／責任／長期影響，以及回答後的接續工作。這些內容可以投影在 `choiceDetails`、`facts`、`whyHuman` 與 `next`，由模型依案件表達；validator 只保存必要結構，不替代內容判斷。

Gate 只是進度投影時不建立形式上的 `currentDecision`。使用者已在需求或聊天中清楚決定的事項，由 Agent 回述後寫入 `decisions`，使 gate 完成；不要求 PM 重複作答。

仍可能改變成果、範圍、人天、責任、相容契約、維護生命週期、部署或驗收的重要選擇，以 `requiresHuman: true` 的 fog 留在案件中。聊天一次呈現其中一項 `currentDecision`；正式估算前，每項都要有決策紀錄或已由證據證明屬於技術推導。純技術未知使用 `requiresHuman: false`，由 Agent 自動接續查證；只要它仍會推翻方案，就同時設為 `blocksReadiness: true`，因此不會因未打擾 PM 而被略過。

Gate 4 選案時，`currentDecision` 使用 `id: "select-scenario"`，並以 `scenarioChoices` 把 PM 看見的選項對應到 scenario ID。`record-answer` 會原子寫入決策紀錄與 `selectedScenarioId`。推薦、單一路線或 Agent 推導都維持未選狀態，直到 PM 明確確認。

## 可信狀態

案件狀態分成兩層：`draft`／`mapping` 是可持續保存的工作中狀態；`estimate-ready`／`complete` 是對外形成評估成果前的正式狀態。Validator 會保留草稿的結構錯誤為 errors，並把尚未收斂的判斷缺口列為 warnings；只有 state 宣稱進入正式狀態時，正式就緒規則才會把缺口升級為 errors。

一個 state 可用於正式估算時至少滿足：

- ID 唯一，引用存在。
- PM 已選定存在且具有人可讀的名稱與摘要的方案。
- `outcome` 有至少一項可驗收成果，並明確寫出責任邊界。
- 成功鏈有成果終點；所有節點已收斂為 `done` 或 `external`，每個節點有 owner、完成證據與可追溯 evidence。
- 升版／混合案件的 `dependencyCoverage` 已完成或以明確邊界收斂，且每個會影響方案的 dependency 都在清單中。
- 每個 decision-bearing dependency 分開記錄 upstream maintainer 與 internal owner，具有 package-first footprint、目標 compatibility claims、選定策略、證據與驗證方式。採用目標為 supported／conditional、resolution 已收斂且 `blocksScenario: false`。
- 所有 `blocksReadiness: true` 的 fog 已解決；`requiresHuman` 只決定由誰回答，不決定它是否阻擋正式估算。
- 數量守恆。
- 已選方案存在。
- 成功鏈的計價節點恰好被一項 work item 承接。
- 每項 work item 都有 PM 可轉述的工作名稱、技術／PM 說明、包含／排除範圍、責任人、完成證據、成功鏈與 evidence 追溯。
- 每項 work item 都完成方法卡：現況限制、實際改法、客戶成果、規模證據、明確計價單位、計價理由、代表費率依據與去重邊界。
- 每項 work item 以 `detailCatalogIds` 綁定至少一個 canonical 工作集合；所有集合皆被引用，direct-touch 清單完整，generated 與 evidence-only 明確說明其計價角色。
- 每項 work item 唯一歸入一個存在的 `clientPackage`；成果包說明必要性、處理方式、客戶成果、範圍證據與責任。
- `calibration.referenceAvailable` 明確說明是否有歷史對照；有資料時記錄範圍、來源與合理性結論。純升版高值達歷史建置成本 80% 時，另說明客戶取得的重建型成果。
- 外部責任與不異動節點有 0 人天原因；未知數量若存在，必須有明確可估算的未知邊界。
- 費率與列合計符合 0.5 日倍數。
- current decision 若要求 PM 回答，必須交代決定、理由、值得看的資訊、公平可比的選項、推薦與後續；PM 能從畫面理解自己要做什麼以及為何值得投入時間。

正式狀態另需與 PM gate 一致：`estimate-ready` 應為前四 gate 已完成、第五 gate 目前待 PM 確認、並保留 `confirm-estimate`；`complete` 應六個 gate 全部完成、沒有待回答的 current decision，且留下 PM 確認人天的決定紀錄。這些是狀態一致性檢查，不是 Agent 的探索順序。

Validator 檢查可機器判定的存在性、引用、數量、依賴 coverage、相容性結論與阻擋狀態一致性；證據品質、探索完整度、方案取捨與未知邊界仍由 Agent 主動判斷。草稿可以先保存，補齊後再升級狀態。

狀態尚未達到正式估算條件仍可保存為 `draft`；validator 會分開回報結構錯誤與尚未完成事項。

## 證據與敏感資料

案件主檔可保存本地來源定位，但聊天與外部產物只投影經整理的命題與結論。能力 token、帳密與可直接操作外部系統的資訊不寫入 state。

## 返回條件

完成合法寫入並取得新 revision 後，返回成果導向決策循環，重新判斷哪個迷霧最值得處理；不要把「成功寫 JSON」誤認為技術結論已成立。
