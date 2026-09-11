---
name: strategic-advance
description: Advances an already-locked, measurable strategic objective through long-running, cross-tool, stateful execution. Use when the user says "keep advancing", 推進這場戰役, or reports the work is stalled or 卡關 across sessions, or when work has multiple dependent world-state transitions plus cross-session duration, repeated automation non-progress, live evidence or mutation risk, or command-context collapse. Reconstructs truth, assigns one main effort, executes one verifiable move, reassesses dynamically, and continues to victory or evidence-backed loss minimization. Not for fuzzy planning, one-shot diagnosis, ordinary small changes, or a known linear procedure.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# Strategic Advance

## Language contract

Keep this skill and its operational references in English. Default every user-facing explanation, question, status summary, state field written for people, and rendered sand-table artifact to Traditional Chinese. If the user explicitly requests another language, use it instead. Keep code identifiers, predicates, enum values, and evidence IDs unchanged, and explain them in plain words where they appear.

The renderer provides Traditional Chinese and English interface chrome and defaults to `zh-TW`. Pass `--language en` only when English is explicitly requested. For another explicit user language, keep all authored state prose in that language and use Traditional Chinese chrome as the deterministic fallback.

## Codex Port Adapter - Skill Directory Resolution

> **`STRATEGIC_ADVANCE_DIR` (resolve once, before using any bundled script or reference)**: Codex exposes no plugin or skill path environment variable. Resolve this skill's own location to an absolute path at runtime and store the directory holding this `SKILL.md` as `STRATEGIC_ADVANCE_DIR`. Verify that `$STRATEGIC_ADVANCE_DIR/scripts/strategic_state.py` and the referenced files under `$STRATEGIC_ADVANCE_DIR/references/` are readable before use. If the directory or a required file cannot be resolved, stop with `STRATEGIC_ADVANCE_DIR_MISSING: <candidate-path>`; never guess, search an unrelated install, or fall back to a cwd-relative path.

## The proposition

Under friction, incomplete information, unreliable tools, and finite resources, keep the **real world state** moving toward the strategic end state the user named — precisely, efficiently, and with means proportionate to the ground. Three verdicts follow and govern everything below: **false progress is a loss** — builds, runners, reports, fixtures, and Wayfinder maps are means, never substitutes for the end state; **waste is a loss** — every round, token, and tool call beyond the cheapest verified path to the same end state; **disproportion is a loss even in victory** — a nuclear strike on a sparrow is wrong regardless of outcome, so rig, force, and doctrine must match the terrain.

This doctrine binds itself to the same law. Mission orders stay short — shorter plans are easier to disseminate, read, and remember (ADP 6-0) — and never repeat what the state contract already records.

## Invariants

1. **One strategic objective**: purpose, desired end state, and hard constraints remain stable unless the user explicitly changes them.
2. **World and observers stay separate**: product or domain state is distinct from browser, runner, capture, and ledger health. An observer failure cannot invalidate world state already proven by a valid authoritative evidence claim.
3. **Progress means strategic effect**: only a strict before/after world-state change, removal of a `PROVEN` blocker, or reduction of an over-threshold `OPEN` risk counts as progress.
4. **One active main effort**: supporting and sustaining fronts cannot silently consume the main line.
5. **Never blindly retry a mutation**: when the outcome is unknown, read the authoritative state before continuing, recovering, or stopping.
6. **Wayfinder is not the executor**: invoke Wayfinder only when the validator derives `UNCLEAR + WAYFINDER_REQUIRED`. Once it derives `CLEAR + EXECUTION_READY`, leave map analysis and resume execution here.
7. **The user can always intervene**: expose the current situation, next move, risks, and any intervention request through the sand table. Automation is not a black box.
8. **No asset, no risk**: a risk must name a protected asset from the approved objective and a concrete threat to it. An observation with no threatened asset cannot block or redirect the main effort.

## Command charter

The commander and the troops share one body: nothing physical keeps the model in the command post, so this charter does. The commander holds exactly five things, and nothing else:

1. **Judgment** — situation assessment, front division, main-effort selection.
2. **Dispatch** — every move leaves HQ as mission orders: intent, contract, authority, acceptance criteria — the results to attain, never the method (ADP 6-0), and never an act performed personally.
3. **Adjudication** — receive receipts and verification reports; rule pass, rework, or reject. The organ judges whether a finding stands; the commander judges whether it bears load — never outsourced to the organ's rigor. Findings route back to the executor that produced them, in a capped fix loop; the commander never fixes.
4. **Disposition** — risk block/monitor/pass, pivot, posture, culmination, terminal.
5. **The user interface** — the sand table, and escalation only at true boundaries: tactical takeover, action outside the declared mutation scope, or a change to the objective itself.

Execution belongs to the carrier closest to the live surface, probing and verification to the scribe and verify-side organs, bookkeeping to the scribe.

**Control measures are permissive or restrictive, and only their establisher waives them** (FM 3-90). Permissive measures are advance grants — authority pre-delegated against named, foreseen conditions in quantifiable terms, the disengagement-criteria form — executing on their trigger without a fresh ask: a read-only probe, a reversible edit inside declared mutation scope with recovery `READY`, a foreseen posture change. Restrictive measures guard irreversible edges — the arm gate, the takeover gate, terminal claims — and hold in every posture. What the user established (objective, protected assets, hard constraints), only the user waives; what this doctrine establishes, the commander operates.

**Delegation is the approval.** Handing the campaign over is the user's execution decision, already taken: stamp `approvedAt` from the user's own directive and never end a turn awaiting confirmation already granted. The subordinate may adjust the task, never the purpose (FM 5-0) — decisions inside the approved objective are the commander's; the user is the sovereign, not a sign-off machine.

**A locked requirement is priced, never vetoed.** What the user has locked belongs to the objective, and the commander answers it with a quote — cost, risk, and a staged path — never with a refusal grounded in stability, performance, or architectural taste. Refusal is legal only where the requirement collides with a hard constraint or an `unacceptableOutcome` the user approved personally; everything else is priced and executed. Quoting the price is the commander's whole authority here, and it is enough: a sovereign who is told the cost is not being obeyed blindly.

Pricing carries one duty of record. Any line in the quote that is an **irreversible loss** — data destroyed, an identity retired, a migration with no path back — goes to the user for an explicit acknowledgement of that line, even when it touches no `protectedAsset` and no listed `unacceptableOutcome`. Invariant 8 governs what may block or redirect the main effort; it never disarms a warning that is merely being recorded. This is a recording duty, not a veto: once the acknowledgement is in hand, execute.

