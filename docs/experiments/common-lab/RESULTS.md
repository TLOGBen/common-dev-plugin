# Skills Lab 分輪實測發現（歷史小計保留）

最新已結束批次與三包結論請看[收斂主報告](../RESULTS-20260907.md)；以下保留各階段的已知範圍與歷史小計，不是全場總量。模型實驗已結束，03:00 截止前不再新增題目。

目前最有價值的變化，不是技能變短，而是更清楚分開「模型做完一個動作」和「人拿到可用結果」。分輪新情境測試已結束，沒有宣布新版全面勝出。

## 已找到並修改

- **Wayfinder**：原本格式中的標題差異會讓 renderer 漏掉決定、問題與範圍外資訊；已修正。實際 A/B 工件又顯示「現在可處理」會使範圍外的產品工作看似可執行，0.1.3 改為「前置就緒」並明示它不代表完成或授權。
- **Estimate**：原程式記錄 PM 人天答覆後仍停在要求保留該問題的狀態，造成自己的 validator 拒絕。Lab 新增「人天已核准，待交付」，確實接續 Gate 6；重試與過期回答不能重复核准。預覽、核准與交付分開顯示，數值與五欄 CSV 不改。
- **共同邊界**：已發生的異動不當成尚未發生；送達不等於唯一性、覆蓋或不存在；工具／組織政策失敗不當成模型能力弱。簡單解釋不加不必要小考。

- **Grilling**：批判方法時曾把「使用者已知道欄位名稱」改成「自行發現欄位」，測的主張就不同了。拒收過度修正的 0.1.4，0.1.5 改成保留明確主張、說清楚方法如何使測試失真。[8 次固定回歸](grilling-claim-heldout-015-a/lead-acceptance.md)不作模型排名。
- **Estimate 0.1.3**：實際鍵盤 Enter 會誤關閉工作明細，已修復並用原生 Tab／Enter／Space／Escape 重測；已核准報告的過期 Gate 5 提醒改標原評估紀錄，未抹除部署及 UAT 條件。[紅綠與瀏覽器證據](../estimate-lab/presentation-fix-013-a/verification.json)。責任或選案變更後會重新確認，連續變更也刷新問題；曾錯誤復活草稿的中間版本已拒收並縮窄修正。[64 項狀態／輸出與 5 項事件測試已在安裝後包內通過](../install-common015-estimate013-20260906-a/result.json)，不宣稱涵蓋所有承諾欄位。

- **Strategic 0.1.7**：途中新增 Estimate／Astra 成果時，缺少保留舊驗收的追加入口。四次 Astra 主手 A/B 都正確完成；基線能自行安全修改，新版兩次使用受測的 extend 入口。採用工具便利性，不新增根技能規則、不宣稱基線能力不足。[完整判斷](../astra-lead-harness/extension-v1-review/lead-disposition.md)。

- **Strategic 0.1.8**：追加可選唯讀交接便箋，不改帳本／schema／根技能。四次 Sol reader 均辨識未決作用與「lint 通過不足以完成」，有無便箋都仍讀原始證據；採用的是可查證的入口，不宣稱縮短閱讀或真人理解改善。[結果與限制](../astra-lead-harness/handoff-brief-reader-v1-run/lead-disposition.md)。

## 實際使用看到什麼

四次同模型的受限實際執行，原版與 Lab 都完成凍結的局部要求，沒有據此排列品質高低。Strategic 兩臂都抓到成功檢查器的假綠燈、版本不匹配與多次送達，拒絕把業務目標寫成完成；Wayfinder 兩臂都保留範圍外工作未實作的事實。它們不等於整個 Strategic 工作流的完整 A/B。

Wayfinder 這一對 Lab 總 token 少約 9.24%，但按公開短上下文 Standard 費率的 API 等價值反而高約 16.96%，因為快取比例不同。這直接反駁「文字短／總 token 少就一定比較省」；不能外推為每個任務的速度或費用。

[主線逐條驗收](runs/astra-execution-012/lead-acceptance.md)保留兩臂可見結果與判讀。最初綜合分數因 Strategic 判準有互相衝突而不適合作排名，見[測量修正](runs/astra-r2-design-freeze/measurement-note.md)。不挑掉失敗樣本來宣布新版勝出。

## Astra 主手新增結果

