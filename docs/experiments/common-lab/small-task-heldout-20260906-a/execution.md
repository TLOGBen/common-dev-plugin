# 小任務 A/B 執行交接

8／8 generation calls 完成，沒有 retry／模型 fallback；品質尚待主線按凍結條件逐案語意審閱，不在此依字數判定勝負。

- 案例／rubric：[cases.json](cases.json)，SHA256 `38a3a9c4c587a05a131f7703c37b5958101fa06d6c94b9a2bc1e2e7778e0fdf8`。
- 正式原始結果：[summary.json](../runs/astra-small-task-013/summary.json)；所有 prompt、stdout JSONL、stderr 與逐 call receipt 同目錄。
- 審閱入口：[manual-review.template.json](../runs/astra-small-task-013/manual-review.template.json)。沒有新增 judge calls。
- 事前封存：[plan-only manifest](../runs/astra-small-task-013-plan/manifest.json)；正式 [manifest](../runs/astra-small-task-013/manifest.json) 的案例與 17 個選定 resource hashes 與計畫封存完全相同。

## 實際時間及用量

模型 CLI 固定請求 `gpt-6-astra`／`high`；raw JSONL 未保證回顯 backend resolved model，因此不多作推論。

正式推論：2026-09-06 13:27:36.075 至 13:29:18.426（Asia/Taipei），並行上限 2，牆鐘 102.34 秒。各臂下表時間為四次 call 各自 elapsed 相加，不是兩個獨立順序 benchmark。

| 實際指標 | A：Common 1.35.2 | B：Common Lab 0.1.3 | 合計 |
|---|---:|---:|---:|
| 完成 calls | 4 | 4 | 8 |
| input tokens | 129342 | 126591 | 255933 |
| 其中 cached input | 103680 | 99840 | 203520 |
| uncached input | 25662 | 26751 | 52413 |
| output tokens | 1665 | 1483 | 3148 |
| total tokens（input + output） | 131007 | 128074 | 259081 |
| call elapsed 合計／秒 | 100.981 | 90.450 | 191.431 |

快取屬於 input 的子集，不再重複加入 total。B 的 total 較少，但 uncached input 較多；不能據此聲稱費用較低。實際金額、公開價估算、本 author 代理自身總 token 均為 `null`（不可觀測）；沒有把文章字數或 skill 檔案大小當成實耗 token。

實際開始順序：define-goal A、better-prompts B、define-goal B、better-prompts A、wait-what A、grilling B、wait-what B、grilling A。逐筆微秒時間在 summary 中；各案例的配對 A/B 順序符合事前設計。

## 機器核對

2026-09-06T05:31:11.776274Z 唯讀核對通過：8 次皆 exit 0／completed、每次一個 usage event、沒有 malformed JSONL 或 model error、所有 fixture before/after hash 相同、8 份 prompt digest 均一致、指定模型與 effort 一致、case/resource 無漂移。正常執行只用了各 skill 讀取；沒有修改 source/exporter、既有輸出或 user/global home。

| 封存檔 | SHA256 |
|---|---|
| summary.json | `97133f70f045accd28403cb7f6260880bb789bb0478245ad9135b62126726e90` |
| manifest.json | `a36dcc31396e6f27479a2c6467a6ace1826fb399d3f60de2f136e9c71c6916fc` |
| frozen-resources.zip | `345d52b0871178dbd3a56e9dfa1d33b67962ea5110422822988c2df8ec89a8ac` |
| frozen-cases.json | `0e18e9816fc995c66ff9559aed1191e0b18fd0aeed12bfab2e3f4391f80063ed` |

## 留給語意審閱的一個具體差異

Grilling A 拿掉「在頁尾」，但保留「備註」名稱；B 的建議同時拿掉欄位名稱與位置。B 的改法可能把「自行找到一個已知欄位」擴成「先判斷需求該放哪個欄位」，是否偏離原測量構念應獨立判斷，不能只因文字更流暢就算改善。兩者都指出位置提示污染 findability 證據；此段是待審差異，沒有另增測項或改 rubric。

Wait-what B 仍明確停下 underlying task；那是解釋期間的控制權交回，不能因有「等你指示」就直接算多餘停頓。A 的完整階梯與結尾選段追問是否增加認知負擔，要依實際取答難度評估，不按五個標題本身扣分。

## 結論範圍

執行完成程度是 8／8 next-reply 樣本與證據封存完成；產品任務完成程度、真人理解率與一週實戰成效均未測。共同 read-only wrapper 禁止真實副作用，因此這輪不是獨立授權邊界驗證，也不是免除後續實戰觀察的依據。
