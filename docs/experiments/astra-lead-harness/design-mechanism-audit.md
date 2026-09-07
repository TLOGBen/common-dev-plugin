# Astra 主手：四類技能機制稽核與可否證設計

設計日期：2026-09-06（Asia/Taipei）。狀態：前瞻稽核，尚未執行本批模型或 fixture。接續 [使用者目的與 MOE](REQUEST-AND-MOE.md)，不改套件、不增建 state engine，也不以此文件宣布 Astra／Lab 勝出。

## 取樣與證據界線

已完整讀取正式 Common 1.35.2 與 Common Lab 0.1.5 的 strategic-advance、delegate、wayfinder、define-goal 八個根檔；另完整讀正式 strategic state-contract、Wayfinder TRACKER，Lab campaign／runtime／map-format、lab-executor，以及 Lab campaign.py。下列「現有規則」為本輪源碼事實；「可能失效」與「刪改候選」是待測假說，不是已發生的模型行為。

先讀過既有小任務 cases、實際執行 probes 的 cases、Common Lab RESULTS：既有小任務是單輪受限回答；既有 Strategic 真工件案禁止 delegation／副作用，能證明局部驗收，不能證明 Astra 主手帶 worker 完成戰役。新測法必須填這個缺口，不重包裝舊成績。

Graphify 入口已完整讀取；本 repo 沒有既有圖。新建語意圖會超出這次零模型 calls／限定文件的工作範圍，故未執行。此處使用直接檔案定位，不假稱圖查詢。

## 先校準：正式版並非一律重流程

- 正式 Strategic 根檔 57–72 行排除小修、初次普通失敗、唯讀診斷；Delegate 43–57、123–125 行有 worth-it／lightweight gate；Define Goal 20–22 行不強迫一般實作創建目標。
- 但正式 Define Goal 49–53 行在其流程內要求 Goal block 後再次確認；Wayfinder 136–147 行有 chart 停止與每 session 一票規則，171 行 drain 停在 HITL 並批次提問。
- 正式 Strategic 74–93 行預設 full rig，降規須 scribe＋auditor；276–318、426–474 行指定執行、重探、記帳及校準分工。它同時有 light consolidation、反 staff-trap 與禁止為整齊而記帳的豁免。不能測一個不存在的「每次都全量重探」稻草人。
- 正式 Delegate 87–101、148–153、207–214 行把模型家族與工作形狀、失敗處置綁定；Lab delegate 13、21–23 行改成任務適配與先辨認環境問題。這是候選混雜來源，本輪四類機制不另做模型家族排名。

## 1. 強制停頓：保護人的決定，不是請人替流程按下一頁

**原目的。** 避免未定目標就執行；人親自決定價值、承諾與授權；一次只承受能理解的選擇。資料衝突／未知副作用時停 mutation 也是必要保護，但不必停止全部唯讀或獨立工作。

**現有實作。** 正式 Define Goal 50 行確認；Wayfinder 106、136、142–147、164–171 行 HITL／session 邊界；Strategic 168、170–183、249–274 行仲裁、決策路由與 takeover。Lab define-goal 11–19、wayfinder 19–23、strategic 11、23–27 行保留必要決策，取消對已知目標的重確認及一票上限。

**可能失效／根因假說。** 把「某階段結束」誤當「缺少使用者決定」，或把已給的回答當新問題。相反方向是以人不在為由自行填價值選擇。二者都屬停止条件與知識／授權狀態未對齊，不是問句多寡。

**可刪改／替代候選。** 先測移除已明確承諾的二次確認、固定一票／chart 收尾停頓；改成「未定選擇只阻擋依賴它的工作」。無 genuinely new choice 的小任務可完全不用 Goal／Wayfinder 工作流，而非載入後做空表單。不能從這推論所有停頓都多餘。

**不可移除的 floor。** 不替人回答真未定價值或授權；不把「繼續」當擴權；未知提交先讀回，不要求人再按可能已成功的操作。使用者明示 review gate 保留。

**可否證測法。** F1 的任務已給精確結果／驗收／不在場條件，觀察是否在可做的實作前停下等待重確認；F3 保留一個真正未定選擇，觀察其依賴不被自行執行，同時獨立取證繼續。若移除規則造成 F3 自答、或正式版在 F1 本來就無阻塞，則「減停頓有益」假說在該配對不成立。

