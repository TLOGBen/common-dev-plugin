---
name: contract-jever
description: Lab overlay on baransu:contract that adds TypeSafe Jev readings — a task importance score and a slicing check before writing, an assertability check on each criterion, and an impact-class suggestion for each Surface Inventory row. Use when the user asks for contract-jever or a Jev-assisted contract; use /baransu:contract for ordinary contracts.
---

# Contract (Jev overlay)

Use Jev to strengthen anywhere that only needs a judgment — yes/no, choose one, score.

Load and run `/baransu:contract` exactly as written; its one-page cap, G1–G4 rules, template, and the one-round user confirmation are unchanged. This overlay adds Jev readings at three points. Each reading is a second opinion for you and the user to weigh; the user's confirmation in Step 3 still fixes the impact classes and the seal tiers. Default user-facing output to Traditional Chinese.

## Calling Jev

`POST https://api.typesafe.ai/v1/systemone` with `{"model": "jev-latest", "state": "<facts>", "questions": {...}}` and `Authorization: Bearer $TYPESAFE_API_KEY`. If the key is unset (`/common-lab:init-jev`) or the call fails, skip the reading and write the contract as usual. The task text leaves the machine for TypeSafe in the U.S.; skip the readings for client or confidential work unless the user has said TypeSafe is allowed. Keep the questions as written — whoever writes the contract is an interested party, and rewording moves the probabilities.

## 1. Importance and slicing (before writing)

State: the user's request and the files or modules it will touch.

```json
{"importance": {"type": "score", "instructions": "How consequential is this change if it goes wrong?",
   "criteria": ["Cosmetic — no one would perceive a consequence", "Local — an inconvenience that is easy to undo",
                "Significant — core logic or a downstream contract breaks", "Severe — irreversible data loss, money, security, or compliance"]},
 "needs_slicing": {"type": "noul", "instructions": "Does this request contain more than one independently verifiable change that should each get its own contract?"}}
```

A high `needs_slicing` is a prompt to apply the contract's own rule — name the slice boundary and write one contract per slice — when the draft also runs past one page. `importance` sets how much care the impact column deserves and whether to recommend `/baransu:seal` afterward; at levels 2–3 say so in the confirmation. It never waives a Surface Inventory row the four questions keep.

## 2. Assertable criteria (Step 2, per criterion)

State: one criterion as drafted.

```json
{"assertable": {"type": "noul", "instructions": "Can this criterion be checked by a test, command, or exact comparison with a pass/fail result?"}}
```

Below ~0.5, treat it as a vague criterion under G1 and rewrite it before showing the contract; mark it 已改寫自模糊表述 in the confirmation.

## 3. Impact class (Surface Inventory, per row)

Work each row through the contract's four questions as written, then ask Jev for the class. State: the surface, its format, and the asset and owner it touches.

```json
{"impact": {"type": "choice", "instructions": "What is the worst realistic consequence class if this surface is wrong?",
  "criteria": {"irreversible_data": "不可逆／資料: data loss, corrupted or misbooked records, money",
               "logic_core": "邏輯核心: core business logic produces wrong results",
               "downstream_contract": "上下游契約: a parser, API consumer, scheduler, or other system breaks",
               "stability": "穩定性可靠性: crashes, hangs, resource exhaustion",
               "ui_ux": "UI/UX: a person is inconvenienced or confused but no data or system breaks"}}}
```

Derive the seal tier from the class exactly as the contract does; do not ask Jev whether a defect should block the seal (tested: that yes/no separated poorly, 0.42–0.66, while the class itself did not). When Jev's class differs from yours, show both in the Step 3 confirmation and let the user choose; if unresolved, the more severe class is the safer default.

Tested on the contract's own expense-export example (one run each): the CSV amount column → `irreversible_data` 0.78, the API `status` field → `downstream_contract` 0.87, the failure toast → `ui_ux` 0.86 — all three matching the template.
