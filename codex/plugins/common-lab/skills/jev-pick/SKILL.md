---
name: jev-pick
description: Pick one option from a known list with TypeSafe Jev (Choice), with a probability for every option. Use it on your own whenever you must choose among enumerable options for a piece of text — which page element to click, which skill or tool fits a request, which category, team, or failure type something belongs to — especially when the list is long enough that reading it all would waste context; and when building routers or classifiers in code. Also triggers on 分類, 路由, 選一個, 挑元素, 該交給誰, route this, classify into, which of these.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# Jev Pick

Hand Jev the real list of options plus the text to decide on, and get back one choice with a probability per option (max 255 options). Default user-facing output to Traditional Chinese.

Always add a `none` option; when Jev picks `none` or confidence is below ~50%, fall back to deciding yourself. The pick is a candidate, not evidence — act on it and check the result. $jev-browser (`jev-pick.mjs`) is a worked example that picks a page element.

```bash
curl -s https://api.typesafe.ai/v1/systemone -H "Authorization: Bearer $TYPESAFE_API_KEY" -H 'Content-Type: application/json' -d '{
  "model": "jev-latest", "state": "<the text to decide on>",
  "questions": {"target": {"type": "choice", "instructions": "Which element should be used to submit the search?",
    "criteria": {"e11": "[11] button Search", "e10": "[10] button Clear", "none": "None of these"}}}}'
```

The reply's `answers.target` holds `choice`, `confidence`, and `probabilities`. Skip silently when `TYPESAFE_API_KEY` is unset ($init-jev sets it up), and never send client or confidential content unless the user has said TypeSafe is allowed — the text leaves the machine.