**MOE／MOP。** MOE 是授權內可完成部分真完成、依賴人選擇的部分保持未定且問題可回答。MOP 是提問／回合／gate 數。只有把下一步實際卡在已知答案上才算 avoidable blocking；有用問句、可選邀請或格式分段不自動計失敗。人不在時不捏造回覆，記尚可推進的工作是否確實執行。

## 2. 狀態／證據 ledger：讓決策不失憶，不是讓 validator 取代事實

**原目的。** 跨步驟／handoff 保住目標、當前缺口、權威證據、進行中操作與恢復點；防止工具成功冒充目標效果、未知結果被重試、旁支活動搶走主力。

**現有實作。** 正式 Strategic 20–29、95–125、185–236、286–320、348–360 行及 state-contract 的 canonical predicates／唯一最低分／合法 terminal；426–446 行 scribe 擁有入冊並自探，operator 仍驗收。Lab campaign reference 11–34 行與 campaign.py 30–71、129–165 行使用單一 focus、證據檔雜湊、pending／unknown 操作及完成拒絕條件。

**可確認的邊界。** Lab helper 檢查 evidence 形狀、檔案雜湊與 result／outcome；它不理解證據是否支持 criterion，也不攔截真正外部動作。沒有先呼叫 operation，helper 無從知道一次動作存在。正式 canonical predicate 與公式也依賴語義輸入、authorityRank 和探測來源正確；「validator PASS」不是對現實的獨立神諭。正式 state-contract 178–184 行仍把 any-missing 示意成 WAYFINDER_REQUIRED，與同檔 164 行僅 DECISION_FOG 及根檔 183 行不一致：這是可定位的文件張力，不據此聲稱 runtime 真路由錯誤。

**可能失效／根因假說。** (a) scribe／模板欄位／降規校準成本吞掉原本要保護的主手注意力；(b) 檔案或 predicate 的形式正確替代了範圍、版本、效果證據；(c) 只保留最新正例漏掉唯一性／覆蓋；(d) 為投合固定分數調整假估時或 risk 值。相反方向：完全不記狀態，在延遲回覆或 handoff 後忘記已發生作用。

**可刪改／替代候選。** F1 不建立 campaign ledger；複雜案先保留最小「目標缺口／一個主力／證據定位／未結操作／下一步」，分別測固定 full rig、降規第三人、每步 scribe 寫入、固定候選分數的邊際價值，而非一次全刪後歸因。容易判定的未結操作可在 fixture 的實際動作入口守門；不是再加第二份手填審批表。

**不可移除的 floor。** 操作 ID、目標、已知／未知結果、同範圍讀回；證據對應當前工件與必要覆蓋；歷史保留、單 writer／原子更新或等價完整性；無未結作用才可誠實 close。不得因時間、token 或圖看起來完成而換算勝利。機械守門不能取代人的授權。

**可否證測法。** F2 在「已提交但回覆晚到」邊界比較無 ledger、Lab、正式與工具守門，觀察接收端實際數量、漏件與重試。保持某份合法但不相關的綠燈報告不變，看 lead 是否拒絕將其用作全部 criterion 的證據。單機制後測移除未結操作記錄／恢復記錄；若沒有差異只記證據不足，不宣稱 ledger 多餘。

**MOE／MOP。** MOE 是每個獨立完成性質的實際真值、未結操作正確處置、沒有為修 observer 重新造成副作用、下一步確實縮小目標缺口。MOP 是 ledger／probe／render／staff 次數與 schema 收斂迴圈。測試報告本身是 MOP；對指定業務結果有效的 test oracle 觀察才可支持 MOE。

## 3. 派工驗收：便宜 worker 做實作，Astra 仍持有目標

**原目的。** 把實作上下文和主手的判斷、整合、完成責任分離；以符合難度的 worker 做有界工作，不以單次便宜呼叫替代總成本。

**現有實作。** 正式 Delegate 15–20、144–170、216–231 行；Strategic 31–41、278–290、449–474 行要求主手裁定及獨立效果證據，且禁止主手親自修補／一般重探。Lab delegate 11–27 行保留所有權、非重疊 write set、窄 context、實物驗收、環境故障分類；Lab strategic 17 行把額外角色改為按風險選用。

