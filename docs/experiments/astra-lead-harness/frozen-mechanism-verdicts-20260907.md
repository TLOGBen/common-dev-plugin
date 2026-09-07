# Astra 當主手：本輪留下的機制與未定問題

模型實驗已結束。以下按機制判讀，不合成原版／Lab 的總勝率。判斷以「人最後拿到什麼」為主；流程次數、文字長度與 token 只是代價。四組決策後接續與兩組無額外技能戰役已結案；不同問題／版本分開判讀。

## 先講目前最重要的答案

Astra 不需要每件事都經過完整戰略流程；也不能因此刪掉跨回合狀態、人的決定與實際效果驗收。較合理的實驗方向是：把可省的固定行程改成按需使用，把不能丟的事實與邊界留在最接近作用的位置。模型本身的機制或神經層原因未觀測，不由行為反推。

| 機制／原目的 | 現在觀測到什麼 | 暫定處置與證據強度 |
|---|---|---|
| 小修前全量 Goal／Wayfinder／Strategic：避免目標不清 | screen-v2 八组均完成；自然路由未啟動這三個 workflow，原版也有入口排除 | 明確小修不需要啟動。這支持正確選用，不支持刪掉複雜案的技能 |
| 無額外 skill 的可執行戰役：多步驟是否必須額外 workflow | None 真 Astra→Luna→Astra 已完成一般服務與交接；Lab.7 worker 多寫 pyc 被 carrier 中止 | 支持此局部任務不必額外 skill；Lab 的未交付受工具／載體混雜，不排整體優劣 |
| Delegate：便宜實作、主手保留驗收 | worker-fit四組全選Luna，獨立oracle全過；Lab複雜組多一次有效的test-only返工，無額外skill組一次交付即過 | 保留目的、按任務選用；本批任務已明寫責任契約，未證明額外skill增益，不是無任何scaffold的比較 |
| 便宜單價能否換成便宜結果 | worker-fit複雜Lab5calls／875616tokens／729.155s，None3calls／405893tokens／339.036s；相同外部行為判準都過 | 總成本含派發、主手監督與返工；不能僅看Luna單價。單對樣本不作模型普遍排名 |
| 直接Astra是否足夠 | direct-policy兩組5／54oracle均過；小169259tokens／58.625s，複雜111855／150.822s | 這是不同工作政策，不是skill單變因。適用可自行實作的小範圍，不滿足明確要求的主手／實作分離MOE |
| 每步 full rig／scribe／auditor：防注意力失控 | v2 原版經一次 scribe timeout 後最終成功11calls；Lab3calls也成功。原版另有大量狀態同步、重讀及輕微計數漂移 | Lab改按风险選角色，作下一週試用。這是全流程觀測，非「每一角色皆無用」的單變因證明 |
| 精確角色接線：讓窄角色真正拿到契約 | original-wired 確實讀了 TOML並傳入契約，但scribe仍自行activation越出角色scope，carrier停住 | 接線必要但不足以保證遵守；不能把成功load角色等同scope安全。先保留作用層約束，不加口號式must |
| worker失敗交回主手：分清沒做完與不能做 | v1 carrier逾時直接結束；v2真partial receipt交回，Astra檢查後自己重新派工，最後完成一般服務 | 採用測試載體的失敗交接修正，未改舊raw。原版曾停不是模型選擇放棄，也不是skill根因 |
| 未結操作／效果身份：防重送與假完成 | 初篩、局部戰略均區分送達、版本、唯一性等獨立性質；接續兩版均不把歷史 published＋最新 approved 拼成當前成功，也不重送 | 保留。ledger是紀錄與檢查入口，不是外部動作防火牆，也不能用證據檔hash證明語義 |
| 已清楚決定再問一次：保護人的選擇 | 小修沒有多問；待費率案兩版保留真正人類決定；ready 兩版均承接 900 核准投用，unknown 兩版均不要求重新選費率 | 取消純階段式確認，保留真選擇。本輪沒有重問費率；原版兩次 scribe 逾時及舊 claims／pivot 同步屬別種摩擦，不能混叫多餘確認 |
| 複雜state所有欄位同步：跨回合不失憶 | 原版claims/derived status同步多次validator拒收後修復；Lab也有途中加目標缺入口的真摩擦 | 保留最小帳本，新增窄extend入口。四次A/B全成功，只證明便利性；不是Astra做不到手動維護 |
| 「已知限制要傳給worker」新增一句 | 12calls A/B/B/A都正確傳非Git限制，無重踩差異 | 不採用.6候選；沒有增益就不為常識再加必讀規則 |
| 唯讀交接便箋：人先找到焦點與缺口 | 四次 Sol reader 全辨識未知作用與 lint-only 不足；有無便箋皆讀回原始證據，無便箋一臂兩個連結拼錯 | .8 採用可選入口，不加根技能／強制讀取，不宣稱省時或真人理解改善 |
| 交付首層：讓人接手，而非看活動 | 兩版戰役final都交代一般服務、證據入口與待費率；Lab測試多加identity約束、原版八/九查詢漂移 | 保留成果／缺口／下一步；內容真值另查，不能用漂亮HTML或PASS印章替代 |

