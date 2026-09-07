# Grilling 0.1.4 候選：六次 source-level 配對交接

6／6 generation calls 完成；沒有新增 judge、retry 或模型 fallback。候選尚未導出，這批结果不能當作發布通過。

- [完整結果](../runs/astra-grilling-014/summary.json) 與同目錄原始 prompt／stdout JSONL／stderr／逐 call receipt。
- [新凍結案例與 rubric](cases.json)，SHA256 `4cf05cff56bf9e467929719632d8362e9bf50f0ca0d5d2c48ed47db36f85a6d7`。
- [source 版本與差異 receipt](source-receipt.json)。A/B 都是 Claude source SKILL；不是 generated Codex package 測試，runner 的 plugin_versions 為 null 正確。
- [主線語意審閱模板](../runs/astra-grilling-014/manual-review.template.json) 尚待填写；本交接不先替主線定分。

## 可觀察的差異

| 場景 | A：0.1.3 source | B：0.1.4 source | 待審意義 |
|---|---|---|---|
| 已知「備註」欄定位 | 再次建議同時拿掉位置與欄位名稱 | 沒改成意圖映射，但把位置提示視作可能應保留的條件，要求重選有／無提示目標 | 候選可能保護了被挑戰的方法，沒有忠實針對已陳述的「自行找到」主張改進 |
| 依書面 runbook 做 mock 恢復 | 保留文件、拿掉逐步口頭帶做，辨識介入紀錄 | 同樣保留文件，清楚區分文件操作與口頭指導成功 | 此樣本未觀察到關鍵退步，也沒證明新增原則必要 |
| 已定位 bug 修復 | 保留定位／重現線索，驗原失敗例及既有例，另提未提供的正整數例 | 保留線索，驗原失敗例與既有例，另問有效輸入範圍 | 兩邊都保留修復而非找 bug 的測量主張；補充案例與 domain 問題是否增加負擔需按原範圍判讀 |

原例 B 的關鍵句是：「若實際要驗證的就是『收到頁尾提示後，能找到並填寫』，原流程合理。拿掉提示則是在測另一個問題，不能直接當成原試驗的必要修正。」這把使用者欲檢验的結果與尚待批判的手段再次混在一起。候選沒有重現同一种偷換，卻可能製造不必要的目標重問，不能算已修復。

這是 supplemental quality observation，不回改上一輪 0.1.3 的任何分數。上一輪凍結第 3 条是 OR；B 已正確指出盲點，原判準仍成立。本輪只用事前新增的 claim-preservation rubric 評估此新問題。

## 真實時間／token

固定 CLI 請求 `gpt-6-astra`／`high`，source 根檔全讀，三個單回合案例，各臂一次，並行上限 2。Backend resolved model 未保證在 JSONL 回顯；不假稱取得額外確認。

推論時間：2026-09-06 13:41:44.926–13:43:47.674（Asia/Taipei），牆鐘 122.744 秒。

| 指標 | A | B | 合計 |
|---|---:|---:|---:|
| 完成 calls | 3 | 3 | 6 |
| input tokens | 95007 | 95120 | 190127 |
| 其中 cached input | 81024 | 81024 | 162048 |
| uncached input | 13983 | 14096 | 28079 |
| output tokens | 1834 | 1700 | 3534 |
| total tokens | 96841 | 96820 | 193661 |
| 逐 call elapsed 合計／秒 | 96.276 | 92.755 | 189.031 |

cached input 是 input 子集，不重複相加。兩臂 total 差 21 tokens 並不支持有意義的節費主張。实际金額與本 author 代理總用量為 `null`；沒有估算美元或拿字數代替 tokens。

## 機器驗證與精確來源

2026-09-06T05:44:30.132414Z 唯讀驗證全部通過：六次 exit 0／completed、usage 都可觀察、無 malformed JSONL／model errors；fixtures 前後相同；prompt hash 一致；plan／正式 case 與 resource hash 一致；live source 與 A/B snapshots 仍符合事前 source receipt；0.1.3 generated export 不變。Skill Creator quick_validate 亦通過，但它不是行為品質證明。

- 候選完整 source：`375236d491b6a78ebfdff009860f3565d0e0bf99e10fd770e742b9364098f9ea`
- 候選 lab-grilling root：`3da0432fb25127464f74631beb374c145b89410422a1f441fe18662b7b81a86f`
- 0.1.3 source 根檔／manifest 回填重建整包：`cb290dad5817816feacbfa8197db1a9303b04c745e191c9c8b99e52990a5d1f5`，符合原凍結值，證明 Common 其餘 source 未變。
- 未變的 0.1.3 generated export：`705e53c49e4e8f132ae8e017a51dab6b21cd4a7e78c2b806864bd009e33d853c`
- 本輪 summary：`841b0be1e2f2701fb057e0c33261989a604424aa3047ffe76963302f4f543404`
- 本輪 manifest：`df720890b991d86480ce68b8e381523d2ff0e2b84841c8440ec63cd65adb3b22`
- 本輪 frozen-resources.zip：`8d1d07417ec6d6c6c20e041ab9dff2f55ee2b8285e2b620c6a812885cc45f8a2`
- 本輪 frozen-cases.json：`b6bb419a394b2bd943b8aa640bcb62cc917fbc5369cdd21e344df8f401577eba`

## 處置

保留候選、失敗觀察與全部封存；不再追加 calls 或修改規則，不導出、不安裝、不碰其他技能／Estimate／exporter。主線應先判斷是否要進一步區分「人的明確主張」與「待被質疑的方法」。本次只是 source-level 單樣本配對，不是真人測試、統計證明或產品實作驗收。