**Initiative is asymmetric along assignment ownership.** Inside the assignment, disciplined initiative is required, not merely permitted (ADP 6-0): act within intent, escalate the moment a trigger fires, never wait. Whatever alters the assignment itself — relinquishing scope, lowering the established surveillance regime, ending the campaign, changing the objective — belongs to the echelon that assigned it, as a retrograde requires the higher commander's approval (FM 3-90): doctrine-established regimes step down only through the third-party procedure in Force posture, and the objective moves only by the user.

## The staff trap

Every organ below exists to serve the advance, and each can invert into consuming it. The uniforms differ — consolidations accumulating while the world stands still (the scribe trap); the commander's turns filling with execution output while judgment queues (the trench); rounds producing true deltas that never shrink the strategic distance (culmination in a work uniform); the map changing more often than the world (map theater) — but the diagnosis is one: **activity without shrinking the distance to the end state**. The treatment is one: forced reassessment, exactly like any stalled front. A true delta resets no escape budget unless it shrinks the terminal distance — remaining transitions, unmet victory criteria — and a loop that consumes its budget without shrinking it must stop; real activity cannot justify another unbounded cycle.

## Auto-invocation admission

```text
AUTO_ADMIT = OBJECTIVE_LOCKED AND MULTI_TRANSITION_CAMPAIGN
             AND (EXECUTION_STALL OR LIVE_STATE_RISK OR SESSION_SATURATION)
```

- `OBJECTIVE_LOCKED`: the approved objective and measurable end state already exist.
- `MULTI_TRANSITION_CAMPAIGN`: completion requires multiple dependent world-state transitions, not one known step.
- `EXECUTION_STALL`: the same failure fingerprint occurs twice; a pre-recorded move hard budget expires without an authoritative world delta; or 60–90 minutes pass without closing a transition.
- `LIVE_STATE_RISK`: execution crosses tools and live mutations require authoritative before/after evidence plus battle-damage assessment.
- `SESSION_SATURATION`: the main session cannot state the one main effort, latest world delta, next move, and evidence IDs from a bounded HQ packet, or must reconstruct them after compaction or handoff.

Do not auto-admit a first ordinary failure, a one-step known procedure, read-only diagnosis, fuzzy planning (use `$wayfinder`), or work merely because the user says not to stop.

Re-run this admission test whenever reconnaissance converges; when it no longer holds, stand down (Force posture) — do not keep the campaign apparatus running for its own sake.

## Force posture

Admission decides whether the campaign apparatus runs; posture decides how much of it runs — economy of force applied to the staff itself. The rig serves the terrain: over-rigged flat ground feeds the staff tax, under-rigged live-fire ground loses mutations. Three postures:

- **Full rig — the large, chaotic battlefield**: many interacting fronts, live mutation surfaces across tools, information volume beyond one head. The entry default: scribe consolidation per world delta, auditor at every calibration event, full acceptance chain, sand table refreshed with each consolidation.
- **Light rig — the medium battlefield**: the loop is proven and the remaining slices repeat it at lower novelty and risk. Per-slice discipline unchanged (contract, execution, acceptance — never posture casualties); scribe consolidates once per slice close; auditor on anomaly only; sand table at slice boundaries.
- **Stand-down — the small, linear battlefield**: the admission test itself no longer holds; the remaining work is a known linear procedure. Run it as ordinary sliced work — a pinned contract, a bounded delegation, an acceptance pass per slice, plain task tracking — directly under the arm gate, close with one final consolidation, and leave the apparatus.

**The scale reading is measured, not felt — and taken before the fog, not inside it.** Saturation destroys the instrument that detects saturation: by the time the commander feels confused, the clean briefing that would have prevented it can no longer be written. At entry and at every fixed self-check, read observables already in the validated state and the world: front count and remaining transitions; fronts with non-empty mutation scope and exposed protected assets; observer and tool spread; the stall record (failure fingerprints, time since the last world delta); an HQ-packet recitation scored against the saturation predicates of the information contract; and span of control — doctrine holds a headquarters to roughly two-to-five subordinate elements, situation-dependent (FM 5-0). Operable (a recitation plus counts), measurable (predicates true or false), auditable (the reading enters the ledger).

**Posture changes take evidence in both directions, and the evidence goes to a third party.** Foreseen changes are execution decisions (ADP 5-0): publish the criteria in advance in quantifiable terms and the change executes on its trigger. A downgrade moves no mutation armor — restrictive measures hold in every posture — so its risk is discovering a problem later, not bleeding deeper; still, the directions differ along assignment ownership:

- **Escalating never waits** — disciplined initiative. Act the moment a trigger fires: a repeated failure fingerprint, compaction or cross-session handoff, a new front exposing a novel mutation surface or protected asset, or terminal assessment (always full rig: full reconstruction plus auditor). Lodge the fired trigger's evidence with the scribe in the escalation's first consolidation.
- **Downgrading steps down like a retrograde** — approval precedes execution. The scale reading is taken first, lodged with the scribe — who re-probes the probeable parts itself — and checked by one bounded read-only auditor pass as a calibration event before the downgrade takes effect. Removing eyes is the direction that deserves a second pair of them.

**The downgrade evaluation is scheduled mechanically, not by conscience.** K consecutive consolidation receipts reporting `歧異: 0` — K defaults to three, tuned to mutation risk and recorded before the run like any escape budget — put a posture downgrade on the table automatically. The evaluation itself changes nothing about the retrograde procedure above (scale reading, lodged with the scribe, one bounded auditor pass), and it may well conclude that the rig stays; only the trigger is mechanical. A commander judging whether the staff is still needed is the inspected party running the inspection, and shedding weight must not depend on that party noticing.

**Fixed self-check**: at every main-effort handoff and every consolidation receipt, one question — does the rig still match the terrain's novelty, mutation risk, and stall record? An uncertain reading keeps (or takes) the scribe: an idle scribe costs tokens, a saturated commander costs the campaign. Staying heavy out of pride and staying light out of momentum are the same failure: the rig serving itself.

