# 直接 Astra：兩題完成，較便宜 worker 不保證整體較省

D1、D2 各1次 fresh Astra/high，產品皆通過相同預封存外部oracle（小型5/5、多約束54/54）；無scope violation。這是實作政策比較，不是純 skill A/B，也不是獨立驗收機制相同的比較。

| 題型／政策 | tokens | 秒 | Standard短上下文API等價USD | 分離實作與主手验收 |
|---|---:|---:|---:|---|
| 小型／直接Astra D1 |169259|58.625|0.338510|否|
| 小型／Astra→Luna None W1 |181177|87.190|0.359164|是|
| 小型／Astra→Luna Lab W2 |190460|99.551|0.389601|是|
| 多約束／直接Astra D2 |111855|150.822|0.491502|否|
| 多約束／Astra→Luna None W4 |405893|339.036|0.621012|是|
| 多約束／Astra→Luna Lab W3 |875616|729.155|1.082690|是|

每種政策／題型只有一次，次序與上下文差異未充分平衡。成本按2026-09-06封存的相同公開價目換算，非帳單或訂閱扣款；Standard、無地區加價等假設與來源見 [價目及界線](../../measurement-index-83calls-20260906/index.json)。主線外部驗收與試驗編排成本另列，不藏進某組而漏掉另一組。

## 實際品質與摩擦

D1先加單數測試使其失敗，再改真實export。node --test只顯示檔案級測試摘要，模型另用node直接執行測試檔，取得3個具名case的真實失敗與PASS證據；最後清楚區分指定命令exit0與直接執行3tests。這次額外檢查有證據目的，不是盲目追求測試數。

D2保留原tests/test_projector.py逐byte不變，新增tests/test_projector_contract.py，19tests全部有capturedPASS。新增檔含24種排列、prefix後gap、巨大revision、額外欄位與nested input不變、全域重送／衝突、型別及必要欄位反例。最終19不是19個原檔測試，也不是oracle的54。主線完整讀取全部變更與新增檔、全部命令、file-change事件及最終交接。

兩題無觀察到模型委派、網路、設定或非授權寫入。D1無無谓Git檢查；D2同樣不依賴Git。結果都明說是自驗，不冒稱主手獨立驗收或已知費用。

## 對 skill 的決定

本例便宜worker確實單價低，但主手仍讀回實作、做獨立驗收，另有派工／回讀與可能返工成本。因此不能只按worker單價宣布節省。這支持Delegate現有「計入supervision與retry」規則，不支持強迫每個已清楚的小任務派工。

也不把直接Astra較快解讀為所有大型工作都應由Astra包辦：它沒有提供使用者重視的「實作與完成目標分離」，更未測跨回合注意力、長程整合或獨立觀點的價值。若使用者明確要責任分離，仍須遵守；本政策只是新合成副本的已授權實驗。

[原始用量核對](usage-review.json)、[D1產品真值](D1-oracle.json)、[D2產品真值](D2-oracle.json)、[原委派四組](../worker-fit-v1-review/lead-disposition.md)。
