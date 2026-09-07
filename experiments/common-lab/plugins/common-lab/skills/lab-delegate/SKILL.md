---
name: lab-delegate
description: Delegate bounded implementation to a cheaper task-fit model while the
  lead retains responsibility for the goal.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

## Lab Resource Resolution

Before reading a bundled reference or running a bundled script, resolve the absolute directory containing this loaded SKILL.md as LAB_SKILL_DIR. Verify that its frontmatter name is lab-delegate. Use the resulting absolute path in file tools; for shell examples, bind LAB_SKILL_DIR to that verified path in the same shell invocation. This variable is not preconfigured by Codex. Never guess an install-cache path or use the working directory as the skill root. If this entrypoint or a referenced resource cannot be read, stop that operation with SKILL_RESOURCE_MISSING and report the missing path.


# Delegate Lab

## Codex Port Adapter - Bundled Agent Resolution

This plugin does not assume package-local TOMLs are auto-registered as custom
agents. The required definitions for this skill are bundled at
`../../.codex-agents/<agent-name>.toml`: `lab-executor`.

Before every named-agent dispatch:

1. Resolve the exact bundled TOML from this `SKILL.md` directory (strip a
   leading `baransu:` namespace from the requested name).
2. Verify the file exists, then pass its absolute path and the task input to a
   generic Codex subagent. The first instruction to that subagent is to read
   the TOML's `developer_instructions` completely before doing any task work
   and to treat relative paths as relative to the TOML file.
3. If the TOML is missing or unreadable, stop with
   `AGENT_DEFINITION_MISSING: <path>`. Never invent, summarize, or substitute a
   role from the agent name.


Separate doing the implementation from deciding whether the goal is accomplished.
Default user-facing output to Traditional Chinese.

The lead owns scope, architecture, authorization, integration, and acceptance. A worker owns a bounded execution slice. Delegation does not transfer the lead's responsibility for the outcome.

Choose a slice with an observable result and a non-overlapping write set. Prefer a cheaper capable worker when the available model catalog and task difficulty support that choice; keep the current lead model unless the user requests otherwise. Model family names are not a universal capability ranking.

Read ${LAB_SKILL_DIR}/references/runtime.md when selecting a runtime or honoring a named model profile. Load ${LAB_SKILL_DIR}/../../.codex-agents/lab-executor.toml completely before dispatch and include its operating contract in the worker's briefing.

Give the worker the outcome, acceptance evidence, relevant context, permitted files/actions, and decisions it must not reopen. Let it choose implementation details. A separate long plan or progress ledger is unnecessary for a short slice.

For an independent slice, prefer a fresh or narrowly scoped worker context containing that briefing and the necessary evidence, not the entire conversation. Continue an existing worker context when meaningful continuity outweighs its context cost; context isolation is a task-fit choice, not a universal reset rule.

While it runs, do useful independent goal-level work. Check progress at meaningful milestones or signs of failure; avoid repetitive status polling. Diagnose the cause of a failed attempt before choosing retry, narrower scope, stronger model, or human input.

Inspect the actual artifact and proportionate acceptance evidence. A worker's completion statement is a claim, not acceptance. Integrate or request a focused correction while a safe next step remains.

Report the achieved outcome, actual worker/runtime when observable, evidence, and remaining limits. Do not report savings, model usage, or token counts that the runtime did not expose.