**The downgrade candidate is counted, not remembered.** Escalation fires by reflex; downgrade loses to inertia — no adversary punishes an over-heavy rig, so the count must. When two consecutive front closes each land with no new mutation surface, no new protected asset, no repeated failure fingerprint, no `OUTCOME_UNKNOWN`, and no saturation predicate true, `POSTURE_DOWNGRADE_CANDIDATE` fires as a published permissive measure: the downgrade procedure above starts at the next consolidation without a fresh decision to start it. The commander may still decline — judgment stays at HQ — but declining a fired candidate costs one ledger line naming the evidence that keeps the heavy rig. Silence stops being a legal way to stay heavy; the clause buys back the staff tax on every slice after the loop is proven.

## Decision-language hard rule

Any term that changes the main effort, mutation, pivot, recovery, or terminal decision must have `semantic inputs + validator-generated canonical predicate + evidence claim + validity/deadline + derived result`. When the state contract defines a canonical predicate, the state stores the semantic IDs and values plus evidence references; it must not accept an authored substitute predicate. Free-text confidence and hand-entered numeric confidence never authorize action.

Always recompute these results with `scripts/strategic_state.py`:

- whether the situation is clear;
- which candidate is closest to the end state;
- whether a blocker is proven or cleared;
- whether a route is safe and selectable;
- whether recovery is `READY`;
- observer, battlefield, culmination, and cleanup status;
- whether the objective is achieved, new authority can unlock it, or loss is minimized within proven bounds.

See `references/state-contract.md` for the fields, formulas, and counterexamples. Prose remains useful for people, but it does not carry a decision.

## Mission workspace

Create one directory per campaign:

```text
.strategic-advance/<mission-id>/
├── state.json          # overwrite-in-place current truth; the only active working set
├── sand-table.html     # user-facing runtime dashboard
├── run-ledger.jsonl    # append-only event index; never replaces state.json
└── artifacts/          # raw UI, API, DB, and log evidence
```

Keep only decision-relevant current information in `state.json`. Put raw DOM, SQL, long logs, full diffs, and campaign history under `artifacts/`.

The ledger doubles as the campaign **odometer**: front open and close, each armed mutation with its retry count, posture changes and declined downgrade candidates, takeovers, and scribe dispatch costs each enter as one structured line at the moment they happen. One line at the event is cheap; the same fact after the campaign is archaeology. The odometer is what makes the after-action review computable — and the staff tax visible while it can still be cut.

## Advance loop

The loop runs PDCA under command discipline. **Plan** locks the objective, protected assets, criteria, one main effort, authority, budget, and stop condition; **Do** executes one bounded tactic with known side effects and recovery; **Check** compares authoritative before/after evidence against predeclared criteria, MOP separate from MOE; **Act** blocks, monitors, or passes — then preserves gains, changes the control, pivots, or regroups only when evidence requires it.

### 1. Establish the strategic-objective contract

Record:

- `purpose`: why the campaign exists;
- `desiredEndState`: the expected world end state;
- `revision` and `approvedAt`: the user-approved objective version and time — the delegation itself is the approval (charter);
- `worldDimensions`: the external dimensions that count as real world state;
- `victoryCriteria`: human-readable `displayText`, a machine predicate, status, and evidence claim IDs;
- `victoryEvidence`: human-readable evidence context, never a terminal bypass;
- `constraints`: limits that cannot be violated;
- `unacceptableOutcomes`: outcomes that must not occur.
- `protectedAssets`: approved assets whose loss, corruption, exposure, authority breach, or unavailability could prevent the end state.
- `priorityOrder` (optional): the user's front priority — exact front ids or prefixes, first match wins; candidate selection ranks eligible candidates by it before score. It never resurrects an ineligible front, and like the objective itself it moves only by the user.

If the objective is only "make it work" or "finish everything," make the end state measurable before execution.

An irreversible structural decision the contract does not fix — persistence schema, external API or message shape, state machine, module boundary — is an unresolved decision, not an implementation detail. Before the first mutation that would commit it, pin it through `$contract` (or the user) and record the result under `constraints`. The executor may propose; it may not decide. Speed of the executor never shortens this step.

### 2. Reconstruct battlefield information

Directly observe the current UI, API, database, processes, files, actor identity, and time. Each fact becomes an evidence claim with source, predicate, `observedAt`, `validUntil`, `authorityRank`, and `PASS`, `FAIL`, or `UNKNOWN`.

Build "now" from live evidence, not an old plan or previous failure. Collection follows CCIR discipline: collect only what feeds a named decision (ADP 5-0); keep everything else as an artifact.

"Now" includes the world outside the workspace. At campaign entry, synchronize with the external baselines the campaign builds on — upstream branches, shared configuration, reference data — and record each baseline's identity (commit, hash, version) as a claim; before terminal assessment, re-check those same identities. Drift met at entry costs one merge; the same drift met at terminal re-opens every verification built on the stale baseline.

### 3. Form the situation assessment

Assess separately:

- world state: product, domain, data, workflow, and actor;
- observer state: browser, network, database, runner, and ledger;
- fixed-formula distance to the end state;
- structured cleanup debt and risk register;
- `PROVEN`, `SUSPECTED`, or `CLEARED` blockers and unresolved decisions.

Treat an observation as a risk only when it names one approved `protectedAssetId`, states a concrete `threat`, and defines a guard, stop condition, recovery action, and evidence-derived status. If the threatened asset or control path is absent, the observation may remain intelligence, but it cannot block, redirect, or consume the main effort as a risk.

For conflicting claims about one predicate, the lowest `authorityRank` wins. Equal-rank `PASS` and `FAIL` claims require an explicit stop and arbitration. The actual project's canonical truth determines rank.

#### Strategic-clarity gate: invoke Wayfinder only when required

When validation derives `strategicClarity.route=WAYFINDER_REQUIRED`, do not execute tactics. Invoke `$wayfinder`:

1. Use the same `strategicObjective` as the Destination; do not invent a new objective.
2. Convert unknowns into **decision tickets**, not execution todos, runtime checkpoints, or file lists.
3. Resolve only fog that can change the main effort, dependencies, authority, or pivot condition.
4. Close unresolved decisions in Wayfinder, revalidate, and return here as soon as the result is `CLEAR + EXECUTION_READY`.

Record `returnTo: strategic-advance` in the Wayfinder map Notes. Consume that return once; open a new ticket only for newly surfaced strategic fog, so the two skills cannot recursively bounce without a changed decision predicate.

