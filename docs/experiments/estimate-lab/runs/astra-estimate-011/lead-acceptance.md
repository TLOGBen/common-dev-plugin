# Estimate E1／E2 主線驗收

結論：兩臂都完成本輪限定的資料評估與高值預覽；原版 E2 額外發現三組表格未渲染的呈現缺陷。這不是完整估算產線、真人 PM 核准或真實系統改造完成。

## 看過什麼

主線完整閱讀四個 final、兩份實際五欄 CSV、評估報告與 handoff，核對原始工具紀錄及前後 hash；再以獨立 parser 核對實際檔案。數字、入口與解析證據見 [parser receipt](preview-parser-verification.json)。所有原始產物保留，未為評審修稿。

| 場景 | 原版 A | Lab B | 有效結論 |
|---|---|---|---|
| E1 Java 17 唯一既定目標 | 5 項固定條件及 guards 滿足 | 同左 | 沒有偷選框架、資料層或部署；limited smoke 不冒充完整回歸與維護支援。 |
| E2 高值預覽 | 7 項固定條件及 guards 滿足；另有呈現缺陷 | 7 項固定條件及 guards 滿足 | 87＝84＋3；別名不加項；generated／coverage 不當人工乘數；四包 5＋3＋3＋2，開發 7.5／測試 5.5。 |

「條件滿足」不是品質百分比。E2 A 的第六項檢查實際五欄文案、工作解釋與可用連結，均成立；不能事後加一條 table 形式判準再改寫舊分數。另列新增缺陷：A 報告第 68、83、127 行開始的別名、coverage、canonical 清冊缺表頭分隔列，markdown-it-py 的 CommonMark＋table extension 實際解析為非表格。B 四組均形成表格。這是 parser 檢查，不是像素或真人易讀性測試。

E1 不需新增文件；E2 各自只新增授權三檔，原始六份附件不變。兩臂都沒有捏造低／基準值或要求為完成高值預覽而補造它們。必要 PM 承諾被放在下一階段，不阻止本次預覽交付。

## 時間與資源

四次 Astra/high 實際呼叫共 613.104 秒；input 538,347（其中 cached 428,544），output 17,844，total 556,191。E2 的 B 192,564 tokens 高於 A 167,352，不宣稱新版省 token。實付 USD 未回報，記 null。

只有每題每臂一個樣本、同模型、非盲主線審查；不足做穩定性、統計顯著性或模型排序結論。原始機器結果見 [summary](summary.json)，裁決見 [lead-acceptance.json](lead-acceptance.json)。