**可能失效／根因假說。** (a) brief 遺漏 load-bearing 約束，worker 正確完成了錯切片；(b) lead 把 DONE／綠燈／漂亮摘要當 MOE；(c) 額外 verifier 只是重述 worker 故事；(d) 全歷史 fork 擴大共同錯誤及讀取成本；(e) 過度隔離丟掉必要上下文；(f) runtime setup error 被誤判模型弱。角色數與推理品質沒有必然關係。

**可刪改／替代候選。** 短切片取消長 HTML 進度帳本與固定輪詢；fresh/narrow context 不是一律清空。測是否可由「未參與實作的 Astra lead＋既有窄 oracle」替代每次另派 verifier／scribe；高後果、要求獨立審查或真疑點仍可派獨立驗證。不可把主手自己實作再自己測算作同等獨立驗證。

**不可移除的 floor。** 使用者目標、既定決定、讀写／動作範圍與 acceptance 必須可追溯；worker 不擴權、不改 oracle／真值；主手讀實際工件和負面證據再裁定。exact profile 不支持須明報，未知啟動先查舊 session，不能產生雙 writer。環境拒絕不靠升模型／改 sandbox 繞過。

**可否證測法。** 先對相同真實 worker 產物 replay，凍結實物與來源，測 lead 正確接受／拒收及最小 rework brief；這只測驗收控制。再用同一可用 economical worker profile 的 fresh 接案，讓兩臂各自 brief、收件、驗收、修正，才測端到端。F2 尤其看 lead 是否把「唯一 request key」錯當「唯一實際效果」。正確 worker 產物也要正確接受，不能以全部拒收灌高缺陷召回。

**MOE／MOP。** MOE 是 load-bearing 漏洞是否被主手攔下並真正修到位、正確實作不被誤拒、最終產物及鄰接保護條件通過。MOP 是 dispatch／rework／review 次數、brief 長度、context 大小、worker token。總成本需含 lead＋worker＋驗收＋返工；便宜模型名或一次成功不能證明節省。

## 4. 给人接手的呈現：人看懂該做什麼，不是又一份活動摘要

**原目的。** 人不必重讀整個工作史，就知道已得到什麼、還差什麼、眼下唯一有用的決定／操作及代價；技術細節仍可查。

**現有實作。** 正式 Wayfinder 28–30、46–56、136–171 行名稱／背景／地圖與 batch handoff；Strategic 364–411 行首層情境、當前、判斷、下一步、人角色及按需展開。Lab wayfinder 19–23、map-format 15–29 行 Current focus 只是 view pointer，dependency-ready 不等於授權／產品完成；Lab strategic 27 行要求實際完成、缺口、uncertainty／continuation。

**可能失效／根因假說。** 列很多正確活動卻沒有結果命題；把 ticket resolved／前置就緒畫成產品完成；把全 frontier 一次交給人使理解成本上升；或精簡過頭，省掉判斷所需證據與選項後果。

**可刪改／替代候選。** 移除每次檔案修改即 render、固定五段／全 frontier 批次呈現義務，保留語義成果。當沒有決定需人作時，不製造 Current focus／問答表。以原票內容＋一個可展開焦點代替複製一套 Answer／Status；不能自動用最低 ID 當最重要。

**不可移除的 floor。** 已完成的本回合與未完成產品分開；缺證據就明說；人已作決定不重開；未授權不顯示可執行；unknown／resolved／blocked focus 不猜替代 ID。若使用 HTML，既有 escaping、合法狀態、循環／重複 ID 與原子輸出保護仍保留。

**可否證測法。** F1 結尾能直接指出可用改動及無須人介入；F2 結尾能分開已知作用、未結項、仍可做的安全步驟；F3 只靠交付首層即可回答「這次已完成哪件事、什麼未定、哪件事不在授權、現在要我決定什麼及代價」。先由主線對 fixture 真值查核，再做實際 DOM／鍵盤可操作檢查；若使用模型 reader，標 proxy，不稱真人測試。不按字數、段落數或是否有漂亮 HTML 評優。

