---
name: suggest-jev
description: Router that lets TypeSafe Jev suggest how to handle a request before any work starts — which skill to load first, which others will be needed, the workflow, how to prove it is done, whether to dispatch subagents (how many, which model family and effort), the difficulty, and the impact — then hands stopping to the before-stopping check in jev-pick and asking to is-truely-need-to-ask-user-jev, with a plain-language check on any question that must go to the user. Load this first, before doing anything on a new request; use it again when a piece of work ends, before pausing or stopping, and before asking the user a question.
---

# Suggest Jev

Use Jev to strengthen anywhere that only needs a judgment — yes/no, choose one, score.

This skill is a router: at three moments it asks Jev for a suggestion and turns the answer into the next step. Jev suggests; you decide. The user's own instructions always win — a skill they named, a budget or subagent limit they set, a way of working they asked for. Default user-facing output to Traditional Chinese.

Skip routing for a one-line reply, a greeting, or a follow-up that continues work already routed. Skip every call silently when `TYPESAFE_API_KEY` is unset (init-jev sets it up) or the call fails.

Every call is `POST https://api.typesafe.ai/v1/systemone` with `{"model": "jev-latest", "state": "<facts>", "questions": {...}}` and `Authorization: Bearer $TYPESAFE_API_KEY`. Keep the questions as written; only fill in the placeholders.

## 1. Start: route the request (one request)

State: the user's request in their words, a few lines of context (what kind of project, what the user has constrained), and the skill catalog — every skill available in this session as `"<name>": "<first clause of its description>"`, plus `"none": "No skill; do it directly"` (at most 255 options).

```json
{"start_skill": {"type": "choice", "instructions": "Which skill should be loaded first to handle this request?", "criteria": {"<skill>": "<what it does>", "none": "No skill; do it directly"}},
 "workflow": {"type": "choice", "instructions": "What overall workflow fits this request?", "criteria": {
   "direct": "Do it now in one or two steps", "investigate_then_fix": "Investigate to find the cause, then change",
   "plan_then_build": "Agree on a plan, then build and verify", "research_then_report": "Gather sources, then write findings",
   "iterate": "Build, test, fix in a loop until it passes", "ask_first": "A user decision is needed before any work"}},
 "completion": {"type": "choice", "instructions": "What is the best way to show this request is done?", "criteria": {
   "tests_pass": "A named test or command passes", "artifact_exists": "A file or artifact exists with the expected content",
   "independent_review": "An independent reviewer checks the result", "user_confirms": "The user looks at it and confirms",
   "evidence_report": "A report citing sources or evidence"}},
 "subagents": {"type": "score", "instructions": "How many subagents should this request use?", "criteria": ["None", "One", "Two or three", "Four or more"]},
 "family": {"type": "choice", "instructions": "If work is handed to a subagent, which model family fits its shape?", "criteria": {
   "gpt": "Bounded execution from a stated goal, autonomous exploration, deep single-problem digging",
   "claude": "A long procedure to follow exactly, structured or templated output, checklist compliance",
   "either": "Mechanical scanning or single-shot verification — take the cheapest tier"}},
 "effort": {"type": "choice", "instructions": "What is the lowest reasoning effort likely to succeed?", "criteria": {
   "low": "Mechanical or well-specified work", "medium": "Ordinary work with some judgment", "high": "Hard single problems or subtle multi-file reasoning"}},
 "difficulty": {"type": "score", "instructions": "How difficult is this request?", "criteria": ["Trivial", "Routine", "Needs investigation or judgment", "Hard, uncertain, or novel"]},
 "impact": {"type": "score", "instructions": "How wide is the impact of the changes this request makes?", "criteria": ["Read-only", "One file or artifact", "Several files in one module", "Cross-module, shared state, or external side effects"]}}
```

Turn the answers into a route:

- **Skills.** Load `start_skill` when its confidence is about 0.6 or higher; below that, pick yourself from the top two. Any other skill with probability above ~0.15 is a candidate to keep in view — load it when its step arrives, not all at once.
- **Workflow and completion.** Follow `workflow`, and decide now how you will prove it is done using `completion`. `ask_first` goes through moment 3 before any work.
- **Subagents.** Default to none. Dispatch only when `subagents` is about 1.5 or higher with confidence of at least ~0.6 and the work splits into independent slices; round down, and stay within any limit the user set. Hand the dispatch to `/common:delegate`, using `family` and `effort` as its starting point; `xhigh` and above need the user's explicit request.
- **Difficulty and impact.** At level 3 on either, or 2 on both, consider pinning the goal or acceptance first (define-goal, contract) or deliberating (think) before building; at level 0–1 on both, just do it.

Tell the user the route in one line before starting, for example: 「路由：先用 hunt，先排查再修，以測試通過為完成標準，不派 subagent。」 Then do the work.

## 2. End, pause, or stop

When a piece of work ends, or you are about to pause, stop, or end your turn, run the before-stopping check in jev-pick and follow its `next` answer: `continue_check_evidence` or `continue_next_item` → keep working; `ask_user` → go through moment 3; `stop_done` or `stop_blocked` → stop and report.

## 3. Before asking the user

Run is-truely-need-to-ask-user-jev first. If the question can be answered without the user, find the answer and continue. If it truly needs the user, check the draft question — state: the context the user already has and the exact draft:

```json
{"plain": {"type": "noul", "instructions": "Is this question in plain language the user can follow without technical background?"},
 "actionable": {"type": "noul", "instructions": "Does this question make clear what the user needs to decide or do?"},
 "main_blocker": {"type": "noul", "instructions": "Does this question address the main thing blocking progress, rather than a side detail?"}}
```

If any answer is below ~0.5, rewrite: plain words first, say what you need from them and why, ask only about the blocker, and drop side questions. Check once more, then ask whichever version scored higher.

## Limits

Routing is a suggestion from a model that sees only the state you send, not the repository. It was tested on a handful of requests, not calibrated. "Load this first" depends on the model choosing this skill; a hook would be needed to guarantee it runs on every request.

Tested (one run each): "the checkout test keeps failing on CI, find out why" routed to hunt 0.92, investigate_then_fix 0.92, tests_pass 0.71, difficulty 1.93; "save this page for offline reading" routed to read 0.99, direct 0.89, artifact_exists 0.71. Both scored subagents near 1 (1.47, 0.83), which is why the dispatch rule above is conservative. For a question about a missing production database URL, a jargon-heavy draft that also tacked on a log-level side question scored plain 0.06; a plain rewrite scored 0.62 with main_blocker rising from 0.75 to 0.91 — `actionable` stayed near 0.8 for both, so lean on `plain` and `main_blocker`.