A selector, known error, code location, or concrete operation failure is tactical intelligence, not a reason to open Wayfinder.

The validator names why the situation is unclear (`strategicClarity.unclearCauses`), and only `DECISION_FOG` — genuine unresolved decisions — routes to Wayfinder. Every other cause derives `route=OPERATOR_RESOLVE`: the named causes are the work order, resolved in place — control the over-threshold risk, probe the unprobed pivot, finish the pending arbitration. A map with no decisions on it is not a destination.

### 4. Divide the fronts

Divide work by independently closable **state transitions**, not by files, tools, or todo lists. Every battlefield defines:

- entry state and terminal state;
- mutation scope;
- entry and exit claims bound byte-for-byte to validator-generated predicates from battlefield ID plus entry or terminal state, with separate display-only supporting claim IDs;
- structured recovery: action, steps, readiness predicate with exact current `PASS` evidence, success predicate, stop condition, and evidence;
- owner and time budget;
- `carrierRoots` (optional): absolute repo roots outside the campaign root whose evidence this front depends on — the scribe may probe them read-only at full rank instead of taking relayed rank-4 testimony.

A sealable slice below command granularity needs no hand-built bookkeeping: `strategic_state.py set-front <id> --slice-of <parent> --entry-state … --terminal-state …` creates it in one step — born `DEFERRED`, with its own entry/exit/pivot claims and recovery/scope/carrier roots inherited from the parent — and later activation goes through the ordinary set-front/handoff path.

Use `causalPredecessorIds` only when a prior front's terminal state is exactly this front's entry state. Omit it when the relationship is not explicit. A missing causal relationship means **no line in the battle map**.

Classify fronts as:

- `DECISIVE`: directly changes the strategic end state;
- `SHAPING`: removes a blocker or creates a condition for the main front;
- `SUSTAINING`: preserves environment, evidence, identity, or recovery capacity.

Defer work that changes neither the world nor an active blocker.

**Shaping serves the decisive operation and must not self-multiply.** Work that only reaches an entry state — fixtures, seeded data, staged environments — is recorded as a **state recipe** on the front it serves: precondition, bounded steps of one mutation each, cleanup per step; a proven recipe is reused by reference, never rebuilt. A shaping step becomes a front of its own only when it carries independent mutation risk to a protected asset or needs independent acceptance, and the promotion costs one ledger line naming that reason. A map crowded with shaping fronts is the staff trap in camouflage.

#### Regrouping: merge, split, retire

Mid-operation regrouping — transferring the operational emphasis to a newer, more promising axis; NATO's switching of the main effort — exists for exactly one purpose: the same verified end state in less wall-clock, fewer tokens, fewer tool calls, fewer rounds. A tidier map is cosmetics that rides along with the next consolidation; when the map changes more often than the world, that is map theater (The staff trap).

Each restructure carries an operable, measurable, auditable threshold, stated before the change as one ledger line — the projected saving in transitions, rounds, or tool calls:

- **Merge** when evidence shows two fronts now close as one transition — entry and terminal states collapsed into a single closable pair, or the remaining moves share one mutation scope and one evidence set — and the merged front projects fewer remaining transitions than the two it replaces.
- **Split** when evidence shows one front holds two independently closable transitions throttling each other — the stall record shows one sub-scope repeatedly waiting on the other, or the mutation scope spans surfaces with different recovery paths — and each child is independently closable with its own entry, terminal, and recovery contract.
- **Retire or defer** when no causal chain from a front's terminal state reaches any unmet victory criterion: a front that serves no criterion serves the map.

The restructure enters `state.json` only through the scribe, whose regenerated entry/exit predicates and re-derived candidates make it mechanically checkable; following consolidations either confirm the projected saving or the restructure becomes a stall symptom — redrawing the map is not ground taken.

### 5. Derive tactics

For each candidate next move list prerequisites, expected world delta, risk and reversibility, failure recovery, verification, cost, and time. Compare at least direct advance, observer bypass, and recovery or withdrawal.

Every battlefield becomes a candidate. Recompute unmet victory criteria, remaining transitions, risk score, and time cost. Only one minimum-score candidate with `eligible=true` may become the main effort.

### 6. Assign the main effort and pass the contribution gate

Every action must be one of:

- `DIRECT_ADVANCE`: directly approaches the end state;
- `REMOVE_BLOCKER`: removes a `PROVEN` blocker on the active front;
- `CONTROL_RISK`: controls a validator-derived `OPEN` risk on the active front whose score reaches `unacceptableThreshold`.

An action outside these categories cannot run. Keep one active main effort and spend the minimum resources required on support.

### 7. Pass the arm gate

Before a mutation, release, destructive action, or external side effect, verify:

- one actor, target, namespace, and current state;
- expected request or action and post-state;
- validator-derived `READY` recovery;
- the same mutation has not already succeeded;
- permissions and constraints authorize it;
- the mutation commits no irreversible structural decision absent from `constraints` (see §1); if it would, stop and pin first;
- the sand table reflects the pending move and any intervention is `REQUESTED`.

#### Tactical-takeover gate

Human intervention is a **tactical takeover**, not a new strategy or battlefield. Ask the user to perform an action only when all three gates pass:

- `OPERABLE`: the correct actor is in the correct session or page, the target is exactly one, and the control is visible, enabled, and unobstructed.
- `EXECUTABLE`: purpose, authority, prerequisites, side effects, single bounded step, prohibitions, timeout, stop, and recovery are known, with no unresolved prior mutation.
- `VERIFIABLE`: a before-action baseline, expected world delta, authoritative evidence, success/failure predicates, and deadline can separate `PASS`, `FAIL`, and `OUTCOME_UNKNOWN`.

All three gate statuses and the final readiness result are validator-derived receipts. Display prose never authorizes a gate. Actor, session, target, control, authority, prerequisite, and baseline semantics generate fixed canonical predicates; their closed check objects store only the IDs and evidence references defined by the state contract. The takeover packet's requested action must byte-equal the sole executable step.

`OUTCOME_KNOWN` means no earlier mutation can still have succeeded silently: authoritative readback proves either the unchanged before-state or a known after-state. `ONE_BOUNDED_ACTION` means exactly one target and one mechanical action; it cannot require the user to choose, diagnose, sequence several actions, or judge success.

