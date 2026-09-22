---
name: define-goal-jever
description: Lab variant of define-goal that adds TypeSafe Jev checks at its judgment points — a one-request quality check of the draft goal before create_goal, a pre-question check before asking the user, an active-goal comparison, and goal-type routing to the right quantification heuristic. Use when the user asks for $define-goal-jever or a Jev-checked goal; use $define-goal for ordinary goal setting.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# Define Goal (Jev)

Use Jev to strengthen anywhere that only needs a judgment — yes/no, choose one, score. This variant keeps define-goal's workflow and quality bar unchanged and adds Jev as a fast second opinion at four judgment points, marked **Jev** below. Jev answers are signals, not verdicts: the quality bar and the user's confirmation still decide.

## Output language

Keep these skill instructions in English. Default user-facing explanations, questions, and newly authored human-readable artifacts to Traditional Chinese. If the user explicitly requests another language, use it instead. Preserve code, identifiers, commands, quoted source text, and established project terminology.

## Overview

Shape the user's intent into an objective an agent can pursue honestly. Prefer measurable outcomes, explicit evidence, and bounded scope over activity descriptions.

This skill covers goal definition and goal-tool creation only. Do not create intermediate planning artifacts, durable snapshots, ledgers, decision logs, or resume files from this skill.

## Workflow

1. Confirm that goal definition is actually needed.
   - Use this skill when the user asks for `$define-goal-jever`, asks to create or set a goal, asks for the goal tool, or wants help turning an intention into a clear objective.
   - If the user only asks for ordinary implementation work, do the work directly instead of forcing goal creation.

2. Restate the likely goal in concrete terms.
   A usable goal names:
   - the specific outcome that will be true
   - the main artifact, system, repo, environment, or user-facing behavior involved
   - how completion will be verified
   - what is in scope
   - what is out of scope when ambiguity would matter
   - the stop condition for asking the user instead of grinding

3. Make it quantitative when the domain supports it.
   Prefer numbers that represent real success, not decorative precision:
   - pass/fail validators: exact tests, checks, CI jobs, evals, commands, or acceptance criteria
   - quality thresholds: latency, error rate, cost, accuracy, recall, precision, coverage, flake rate, bundle size, memory, uptime, completion rate, or manual review criteria
   - artifact constraints: file paths, affected modules, allowed commands, output formats, target environments, deadlines, or maximum blast radius
   - evidence counts: number of reproduced failures, successful reruns, reviewed examples, migrated records, addressed comments, or verified cases

   **Jev — goal type.** The `kind` question in the quality check below classifies the draft goal (bug, test, performance, quality, research, operations); use its answer to pick the matching Quantification Heuristic. Below ~60% confidence, pick by reading the goal yourself.

4. Repair weak goals before setting them.
   - Rewrite vague goals into measurable objectives when local context makes the rewrite safe.
   - Ask one concise clarification question when the missing detail changes the intended outcome or validation.
   - Reject pure activity goals such as "make progress," "keep investigating," "improve things," or "work on X" unless they are sharpened into a verifiable outcome.

   **Jev — ask or rewrite.** Before sending a clarification question, run the pre-question check from Jev Checks: if it is answerable from the repo, logs, or conversation and needs no user-only decision, look it up and rewrite instead of asking; if it is user-only, ask, and rewrite it first when clarity is low.

5. Check active goal state before creating a goal.
   - Call `get_goal`.
   - If there is no active goal and the objective meets the quality bar, call `create_goal`.
   - If there is an active goal that still matches the user's intent, continue using it instead of creating a duplicate.
   - If there is an active goal that conflicts with the new request, ask whether to finish the current goal, mark it complete if done, or start a separate goal-backed thread.

   **Jev — active-goal comparison.** With the active goal from `get_goal` and the new request in the state, ask one Choice: `same_goal` (continue), `refinement` (tighten it and confirm), `conflict` (ask as above), `unrelated` (separate work). Treat `conflict` and low confidence alike: ask the user.

6. Create the goal only after it passes the quality bar.
   - **Jev — quality check.** Before calling `create_goal`, run the quality check from Jev Checks on the draft objective. Any of `outcome`, `evidence`, `threshold`, or `scope` below ~0.5 means that part is missing or vague: repair it, then re-check once. A low `stop` score is common even in good goals; add a stop condition when the work can stall or grind. Do not present the scores as the verdict — use the repaired objective.
   - Use a single concise objective string.
   - Include the verification evidence in the objective itself.
   - Include scope bounds when they constrain the work.
   - Include a token budget only when the user explicitly requested one.
   - Do not call `create_goal` for an ordinary multi-step task unless the user explicitly asked for goal-backed work.