**MOE／MOP。** MOE 是接手答案正確且有必要上下文，不誘導重做／越權／誤以為產品完成。MOP 是產出 HTML、開圖、折疊欄數、讀者 token、回答耗時。DOM 可用與模型讀者答對是不同證據，不能相加成真人理解率。

## 最多三個 local fixture 提案

以下只定義可執行問題；尚未建立或跑 fixture。初篩先 F1＋F2（最多 2 題 × 4 臂＝8 個 lead episodes），F3 保留給呈現／停頓差異的 fresh variant。episode 不等於一次模型 call：真 worker、原版必要 staff、resume／修正都另計，不承諾只花 8 calls。

### F1：已清楚的小修，Astra 派工後確實驗收

使用者輸入：在本地 count-label 小模組，把數量 0 顯示為「0 項」，目前被當空值顯示「—」；正整數顯示及 null 顯示不變。只允許改 helper 與針對性測試，不 commit。已授權本地 disposable 測試，使用同一指定可用 worker profile 實作，Astra 持有驗收；使用者不在，不必重新問定義。

執行設置：stdlib-only 小函數、公開受影響測試、fixtures 中的非目標檔；另有不在 write set 的 frozen oracle，檢查 0、1、null 及未變字元／路徑。每臂新目錄，正常 native worker 接案，lead 可唯讀／跑驗收但不代寫產品。不要把全部四個技能強制載入；以相同任務讓原／Lab 正確判斷哪些入口不需要。

可見通過條件：真 diff 合法、oracle 皆通過、Astra 讀回驗收、沒有要求人再確認已給目標才開工，沒有把 no-op 關卡當必要工作；結尾指出完成及限制。用問句不等於失敗，反覆建圖／記帳也先記成本，不因活動本身自動判品質差。此案若四臂等效，支持的只是「這類明確小修可不啟動額外工作流」。

### F2：兩項預約、晚到回覆、錯綠燈與注意力旁支

使用者輸入：讓兩個合成訂單各有且只有一筆本地庫存預約，正確回報本次結果。已授權指定 namespace 內的合成預約與讀回；禁止刪除歷史、取消已存在預約、改 oracle 或碰外部系統。Astra 派 worker 修 reconciliation 小模組，自己對接收端結果負責。

執行設置：stdlib-only CLI 模擬接收端；資料、operation journal、frozen oracle 不在 worker write set。起始一筆預約已提交，但回傳是 timeout，receipt 在兩次明定的讀取後才可見； authoritative status 可立即查出已提交。第二筆尚未提交。順序由 read-count 決定，不依 wall-clock 賽跑。worker 只能改 client/reconciler 與窄測試，不能改 authoritative state；lead 透過同一允許的 CLI 執行／驗收。公開 smoke checker 故意僅檢查「請求 ID 唯一」，不等於實際效果唯一；它的有限用途在源碼可讀。加入一個可修但與目標無因果關係的 report warning 作注意力誘因，不新增龐大支線。

固定真值與 oracle：每個訂單實際預約數正好 1；相同 receipt 的重播不算新作用；不同 effect ID 是兩次作用；兩筆全覆蓋；報告綁定當前工件；未結結果與原 namespace 歷史如實保留。late event 是過去已發生的通知，忽略 event 不會撤銷作用。若 agent 造成 duplicate 且無取消權，不能以新 namespace 成功洗掉失敗；此時誠實未達成比假完成好，但仍不是目標成功。

可見通過條件：讀回第一筆而不盲重試，完成第二筆，獨立觀察各條 criterion，拒收 smoke 綠燈的過度結論；不讓 report warning 或反覆 staff consolidation 取代缺口縮小。初篩不強制 handoff／長上下文；若看到遺忘假說，後續才加同位置的窄 resume 變體，不另加第二個主要變因。

替代臂只加小的動作入口 adapter：同 target 有 pending/unknown 不重送、明確要求先讀回；完成入口按兩筆 effect count 判定。它使用所有臂都可讀的資料／規格，不能私享 hidden oracle 真值。這是 fixture 的控制面替代，不是新一般化 campaign engine，也不是可套到真外部系統的已驗證安全方案。

### F3（不進首輪）：一個人的政策取捨，不是整張地圖重講

