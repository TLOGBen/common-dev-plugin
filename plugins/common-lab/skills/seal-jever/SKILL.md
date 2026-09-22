---
name: seal-jever
description: Lab overlay on baransu:seal that adds TypeSafe Jev readings on the dispatcher side — an importance score that sizes the verification allowance, a consequence grade for findings on surfaces the contract never classified, a severity score for ranking admissible probes, and a check before every mutation probe on whether it can change the "done" verdict or is only MOP. Use when the user asks for seal-jever or a Jev-assisted seal; use /baransu:seal for ordinary seals.
---

# Seal (Jev overlay)

Use Jev to strengthen anywhere that only needs a judgment — yes/no, choose one, score.

Load and run `/baransu:seal` exactly as written; the baseline, the verify-only seal-agent, the fix loop, the re-verification cap, and the sealed marker are unchanged. This overlay adds Jev readings in the main session (the dispatcher) — never inside the seal-agent, which stays a clean, verify-only context. Readings are second opinions: the contract's Surface Inventory impact class stays the severity source of truth, and first-hand evidence (a probe result, actual code at file:line) outranks any score. Default user-facing output to Traditional Chinese.

## Calling Jev

`POST https://api.typesafe.ai/v1/systemone` with `{"model": "jev-latest", "state": "<facts>", "questions": {...}}` and `Authorization: Bearer $TYPESAFE_API_KEY`. If the key is unset (`/common-lab:init-jev`) or the call fails, skip the reading and seal as written. Contract text and findings leave the machine for TypeSafe in the U.S.; skip the readings for client or confidential work unless the user has said TypeSafe is allowed. Keep the questions as written — the implementer and the dispatcher both have a stake in a clean seal, and rewording moves the probabilities.

## 1. Importance → verification allowance (before dispatch)

When recording the required criteria and the finite review/repair allowance (see the seal's verification-effort guidance), state the contract's goal, criteria, and the promised result, and ask:

```json
{"importance": {"type": "score", "instructions": "How consequential is it if the promised result is wrong after this change ships?",
  "criteria": ["Cosmetic — no one would perceive a consequence", "Local — an inconvenience that is easy to undo",
               "Significant — core logic or a downstream contract breaks", "Severe — irreversible data loss, money, security, or compliance"]}}
```

Levels 0–1 support the seal's default starting allowance (one independent review, one focused recheck); levels 2–3 support a bounded discriminating check on the consequential failure paths. The score never raises the re-verification cap and never replaces the contract's impact classes; it only helps size the allowance you record before dispatch.

## 2. Grading findings on unclassified surfaces (fix loop)

For a finding on a surface the contract's Surface Inventory never classified, state the finding, the surface, and the evidence the agent returned, and ask:

```json
{"grade": {"type": "choice", "instructions": "By consequence severity only, how should this finding be graded?",
  "criteria": {"must_fix": "Irreversible consequences (data corruption or loss) or a broken shipped contract (published behavior, licensing, compliance)",
               "surface_asset": "Styling, copy, color tokens, spacing — a low-severity prior unless evidence shows more",
               "low_rank": "A real but minor issue; logged for the user, not fixed"}}}
```

Jev may raise a grade, never lower one that first-hand evidence supports; when your grade and Jev's differ, take the more severe unless evidence settles it, and note both in the report. Grade by consequence only, as the seal requires — not by which mandate point found it, how cheap the fix looks, or how visible the surface is.

## 3. Ranking admissible probes

When several probes have paid their operation-chain entry fee, state each probe's target and the defence breach it would expose, and ask:

```json
{"breach": {"type": "score", "instructions": "How severe is the defence breach this probe would expose if it bites?",
  "criteria": ["Cosmetic surface only", "A local, easily noticed defect", "A family of hollow checks over core logic or a contract", "Irreversible data, money, security, or compliance exposure"]}}
```

Use the scores to order the probes, heaviest first, as the seal's selection standard asks. A probe that would expose a whole family of hollow assertions ranks at the heaviest surface that family guards, whatever its score; the streetlight ban still applies.

## 4. Does this mutation decide "done", or is it only MOP? (before every mutation probe)

The seal treats mutation as a method, not a quota: a probe earns its place only when it can resolve a specific, consequential uncertainty about whether a required outcome holds. Before running each planned mutation, state the contract criteria, the current evidence for the targeted criterion (including how the existing test builds its expected value), and the probe — the mutation, the expected detector, and the criterion it targets — and ask:

```json
{"changes_verdict": {"type": "noul", "instructions": "Could the result of this probe change whether a required criterion is judged met?"}}
```

Below ~0.3 the probe is **MOP** — verification activity that will not move the verdict. Drop it, or record it as optional in the report; do not run it to fill a round. Above ~0.7 it decides "done": run it, and give it the seal's full probe discipline (named mutation, expected detector, baseline, isolation, stopping point, recovery plan). In between, keep it only if you can name the criterion it would flip and why the cheaper existing evidence is insufficient — the seal's own expansion question. The reading never admits a probe that has not paid its operation-chain entry fee, and never excuses skipping a probe that first-hand evidence shows is needed.

Tested (one run each) against an expense-export contract: mutating the `formatAmount()` helper that the existing test also uses to build its expected value — a hollow-judge probe that does decide the criterion — scored 0.86; mutating a debug-log-only helper scored 0.16; mutating a toast color token scored 0.12. A three-way Choice (`decides_done` / `mop` / `redundant`) was tried first and misread the hollow-judge probe (confidence 0.19), so the yes/no form is the one to use.
