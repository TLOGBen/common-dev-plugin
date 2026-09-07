---
name: lab-estimate
description: Evaluate an unfamiliar existing system upgrade or change request in the opt-in Estimate Lab, from customer outcomes and evidence to PM decisions and explainable effort.
metadata:
  version: 0.1.0
---

# Estimate Lab

Help the PM choose an achievable outcome and explain what the estimate buys.
Default conversation and human-readable deliverables to Traditional Chinese.
Use this package for the requested assessment; product implementation and commercial commitments remain separate work.

## Find the next useful move

1. Recover the customer's outcome, preserved behavior, scope, responsibility and acceptance from the request and existing case.
2. Reuse explicit answers. A named runtime target settles that target only; it does not select every framework, deployment or lifecycle choice.
3. Investigate the fact most likely to change feasibility, scope, responsibility or effort.
4. When the remaining question requires a human commitment, present a concise, comparable decision and wait for its answer.
5. Accept that answer into the case, then continue the work it authorizes until the next real decision or verified delivery.

The gates describe progress and commitments, not a fixed questionnaire.
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

Read [PM decisions](${CLAUDE_PLUGIN_ROOT}/skills/lab-estimate/references/pm-decision-pauses.md) for a commitment boundary.
Read [scenario comparison](${CLAUDE_PLUGIN_ROOT}/skills/lab-estimate/references/scenario-guide.md) when alternatives matter.

## Establish evidence and one workset

Read [discovery](${CLAUDE_PLUGIN_ROOT}/skills/lab-estimate/references/discovery-guide.md) when the current system is unfamiliar.
For upgrades, mixed work or a CR touching runtime, framework, code generation, deployment or private components, read [dependency behavior](${CLAUDE_PLUGIN_ROOT}/skills/lab-estimate/references/dependency-behavior.md).
A support label or evidence ID does not prove compatibility: preserve a usable source, the observed scope and what could still invalidate the route.
Read [success chains](${CLAUDE_PLUGIN_ROOT}/skills/lab-estimate/references/evidence-and-success-chain.md) to connect the desired result with work, external owners and completion evidence.

Build canonical detailCatalogs once and reuse their stable IDs across work items and reports.
Keep direct-touch detail, reproducible generated outputs and coverage-only evidence distinct.
Verify that the stated work scope matches the referenced workset; pricingUnits may be smaller when the method is shared or batched.
Unique IDs do not prove unique work: reconcile overlapping purpose, operation and completion evidence before pricing.
Use delegation only when authorized, available and useful for an independent evidence slice; select capabilities to fit that slice.
For such a slice, read [inventory handoff](${CLAUDE_PLUGIN_ROOT}/skills/lab-estimate/references/inventory-sidekick-brief.md); the main agent retains cross-slice acceptance and reconciliation.

## Explain the effort

Read [estimation](${CLAUDE_PLUGIN_ROOT}/skills/lab-estimate/references/estimation-guide.md) after the route and success conditions are settled.
Price the shared foundation once, uniform conversion as a batch, and known exceptions as their additional work.
Confirmed unchanged work and external responsibility contribute zero to our estimate.
Keep impact counts separate from independently owned pricing units and explain the rate through a representative implementation.
Use the same scope for low, baseline and high; preserve half-day arithmetic and development/testing splits.
Assign each work item to one customer outcome package; external numbers are sums of those work items.

## Keep acceptance and delivery concrete

Read [case state](${CLAUDE_PLUGIN_ROOT}/skills/lab-estimate/references/case-state.md) before initializing or updating assessment-state.json.
Use the bundled case_state.py revision checks for changes; stale writes must leave the last good state intact.
Before asking for effort acceptance, explain each package's work, cost driver, development/testing responsibility and completion result.
Read [report design](${CLAUDE_PLUGIN_ROOT}/skills/lab-estimate/references/pm-report-design.md) when preparing that explanation or inspecting the report.
Read [deliverables](${CLAUDE_PLUGIN_ROOT}/skills/lab-estimate/references/deliverables.md) to generate the five-column CSV and reports from one revision.
Generate previews without describing them as accepted or delivered.
After a clear PM answer, record it and continue the authorized delivery checks; do not equate agreement with usable delivery.

Judge the actual result: a reader of the external table can explain scope, main actions, the plain-language cost driver and completion.
Give that reader only the real customer-facing artifact, not internal method cards or expected answers.
Check semantic truth against the canonical case separately; a reader cannot infer evidence absent from the artifact.
Repair failed explanations in state and regenerate without silently changing effort.
Report the accepted scope, usable artifact entry points, observed validation and remaining limitations.
Validator success supports reliable mechanics; it does not replace evidence, PM understanding or a working handoff.
