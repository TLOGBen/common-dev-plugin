# Grilling 0.1.5：八次 source-level 回歸交接

8／8 generation calls 完成。候選在原例兩次回答都保留已知欄位名稱、移除污染證據的位置提示，未重開已陳述目標；本輪是有限的正向證據，不是通用改善或統計證明。尚未導出，正式凍結 rubric 評分由主線處理。

- [結果與原始輸出](../runs/astra-grilling-015/summary.json)；同目錄有 prompt、stdout JSONL、stderr、每 call receipt。
- [事前凍結案例](cases.json) 與 [source receipt](source-receipt.json)。第五條判準在結果前加入；原三案輸入、前四條 criteria、guards 完全未變。
- [語意審閱模板](../runs/astra-grilling-015/manual-review.template.json)。不改 0.1.3／0.1.4 既有分數；0.1.4 失敗 source 保存在 rejected-014。

## 具體可觀察差異

| 配對 | A：0.1.3 | B：0.1.5 |
|---|---|---|
| 已知欄位 pair-1 | 保留「備註」名稱，移除位置提示，分開自行／協助完成 | 同樣保留名稱、移除位置提示，另避免受測者互看 |
| 已知欄位 pair-2 | 重問有／無提示目標，又建議拿掉欄位名称，混入意圖映射 | 保留名稱、移除位置提示；另問同事對表單的熟悉程度，沒有重開目標 |
| Runbook | 保留文件、移除逐步口頭帶做，問協助算不算成功 | 同樣保留文件與操作目標，區分協助下完成 |
| 已定位 bug | 保留定位線索、驗原失敗例及既有例，問單例／完整函式範圍 | 同樣保留線索、要求原例失敗→通過與既有例不退步，明示兩例不足以證明全函式正確 |

Runbook 的協助判定、bug 的輸入／驗收範圍與受測者熟悉程度，並非已明說的目標本身；不能僅因是問句而依第五條扣分。原例 pair-2 的 A 則明確重問「你真正想驗證的是『沒有提示也找得到』，還是『知道位置後能順利填寫』」，接著把欄位名稱也移除。B 兩次保留「請找到表單的『備註』欄」，並修正的是位置提示，沒有保護錯的方法。

這輪 A 一次對、一次偏移，說明單次回答不穩定；B 的 2／2 原例只能支持這兩個樣本，不足以推估真實故障率。其他兩案兩邊都維持原主張，沒有由此硬判新版全面勝出。

## 真實時間與用量

CLI 請求固定 gpt-6-astra／high。A/B 都讀 Claude source 根檔，不是 generated-package 驗證；Codex plugin_versions=null，由 source receipt 的 0.1.3／0.1.5 manifest 歸屬補足。每次 ephemeral context，兩組原例各自 fixture，臂順序相反；沒有 judge、重試或 fallback。

推論時間：2026-09-06 13:53:21.675–13:55:28.489（Asia/Taipei），並行上限 2，牆鐘 126.807 秒。

| 指標 | A | B | 合計 |
|---|---:|---:|---:|
| 完成 calls | 4 | 4 | 8 |
| input tokens | 126620 | 126888 | 253508 |
| 其中 cached input | 96128 | 108032 | 204160 |
| uncached input | 30492 | 18856 | 49348 |
| output tokens | 2299 | 2211 | 4510 |
| total tokens | 128919 | 129099 | 258018 |
| 各 call elapsed 合計／秒 | 128.280 | 120.299 | 248.579 |

cached input 為 input 子集，不重複加到 total。B total 反而多 180 tokens；快取命中不同，不能由 uncached 差異宣稱技能帶來節費。美元、本 author 自身總用量皆 null，不估算。raw JSONL 未保證回顯 backend resolved model，僅報確實請求的 model／effort。

## 機器驗證與封存

2026-09-06T05:56:26.797601+00:00 核對通過：8 calls 皆 exit 0／completed、usage 可觀察、無 malformed JSONL／model error；全部 fixtures 不變、prompt digests 相同、plan／正式案例及 resource hashes 一致。live source 與所有 snapshots 符合推論前 receipt；0.1.3 frozen export、0.1.4 summary 及舊三案判準不變。Skill Creator quick_validate 通過，但不代替行為驗收。

- 0.1.5 完整 source SHA256：`8a5ab67d3a4fa87bf3f1742a9cd993ceab1b45809aa3250597f8e6f806222fcf`
- 0.1.5 grilling root SHA256：`24d5178d69cf00bcca128230e847e921247cca00976768dd7d238d0a285fd3e2`
- cases SHA256：`f840c85b6eaa7d820147e81f05ea27bc434ef095cbb95a6d4185ff399a73d5f7`
- summary SHA256：`8b98ddf04635934ad57391e66ae8d7fe17b456026c864b9bedc0bc9df6c64979`
- manifest SHA256：`eb8c3055fe2ed611aa5542bcfd4e321cf62e67668963e2481cd01f9c2a579f1d`
- frozen-resources.zip SHA256：`26f2d91c19a482ce88d95c5bf418c140eded0db6c21e9513fb9b4afec7e40018`
- frozen-cases.json SHA256：`9236bdc07126619c496ec3a9eb290fa403e3c5f1f4e3cd92d864a4c83ed08fab`

其他 Common source 未變的證據：在記憶體中的雜湊清單虛擬回填封存 grilling root／manifest，整包 hash 分別精確重建 0.1.4 的 375236d491b6a78ebfdff009860f3565d0e0bf99e10fd770e742b9364098f9ea 和 0.1.3 的 cb290dad5817816feacbfa8197db1a9303b04c745e191c9c8b99e52990a5d1f5。沒有實際回退 source；source receipt 有完整差異。

## 交回邊界

只修改 lab-grilling 原則段落及 plugin version 0.1.4→0.1.5；沒有新增框架、別的技能或特定表單規則。候選及全部舊證據保留，主線決定是否導出；本次不導出、不安裝、不改 exporter／Estimate／docs index、不 commit/push。尚未測真人理解率、產品執行或一週實戰。
