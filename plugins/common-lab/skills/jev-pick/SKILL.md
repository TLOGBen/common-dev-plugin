---
name: jev-pick
description: Pick one option from a known list with TypeSafe Jev (Choice), with a probability for every option. Use it on your own whenever you must choose among enumerable options for a piece of text — which page element to click, which skill or tool fits a request, which category, team, or failure type something belongs to — especially when the list is long enough that reading it all would waste context; and when building routers or classifiers in code. Also holds the fixed before-stopping check — run it whenever you are about to stop or end a turn with work possibly unfinished. Also triggers on 分類, 路由, 選一個, 挑元素, 該交給誰, route this, classify into, which of these.
---

# Jev Pick

Hand Jev the real list of options plus the text to decide on, and get back one choice with a probability per option (max 255 options). Default user-facing output to Traditional Chinese.

Always add a `none` option; when Jev picks `none` or confidence is below ~50%, fall back to deciding yourself. The pick is a candidate, not evidence — act on it and check the result. /common-lab:jev-browser (`jev-pick.mjs`) is a worked example that picks a page element.

```bash
curl -s https://api.typesafe.ai/v1/systemone -H "Authorization: Bearer $TYPESAFE_API_KEY" -H 'Content-Type: application/json' -d '{
  "model": "jev-latest", "state": "<the text to decide on>",
  "questions": {"target": {"type": "choice", "instructions": "Which element should be used to submit the search?",
    "criteria": {"e11": "[11] button Search", "e10": "[10] button Clear", "none": "None of these"}}}}'
```

The reply's `answers.target` holds `choice`, `confidence`, and `probabilities`. Skip silently when `TYPESAFE_API_KEY` is unset (/common-lab:init-jev sets it up).

## Before stopping a turn

When you use this check, ask this fixed question with a state of facts only — the goal as the user stated it, what was done with its evidence, which approaches were already tried and how each failed, what is unfinished, and why you want to stop. Listing the failed approaches matters: without them a stop after one dead end reads as blocked, when another route was still open. Keep the options as written; changing them per call lets the wish to stop steer the answer.

```json
{"next": {"type": "choice", "instructions": "Given the goal, the work done, the unfinished items, and the reason for stopping, what should the agent do next?",
  "criteria": {"stop_done": "Goal met and verified; stop and report",
               "continue_check_evidence": "An open point can be answered from existing files, logs, or earlier results; check it and continue",
               "continue_next_item": "Unfinished items remain that need no user input; continue",
               "continue_change_approach": "The planned next step repeats an approach that already failed with no new information; continue with a different approach",
               "ask_user": "A decision only the user can make (preference, authorization, irreversible action) blocks progress",
               "stop_blocked": "Blocked by something outside the agent's reach; stop and explain"}}}
```

Follow a confident answer; below ~50% use your own judgment and say the check was inconclusive. It never overrides the user: if they told you to stop or to ask, do that, and a preference, authorization, or irreversible choice still goes to them whatever Jev says.