## 這次「根因」能說到哪裡

- 可直接定位：未註冊角色的路徑沒被搜尋到；carrier遇timeout原本不回報主手；validator需要同步衍生欄位；role-scope文字留進整體scope；非Git仍呼叫Git；同值同型別的tags被assertIs誤拒；canonical bytes 不變但 dict key order 被測試誤拒；顯式 py_compile 即使 -B 仍寫 pyc。
- 有支持但未隔離：固定staff與複雜schema增加上下文、協調与收斂成本。模型、brief、輸出長度、動作選擇共同變動，不能把整段時間差歸給單一規則。
- 評測設計的真錯誤：先前evolve評審只拿到較廣案例文件，沒拿到actor的窄審查prompt，主線一度把遵守範圍誤當漏查；從第5輪panel補同等實際scope，保留舊票與更正。這應修派發的上下文，不反射性加skill規則。
- 尚不能知道：所有大型系統是否都適合精簡；Fable／Opus的普遍表現；真人一週使用是否更省心；Astra內部推理／MoE路由如何造成差異。

此處 MOE 指 Measures of Effectiveness（目標效果），不是模型內部 Mixture of Experts。量測的是實際成果、作用邊界、正確接受／拒收、可繼續的進度與人的接手；MOP另記角色／讀取／測試／停頓／tokens等過程。

## 證據入口

- [screen-v2](screen-v2-review/)：8episodes、24calls、2,567,794known tokens；沒有啟用Strategic，不能用來否定整個戰役機制。
- [campaign-v2 原版完成](campaign-v2-review/03-campaign-original/lead-review.md)：11calls、2392.538543553秒；10known5,571,700tokens，1timeout未知；一般服務oracle16/16，whole未完成。
- [campaign-v2 Lab](campaign-v2-review/02-campaign-lab/lead-review.md)：3calls、360.791388459秒、522,261known tokens；一般服務oracle16/16，whole未完成。
- [精確接線反例](campaign-v2-review/01-campaign-original-wired/critical-finding.md)：角色定義已讀仍越出scribe寫入權限；這一組不算成功交付。
- [extend窄入口取捨](extension-v1-review/lead-disposition.md)：4calls、492,512known tokens，兩版本都達標。
- [新增Delegate常識條款未採用](delegate-context-v1-review/disposition.md)。
- [決定後接續結果](resume-v1-review/lead-disposition.md)：8calls／6known 2,168,379tokens、2scribe timeout 未知；四組均達各自語義要求，未知成果仍未知，synthetic批准不等於真人回覆。
- [無額外技能局部戰役](campaign-noextra-v1-review/lead-disposition.md)：5calls／713,069known tokens，None 完成、Lab 因 pyc 越出精確白名單被載體中止，未追溯改判。
- [唯讀便箋 reader](handoff-brief-reader-v1-run/lead-disposition.md)：4calls／223,303known tokens，窄幅採用可選入口；沒有真人試用宣稱。

- [任務適配配模四組](worker-fit-v1-review/lead-disposition.md)：14calls全部known1,653,146tokens；兩種難度均完成，未觀察到額外Lab的穩定收益。
- [直接Astra政策對照](direct-policy-v1/lead-disposition.md)：2calls全部known281,114tokens；自驗不冒充獨立驗收，總流程政策不同。
- [評測範圍更正](../../../.codex/evolve/lab-verifier/measurement-addendum-3.md)：流程本身也必須接受反證；不是評審一致就能替代正確任務上下文。

用量是實報input（內含cache）加output；reasoning屬output不另加，未知不是零。上述不同批次不含全部研發成本，API等價價格不等於實際帳單。
