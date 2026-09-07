# 主線驗收：Common Lab 0.1.5

判定：接受進入 opt-in 實驗套件。這是主線代理完整閱讀八則 final、技能與凍結案例後提供的判定，記錄者未另開 judge calls，也不冒稱真人測試。

| 凍結判準結果 | A：0.1.3 | B：0.1.5 |
|---|---:|---:|
| 四筆回答、每筆五項，最高 40 分 | 37／40 | 40／40 |
| construct guard 違反 | 1 | 0 |

B 四筆的五項均滿足；A 除 known-field-pair-2 外均滿足。A 該筆第 2 項不滿足，因為拿掉欄位名稱，偷加意圖到欄位的映射；同時違反 construct guard。第 5 項僅 partial：它重開已明說的目標，但已給出可用 critique，不能宣稱真的強制等待或多了一回合。

Runbook 的協助判定、有效輸入 domain、驗收範圍等真正未定問題仍屬合法問題，不因是問句就列為摩擦失敗。原四項與新第五項已在本輪結果前凍結；舊 0.1.3／0.1.4 分數不改。

- [逐案分數／guards 與來源](lead-acceptance.json)
- [八則完整結果](../runs/astra-grilling-015/summary.json)
- [事前凍結案例](cases.json)
- 接受的 source SHA256：`8a5ab67d3a4fa87bf3f1742a9cd993ceab1b45809aa3250597f8e6f806222fcf`

接受只代表這輪小樣本 regression 足以進實驗套件，不代表人類可用性、一般模型優劣或統計顯著。後續僅授權導出到全新 experiments/common-lab-v0.1.5，保留 staging／receipt；不覆寫 frozen export、不安裝、不改其他套件。