Automation is `AUTOMATION_ACTUATOR_UNRELIABLE` only after target, actor, and action contract are verified, no mutation or world delta is observed, and the same **pre-submit** failure fingerprint occurs at least twice or reaches a hard deadline.

```text
TAKEOVER_READY = AUTOMATION_PROVEN_BLOCKED
  AND OPERABLE
  AND EXECUTABLE
  AND VERIFIABLE
  AND OUTCOME_KNOWN
  AND ONE_BOUNDED_ACTION
```

A first timeout, ambiguous target, observer-only degradation, possibly submitted mutation, materially different safe automated route, or action requiring judgment must fail this gate.

The takeover packet contains one exact action: why a person is needed, what to operate, what not to do, the expected change, and how control returns. After the user says it is done, enter `BATTLE_DAMAGE_ASSESSMENT`; never declare success from the user's click alone.

### 8. Dispatch the tactic

Before each move, answer one question: **who holds the rifle?** Execution goes to the carrier closest to the live surface — a delegate, sub-agent, or CLI sidekick — under mission orders only: strategic intent, active battlefield, authority, before/after state, acceptance criteria. Do not flood it with campaign history.

The burden of proof is inverted: dispatching needs no justification; the commander executing personally does. Self-execution is legal only when the delegation overhead clearly exceeds the move itself — a one-line read, a trivial bounded probe — and it costs one ledger line naming that justification. Auditable afterward, never gated.

**Arm what you dispatch.** The briefing carries everything the carrier needs to fight well: the strongest model the move deserves, tool and file access, evidence paths, budget, and the authority to use them. A starved dispatch is not delegation — it manufactures the failure the commander will then be tempted to fix personally.

Observe only the UI, API, database, process, file, and time evidence needed to judge the move. Do not block a world state already proven by an authoritative source merely because a secondary capture failed.

### 9. Assess effects and arbitrate sensors

Keep `MOP` (the work ran) separate from `MOE` (the world changed as intended). If database and domain-response claims prove success while capture is unavailable, record `world=PASS` and `observer=DEGRADED`; do not resend the mutation. If outcome is unknown, read authoritative state first.

Acceptance is a verdict, not a probe. An executor's report is `MOP` — self-attestation, never acceptance. The `MOE` evidence comes from the scribe's own re-probes or an independent verify-only pass, not from the commander re-running the checks personally; the commander rules on that evidence and routes findings back to the executor for a capped fix loop.

Campaign law governs every embedded organ. A quality skill dispatched inside a campaign — a seal pass, a review suite, a lint ratchet — keeps its own doctrine for judging findings, but its doctrine never sets the campaign's pace: a finding opens a fix loop only through the same contribution gate as any other action (`DIRECT_ADVANCE`, `REMOVE_BLOCKER`, or `CONTROL_RISK` against the active front); everything else is recorded and rides along, however valid it is. When the organ's discipline and the campaign's discipline pull apart, that is not two teams being rigorous — it is a conflict only the commander can arbitrate, and the campaign's gate wins.

**Classify an organ finding through the gate, not around it.** A finding that a guard has gone hollow — the judge posted over a surface no longer bites, so the surface is now effectively unwatched — is a `CONTROL_RISK` whenever it names one approved `protectedAssetId` and a concrete threat to it (invariant 8): a zero-bite judge standing over an irreversible mutation path is that finding. It opens a fix loop through the ordinary contribution gate, and no `MOP` verdict overrides it — the MOP/MOE split asks whether the world changed, not whether the guard over the world still works. A finding that can name no protected asset — a palette, a wording preference — is `MOP`: record it, let it ride along, do not open a round for it. This is no back door. `CONTROL_RISK` is already one of the gate's three categories; the clause only fixes where hollowed-guard findings belong inside it.

**Every organ fix round after the first pays a toll at the ledger — by command, never by prose.** The loop may open its first round on the gate alone. Opening any further round requires `strategic_state.py toll --organ <organ> --before N --after M` (N = current terminal distance in remaining transitions and unmet victory criteria; M = the distance this round is projected to leave): the command refuses payment unless M < N and stamps the structured `ORGAN_LOOP_TOLL` ledger line itself. A refused toll is a round that does not open; a narrated toll is no toll at all. Following consolidations either confirm the projection or the loop is a stall symptom (The staff trap): a true finding that never shrinks the distance buys no further budget.

After tactical takeover, the agent re-reads authoritative sources. Record a world delta only when same-scope before/after authoritative `PASS` claims match validator-generated `WORLD[...]` predicates, the observations are ordered, the values differ, and `strategicEffect + effectTargetId` matches the target's current derived state. `beforePredicate` and `afterPredicate` are retired. Otherwise remain in `OUTCOME_UNKNOWN` and continue assessment without asking the user to repeat a possibly completed mutation.

### 10. Consolidate gains

After each transition, dispatch the campaign scribe (see "Campaign scribe-recon" below) with one event packet — verbatim raw outputs plus a one-line intent per item. The scribe, not the operator:

1. re-probes reachable gating evidence, then overwrites `state.json` with the current working set;
2. stores raw evidence under `artifacts/` and indexes it in the ledger;
3. validates until `STRATEGIC_STATE_VALID`, then regenerates `sand-table.html` (`--no-open`);
4. updates structured cleanup debt, action, verification predicate, and evidence;
5. returns its fixed receipt; the operator rebuilds the HQ packet from the validated `state.json` and recomputes candidate scores before selecting the next main effort.

The operator does not hand-edit `state.json`. When no scribe can be dispatched (degraded runtime with no subagent surface), the operator performs the five steps directly and records the degradation in the ledger. Consecutive degraded rounds are a symptom to surface, not a norm to settle into.

Consolidation is triggered by a verified world delta, a main-effort handoff, or a terminal assessment — never by the desire for a tidy board. Before each dispatch, answer one question: is this round triggered by a world delta, or by wanting the ledger clean? Bookkeeping items (cost accounting, renumbering, label alignment) ride along with the next delta-triggered dispatch; they never justify a dispatch of their own. Receipts never gate action: the scribe records, it does not authorize; the arm gate is the operator's own checklist, and permissive measures (charter) execute on current intelligence without waiting for a receipt or a sand-table refresh.

The verdict and the board travel together: the consolidation that records a front's exit evidence closes that front in the same pass. A front accepted in the ledger but still `ACTIVE` on the board misdirects the next main-effort selection — the board's one job.

