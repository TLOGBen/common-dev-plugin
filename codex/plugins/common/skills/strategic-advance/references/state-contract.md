# Strategic State Contract

`state.json` is the overwrite-only source of current truth. Append raw events to `run-ledger.jsonl` and store large evidence artifacts under `artifacts/`.

## Contents

1. [Version 6 invariants](#version-6-invariants)
2. [Required top-level fields](#required-top-level-fields)
3. [Operational decision terms](#operational-decision-terms)
4. [Authoritative evidence](#authoritative-evidence)
5. [Verified world-state change](#verified-world-state-change)
6. [Strategic clarity and Wayfinder](#strategic-clarity-and-wayfinder)
7. [Battlefields, candidates, and risks](#battlefields-candidates-and-risks)
8. [PDCA and bounded review contract](#pdca-and-bounded-review-contract)
9. [Recovery, observers, cleanup, and culmination](#recovery-observers-cleanup-and-culmination)
10. [Action gates and tactical takeover](#action-gates-and-tactical-takeover)
11. [Loss minimization assessment](#loss-minimization-assessment)
12. [Legal terminal states](#legal-terminal-states)
13. [Strategic Advance board](#strategic-advance-board)

## Version 6 invariants

Version 6 does not permit subjective labels such as "high confidence," "clear," "safe," "nearly complete," or "loss minimized" to control execution. Any term that can change the main effort, authorize a mutation, trigger a pivot, or declare a terminal state must be recomputable from JSON fields.

```text
Decision endpoint = Semantic inputs + Canonical predicate + Evidence claim
                    + Validity window + Derived result
```

Free text explains a decision to a person; it never opens a gate by itself. Where this contract defines a canonical predicate, the state stores the semantic IDs and values plus evidence references. The validator generates the predicate, so an authored substitute field is rejected rather than trusted.

Canonical predicates JSON-encode every interpolated semantic value: strings are quoted and escaped, booleans are lowercase, numbers are unquoted, and encoded values contain no optional whitespace. For example:

```text
RISK["duplicate-finalization"]@FRONT["finalize-sample-operation"].STATUS == "CONTROLLED"
```

## Required top-level fields

| Field | Purpose |
|---|---|
| `schemaVersion` | Must be `6`. |
| `strategicObjective` | Revision, approval time, world dimensions, victory criteria, hard constraints, and the non-empty closed list of protected assets. |
| `plainBriefing` | Context, current situation, reasoning, next move, and user role. |
| `currentTruth` | World state, evidence claims, observer health, and cleanup debt. |
| `riskRegister` | Scored risks that name one protected asset, one concrete threat, thresholds, guards, stop conditions, recovery actions, and derived status checks. |
| `blockers` | Proven, suspected, or cleared blockers. |
| `battlefields` | Entry, exit, evidence, recovery, and permitted state transitions. |
| `decision` | Candidate scores, one main effort, and a pivot claim bound to the validator-generated active-front predicate. |
| `strategicClarity` | Derived `CLEAR/UNCLEAR` status and Wayfinder route. |
| `progress` | Main-effort start, last world change, repeated failures, alternate-route readiness, and culmination policy. |
| `executionAssessment` | Actuator status and the known result of the latest action. |
| `takeoverReadiness` | Optional. Derived `OPERABLE`, `EXECUTABLE`, and `VERIFIABLE` takeover gates; absent whenever no tactical takeover is contemplated. |
| `intervention` | Tactical-takeover state and return-of-control contract. |
| `lossMinimizationAssessment` | Evidence contracts for unattainability, unacceptable-outcome avoidance, residual loss, and preserved gains. It contains no hand-entered result. |
| `terminalAssessment` | Campaign in progress, objective achieved, new authority required, or loss minimized within proven bounds. |
| `latestVerifiedAdvance` | Closed receipt for the latest strict before/after change in an approved world dimension and its currently satisfied strategic-effect target. |

See `example-state.json` for an executable fixture.

## Operational decision terms

| Term | Required condition | Validator behavior |
|---|---|---|
| Clear situation | Objective is approved, exactly one eligible candidate has the minimum score, no unresolved decision or `SUSPECTED` blocker remains, and the canonical active-front pivot claim is current, authoritative, and `FAIL`. | Derive `CLEAR` and `EXECUTION_READY`; a `PASS` pivot claim forces reassessment. |
| Authoritative evidence | A claim is current and has the lowest `authorityRank` among claims for the same predicate. | Reject lower-authority support and fail on equal-authority conflict. |
| Verified world change | Same scope and approved dimension; authoritative before/after `PASS` claims on canonical `WORLD[...]` predicates; ordered timestamps; different values; and a currently satisfied effect target. | Validate the closed receipt, identity, dimension, claims, values, time, effect type, and target state. |
| Proven blocker | `status=PROVEN` plus predicate, observation, authoritative evidence, remediation, and a clear predicate. | An `ACTIVE` battlefield cannot have a proven blocker. |
| Closest path to victory | One eligible candidate has the unique minimum score under the fixed formula. | Recompute `totalScore`; ignore stated preference. |
| Safely eligible | No unacceptable open risk or proven blocker; mutation recovery is ready; battlefield is not `COMPLETE` or `DEFERRED`. | Recompute candidate `eligible`. |
| Operationally controllable risk | The risk names an approved protected asset and concrete threat, and provides a guard, stop condition, recovery action, threshold, and closed status checks. | Reject observations that cannot identify what is threatened or how execution can contain and recover from the threat. |
| Executable recovery | Bounded steps, success predicate, stop condition, action, and current authoritative evidence exist. | An active mutation battlefield fails validation unless recovery is `READY`. |
| Healthy observer | Every required claim is currently observable. | Derive one of four observer states from claim coverage and deadline. |
| Victory-blocking cleanup | Open debt has `blocksVictory=true`, `severity=BLOCKING`, residue, owner, action, predicate, and evidence. | Prevent achievement while it remains open. |
| Near culmination | Elapsed time or repeated failures cross policy thresholds, adjusted for alternate-route readiness. | Derive `LOW`, `MEDIUM`, or `HIGH`. |
| Safe routes exhausted | No route is `OPEN`, at least one is `REQUIRES_AUTHORITY`, and the action outcome is known. | Only then allow `NEW_AUTHORITY_REQUIRED`. |
| Loss minimized | Victory is authoritatively proven unattainable, no open or authority route remains, unacceptable outcomes and bounded residual loss are proven, listed gains are preserved, and blocking cleanup is closed. | Derive `LOSS_MINIMIZED`; never accept a manual loss result. |

## Authoritative evidence

Each evidence claim must have a source, observation and expiry times, authority rank, predicate, and status:

```json
{
  "id": "claim-active-task-count",
  "sourceType": "DB",
  "sourceRef": "authoritative state-store readback",
  "observedAt": "2026-08-14T09:28:00+08:00",
  "validUntil": "2026-08-14T12:00:00+08:00",
  "authorityRank": 1,
  "predicate": "ACTIVE_TASK_COUNT == 1",
  "status": "PASS"
}
```

- Rank `1` is most authoritative; larger numbers have less authority.
- Expiry degrades authority, never legality: an expired `PASS` or `FAIL` keeps its recorded status but stops counting as observed, so it loses authoritative weight. Only claims gating the current decision (an `ACTIVE` front's entry, recovery readiness, pivot, victory evidence) surface targeted validator errors when stale — that short list is a light consolidation's work order.
- Historical records — a `COMPLETE` front's exit claim, `latestVerifiedAdvance` before/after claims, an `ENABLES_NEXT_TRANSITION` target entry — validate against rank arbitration without freshness: best `authorityRank` wins, and among equals the latest `observedAt` wins. History never requires present-tense re-probing, but a higher-authority refutation still overturns it.
- Conflicting `PASS` and `FAIL` claims at the highest equal rank fail validation.
- `currentTruth.confidence` is retired. Numeric confidence may appear in analysis artifacts, never in a decision gate.

## Verified world-state change

Declare the dimensions that count as world state in `strategicObjective.worldDimensions`, for example:

```json
["operationStatus", "activeTaskCount", "resourceState"]
```

Only a structure like the following may refresh `progress.lastWorldStateChangeAt`:

```json
{
  "at": "2026-08-14T09:20:00+08:00",
  "scopeIdentity": "sample-operation-001",
  "dimension": "operationStatus",
  "from": "PREPARING",
  "to": "AWAITING_FINAL_CONFIRMATION",
  "beforeValue": "PREPARING",
  "afterValue": "AWAITING_FINAL_CONFIRMATION",
  "beforeClaimId": "claim-operation-preparing",
  "afterClaimId": "claim-operation-ready",
  "strategicEffect": "ENABLES_NEXT_TRANSITION",
  "effectTargetId": "finalize-sample-operation",
  "evidence": ["authoritative state changed in the expected scope"],
  "evidenceClaimIds": [
    "claim-operation-preparing",
    "claim-operation-ready"
  ]
}
```

`latestVerifiedAdvance` is closed to exactly `at`, `scopeIdentity`, `dimension`, `from`, `to`, `beforeValue`, `afterValue`, `beforeClaimId`, `afterClaimId`, `strategicEffect`, `effectTargetId`, `evidence`, and `evidenceClaimIds`. `beforePredicate` and `afterPredicate` are retired.

The contract requires:

1. One `scopeIdentity` and one approved world dimension.
2. Current authoritative `PASS` claims whose predicates byte-equal these validator-generated forms:
   - `WORLD["<scopeIdentity>"].DIMENSION["<dimension>"] == <canonical-json-beforeValue>`
   - `WORLD["<scopeIdentity>"].DIMENSION["<dimension>"] == <canonical-json-afterValue>`
3. `from` and `to` equal the string forms of `beforeValue` and `afterValue`; `evidenceClaimIds` contains exactly the two named claim IDs.
4. A before observation earlier than the after observation, with different values; `at` equals the after observation and `progress.lastWorldStateChangeAt`.
5. One allowed strategic effect and an `effectTargetId` whose current derived state agrees with that effect:
   - `SATISFIES_VICTORY_CRITERION`: the referenced victory criterion derives `PASS`;
   - `REMOVES_PROVEN_BLOCKER`: the referenced blocker derives `CLEARED`;
   - `CONTROLS_UNACCEPTABLE_RISK`: the referenced risk derives `CONTROLLED` or `CLOSED`, and its score is at least its declared threshold;
   - `ENABLES_NEXT_TRANSITION`: the referenced battlefield's canonical entry claim is current authoritative `PASS`.

Builds, runners, reports, fixtures, documentation, selector changes, browser restarts, and observer repairs are measures of performance. They can remove a blocker, but they are not measures of effectiveness and must not masquerade as a world delta.

## Strategic clarity and Wayfinder

The validator derives `strategicClarity`; operators do not label it manually. Clarity requires:

- an objective revision and approval time;
- exactly one minimum-score eligible candidate;
- no unresolved decision;
- no `SUSPECTED` blocker; and
- a current authoritative `pivotClaimId` whose predicate byte-equals `BATTLEFIELD["<activeFrontId>"].PIVOT_TRIGGERED == true` and whose status is `FAIL`.

`FAIL` means the pivot condition has not triggered. `PASS` means it has triggered and makes the situation unclear until the main effort is reassessed. `pivotPredicate` and `pivotWhen` are retired because their semantics cannot be operator-defined.

A pivot claim is born `UNKNOWN` before any evidence has been recorded against it. The gate's `pivot_clear` check requires an authoritative `FAIL` specifically — `UNKNOWN` satisfies neither `FAIL` nor `PASS`, so it fails `pivot_clear` exactly as `PASS` would. Because clarity demands `FAIL` and not merely "not `PASS`," `pivotCondition` must be phrased as a continuously evaluable state statement — true or false at any point in the campaign, including before the first action runs — or the first consolidation is unconditionally `UNCLEAR` with no evidence able to close it.
`strategicClarity.unclearCauses` is a derived receipt listing why the situation is not clear — `OBJECTIVE_UNAPPROVED`, `DECISION_FOG`, `BLOCKER_SUSPECTED`, `NO_ELIGIBLE_CANDIDATE`, `AMBIGUOUS_CANDIDATE`, `PIVOT_UNPROBED`, `PIVOT_TRIGGERED` — and is empty when clarity is `CLEAR` or terminal. Only `DECISION_FOG` (non-empty `unresolvedDecisions`) derives `route=WAYFINDER_REQUIRED`; every other cause derives `route=OPERATOR_RESOLVE`, and the named causes are the commander's in-place work order.

All conditions satisfied:

```text
CLEAR + EXECUTION_READY
```

No active battlefield and no eligible candidate on an otherwise legal terminal posture:

```text
CLEAR + TERMINAL
```

Any condition missing:

```text
UNCLEAR + WAYFINDER_REQUIRED
```

When unclear, record the decision questions or expose the candidate tie or suspected blocker, and provide `wayfinderMapPath`. Use Wayfinder only for decisions that can change the main effort, dependency structure, authority, or pivot. Return to Strategic Advance as soon as one main effort is uniquely selectable.

## Battlefields, candidates, and risks

### Battlefield states

Every battlefield stores `id`, `entryState`, `terminalState`, `entryClaimId`, and `exitClaimId`. The validator generates these exact predicates:

```text
BATTLEFIELD["<id>"].ENTRY["<entryState>"] == true
BATTLEFIELD["<id>"].EXIT["<terminalState>"] == true
```

The referenced claims must be current, authoritative, and byte-equal the generated predicates. The general `evidenceClaimIds` list is display context and never gates status.

- `ACTIVE`: entry claim is authoritative `PASS`, exit is not `PASS`, and no proven blocker applies.
- `PENDING`: entry is not yet `PASS`.
- `BLOCKED`: at least one proven blocker targets the battlefield.
- `COMPLETE`: exit claim is authoritative `PASS`.
- `DEFERRED`: a non-empty `deferReason` explains why resources are withheld.

Retired free-form fields include `authoritativeEvidence`, `recoveryPath`, `blocksActiveFront`, `entryPredicate`, and `exitPredicate`.

### Candidate formula

```text
totalScore = unmetVictoryCriteria × 100
           + remainingTransitions × 10
           + riskScore × 5
           + costMinutes
```

Lower is closer to victory. Recompute `unmetVictoryCriteria` from the criteria the candidate is expected to close and `riskScore` from the risk register. Only candidates with `eligible=true` may become the main effort. A tie for the minimum score means the situation is unclear.

### Unacceptable risk

```text
risk score = probability × impact
unacceptable = status OPEN AND score >= unacceptableThreshold
```

`strategicObjective.protectedAssets` is a non-empty list of closed `{id, displayText}` objects. A risk is not merely an observation: it must identify one registered `protectedAssetId`, state one concrete `threat` to that asset, and define a guard, stop condition, and recovery action. Without both the threatened asset and a bounded control path, the observation cannot block or redirect the main effort as a risk.

Each risk object is closed to exactly `id`, `affectedFrontId`, `protectedAssetId`, `threat`, `status`, `probability`, `impact`, `score`, `unacceptableThreshold`, `guard`, `stopCondition`, `recoveryAction`, and `statusChecks`. `statusChecks` contains exactly `CONTROLLED`, `ACCEPTED`, and `CLOSED`; each nested check is closed to `{evidenceClaimIds}`. The validator generates each predicate:

```text
RISK["<risk-id>"]@FRONT["<affected-front-id>"].STATUS == "CONTROLLED"
RISK["<risk-id>"]@FRONT["<affected-front-id>"].STATUS == "ACCEPTED"
RISK["<risk-id>"]@FRONT["<affected-front-id>"].STATUS == "CLOSED"
```

Exactly one authoritative `PASS` check derives that status; no passing check derives `OPEN`; multiple passing checks are invalid. An authored `predicate` inside a status check is rejected, and stored `status` is only a derived receipt.

`CONTROL_RISK` is legal only while a validator-derived open risk affects the active battlefield and meets or exceeds its threshold. A support-front risk cannot authorize risk-control work on the main effort.

## PDCA and bounded review contract

Every execution or specialist-review cycle is bounded and objective-relative:

- **Plan** locks the objective revision, protected assets, risk taxonomy, acceptance or severity threshold, evidence bar, authority, scope, time or round budget, and stop condition.
- **Do** performs one bounded tactic, control, or read-only review pass with known side effects and recovery.
- **Check** compares current authoritative evidence, before/after world state, control effect, and residual risk with the predeclared criteria. MOP never substitutes for MOE.
- **Act** emits one `BLOCK`, `MONITOR`, or `PASS` disposition, preserves gains, changes the control, pivots, or re-divides fronts only when the evidence requires it.

A security or other specialist review must have this contract before dispatch. `BLOCK` requires current authoritative evidence of an active-front risk at or above threshold that threatens a victory criterion, hard constraint, or unacceptable outcome. `MONITOR` covers below-threshold, support-only, or recoverable risk without taking the main effort. `PASS` requires the relevant gates to be green and the risk to be absent, within appetite, or derived `CONTROLLED`, `ACCEPTED`, or `CLOSED`.

Findings outside the declared scope or below its threshold go to a later backlog and cannot change the current main effort. Reaching the budget or stop condition ends the review. A further pass requires a newly approved contract; review activity cannot authorize an unbounded loop.

## Recovery, observers, cleanup, and culmination

### Recovery readiness

Recovery is `READY` only when it has an action, bounded non-empty steps, a `readinessPredicate`, a success predicate, a stop condition, and current authoritative `PASS` evidence whose predicate exactly equals `readinessPredicate`. A current `FAIL` claim is observed, but it never makes recovery ready. "Investigate later" and "roll back if necessary" are not executable recovery plans.

### Observer status

For each observer, record `requiredClaimIds`, `decisionCriticalClaimIds`, and `deadlineExceeded`:

- all required claims observable: `HEALTHY`;
- critical claims observable but non-critical claims missing: `DEGRADED`;
- a critical claim missing after the deadline: `FAILED`;
- a critical claim missing before the deadline: `UNKNOWN`.

Current `PASS` and `FAIL` claims both count as observed. `UNKNOWN` and expired claims do not.

### Cleanup debt

Each item needs residue, severity, `blocksVictory`, owner, cleanup action, verification predicate, status, and evidence claim IDs. `CLOSED` is a derived receipt: every referenced claim must be current and authoritative, its predicate must exactly equal `verificationPredicate`, and it must be `PASS`. Otherwise the item remains `OPEN`. Unstructured cleanup strings are not accepted.

### Culmination risk

`progress.activeFrontStartedAt` is the start time for the current main effort. Reset it whenever `activeFrontId` changes. Derive elapsed time from `state.updatedAt - activeFrontStartedAt`; never store `activeFrontElapsedMinutes`.

The validator derives culmination risk:

- `HIGH`: elapsed time reaches the high-risk threshold, or repeated failures reach their limit with no ready alternate;
- `MEDIUM`: elapsed time reaches the reanalysis threshold, or repeated failures reach their limit;
- `LOW`: neither threshold is reached.

## Action gates and tactical takeover

Every `takeoverReadiness.*.status` and `takeoverReadiness.result` field is a validator-derived receipt, never an authorization input. Human-facing `evidence` prose is display-only. `takeoverReadiness` is closed to `actionId`, `actorId`, `sessionId`, `contextId`, `scopeIdentity`, `operable`, `executable`, `verifiable`, and `result`.

### `OPERABLE`

`operable` is closed to `status`, `evidence`, `actorCheck`, `sessionCheck`, `targetCheck`, and `controlCheck`. Actor, session, and target checks are closed to `{evidenceClaimIds}`. The control check is closed to `{requiredConditions, evidenceClaimIds}`, and its conditions must be exactly `VISIBLE`, `ENABLED`, and `UNOBSTRUCTED`.

The validator generates these predicates from the readiness IDs:

```text
ACTOR["<actorId>"].VERIFIED == true
SESSION["<sessionId>"].CONTEXT["<contextId>"].READY == true
TARGET["<scopeIdentity>"].CARDINALITY == 1
CONTROL["<scopeIdentity>"].VISIBLE_ENABLED_UNOBSTRUCTED == true
```

All four checks must derive `PASS`; the target must derive `EXACT_ONE`.

### `EXECUTABLE`

`executable` is closed to `status`, `objective`, `authorizedActor`, `authorityCheck`, `prerequisiteChecks`, `steps`, `prohibitedActions`, `sideEffects`, `timeoutSeconds`, `stopCondition`, and `recoveryAction`. The authority check is closed to `{evidenceClaimIds}`. Each prerequisite is closed to `{requirementId, evidenceClaimIds}`.

```text
ACTOR["<actorId>"].AUTHORIZED_FOR["<actionId>"] == true
ACTION["<actionId>"].REQUIREMENT["<requirementId>"].SATISFIED == true
```

`authorizedActor` must equal `actorId`; authority and every non-empty prerequisite must derive `PASS`; the structure must contain exactly one non-empty mechanical step, non-empty prohibitions and side effects, a positive timeout, stop condition, and recovery action. `OUTCOME_UNKNOWN` makes this gate `FAIL`.

### `VERIFIABLE`

`verifiable` is closed to `status`, `expectedWorldDelta`, `expectedWorldDeltaContracts`, `baselineChecks`, `evidenceSources`, `successPredicates`, `failurePredicates`, `unknownOutcomeRule`, and `deadlineAt`. A baseline check is closed to `{id, evidenceClaimIds}`. A world-delta contract is closed to `{scopeIdentity, dimension, beforeValue, afterValue, baselineCheckId}`.

Each contract gets one dedicated baseline and generates:

```text
WORLD["<scopeIdentity>"].DIMENSION["<dimension>"] == <canonical-json-beforeValue>
```

Baselines and contracts must form an exact 1:1 mapping. All contracts name the same `takeoverReadiness.scopeIdentity`; each scope/dimension pair is unique; every dimension is declared in `strategicObjective.worldDimensions`; values are distinct scalars; and every baseline derives `PASS`. Success and failure predicates are non-empty and disjoint, `deadlineAt` is later than `state.updatedAt`, and `unknownOutcomeRule` is exactly `NO_DECISIVE_EVIDENCE_BY_DEADLINE`.

The validator also derives `executionAssessment.actorIdentity` from actor plus session checks, `targetIdentity` from the target check, and `actionContract` from the executable contract. Hand-entered receipt values cannot repair a failed underlying check.

```text
TACTICAL_ACTION_READY = AUTOMATION_ACTUATOR_UNRELIABLE
  AND OPERABLE AND EXECUTABLE AND VERIFIABLE
  AND OUTCOME in {NOT_ATTEMPTED, NO_CHANGE}
  AND no observed mutation or world delta
  AND actor VERIFIED AND target EXACT_ONE AND action contract VERIFIED
  AND exactly one bounded step
```

`UNRELIABLE` requires at least one started automation attempt. A hard deadline cannot turn zero attempts into a proven automation wedge. During `REQUESTED`, `intervention.requestedAction` must byte-equal the sole executable step. A user acknowledgement moves the campaign into `BATTLE_DAMAGE_ASSESSMENT`; it does not prove success.

## Loss minimization assessment

`lossMinimizationAssessment` defines evidence contracts; it never stores `status`, `result`, `lossMinimized`, or another self-declared boolean. Its objects are closed to the fields shown below; undefined fields are rejected. Each predicate-bearing item must reference at least one current authoritative claim whose predicate exactly matches the item predicate. The validator derives whether that item is proven from claim status and validity.

```json
{
  "victoryUnattainable": {
    "predicate": "STRATEGIC_VICTORY_UNATTAINABLE_UNDER_CURRENT_CONSTRAINTS == true",
    "evidenceClaimIds": ["claim-victory-unattainable"]
  },
  "unacceptableOutcomeChecks": [
    {
      "outcome": "exact text from strategicObjective.unacceptableOutcomes",
      "predicate": "UNACCEPTABLE_OUTCOME_ABSENT == true",
      "evidenceClaimIds": ["claim-outcome-absent"]
    }
  ],
  "residualLossMeasurements": [
    {
      "id": "residual-resource-count",
      "metric": "ACTIVE_RESIDUAL_RESOURCE_COUNT",
      "displayText": "Residual resources are bounded to one isolated item",
      "predicate": "ACTIVE_RESIDUAL_RESOURCE_COUNT <= 1",
      "evidenceClaimIds": ["claim-residual-resource-count"]
    }
  ],
  "preservedGains": [
    {
      "id": "preserved-clean-resources",
      "displayText": "Previously cleaned resources remain clean",
      "predicate": "REOPENED_CLEAN_RESOURCE_COUNT == 0",
      "evidenceClaimIds": ["claim-clean-resources-preserved"]
    }
  ]
}
```

- `victoryUnattainable` is one explicit predicate, not a confidence statement.
- `unacceptableOutcomeChecks` must cover every unique `strategicObjective.unacceptableOutcomes` string exactly once; no extra or duplicate outcome is accepted.
- `residualLossMeasurements` is non-empty. Every listed measurement must have authoritative `PASS` evidence before the loss terminal is legal.
- `preservedGains` may be empty. If any gains are listed, every one must have authoritative `PASS` evidence.
- Unknown evidence is valid while a campaign is in progress, but cannot satisfy the loss terminal.

## Legal terminal states

Victory-criterion statuses are derived from exact predicate/evidence contracts just like loss checks. An unrelated authoritative `PASS` claim cannot close a victory criterion.

Each `alternativeRoutes[]` item contains three closed evidence checks under `statusChecks`: `CLOSED`, `UNSAFE`, and `REQUIRES_AUTHORITY`. Exactly one proven check derives that receipt; no proven check derives `OPEN`; more than one proven check is invalid. Route status and `requiredAuthority` therefore cannot be hand-entered to force a terminal.

Every legal terminal additionally requires all campaign activity to be stood down: zero `ACTIVE` battlefields, zero eligible candidates, `takeoverReadiness` absent or `result=NOT_READY`, and `intervention=NOT_REQUIRED/NONE/NONE`. A sand table cannot be terminal while still asking the user to click or while retaining an active main effort.

### `STRATEGIC_OBJECTIVE_ACHIEVED`

All victory criteria must be evidence-derived `PASS`, and no open victory-blocking cleanup debt may remain.

### `NEW_AUTHORITY_REQUIRED`

Use this state only when all of the following hold:

1. Victory criteria remain unmet.
2. The latest action outcome is not `OUTCOME_UNKNOWN`.
3. No alternate route is `OPEN`.
4. At least one route is `REQUIRES_AUTHORITY`.
5. `requiredAuthority` names the missing permission or resource.

### `LOSS_MINIMIZED`

Use this state only when all of the following hold:

1. Victory criteria are not all `PASS`.
2. `victoryUnattainable` is proven by current authoritative `PASS` evidence.
3. The latest action outcome is not `OUTCOME_UNKNOWN`.
4. `alternativeRoutes` is non-empty and contains neither `OPEN` nor `REQUIRES_AUTHORITY`.
5. Every unacceptable outcome has one evidence-backed `PASS` check.
6. Residual-loss measurements are non-empty, and every listed measurement is evidence-backed `PASS`.
7. Every listed preserved gain is evidence-backed `PASS`; an empty list is legal.
8. No open cleanup item with `blocksVictory=true` remains.
9. `requiredAuthority` is empty.

Terminal precedence is `STRATEGIC_OBJECTIVE_ACHIEVED`, then `NEW_AUTHORITY_REQUIRED`, then `LOSS_MINIMIZED`, then `IN_PROGRESS`. In particular, any `REQUIRES_AUTHORITY` route prevents the loss terminal; when the authority predicate is otherwise complete, it derives `NEW_AUTHORITY_REQUIRED` instead.

Every other state is `IN_PROGRESS`.

## Strategic Advance board

The first layer must explain context, current situation, reasoning, next move, and user role in the user’s language. Keep claim IDs, scores, risks, recovery details, and predicates in technical details.

Every victory criterion must include a human-facing `displayText` and a machine-facing `predicate`. Show `displayText` and status in the first layer; keep IDs and predicates in technical details.

The `takeoverReadiness` block exists only while a tactical takeover is contemplated; a state without it is the normal autonomous posture. When present, retain all three gates in state. Expand them in the board only during `TACTICAL_TAKEOVER` with phase `TAKEOVER_REQUESTED` or `USER_ACTION_IN_PROGRESS`. Do not show the three gate cards during autonomous work, `NOT_REQUIRED`, or `BATTLE_DAMAGE_ASSESSMENT`.

From the skill directory, run:

```bash
python scripts/strategic_state.py validate references/example-state.json
python scripts/strategic_state.py self-test references/example-state.json
python scripts/strategic_state.py summary references/example-state.json
python scripts/strategic_state.py render-all references/example-state.json <output-directory>
```

The HTML board recomputes "time since last world-state change" every minute and displays the absolute baseline timestamp. Updating state, reports, or logs never resets that clock.
