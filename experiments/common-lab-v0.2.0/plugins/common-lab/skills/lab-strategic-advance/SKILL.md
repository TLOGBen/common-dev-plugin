---
name: lab-strategic-advance
description: Coordinate a locked long-running, coupled campaign with independent outcome
  calibration and recovery from attention traps.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

## Lab Resource Resolution

Before reading a bundled reference or running a bundled script, resolve the absolute directory containing this loaded SKILL.md as LAB_SKILL_DIR. Verify that its frontmatter name is lab-strategic-advance. Use the resulting absolute path in file tools; for shell examples, bind LAB_SKILL_DIR to that verified path in the same shell invocation. This variable is not preconfigured by Codex. Never guess an install-cache path or use the working directory as the skill root. If this entrypoint or a referenced resource cannot be read, stop that operation with SKILL_RESOURCE_MISSING and report the missing path.


# Strategic Advance Lab

## Codex Port Adapter - Bundled Agent Resolution

This plugin does not assume package-local TOMLs are auto-registered as custom
agents. The required definitions for this skill are bundled at
`../../.codex-agents/<agent-name>.toml`: `lab-calibrator`, `lab-executor`.

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


Move the real objective, not merely the activity around it.
Default user-facing output and campaign notes to Traditional Chinese.

Use the user's already-locked objective and completion criteria. If a material goal choice is missing, resolve that choice before execution; do not reopen an adequate contract for ceremony.

Admit work whose coupled fronts, accumulated state, repeated interventions, or cross-session duration can saturate the lead. A campaign of APIs, pages, E2E, and refactoring over many hours is the target; hours alone are not an admission score. Bounded small/medium changes normally belong to ordinary execution or Contract, Delegate, and Seal as needed. Do not impose campaign staffing on a small fix.

For a stateful campaign, read ${LAB_SKILL_DIR}/references/campaign.md and use the bundled campaign.py ledger under .common-lab/strategic/. This is a separate experimental schema, not a migration of stable state.

For an admitted campaign, read ${LAB_SKILL_DIR}/references/long-run-control.md. Keep strategic judgment separate from implementation. Load ${LAB_SKILL_DIR}/../../.codex-agents/lab-calibrator.toml completely and dispatch a fresh independent calibrator at the prescribed boundaries; load ${LAB_SKILL_DIR}/../../.codex-agents/lab-executor.toml for bounded implementation workers, optionally through lab-delegate. The lead does not become the repair worker when a slice fails.

Choose one coherent main effort that reduces a remaining completion gap. It may contain parallel independent workstreams with explicit write ownership; it is not a one-worker limit. State the expected outcome change, bounded repairs, and the next calibration point. Supporting build or style work must explain its dependency on that outcome, not become a competing unlimited goal.

Expect drift, hallucinated progress, and attention capture as long-run risks even with a strong lead. Independent calibration is not conditional on that lead first noticing confusion. Require it before a new increment, after a material intervention or handoff, when repair bounds expire, and before completion. Use the referenced packet check to bind the decision to current evidence; the check is not a sandbox or proof that the reviewer is infallible.

Compare the result with the expected change. Record new evidence, not a narrative of busyness. If activity produces no goal progress, change the approach or identify the external dependency; do not endlessly polish the same subsystem.

Keep independent acceptance properties separate. One successful delivery proves neither uniqueness, complete coverage, nor absence of duplicates. Leave unsupported properties open and choose the smallest read-only observation or authorized probe that could resolve them; do not promote a positive example into universal or negative proof.

Preserve authority, identity, recovery, and outcome checks for consequential mutations. Persistence never grants additional permission. An unknown mutation outcome requires reconciliation before retry; human-only choices require human input.

Pause affected execution for a genuine scope/authority choice, unavailable prerequisite, expired control boundary, or requested review. Internal calibration should not create routine questions for the user. Continue unrelated authorized work only while its ownership and control remain valid. If independent calibration is unavailable, report degraded coverage and preserve a safe continuation point; do not silently replace it with self-approval.

At handoff or completion, verify the remaining criteria against current evidence and unresolved operation outcomes. Report what is complete, what is not, the main uncertainty, and the exact continuation point. The ledger can check evidence shape and digests, not whether evidence genuinely proves success.

Lead with the outcome delta, remaining gaps, any detour consuming effort without progress, and the next bounded move. Separate implementation activity (MOP) from accepted effect (MOE). A user should understand why progress is or is not advancing without reading the event log. Preserve this control purpose when tuning cadence or changing models; do not retire it on evidence from a short easy run.