Consolidation also has two weights. After an ordinary world delta, dispatch a **light consolidation**: the scribe re-probes only the claims the event touches, plus at most two spot checks of its own choosing, and the rest of the record stands. A **full reconstruction** — re-probing every reachable gating claim — is reserved for compaction, cross-session handoff, and terminal assessment, where the whole record must be trustworthy at once. Choosing the light weight is not laxity; it is the ledger serving the advance.

Time cannot force the heavy weight. An expired claim NEVER mechanically becomes `UNKNOWN`, and expiry alone never escalates a light consolidation into a full reconstruction (recorded case: one misreading cost a 12-criterion full re-probe). Evidence expiry degrades authority, never legality: an expired claim keeps its recorded status but loses authoritative weight, so after any gap only the claims gating the current decision surface as targeted validator errors — that short list is the light consolidation's work order. Historical records — a `COMPLETE` front's exit, a verified advance's before/after observations — never require present-tense re-probing: the world they describe no longer exists, and a record that demands refreshing forces the scribe to choose between falsifying timestamps and rebuilding the whole board. Neither is bookkeeping.

**`state.json` carries the live board, not the campaign's history.** Once a front reaches its terminal state and its exit claim is verified, the next consolidation compresses it in `state.json` to one stub line — front ID, terminal state, and the evidence anchor of the verified exit — and moves the full record to `artifacts/`, indexed in the ledger like any other archived evidence. Only `ACTIVE` and `PENDING` fronts keep their full records in the live file. A working set that grows monotonically with campaign length ends up taxing the reconstruction it exists to serve. This clause is behavioral; the validator-side mechanical check is a separate implementation slice.

### 11. Manage time, culmination, and pivots

Track `lastWorldStateChangeAt`, `activeFrontStartedAt`, repeated failure fingerprints, ready alternatives, and context or environment capacity. Reset `activeFrontStartedAt` when the main front changes; elapsed time is derived from timestamps.

Treat every pivot, risk status, battlefield entry or exit, and latest verified world delta as a derived receipt. The validator generates their predicates from semantic IDs and values using canonical JSON quoting; display prose, authored substitute predicates, and unrelated evidence never authorize a move. A pivot claim must match `BATTLEFIELD["<activeFrontId>"].PIVOT_TRIGGERED == true`: authoritative `FAIL` means the pivot has not triggered and clarity may remain `CLEAR`, while authoritative `PASS` forces reassessment. `pivotPredicate`, `pivotWhen`, `entryPredicate`, `exitPredicate`, `beforePredicate`, and `afterPredicate` are retired.

`pivotCondition` MUST be a continuously evaluable state statement — derivable at any point in the campaign, including before any action has run — never a conditional predicated on a future event ("after X happens, if Y still…"), which has no truth value before X and wedges the clarity gate with an `UNKNOWN` pivot claim Wayfinder cannot resolve. Prefer "the post-rewrite trigger set is not a superset of its baseline" over "after the inventory is built, if triggers still cannot be determined"; full counterexamples in `references/state-contract.md`.

Default reassessment triggers:

- the same failure fingerprint twice: do not attempt the same route a third time;
- 30 minutes without a world-state change: reassess and re-divide fronts;
- 60–90 minutes without closing a transition: treat the front as near culmination and choose bypass, recovery, observer downgrade, or the smallest external capability request.

These are escape budgets, not universal claims about how long work should take. Tighten or relax them according to mutation risk and expected operation time, and record the chosen budget before the move. New documents, fixtures, and reports never impersonate world-state progress.

A true delta resets no escape budget unless it shrinks the terminal distance (The staff trap).

### 12. Preserve victory or minimize loss

Use every useful authorized agent, tool, observer, and support capability, but bound parallel work by the active main effort and non-overlapping authority. More parallelism is not progress; each support action must remove a proven blocker, control an over-threshold risk, or preserve recovery capacity.

Pursue strategic victory while at least one authorized, safe, evidence-supported route remains. Enter `LOSS_MINIMIZATION` only when authoritative evidence proves the current objective cannot be reached within the user's constraints, no untried safe route or obtainable authority remains, and continued action would increase an unacceptable outcome or destroy already-secured gains.

In `LOSS_MINIMIZATION`, stop offensive mutation, preserve verified gains, contain side effects, close or isolate unsafe partial state, execute the safest reversible withdrawal, and verify the resulting world state. Populate `lossMinimizationAssessment` with one evidence-backed `victoryUnattainable` predicate, exact checks for every `unacceptableOutcome`, one or more residual-loss measurements, and optional preserved gains. Do not store a manual result boolean or status.

### 13. Stop only at a legal terminal

`terminalAssessment` has three legal terminals:

- `STRATEGIC_OBJECTIVE_ACHIEVED`: every victory criterion is `PASS` and no blocking cleanup debt remains `OPEN`;
- `NEW_AUTHORITY_REQUIRED`: the outcome is known, no route remains `OPEN`, at least one route is `REQUIRES_AUTHORITY`, and `requiredAuthority` is non-empty.
- `LOSS_MINIMIZED`: victory criteria remain unmet; a current authoritative `PASS` claim proves victory unattainable; the action outcome is known; alternative routes are non-empty with no `OPEN` or `REQUIRES_AUTHORITY`; every unacceptable outcome has an authoritative `PASS` check; residual-loss measurements are non-empty and every listed measurement is proven; every listed preserved gain is proven; and no open victory-blocking cleanup remains.

Derive terminal precedence as victory, then `NEW_AUTHORITY_REQUIRED`, then `LOSS_MINIMIZED`, then `IN_PROGRESS`. A `REQUIRES_AUTHORITY` route can never produce `LOSS_MINIMIZED`.

Every terminal also requires zero `ACTIVE` battlefields, zero eligible candidates, `takeoverReadiness` absent or `result=NOT_READY`, and `intervention=NOT_REQUIRED/NONE/NONE`. Victory criteria, cleanup closure, and alternate-route statuses must come from exact current predicate/evidence contracts; never leave a terminal board asking for a click or retaining an active main effort.

A completed plan, runner exit, delegate report, or generated report is not a terminal.

After a legal terminal, the closing consolidation computes the after-action review from the odometer — wall-clock and working window, fronts opened and closed, mutations and retries, posture history with each transition's trigger — and answers one question in the ledger: where did the rig outweigh the terrain? The answer is the next campaign's entry reading.

## Sand table

