# Verification effort follows consequence

Use the current acceptance record and real changed behavior. The purpose is enough independent evidence to judge the promised result, not maximum test activity.

Before dispatch, briefly record the required criteria, protected outcomes, plausible failure paths, permitted checks, and a finite review/repair allowance in the existing task notes or receipt. Choose the allowance from risk, current evidence, and the user's budget. For a bounded change, start with one independent review and one focused recheck after authorized repairs unless the evidence justifies a different allowance. This starting point is not a universal quality threshold or a reason to stop useful authorized work without replanning.

## Judge findings and spending separately

- A demonstrated violation of a required outcome blocks that criterion, even if the visible change is tiny. A formatting requirement can often be settled by a scoped formatter/linter or exact comparison; it need not trigger mutation testing of the component's unrelated behavior.
- A hidden authorization, financial, consistency, or recovery defect may have serious consequences. Screenshots and green tests of another layer cannot waive the actual failed path.
- A plausible but unsupported consequential failure merits a bounded discriminating check. Mark it unverified, not a confirmed defect or an automatic pass.
- An optional improvement or a merely imaginable defect without a causal path does not expand the acceptance task. Keep it separate without silently changing the user's scope.

For each proposed expansion ask: what required outcome could fail, what observation would decide it, and why is the cheaper existing evidence insufficient? Do not select severity by visibility, line count, number of agreeing reviewers, or how interesting the test is.

## Mutation is a method, not a quota

Use a mutation probe only when it can resolve a specific consequential uncertainty about whether the available verification detects a plausible broken result. Name the mutation, expected detector, baseline, isolation, and stopping point first. Prefer an adequate direct behavior check when it answers the question more simply. No fixed number or percentage of mutations is required.

Only operate in an authorized isolated copy with a recovery plan. A test that mocks the mutated layer is not coverage of it. An unavailable probe leaves the exact claim unverified unless another adequate observation establishes it; do not invent a result or relax authorization.

## Reassessment without a five-round treadmill

Rechecks target the actual correction and affected contracts. Record what new evidence each round produced. At the allowance, repeated failed hypothesis, or proposed wider refactor, stop the affected cycle and return: required gap, evidence gained, work spent, bounded alternatives, and the next proposed allowance.

The lead may renew within existing scope when a materially different check or repair is justified by evidence and proportionate to impact. In an admitted long-running campaign, its independent calibrator must assess the renewal against remaining MOE before work continues. Do not ask the same author to rubber-stamp its own detour. New user-owned priorities, risk acceptance, or external authority require the user; routine focused repairs do not.

If adequate evidence is already present and there are no unresolved required gaps, finish. If the budget is spent with gaps remaining, report incomplete or unverified. Never create a passing receipt merely to terminate a loop, and never keep testing merely to avoid handing back a bounded conclusion.