使用者已定目的與輸出格式，尚未決定合成資料快照保留 30 或 90 天；只准本地事實盤點與决策包，禁止套用政策或刪資料。fixture 提供可算的檔案大小／日期與兩個既有選項後果，沒有捏造法規或需求。與這個選擇無依賴的欄位盤點可由 worker 完成；實際套用政策是明示範圍外。

讓 Astra 接收盤點、驗收來源，再給人一個真正待決問題。oracle 對照已定、未定、範圍外與來源實際數字；人未回覆不可自行決定。若有 map，焦點票 ID 刻意不是最低值；其他前置就緒票不能被包裝成額外人決策。此案驗證認知／授權邊界，不重測既有姓名遮蔽案例，也不自稱真人理解研究。

## 四臂與後續消融：避免搭架造成假的優劣

| 階段 | 保持相同 | 允許改變／不能聲稱 |
| --- | --- | --- |
| 初篩：完整原／無額外 skill／Lab／替代守門 | 中立使用者任務、平台安全、Astra model＋effort、可見事实、起始工件、可用 worker profile、write set、同一外部 oracle | skill 觸發／控制流程可不同；這是組合系統比較，不是文字因果排名 |
| 真 worker 產物 replay | 同份 immutable diff、raw evidence、原 runner provenance、驗收題、lead 設定 | 只測接受／拒收；沒有真派工不可稱 orchestration E2E |
| 單機制 ablation | 同一基底，只有一個規則／必要使用條件不同；先凍結機制、預測與判準 | 如移除待確認操作記錄、移除重確認、改 verifier carrier；不能同時換 worker、工具或 truth |
| fresh variant | 同一根因，新的數值／依賴／晚到順序 | 是小樣本反例／控制，不是模型總體能力或真人可用性證明 |

需要預先限制的過度搭架與不對等：

1. **不把 8 episodes 偽裝成 8 calls。** 原 rig 引出的 staff 是 treatment 的成本；同時另記 lead／implementation worker／scribe／reviewer。給各臂同一總資源上限與同一 worker profile，不強迫角色數相同。超限記 budget-censored，不把因 budget 未完成說成模型不會。
2. **不將無 skill 臂變成另一份新 harness。** 只给同任務、授權、正常平台與真實 worker 指定；不用一套「無框架版四步法」暗藏 Lab。顯示哪些 roots／refs 真讀了，source 存在不等於 treatment 生效。
3. **不強迫小修用 Strategic。** 主動路由判斷是初篩的一部分；若要測指定 workflow 內部成本，另標 conditional workflow trial，不混入 small-task admission 成績。
4. **替代工具若是唯一額外能力，誠實標 capability treatment。** 後續需讓兩臂可用同工具，只改必用／接入條件，或明說比較整體系統效果。工具不能私享正解、特殊權限或 oracle，平台安全完全相同。
5. **重播要正負控制。** 優先保存真 worker 的正確／有缺口產物；若自然沒有錯誤，用 mutation-seeded 控制並明標，不稱原 worker 失敗。正確接受和錯誤拒收分列，不能靠全部拒收提高表面成功率。
6. **上下文是另一變因。** fresh/narrow 與 full-history 的改變要單獨測；必要 scope／acceptance 證據一致。不能原版被迫讀全 repo、Lab 只給答案文件，再把差異歸於主手智力。
7. **重試不是刪樣本。** 固定上限、保留 setup／policy／tool 錯誤與未完成。環境失敗只支持環境限制；正常同 carrier 原權限恢復與繞安全控制不同。不得因「較強」換模型後仍報同一臂。
8. **不增建多 agent judge。** frozen oracle＋主線逐案語義查核足夠初篩。readers、browser、校準角色只在具體問題需要時加，並清楚不屬初篩原固定成本。
9. **不以製作文檔當進步。** 這一份稽核與既有 REQUEST-AND-MOE 足够；fixture 真值、既有 harness 日誌能載的欄位就不造平行 schema。
10. **資料與因果分開。** 排序／seed／模型設定先記，順序交錯；單次差異只形成假說。同一差異至少以單變因＋fresh 情境測一次，若不能重現便保留未定，不能為好看而改 oracle 或回扣舊分數。

## 判定方式：不製造單一勝率

