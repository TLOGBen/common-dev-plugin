---
name: jev-score
description: Grade text on an ordered rubric with TypeSafe Jev (Score), with a probability for each level. Use it on your own whenever you need a quick independent rating of text on fixed levels — how well a completion claim cites evidence, how severe a finding is, how clear an instruction or question is — as a second opinion beside your own judgment; and when building composite scoring or a shadow judge next to an LLM reviewer in code. Also triggers on 評分, 打分, 分級, rubric, 嚴重度, 影子評審, score this, rate on a scale.
---

# Jev Score

Describe 2–10 ordered levels and let Jev return the level with a probability for each one. Default user-facing output to Traditional Chinese.

Use one question per dimension and combine scores with weights in code, not in the question. Treat the score as a second opinion: when it disagrees with your own judgment, look again rather than deferring to it, and never let it replace a required review.

```bash
curl -s https://api.typesafe.ai/v1/systemone -H "Authorization: Bearer $TYPESAFE_API_KEY" -H 'Content-Type: application/json' -d '{
  "model": "jev-latest", "state": "<the text to grade>",
  "questions": {"evidence": {"type": "score", "instructions": "How well does this completion claim cite verifiable evidence?",
    "criteria": ["No evidence", "Evidence mentioned but not checkable", "Checkable evidence cited"]}}}'
```

The reply's `answers.evidence` holds `score` (the expected level as a decimal, 0 = first level, e.g. `1.45`), `probabilities` per level index, `legend` mapping each index to its level text, and `confidence`; a low confidence with probability split across two levels means the text sits between them. Jev sees only the `state`, not files or context, so put everything the grade depends on into it. Skip silently when `TYPESAFE_API_KEY` is unset (/common-lab:init-jev sets it up).
