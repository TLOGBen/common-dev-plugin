---
name: lab-delegate
description: Delegate bounded implementation to a cheaper task-fit model while the lead retains responsibility for the goal.
---

# Delegate Lab

Separate doing the implementation from deciding whether the goal is accomplished.
Default user-facing output to Traditional Chinese.

The lead owns scope, architecture, authorization, integration, and acceptance. A worker owns a bounded execution slice. Delegation does not transfer the lead's responsibility for the outcome.

Choose a slice with an observable result and a non-overlapping write set. Prefer a cheaper capable worker when the available model catalog and task difficulty support that choice; keep the current lead model unless the user requests otherwise. Model family names are not a universal capability ranking.

Read ${CLAUDE_PLUGIN_ROOT}/skills/lab-delegate/references/runtime.md when selecting a runtime or honoring a named model profile. Load ${CLAUDE_PLUGIN_ROOT}/agents/lab-executor.md completely before dispatch and include its operating contract in the worker's briefing.

Give the worker the outcome, acceptance evidence, relevant context, permitted files/actions, and decisions it must not reopen. Let it choose implementation details. A separate long plan or progress ledger is unnecessary for a short slice.

For an independent slice, prefer a fresh or narrowly scoped worker context containing that briefing and the necessary evidence, not the entire conversation. Continue an existing worker context when meaningful continuity outweighs its context cost; context isolation is a task-fit choice, not a universal reset rule.

While it runs, do useful independent goal-level work. Check progress at meaningful milestones or signs of failure; avoid repetitive status polling. Diagnose the cause of a failed attempt before choosing retry, narrower scope, stronger model, or human input.

Distinguish reasoning or implementation failure from runtime setup, sandbox, access, and authentication failure. An environment failure is not evidence that the model is too weak. Report the actual boundary and try only an already permitted in-scope alternative; do not upgrade models, broaden permissions, or switch runtimes to bypass the failed control.

Inspect the actual artifact and proportionate acceptance evidence. A worker's completion statement is a claim, not acceptance. Integrate or request a focused correction while a safe next step remains.

Report the achieved outcome, actual worker/runtime when observable, evidence, and remaining limits. Do not report savings, model usage, or token counts that the runtime did not expose.