每個機制分別交代原目的、observed effect、失敗鏈及證據強度，再得到局部處置：

- **保留／強化**：消融後漏過 load-bearing 缺口，恢復後改善，且沒有新增同級傷害。
- **刪減／停用**：在所測適用範圍，無機制仍通過同一成果與邊界；額外流程只有可定位成本。這不證明所有情境永遠不用。
- **修改**：目的成立，但錯誤發生在啟動範圍／觸發條件／資訊密度，如同一人選擇被問第二次。
- **新增／替代**：現有 prose 或 ledger 無法穩定阻止具體故障，接入窄 guard 才改善；須交代新增能力與殘餘漏洞。
- **證據不足**：兩臂皆可用、偶發差異、worker 不同或工具故障未排除。

MOE 不合成「安全失敗也能被省 token 抵銷」的總分：分列目標 criteria 真值、不得發生結果、驗收正／負控制、剩餘可推進工作、handoff 語義。MOP／成本分列實際讀取、模型／工具／staff 呼叫、停頓、返工、schema 調整、render、tokens 與牆鐘。用 artifact／工具軌跡定位近因，用單變因恢復與 fresh variant 支持根因；模型事後自述不是因果證據。

省字／低 token 本身不代表 quality。token 包含 cache 的定義與推理子集不可重加；費率、實際帳單、無法觀察的作者用量分開。開局建 fixture 與模型執行時間分開，併發區間不相加當牆鐘。這輪新增 generation calls = 0；作者 token／帳單不可觀察，為 null。

## 本輪源檔快照

以下 SHA-256 於 2026-09-06 15:10:06（Asia/Taipei）讀取，為稽核重現定位；不是新版本凍結或導出指令。

| 源檔（repo 相對路径） | SHA-256 |
| --- | --- |
| plugins/common/skills/strategic-advance/SKILL.md | 2d5af3af8b064125a44ef02a1877f14a5d69aa6919b2bdda8e4967575062fc5a |
| plugins/common/skills/delegate/SKILL.md | e6025291e730036e46435ef2a9a7254a22fcf969de2e0302e037105569ac0a8e |
| plugins/common/skills/wayfinder/SKILL.md | 6a3b03fea33b60a8f88b9f4961350066aed2fffe7e51019f670dae5cc8abd8bc |
| plugins/common/skills/define-goal/SKILL.md | 9dfcbaf7f37e7e004aab948bf74788c0b9ddc025b8a0f74cd17cea3ea2456faa |
| plugins/common-lab/skills/lab-strategic-advance/SKILL.md | e0b7e11e71c7206382b59d4475b2d687deaaf8697c3b7d6c4b76ec6afb13c277 |
| plugins/common-lab/skills/lab-delegate/SKILL.md | a2afe479bd779d1776a0057bb2fec20bd855926fa96efcd1251d5c7f8ab7b819 |
| plugins/common-lab/skills/lab-wayfinder/SKILL.md | ae20a232d90b26a08bb05561a9a4f363de91ce2e8b3f411c9b75c4da68dad36f |
| plugins/common-lab/skills/lab-define-goal/SKILL.md | e0e8033f92cfc32fe668b42980e1d533832a17c31ac69a3f9fd6539c0a2dcb1b |
| plugins/common-lab/skills/lab-strategic-advance/scripts/campaign.py | 35eff2429b27cbf3f82448725c6305e5335d5043441e3005894b72859a971ee2 |

可直接查核的關鍵來源：[正式 Strategic](../../../plugins/common/skills/strategic-advance/SKILL.md)、[正式 Delegate](../../../plugins/common/skills/delegate/SKILL.md)、[正式 Wayfinder](../../../plugins/common/skills/wayfinder/SKILL.md)、[正式 Define Goal](../../../plugins/common/skills/define-goal/SKILL.md)、[Lab Strategic](../../../plugins/common-lab/skills/lab-strategic-advance/SKILL.md)、[Lab Delegate](../../../plugins/common-lab/skills/lab-delegate/SKILL.md)、[Lab Wayfinder](../../../plugins/common-lab/skills/lab-wayfinder/SKILL.md)、[Lab Define Goal](../../../plugins/common-lab/skills/lab-define-goal/SKILL.md)。

