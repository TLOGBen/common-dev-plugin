---
name: strategic-advance-jever
description: Lab overlay on common:strategic-advance that adds TypeSafe Jev readings at four judgment points — tagging each intelligence item against the MOE before a scribe consolidation, a posture reading (full / light / stand-down) at the fixed self-check, split/merge confidence when regrouping fronts, and a priority score when choosing the main effort. Use when the user asks for strategic-advance-jever or wants a Jev-assisted campaign; use strategic-advance for ordinary campaigns.
---

# Strategic Advance (Jev overlay)

Use Jev to strengthen anywhere that only needs a judgment — yes/no, choose one, score.

Load and run `/common:strategic-advance` exactly as written; its doctrine, state contract, scribe, validator, and gates are unchanged. This overlay only adds Jev readings at four points. Every reading is **intelligence, never evidence and never command**: it can tell the operator where to look, it never becomes a gating claim, and it never chooses the main effort, triggers a pivot, or changes posture on its own. Default user-facing output to Traditional Chinese.

The scribe cannot call Jev (its Bash set excludes network calls), so every reading runs on the operator side, before the dispatch or decision it informs, and travels into the event packet as a labelled intelligence line: `jev: <item> ev_V1=0.84 ev_V2=0.81 outcome=0.95`.

## Calling Jev

`POST https://api.typesafe.ai/v1/systemone` with `{"model": "jev-latest", "state": "<facts>", "questions": {...}}` and `Authorization: Bearer $TYPESAFE_API_KEY`. If the key is unset (`/common-lab:init-jev`) or the call fails, skip the reading and run the campaign as written. Keep the questions as written here — the operator is an interested party, and rewording moves the probabilities.

## 1. Intelligence vs the MOE (at each consolidation)

Before dispatching the scribe, read every packet item against the locked victory criteria. State: one item's verbatim excerpt plus its one-line intent. Ask one Noul per unmet victory criterion, plus one outcome question:

```json
{"ev_V1": {"type": "noul", "instructions": "Does this item bear on this victory criterion, even as partial evidence: <V1 text verbatim>?"},
 "ev_V2": {"type": "noul", "instructions": "Does this item bear on this victory criterion, even as partial evidence: <V2 text verbatim>?"},
 "outcome": {"type": "noul", "instructions": "Does this item report an observed result in the world, rather than only reporting that work was performed?"}}
```

Read `ev_*` only together with `outcome`: `ev_*` asks whether the item bears on a criterion, not whether it covers it, so a high `ev_*` alone says nothing about how much of the criterion is shown — judging coverage stays with the operator. Every `ev_*` below ~0.3 → the item is **off-MOE**; mark it in the packet and ask whether this consolidation is driven by a verified world delta or only by bookkeeping (the scribe trap). An `ev_*` high with `outcome` low → **MOP, not MOE**: an execution report that points the scribe at a claim to re-probe, never acceptance. When off-MOE items dominate two consecutive consolidations, raise it at the next fixed self-check and with the alignment auditor; do not pivot on the reading alone.

Tested on a synthetic import campaign (one run each): an import log showing 0 failed records scored 0.84 / 0.81 on the two criteria and 0.95 outcome; a logging refactor scored 0.14 / 0.12 (off-MOE); "applied the retry patch and redeployed" scored 0.55 / 0.65 with outcome 0.24 (MOP). Wording matters: "direct evidence about whether it is met" scored the relevant log only 0.25 / 0.37; keep "even as partial evidence". The cost of that recall showed in a field report: process evidence was read as strongly supporting a coding-style criterion — exactly the reading `outcome` and the operator's own coverage check exist to catch.

## 2. Posture reading (at every fixed self-check)

Alongside the doctrine's measured scale reading, ask one Choice. State: the observables the doctrine already names — front count and remaining transitions, fronts with non-empty mutation scope, observer and tool spread, the stall record, time since the last world delta, span of control.

```json
{"posture": {"type": "choice", "instructions": "Which force posture fits this battlefield now?",
  "criteria": {"full": "Many interacting fronts, live mutation surfaces across tools, information volume beyond one head",
               "light": "The loop is proven; remaining slices repeat it at lower novelty and risk",
               "stand_down": "The remaining work is a known linear procedure; the campaign apparatus is no longer needed"}}}
```

The reading enters the ledger next to the doctrine's own reading. It can support a downgrade candidate but never replaces the mechanical downgrade count or the approval that precedes a downgrade; escalation stays a reflex whatever Jev says.

## 3. Split / merge confidence (when regrouping)

Before proposing a restructure, state the front(s) involved — entry and terminal states, mutation scope, recovery path, and the stall record — and ask:

```json
{"regroup": {"type": "choice", "instructions": "Given these fronts and their evidence, what regrouping fits?",
  "criteria": {"keep": "The fronts are fine as they are",
               "split": "One front holds two independently closable transitions throttling each other",
               "merge": "Two fronts now close as one transition, sharing one mutation scope and one evidence set",
               "retire": "No causal chain from this front's terminal state reaches any unmet victory criterion"}}}
```

A confident `split`, `merge`, or `retire` is a reason to write the doctrine's threshold ledger line (projected saving in transitions, rounds, or tool calls) and check the evidence — not a restructure by itself. Below ~60% confidence, keep the map as it is.

## 4. Priority score (when choosing the main effort)

For each candidate front, state its terminal state and the unmet victory criteria, and ask:

```json
{"priority": {"type": "score", "instructions": "How directly does closing this front move the remaining victory criteria?",
  "criteria": ["Serves no remaining criterion", "Supports a criterion indirectly", "Unblocks other fronts toward a criterion", "Directly closes a remaining criterion"]}}
```

Rank candidates by `score` as one input. The operator still assigns the one main effort under the doctrine; a protected-asset risk, an authorization boundary, or the user's direction outranks any score.
