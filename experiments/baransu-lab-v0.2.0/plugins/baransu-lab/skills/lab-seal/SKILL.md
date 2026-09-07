---
name: lab-seal
description: Independently verify a completed change against acceptance criteria and
  issue an experimental evidence receipt.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

## Lab Resource Resolution

Before reading a bundled reference or running a bundled script, resolve the absolute directory containing this loaded SKILL.md as LAB_SKILL_DIR. Verify that its frontmatter name is lab-seal. Use the resulting absolute path in file tools; for shell examples, bind LAB_SKILL_DIR to that verified path in the same shell invocation. This variable is not preconfigured by Codex. Never guess an install-cache path or use the working directory as the skill root. If this entrypoint or a referenced resource cannot be read, stop that operation with SKILL_RESOURCE_MISSING and report the missing path.


# Seal Lab

## Codex Port Adapter - Bundled Agent Resolution

This plugin does not assume package-local TOMLs are auto-registered as custom
agents. The required definitions for this skill are bundled at
`../../.codex-agents/<agent-name>.toml`: `lab-verifier`.

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


Decide whether the promised result is supported by the delivered artifact.
Default user-facing output and receipts to Traditional Chinese.

Pin the actual artifact/diff and reuse its acceptance record or the user's explicit criteria. Read ${LAB_SKILL_DIR}/../lab-contract/references/acceptance.md for the receipt contract. If no target or criterion can be established, report the missing input; do not reconstruct success from the author's memory.

Choose verification by the causal risks of the changed behavior. Use the narrowest real checks that establish the required outcome, expanding when shared behavior, integration boundaries, or concrete findings justify it. Do not run a full suite or five-point excavation merely because this skill was invoked.

Read ${LAB_SKILL_DIR}/references/verification-effort.md before dispatch to pin the impact-based check and repair allowance. This is a defense against verification becoming an unbounded goal, not permission to waive a required criterion. Report effort separately from accepted outcome; the verifier supplies evidence, while the lead owns continuation priority and an active campaign's calibrator owns its strategic checkpoint.

Load ${LAB_SKILL_DIR}/../../.codex-agents/lab-verifier.toml completely and dispatch a fresh independent verifier with the immutable target identity, criteria, raw evidence, relevant baseline failures, and permitted check scope. The verifier reports only; it does not repair or change acceptance.

Cover the affected real paths, including zero-test layers and adjacent independently verifiable conditions. A passed parameter is not proof its filter takes effect; a mock of the changed layer is not its coverage. Preserve exact requirement constants and check consequential cross-surface behavior without mandating a particular implementation pattern.

When primary evidence disproves a contract premise, judge the result against that evidence and the user's actual outcome. Record the narrow premise correction and retain unaffected criteria. This is neither a literal-wording veto nor permission to redesign the user's scope.

The lead may repair only when the original request already includes implementation/fixing and the change remains authorized and in scope. A verification-only request remains read-only even for a serious defect; report the blocker instead. Risk severity does not create permission.

After an authorized fix, independently recheck the finding and the affected acceptance paths. Do not restart an unrelated full review. At the declared allowance, repeated no-progress, or scope growth, return the unresolved finding and evidence to the lead for bounded replanning. Further work needs a reason tied to a remaining required outcome and a renewed allowance, not merely another possible test. Routine internal replanning stays internal; only a user-owned tradeoff or authority change requires asking the user. Exhaustion never converts unverified into passed.

Use isolated disposable copies for any authorized mutation probe; never inject a probe into the user's live worktree or external state. If isolation or recovery is not available, choose non-mutating evidence and report its limitation.

Issue a new receipt under .baransu-lab/receipts/ with target identity, per-criterion result/evidence, verifier independence, and remaining limits. Independent success requires supported required criteria, no unresolved blocker, and unchanged target identity since verification.

Do not write the stable sealed marker, change a stable CONTRACT.md, or emit stable seal-guard telemetry. This experimental receipt does not satisfy the original Stop hook or authorize shipping, archiving, cleanup, or external actions.