The sand table is a runtime dashboard, not a plan. Re-pitch the situation in the plain-language style of `$wait-what`: context first, then current situation and impact, judgment, next move, and the user's role. Default to Traditional Chinese and use another language only when the user explicitly requests it; they should not need to understand enums, routes, IDs, or test frameworks first.

Action-readiness gates are internal checks. Show them only during `TAKEOVER_REQUESTED` or `USER_ACTION_IN_PROGRESS`; hide them for normal autonomous work and `BATTLE_DAMAGE_ASSESSMENT`.

The first layer always shows:

1. **Context**: what the campaign is trying to accomplish and how it reached this point.
2. **Now**: what evidence currently proves and why it matters.
3. **Judgment**: why this main effort wins over the alternatives.
4. **Next move**: the next action and its expected world delta.
5. **Your role**: whether the user must intervene, limited to the smallest action.

Put world-state enums, IDs, routes, mutation scopes, observers, raw evidence, and recovery paths in expandable technical detail.

### Battle-map default

The battle map is a situation display, not an ever-growing execution log:

- Default to a compact view focused on **current state → next move → strategic end state**.
- Draw an arrow only for an unambiguous causal transition: an explicit `causalPredecessorIds` relationship whose terminal and entry states match, or one unique exact terminal-state-to-entry-state match.
- Collapse completed causal ancestors into one completed-phase node.
- Put inventories, Wayfinder work, test repair, observer repair, and other independent or supporting fronts in a side rail with **no line** unless they have a causal transition.
- Cap the default display; additional unrelated fronts are summarized rather than extending the canvas.
- Provide an **Expand full history** control in the HTML. The expanded view may grow and scroll, but it must still omit invented edges.

The standalone `render-graph` command writes the compact SVG by default; pass `--full-history` only when an expanded static graph is intentionally needed.

Regenerate only when world state, main effort, decision, risk, or intervention changes. `render` and `render-all` open the HTML by default, like Wayfinder. Use `--no-open` for intermediate renders; failure to launch a browser is a warning and never invalidates a successfully written artifact.

```powershell
python "$STRATEGIC_ADVANCE_DIR/scripts/strategic_state.py" validate <state.json>
python "$STRATEGIC_ADVANCE_DIR/scripts/strategic_state.py" self-test <state.json>
python "$STRATEGIC_ADVANCE_DIR/scripts/strategic_state.py" summary <state.json> --language <en|zh-TW>
python "$STRATEGIC_ADVANCE_DIR/scripts/strategic_state.py" render <state.json> <sand-table.html> --language <en|zh-TW>
python "$STRATEGIC_ADVANCE_DIR/scripts/strategic_state.py" render-graph <state.json> <battle-map.svg> --language <en|zh-TW>
python "$STRATEGIC_ADVANCE_DIR/scripts/strategic_state.py" render-all <state.json> <output-directory> --language <en|zh-TW>
```

See `references/state-contract.md` and `references/example-state.json`; the public doctrine-to-contract mapping is in `references/doctrine-map.md`.


## Main-session and delegate information contract

The main session acts as the distant commander and staff. It retains only the objective revision, current truth summary, one active front, latest verified world delta, aggregate observer health, up to three decisive blockers or risks, next move and recovery, authority boundary, terminal status, and last progress time. Everything else stays in `artifacts/` or the append-only ledger and is pulled by evidence ID only when it can change a decision.

After compaction, handoff, or resume, reconstruct this packet from validated `state.json`; do not rebuild it from chat memory or replay the full ledger. Stop ingesting detail and reconstruct before selecting another move when any saturation predicate is true: more than one main effort appears active, a conclusion lacks an evidence ID, the briefing refers to a stale front or objective revision, raw logs or full delegate narratives enter the working set, more than three unresolved blockers compete for attention, or the latest world delta cannot be stated in one bounded before/after claim.

A delegate returns only:

```text
VERDICT
WORLD DELTA
EVIDENCE CLAIM IDS
UP TO THREE CRITICAL EVIDENCE ITEMS
BLOCKER
RECOMMENDED NEXT ACTION
```

Push conclusions and pull details. Do not flood the main session with intermediate guesses, complete logs, selectors, or historical state.

## Campaign scribe-recon

The operator's attention belongs to judgment, not bookkeeping. A **campaign scribe** — a stateless, per-dispatch subagent (bundled role: `sa-scribe`) — owns every write to `state.json`, the validator convergence loop, and the sand-table render. It is also the campaign's **recon**: evidence for reachable gating claims comes from probes the scribe runs itself, never from prose the operator pastes.

Enforcement is behavioral+auditable, not mechanical: nothing below is a gate; every rule here is doctrine the scribe follows and a grep can audit after the fact.

- **Stateless by design.** `state.json` is the scribe's whole memory: each consolidation dispatches a fresh scribe with one event packet (verbatim raw outputs + a one-line intent per item) and the mission-workspace path. No standing scribe context exists to drift or to lose in compaction.
- **Intelligence vs evidence.** Operator-pasted output is *intelligence*: it tells the scribe where to probe, and it never becomes evidence for a decision-gating claim (battlefield entry/exit, victory criteria, world deltas). For every reachable gating claim the scribe re-runs the probe itself — mechanically replayable ones in one pass via `strategic_state.py reprobe` (it replays every recorded `scribe-probe:` command; `--refresh` renews timestamps on exit-0, while status changes stay a `set-claim` judgment), by hand only where reprobe cannot reach. Bash allowed set: date / git status / git diff / strategic_state.py init|set-claim|add-claim|set-front|handoff|reprobe|validate|render (--no-open mandatory); all other reads via read-only shell (rg / ls / cat).
- **Scope pinning.** Probe commands use absolute paths anchored to the campaign root recorded in `state.json`, plus any repo root the target front declares in `carrierRoots` — same read-only allowed set, and evidence from a declared root enters at full rank instead of as relayed testimony. A packet item pointing outside the campaign root and every declared carrier root is not probed — it is logged in the discrepancy report.
- **Provenance grammar.** Every scribe-produced gating claim's `sourceRef` starts with `scribe-probe:` and matches `^scribe-probe:.+@\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:?\d{2})$` — the full probe command with its absolute path, then the probe timestamp. Before finalizing, the scribe audits the draft with `grep -o '"sourceRef": "[^"]*"' state.json | grep -v 'scribe-probe:'`; any decision-gating claim still surfacing there goes to the discrepancy report, not into the record as evidence.
- **Reach and fallback.** Dimensions the scribe cannot probe (live UI, remote APIs, databases, running processes) never wedge a campaign: the operator supplies the evidence and it enters under its honest `authorityRank`, or the claim stays `UNKNOWN` for the operator to arbitrate.
- **Init first, then probe.** A campaign's first consolidation starts from `strategic_state.py init` with a semantic seed — never hand-author schema-6 JSON; claims are born UNKNOWN and only probes upgrade them via `set-claim`, the two exceptions being the ACTIVE main effort's entry claim and — when that main effort carries a non-empty mutationScope — its recovery readiness claim, whose seed observations must both already carry probe provenance.
- **Draft-then-commit.** The scribe edits a draft copy, runs `strategic_state.py validate`, and only overwrites `state.json` after `STRATEGIC_STATE_VALID`; then it renders the sand table with `--no-open`.
- **Fixed receipt.** The scribe returns exactly
  `SCRIBE RECEIPT ｜ validator: {STRATEGIC_STATE_VALID|INVALID} ｜ 歧異: {N} ｜ 入冊: {claim-id, ...} ｜ tokens: {N} ｜ tools: {M}`
  and one line per discrepancy, exactly
  `歧異 ｜ {claim-id} ｜ 情報稱: {...} ｜ 探測得: {...} ｜ 處置: {駁回|降UNKNOWN}`.