原版戰役在 scribe 逾時後收到真實 partial receipt，由同一 Astra 自主重新派工，最後完成一般服務。實驗版也完成同一可執行成果，兩版都保留尚待人的 premium 決定；不再以早期載體中止推論原版做不到。[逐機制暫定取捨](../astra-lead-harness/MECHANISM-VERDICTS.md)分開目的、觀測、根因證據強度與 MOE。[決定後接續四組](../astra-lead-harness/resume-v1-review/lead-disposition.md)均達各自要求：已核准 900 正確投用，作用不明則不重送、保留未知；兩版都沒要求重選費率。原版兩個 scribe 各 600 秒逾時由主手收回局部成果並更正狀態，不能說原版不會接續。

[無額外技能完整局部戰役](../astra-lead-harness/campaign-noextra-v1-review/lead-disposition.md)中，Astra 同樣能派 Luna、驗收與投用；Lab 那組因 worker 顯式 py_compile 寫入白名單外的快取被載體中止，不能當純 skill 較差的證據。成功組的測試另誤綁 dict 欄位順序，已用 canonical 內容不變的合法替代實作重現。

## 用量與時間的範圍

更新的固定索引涵蓋 **182 次 CLI 呼叫**，其中 **179 次已知 19,892,206 tokens，3 次逾時未知**；input 19,531,341（含 cached 16,832,640）、output 360,865（含 reasoning 111,542），不重複相加。呼叫時間相加 13,414.550 秒；區間聯集 10,705.122 秒，均非整場工時。沿用 2026-09-06 公開 Standard 短上下文費率的已知 API 等價小計 **US$36.10703888**，不是帳單；因三次未知不宣稱完整價或有限上界。詳[182 次原始回溯與校準索引](../measurement-index-182calls-20260906/index.json)。仍排除原生研發及之後已結案的三批：resume-v1 為 8calls／6known 2,168,379tokens／2unknown；便箋 reader 4calls／223,303tokens；無額外技能戰役 5calls／713,069tokens。這些已有各自用量來源，尚未併入上述凍結索引。

以下119次數字保留為早先固定小計，不是現在總量。

目前可逐次回溯的索引涵蓋 119 次 CLI 呼叫，共 **8,027,651 token**：input 7,874,828（其中 cached 6,525,696）、output 152,823。Reasoning 40,473 是 output 的子集合，不重加；119 次回報的 cache write 均為 0。

單次牆鐘相加為 5,755.931 秒，有重疊；實際呼叫區間聯集為 3,971.336 秒，不含各批之間空檔，也不是整個研發工時。按公開短上下文 Standard 費率的 API 等價值為 **US$20.90600840**，不是帳單。長上下文、服務層級等不確定性與逐筆原始檔定位均在[索引](../measurement-index-119calls-20260906/index.json)。這是固定小計，後續 verifier 與主線仍另計。

主線與原生 worker 用量另記，不能拿 CLI 小計冒充整個研究成本。[原生部分快照](../native-usage-20260906/snapshot-a.json)截至 2026-09-06 12:53:37（Asia/Taipei）的可分離增量為 79,911,609 token，已排除 fork 繼承歷史；它不含之後工作、早於基準的用量與未能歸屬的 session。尚無實際美元帳單。

## 目前不能宣稱

1. 模型 reader 能回述，不等於真人已理解、批准或能順利接手。表格本身的語意真實還要獨立核對。
2. Fable 的正常呼叫被組織政策阻擋，Opus 未實測；不能據此排序。Astra／Sol／Luna 的結果也只適用已測案例。
3. 包能安裝、測試通過，不等於使用者的 App 已載入或真實案件已完成。正式來源與全域安裝保留。
4. 暫存安裝、renderer 測試與 A/B 下一步演練是不同證據，不合成一個「完成率 100%」。

新增實作與讀者結果也沒有被簡化成勝率：[Estimate 4 次實際產物](../estimate-lab/runs/astra-estimate-011/lead-acceptance.md)兩版都守住 87／136／13 的計價邊界，但 A 有三組 Markdown 表格缺分隔列；[8 次模型讀者](../estimate-lab/runs/sol-e4-reader-v1/lead-review.md)能解釋內容，仍不能替代實際渲染。合成核准控制也不是真人已接受的正例。

[Baransu 局部實作](../baransu-lab/contract-execution-v1-verification/README.md)兩版獨立 oracle 都通過 8 例。新版交接混用了檔內案例數與當時 runner 的檔案級摘要，屬呈現誤差；不因程式正確而忽略，也不因案例數多就判品質較高。兩個 fresh verifier 已完成：原版 mutation 找到測試拒絕能力缺口，新版指出交接計數誤差；其中另有主線 dispatch 漏交授權／歷程造成的判斷摩擦。[主線逐項判讀](../baransu-lab/runs/sol-contract-verification-v1/lead-review.md)不把未知當違反，原版完整 seal／hook 尚未執行。
