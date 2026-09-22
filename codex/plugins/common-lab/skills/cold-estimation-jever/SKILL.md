---
name: cold-estimation-jever
description: analysis-estimation:cold-estimation 的 Lab 疊加版：在工項清單與定價之間加上 TypeSafe Jev 的判斷——每個工項的困難度分數（決定哪些要先做窄技術覆核）、必要性檢查（抓範圍擴張）、定價後每列人天的依據可信度（決定要向定價者追問哪幾列）。使用者要求 cold-estimation-jever 或「用 Jev 輔助初估」時使用；一般初估用 cold-estimation。
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# Cold Estimation（Jev 疊加版）

Use Jev to strengthen anywhere that only needs a judgment — yes/no, choose one, score.

照原樣載入並執行 `$cold-estimation`：開場路線確認、查證、合併、獨立定價 subagent、交付格式全部不變。本疊加版只在三個判斷點加上 Jev，作為主 Agent 的第二意見。Jev 的分數**只決定「該先查哪裡、該追問哪一列」，不直接改人天**：原技能禁止用泛用緩衝代替未知，所以困難度分數絕不能變成加乘係數，依據可信度低也不能自行重估另一套數字。以繁體中文交付。

## 呼叫方式

`POST https://api.typesafe.ai/v1/systemone`，body 為 `{"model": "jev-latest", "state": "<事實>", "questions": {...}}`，標頭 `Authorization: Bearer $TYPESAFE_API_KEY`。沒有金鑰（用 `$init-jev` 設定）或呼叫失敗時略過，照原技能估算。

題目照下方原文使用，不要每次改寫：估算的人本身有立場，措辭一變機率就會跟著變。

## 1. 困難度（工項清單形成後、定價前）

state：單一工項的 ID、選定改法、具體施工與驗證操作、代表證據。

```json
{"difficulty": {"type": "score", "instructions": "How technically difficult is this work item?",
  "criteria": ["Routine, repeated operation", "Ordinary change needing some judgment",
               "Needs investigation or has an unconfirmed technical assumption",
               "High uncertainty: an unverified compatibility, unknown behavior, or new technology"]}}
```

`score` ≥ 2 且依據只有預設版本、摘要或間接推論的工項，是原技能「先依 pm-delivery.md 做一次窄技術覆核」的優先候選；其餘照原流程。困難度只用來排查證的先後，不寫進人天、不加緩衝。

## 2. 必要性（工項清單形成後、定價前）

state：單一工項，加上已確認的範圍與甲方責任摘要。

```json
{"required": {"type": "noul", "instructions": "Is this work item required to preserve an existing capability or deliver the confirmed scope?"}}
```

低於約 0.3 的工項，回頭檢查是否屬於原技能明禁的「自行加入業務擴充或另立全面測試專案」，或是甲方已承擔的責任；確認後移除或改列待決，不要靜默保留。

## 3. 人天依據可信度（定價 subagent 回傳後）

state：定價回傳的單一列——ID、操作、計次、原始 E／V 與算式。

```json
{"basis": {"type": "score", "instructions": "How well do the stated operations, counts, and responsibilities support this person-day number?",
  "criteria": ["No operational basis; the number is a guess",
               "Some basis, but a count or operation that changes the magnitude is missing",
               "Concrete operations and counts that trace to the number"]}}
```

`score` < 1 的列，照原技能的做法「向定價者指出具體列並補事實」，一次列出這些列的 ID 與缺的操作或次數；仍無法定價就明列待估。這個分數是給主 Agent 追問用的，不放進交付表、不改交付格式。

實測（各一次）：「修改 12 支 DAO 查詢語法、每支 0.25 人天加 0.1 人天驗證、合計 4.2 人天」的依據可信度 1.89、困難度 0.31；「框架升版相關調整，預估 5 人天」的依據可信度 0.27、困難度 2.43。