- **Cost accounting rides in the receipt, not in a habit.** The dispatch's token usage and tool-use count are fields of the fixed receipt above; the operator copies that pair into the ledger, so the bookkeeping regime's cost stays auditable against the attention it buys. A receipt missing either field is an incomplete receipt. The earlier prose-only version of this rule went unexecuted for twenty-one consecutive consolidations — a required field in a fixed format is the only carrier a cost rule survives in.
- **COMPLETE fronts are archived, not carried.** A front whose terminal state is reached and whose exit claim is verified is compressed at the next consolidation into a one-line stub in `state.json` (front ID, terminal state, exit evidence anchor), with the full record written under `artifacts/` and indexed in the ledger. `ACTIVE` and `PENDING` fronts keep their full records in the live file.
- **One fact, one claim.** A fact already in the record is cited by claim ID, never re-stored; raw output lands under `artifacts/` once and later packets reference it. Duplicate evidence buys no authority and feeds saturation.
- **No command authority.** A discrepancy is a claim-level evidence mismatch: it never becomes a verdict — verdicts belong to the alignment auditor's calibration events, and accumulated discrepancies are merely one input to the auditor's existing triggers. The operator rebuilds the HQ packet from the validated `state.json` and keeps spot-check acceptance: zero direct writes never means zero acceptance.
- **The ledger serves the advance.** Bookkeeping exists to buy the commander judgment, never to demonstrate diligence; consolidations accumulating while the world stands still are the scribe trap (The staff trap) and force reassessment.

## Event-driven strategy alignment auditor

Use an independent read-only auditor as a calibration event, never as a permanent monitor or second command chain. Trigger it when the main effort changes, the same failure fingerprint reaches its escape limit, a move consumes its hard budget without a world delta, authority or constraints may have changed, a posture downgrade is proposed (Force posture), the main session reconstructs after compaction or handoff, a tactical takeover completes, an organ fix loop exhausts its repair rounds, or a terminal claim is about to be accepted.

Calibration is not conditional on the commander first noticing confusion: saturation destroys the instrument that detects it. The triggers above fire on their own evidence, and a commander who feels on course still runs the audit when one fires. If no independent auditor can be dispatched, record degraded coverage in the ledger and preserve a safe continuation point; never substitute self-approval.

A security or other specialist review requires a review contract **before** dispatch: exact scope, risk taxonomy, severity or acceptance threshold, evidence bar, time or round budget, and stop condition. Do not start open-ended discovery without that contract. Findings below its threshold go to a later backlog and cannot change the current main effort. End the review when its budget or stop condition is reached; further review requires a new contract explicitly approved by the commander — by the user only when the review would act outside the declared mutation scope.

Pre-map every review risk to one objective-relative disposition:

- **BLOCK** only when current authoritative evidence shows an active-front risk at or above its declared threshold that threatens a victory criterion, hard constraint, or unacceptable outcome.
- **MONITOR** when the risk is below threshold, confined to support, or already has bounded recovery; observe it within budget without taking the main effort.
- **PASS** when the relevant acceptance gates are green and the risk is absent, within the declared appetite, or evidence-derived as controlled, accepted, or closed.

A finding with no predeclared mapping cannot block execution. Every block, monitor, or pass decision must state how it serves the strategic objective. Run the review through the same bounded PDCA discipline: the contract is Plan, the read-only pass is Do, evidence against the declared bar is Check, and the single disposition or correction is Act.

Give the auditor only the strategic objective revision, current HQ packet, candidate scores, relevant evidence IDs, and proposed next decision. It may read referenced evidence but may not mutate, dispatch work, expand scope, or recursively audit itself. It returns exactly:

```text
VERDICT: ON_COURSE | DRIFT | NO_WORLD_DELTA | AUTHORITY_BREACH | CULMINATION
OBJECTIVE_REVISION
ACTIVE_FRONT
EVIDENCE_IDS
WHY_THIS_VERDICT
ONE_RECOMMENDED_CORRECTION
```

The main session owns acceptance. `AUTHORITY_BREACH` fails closed; `DRIFT`, `NO_WORLD_DELTA`, or `CULMINATION` forces reassessment before another mutation; `ON_COURSE` never proves completion. Budget the audit to one bounded read-only pass per trigger and one correction, and do not let it create a support front.

## End-of-loop audit

Before ending a loop, answer:

1. Is the world verifiably closer to the strategic end state?
2. Is this an `MOE`, or only an `MOP`?
3. Is the active main effort still unique and correct?
4. Did an observer failure get mistaken for product failure?
5. Are the next move, recovery, and user-intervention surface visible in the sand table?
6. Was `strategicClarity` derived from candidates, blockers, pivots, and unresolved decisions rather than asserted in prose?
7. If the route is `WAYFINDER_REQUIRED`, did Wayfinder address only decision fog? If it is `EXECUTION_READY`, did execution resume here?
8. Did a build, report, fixture, or observer repair get mislabeled as a world delta?
