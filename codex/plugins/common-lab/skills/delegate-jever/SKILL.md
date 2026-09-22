---
name: delegate-jever
description: Lab overlay on common:delegate that adds TypeSafe Jev readings — scoring the task-size dimensions that pick the lightweight, full, or supervised path; family fit and starting effort; a drift/progress reading at each supervised patrol; and failure classification before acting on a failed run. Use when the user asks for delegate-jever or a Jev-assisted delegation; use delegate for ordinary delegation.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# Delegate (Jev overlay)

Use Jev to strengthen anywhere that only needs a judgment — yes/no, choose one, score.

Load and run `$delegate` exactly as written; its worth-it test, live model catalog, briefing contract, permissions, ledger, and acceptance are unchanged. This overlay adds Jev readings at four points as a second opinion for the lead. The lead still decides, and the delegate's hard rules still bind: `xhigh` / `max` / `ultra` need an explicit user request, a model name comes from the live catalog, and supervision never expands authorization. Default user-facing output to Traditional Chinese.

## Calling Jev

`POST https://api.typesafe.ai/v1/systemone` with `{"model": "jev-latest", "state": "<facts>", "questions": {...}}` and `Authorization: Bearer $TYPESAFE_API_KEY`. If the key is unset (`$init-jev`) or the call fails, skip the reading and delegate as written. Task text, ledgers, and diffs leave the machine for TypeSafe in the U.S.; skip the readings for client or confidential work unless the user has said TypeSafe is allowed. Keep the questions as written — the lead wants the task to fit a cheap path, and rewording moves the probabilities.

## 1. Task size → path (before dispatch)

State: the task as it will be briefed, the files or modules in scope, and the expected validation.

```json
{"stages": {"type": "score", "instructions": "How many execution stages does this task need?", "criteria": ["Single verification or artifact", "2-3 stages", "4+ stages or iterative repair"]},
 "write_surface": {"type": "score", "instructions": "How large is the write surface?", "criteria": ["Read-only or one non-code artifact", "1-3 files in one module", "4+ files, cross-module or cross-repo, or a shared worktree"]},
 "duration": {"type": "score", "instructions": "How long will execution and validation take?", "criteria": ["Under 2 minutes", "About 2-10 minutes", "Over 10 minutes or highly uncertain"]},
 "drift_cost": {"type": "score", "instructions": "How costly is it if the result drifts from the goal?", "criteria": ["Easy rerun, directly comparable result", "Reversible local code change", "Workflow, transaction, schema, public contract, or external side effect"]}}
```

Round each `score` and sum them against the delegate's bands (0–2 lightweight, 3–5 full, 6–8 supervised). A dimension with low confidence counts as genuinely uncertain — take the higher value, as the delegate already requires. Compare with your own scoring; where they differ by a band, look again at that dimension before choosing, and keep the hard overrides. Pre-task sizing is the least proven of these readings: record Jev's total next to the path you took and how the run actually went.

Tested (one run each): "list every file mentioning CLAUDE_PLUGIN_ROOT and count per plugin" scored drift_cost 0.03 with write_surface split (confidence 0.0) — an honest "uncertain"; "migrate the orders table from integer cents to decimals across 3 services" scored ~2 on stages, write surface, and drift cost.

## 2. Family fit and starting effort (before dispatch)

Same state, one request:

```json
{"family": {"type": "choice", "instructions": "Which model family fits the shape of this work?",
  "criteria": {"gpt": "Bounded execution from a stated goal, autonomous multi-file exploration, deep single-problem digging",
               "claude": "A long multi-step procedure to follow exactly, structured or templated output, checklist compliance",
               "either": "Mechanical scanning, single-shot verification, grep-shaped inventory — take the cheapest tier"}},
 "effort": {"type": "choice", "instructions": "What is the lowest reasoning effort likely to succeed at this task?",
  "criteria": {"low": "Mechanical or well-specified work", "medium": "Ordinary implementation with some judgment", "high": "Hard single problems or subtle multi-file reasoning"}}}
```

Resolve the concrete model from the live catalog inside the chosen family, at the lowest viable tier. When the catalog lists several candidates in the family, you may ask one more Choice whose options are the catalog's own model IDs and descriptions, plus `none`. Escalate later only as the delegate says — one dimension at a time, after re-checking family fit.

## 3. Patrol reading (supervised path, each patrol)

Out-of-scope writes are a set comparison between the declared write set and `git status --porcelain` / `git diff --name-only`; do that in code, not with Jev. For the semantic part, state: the goal and acceptance, the ledger's latest entries, the previous patrol's summary, and `git diff --stat` plus the load-bearing hunks.

```json
{"drift": {"type": "noul", "instructions": "Has the work moved away from the stated goal or acceptance criteria?"},
 "repeat": {"type": "noul", "instructions": "Is the sidekick retrying on the same wrong assumption, even with different actions?"},
 "progress": {"type": "noul", "instructions": "Since the previous patrol, is there new progress toward the goal?"}}
```

These readings do not trigger intervention by themselves. They tell you where to look: a high `drift` or `repeat`, or low `progress` across two patrols with corroborating stale signals, meets the delegate's own conditions for a checkpoint. Keep the delegate's stall rule — never restart from one empty poll.

## 4. Failure classification (after a failed run)

State: the failure output, stderr excerpt, and the ledger's last entries.

```json
{"failure": {"type": "choice", "instructions": "Which class does this failure belong to?",
  "criteria": {"environment": "Auth failure, sandbox or network restriction, unsupported model parameter",
               "strategy_unavailable": "A specific strategy or tool was unavailable and the sidekick gave up instead of rerouting",
               "family_mismatch": "Output drifted off the goal, ignored parts of the briefing, or came back confidently wrong in shape",
               "unreachable": "The task was unreachable or acceptance was not met"}}}
```

Handle it per the delegate's failure table. `environment` never counts as rework and never escalates the model; `family_mismatch` re-picks the family instead of raising the tier.
