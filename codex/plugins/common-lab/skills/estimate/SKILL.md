---
name: estimate
description: Evaluate an unfamiliar existing system upgrade or change request in the
  opt-in Estimate Lab, from customer outcomes and evidence to PM decisions and explainable
  effort.
metadata:
  version: 0.2.0
compatibility: Designed for Claude Code; ported to Codex.
---

## Lab Resource Resolution

Before reading a bundled reference or running a bundled script, resolve the absolute directory containing this loaded SKILL.md as LAB_SKILL_DIR. Verify that its frontmatter name is estimate. Use the resulting absolute path in file tools; for shell examples, bind LAB_SKILL_DIR to that verified path in the same shell invocation. This variable is not preconfigured by Codex. Never guess an install-cache path or use the working directory as the skill root. If this entrypoint or a referenced resource cannot be read, stop that operation with SKILL_RESOURCE_MISSING and report the missing path.


# Estimate Lab

## Codex Port Adapter - Bundled Agent Resolution

This plugin does not assume package-local TOMLs are auto-registered as custom
agents. The required definitions for this skill are bundled at
`../../.codex-agents/<agent-name>.toml`: `estimate-auditor`.

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


Help the PM choose an achievable outcome and explain what the estimate buys.
Default conversation and human-readable deliverables to Traditional Chinese.
Use this package for the requested assessment; product implementation and commercial commitments remain separate work.
Start new experiments under .estimate-lab/<case>. Do not silently migrate or update an existing stable case: the Lab's acceptance states require its own runtime. Preserve the original and use an explicitly scoped copy for an authorized migration experiment.

## Find the next useful move

1. Recover the customer's outcome, preserved behavior, scope, responsibility and acceptance from the request and existing case.
2. Reuse explicit answers. A named runtime target settles that target only; it does not select every framework, deployment or lifecycle choice.
3. Investigate the fact most likely to change feasibility, scope, responsibility or effort.
4. When the remaining question requires a human commitment, present a concise, comparable decision and wait for its answer.
5. Accept that answer into the case, then continue the work it authorizes until the next real decision or verified delivery.

The gates describe progress and commitments, not a fixed questionnaire.
Keep the protective mechanisms that prevent stale approval, double pricing, and invented feasibility; choose investigation methods by judgment. A more capable model or a shorter prompt does not eliminate long-run drift. On a resumed or materially redirected assessment, recover the current revision, original outcome, actual PM decisions, responsibility, workset and unresolved contradictions before continuing dependent conclusions.
Keep recommendations distinguishable from accepted choices.
A single feasible route still needs acceptance when it changes the customer's commitment.
Technical facts that the agent can establish belong to the agent.

## Share the decision in useful language

State the decision, the consequence of each option, the recommendation and its conditions, and what happens after the answer.
Explain ambiguous route names through the development approach and the final delivered state.
Include enough cost, risk, responsibility and acceptance differences for an informed choice.
Use a small diagram or a persistent map only when it helps someone understand dependencies or resume the decision.
An available Wayfinder may help with that need; otherwise use a local summary of the destination, settled decisions and unresolved questions.
Do not require another plugin or a separate ticket workflow to begin or continue an assessment.

Read [PM decisions](${LAB_SKILL_DIR}/references/pm-decision-pauses.md) for a commitment boundary.
Read [scenario comparison](${LAB_SKILL_DIR}/references/scenario-guide.md) when alternatives matter.

## Establish evidence and one workset

Read [discovery](${LAB_SKILL_DIR}/references/discovery-guide.md) when the current system is unfamiliar.
For upgrades, mixed work or a CR touching runtime, framework, code generation, deployment or private components, read [dependency behavior](${LAB_SKILL_DIR}/references/dependency-behavior.md).
A support label or evidence ID does not prove compatibility: preserve a usable source, the observed scope and what could still invalidate the route.
Read [success chains](${LAB_SKILL_DIR}/references/evidence-and-success-chain.md) to connect the desired result with work, external owners and completion evidence.

Build canonical detailCatalogs once and reuse their stable IDs across work items and reports.
Keep direct-touch detail, reproducible generated outputs and coverage-only evidence distinct.
Verify that the stated work scope matches the referenced workset; pricingUnits may be smaller when the method is shared or batched.
Unique IDs do not prove unique work: reconcile overlapping purpose, operation and completion evidence before pricing.
Use delegation only when authorized, available and useful for an independent evidence slice; select capabilities to fit that slice.
For such a slice, read [inventory handoff](${LAB_SKILL_DIR}/references/inventory-sidekick-brief.md); the main agent retains cross-slice acceptance and reconciliation.

When assessment spans context handoffs, parallel inventories, or unresolved cross-slice contradictions, read [long-run reconciliation](${LAB_SKILL_DIR}/references/long-run-reconciliation.md). Load ${LAB_SKILL_DIR}/../../.codex-agents/estimate-auditor.toml for the fresh read-only audit of consequential claims before presenting a formal estimate. Do not impose this extra role on a small bounded case; never substitute a fluent reader test for evidence reconciliation.

## Explain the effort

Read [estimation](${LAB_SKILL_DIR}/references/estimation-guide.md) after the route and success conditions are settled.
Price the shared foundation once, uniform conversion as a batch, and known exceptions as their additional work.
Confirmed unchanged work and external responsibility contribute zero to our estimate.
Keep impact counts separate from independently owned pricing units and explain the rate through a representative implementation.
Use the same scope for low, baseline and high; preserve half-day arithmetic and development/testing splits.
Assign each work item to one customer outcome package; external numbers are sums of those work items.

## Keep acceptance and delivery concrete

Read [case state](${LAB_SKILL_DIR}/references/case-state.md) before initializing or updating assessment-state.json.
Use the bundled case_state.py revision checks for changes; stale writes must leave the last good state intact.
Before asking for effort acceptance, explain each package's work, cost driver, development/testing responsibility and completion result.
Read [report design](${LAB_SKILL_DIR}/references/pm-report-design.md) when preparing that explanation or inspecting the report.
Read [deliverables](${LAB_SKILL_DIR}/references/deliverables.md) to generate the five-column CSV and reports from one revision.
Label previews as previews. Delivering a requested preview does not establish PM acceptance or complete an assessment that still requires approval.
After a clear PM answer, record it and continue the authorized delivery checks; do not equate agreement with usable delivery.
Acceptance belongs to the scope that was accepted; a later commitment change needs renewed acceptance, not a reused historical answer.
The Lab's estimate-approved state means effort is accepted and Gate 6 delivery remains current; complete follows actual artifact and reader checks.

Judge the actual result: a reader of the external table can explain scope, main actions, the plain-language cost driver and completion.
Give that reader only the real customer-facing artifact, not internal method cards or expected answers.
Check semantic truth against the canonical case separately; a reader cannot infer evidence absent from the artifact.
Repair failed explanations in state and regenerate without silently changing effort.
Bound each explanation repair to a specific reader misunderstanding. If another pass adds words without resolving it, inspect the underlying scope or evidence instead of endlessly polishing the report. Fresh-reader success is a proxy for understandability, not proof that the PM accepted or a human understood.
Report the accepted scope, usable artifact entry points, observed validation and remaining limitations.
Validator success supports reliable mechanics; it does not replace evidence, PM understanding or a working handoff.
