---
title: 把成果交回給人
kicker: SKILL LAB · 中途試呈現
author: Codex
template: kami/long-form
---

# 小修正已完成，還沒證明省成本

這次小型修正中，Astra 在兩組都選 Luna 實作，收回後自行驗收，沒有返工。加入 Delegate 的一組多用 9,283 tokens、約 12.36 秒，這一對樣本未顯示成本下降。兩組都修好單數標籤並保留原有測試；較複雜的任務仍在測試，費用帳單與真人閱讀結果尚未取得。

| 本次實際執行 | 無額外 skill | Lab Delegate 0.1.8 |
|---|---:|---:|
| 主手／實作 | Astra／Luna high | Astra／Luna high |
| 完整 CLI tokens | 181,177 | 190,460 |
| 經過時間 | 87.190 秒 | 99.551 秒 |
| 外部功能驗收 | 4 組輸出正確 | 4 組輸出正確 |
| 主手收回驗收 | 已完成 | 已完成 |
| 返工 | 無 | 無 |

## 這兩組如何把結果送回人手上

```diagram
{
  "kind": "graph",
  "nodes": [
    {
      "id": "request",
      "label": "使用者定成果與邊界"
    },
    {
      "id": "lead",
      "label": "Astra 判斷並派工"
    },
    {
      "id": "worker",
      "label": "Luna 修改與測試"
    },
    {
      "id": "accept",
      "label": "Astra 回讀並驗收"
    },
    {
      "id": "human",
      "label": "使用者拿到成果與限制"
    }
  ],
  "edges": [
    {
      "from": "request",
      "to": "lead"
    },
    {
      "from": "lead",
      "to": "worker"
    },
    {
      "from": "worker",
      "to": "accept"
    },
    {
      "from": "accept",
      "to": "human"
    }
  ]
}
```

## 人還不能據此決定什麼

:::warn
這只有 1 對小型任務；不是模型能力排名，也不是你的下一週實戰。外部紀錄有漏輸出的情形，缺紀錄不等於模型沒看到；實際帳單仍未知。
:::

技能載入、命令、程式、實際 export、角色寫入範圍與各次用量已分開核對。完整來源放在同一實驗工作區的 worker-fit-v1-review／small-pair-lead-review.md 與 usage-small-pair.json。
