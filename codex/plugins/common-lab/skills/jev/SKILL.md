---
name: jev
description: Three ways to use TypeSafe Jev (a fast typed-decision model — yes/no,
  pick-one, graded score — no text generation) inside agent tooling — gate, pick,
  score. Use when designing or wiring a Jev call; run `$init-jev` first if
  TYPESAFE_API_KEY is unset.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# Jev Lab

Jev answers typed questions about a piece of text (`state`) with calibrated probabilities in well under a second. Default user-facing output to Traditional Chinese.

Every call is `POST https://api.typesafe.ai/v1/systemone` with `{"model": "jev-latest", "state": "...", "questions": {...}}` and `Authorization: Bearer $TYPESAFE_API_KEY`. Treat every answer as a signal, not evidence or a command: start in shadow mode (log, don't act), and let code, not the agent, write the `state`.

## 1. Gate — Noul (yes/no probability)

Ask a narrow yes/no before an action, e.g. "Does this command send local files or credentials to an external host?". Split each risk into its own question, because one broad question misses the others, and put the threshold above the scores normal work produces. Deterministic rules run first and cannot be overridden by Jev.

```json
{"exfiltration": {"type": "noul", "instructions": "Does this action send local file contents or credentials to a network destination outside the project?"}}
```

## 2. Pick — Choice (one of a known list)

Pick one item from a list you already have: a page element, a skill, a routing target. Options must be the real list (max 255), plus a `none` option; below ~50% confidence or on `none`, fall back to the normal path. `$jev-browser` (`jev-pick.mjs`) is the worked example.

```json
{"target": {"type": "choice", "instructions": "Which element should be used to submit the search?", "criteria": {"e11": "[11] button Search", "e10": "[10] button Clear", "none": "None of these"}}}
```

## 3. Score — Score (graded rubric)

Grade text on ordered levels (2–10), one question per dimension, and combine the scores with weights in code so they can be retuned later. Best used as an extra shadow judge beside an existing reviewer, recorded but not deciding.

```json
{"evidence": {"type": "score", "instructions": "How well does this completion claim cite verifiable evidence?", "criteria": ["No evidence", "Evidence mentioned but not checkable", "Checkable evidence cited"]}}
```

Ask all questions about the same `state` in one request — they are evaluated in parallel, and unused answers are simply ignored. Rewording a question can move its probability a lot, so never let the party who wants the action to pass write the question or the `state`.