## Goal Quality Bar

Before `create_goal`, the objective should answer:

- What concrete thing will be true when this is done?
- What evidence will prove it?
- What quantitative or binary threshold defines success?
- What scope boundaries matter?
- What should cause the agent to stop and ask?

Good:

> Reduce checkout API p95 latency below 250 ms for the documented slow path by making the smallest safe server-side change, then verify with `npm run test:checkout` and the existing local latency benchmark showing p95 under 250 ms across 3 consecutive runs.

Good:

> Resolve the open review comments on PR 123 that request code changes, update only the affected auth files and tests, and verify with the targeted auth test command plus `gh pr view 123` showing no unresolved change-request threads.

Weak:

> Make checkout faster.

Weak:

> Keep investigating the PR comments.

## Quantification Heuristics

- For bugs, define success as reproduction first, fix second, and a failing-then-passing validator when possible.
- For tests, name the exact command and required pass condition.
- For performance, name the metric, target threshold, measurement method, and number of runs.
- For quality work, define an observable acceptance bar such as reviewed examples, lint/typecheck/test pass, or user-approved artifact.
- For research, define the decision the research must enable, the sources or systems in scope, and the evidence standard.
- For operations, define healthy state, monitoring window, failure threshold, and rollback or escalation trigger.

## Clarifying Questions

Ask only when a reasonable rewrite would risk pursuing the wrong outcome. Keep the question short and oriented around the missing validator or scope boundary.

Useful question shapes:

- "What metric should define success here: latency, cost, accuracy, or user-visible behavior?"
- "Which environment should I verify against: local, staging, or production?"
- "What is the minimum evidence you want before I mark this goal complete?"

If the user cannot provide a metric, propose the most honest binary validator available and ask for confirmation.

## Jev Checks

Call `POST https://api.typesafe.ai/v1/systemone` with `{"model": "jev-latest", "state": "<text>", "questions": {...}}` and `Authorization: Bearer $TYPESAFE_API_KEY`. If the key is unset (run $init-jev to set it up) or the call fails, skip the check and follow define-goal as written; never block goal definition on Jev. The goal text leaves the machine for TypeSafe in the U.S., so skip these checks for client or confidential goals unless the user has said TypeSafe is allowed.

**Quality check** — state: the draft goal text only.

```json
{"outcome":   {"type": "noul", "instructions": "Does this goal name a concrete outcome that will be true when it is done, rather than an activity?"},
 "evidence":  {"type": "noul", "instructions": "Does this goal name the evidence or validator that will prove it is done?"},
 "threshold": {"type": "noul", "instructions": "Does this goal define a quantitative or binary threshold for success?"},
 "scope":     {"type": "noul", "instructions": "Does this goal state scope boundaries that constrain the work?"},
 "stop":      {"type": "noul", "instructions": "Does this goal say what should make the agent stop and ask?"},
 "kind":      {"type": "choice", "instructions": "What kind of goal is this?",
   "criteria": {"bug": "Fix a bug", "test": "Add or fix tests", "performance": "Improve a performance metric",
                "quality": "Improve quality of an artifact", "research": "Research to enable a decision",
                "operations": "Keep a system healthy", "other": "None of these"}}}
```

On this skill's own examples, the "Good" latency goal scored 0.93–0.99 on outcome, evidence, threshold, and scope but 0.15 on stop (it has no stop condition); "Make checkout faster" and "Keep investigating the PR comments" scored 0.06–0.44 across the board. One run each — a sanity check, not a calibration.

**Pre-question check** — state: the exact draft question plus the facts already known.

```json
{"answerable_locally": {"type": "noul", "instructions": "Can this question be answered from the repository, logs, or earlier conversation without the user?"},
 "user_only": {"type": "noul", "instructions": "Does this question ask for a preference, an authorization, or approval of an irreversible action that only the user can give?"},
 "clarity": {"type": "score", "instructions": "How clearly can the user answer this question without extra context?",
   "criteria": ["Unclear what is being asked", "Answerable but needs context", "Clear and answerable at a glance"]}}
```

**Active-goal comparison** — state: the active goal from `get_goal` and the new request, labeled.

```json
{"relation": {"type": "choice", "instructions": "How does the new request relate to the active goal?",
  "criteria": {"same_goal": "Same goal restated", "refinement": "Narrows or sharpens the active goal",
               "conflict": "Changes or contradicts the active goal's outcome, scope, or validator",
               "unrelated": "Separate work that does not touch the active goal"}}}
```

Keep these questions as written; the agent drafting the goal should not reword them per call, because rewording moves the probabilities. The questions judge only what the text says, so a high score means the goal reads as complete, not that its validator is the right one — that part stays with you and the user.
