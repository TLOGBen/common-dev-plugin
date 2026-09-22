---
name: think-jever
description: Lab overlay on baransu:think that adds a TypeSafe Jev confidence section — how well this run's evidence supports each bet the stance rests on and the stance as a whole, whether a guessed phrase in the restatement would change the shape of the answer, and whether a remaining choice is genuinely the user's. Use when the user asks for think-jever or a deliberation with Jev confidence scores; use /baransu:think for ordinary deliberation.
---

# Think (Jev overlay)

Use Jev to strengthen anywhere that only needs a judgment — yes/no, choose one, score.

Load and run `/baransu:think` exactly as written; the restatement-first alignment, the stance, premise verification, the two-way attack, the presentation contract, and the five-section plan file are unchanged. This overlay adds Jev readings at three points and one confidence section in the presentation. The readings are second opinions: premises are still verified by quoted commands or authoritative documents, and a score is never a substitute for 已實查. Default user-facing output to Traditional Chinese.

## Calling Jev

`POST https://api.typesafe.ai/v1/systemone` with `{"model": "jev-latest", "state": "<facts>", "questions": {...}}` and `Authorization: Bearer $TYPESAFE_API_KEY`. If the key is unset (`/common-lab:init-jev`) or the call fails, skip the readings and deliberate as written. Keep the questions as written — you are the author of the stance being scored.

## 1. Guessed phrases (during alignment)

For each phrase in the restatement you had to guess, state the restatement, the phrase, and the candidate answers, and ask:

```json
{"shape_changing": {"type": "noul", "instructions": "Would different answers to this guessed phrase change the shape of the solution, rather than only a parameter of it?"}}
```

The think skill asks only shape-changing questions. Above ~0.7, ask it; below ~0.3, leave it as a parameter and mark it 未知，先不問. In between, use the skill's own test.

## 2. Bets and stance (after premise verification, before presenting)

State: the confirmed restatement, the stance sentence with its decisive reason, the verified and 未實查 premises with their quoted fragments, and one bet.

```json
{"bet_support": {"type": "score", "instructions": "How well does the evidence gathered in this run support this bet?",
  "criteria": ["Unsupported; an assumption", "Plausible but unverified", "Partly verified; a load-bearing part is still unverified", "Verified by quoted commands or authoritative documents"]}}
```

Ask it once per bet, then once for the stance as a whole with the question "How well does this run's evidence support the recommendation over the alternatives considered?" and the same levels. A bet at level 0–1 is either verified now (re-derive it from the repo) or named plainly as the load-bearing premise in Approach, with what happens if it fails.

## 3. Whose choice is it (before handing a choice to the user)

State: the remaining choice and its consequence.

```json
{"user_owned": {"type": "noul", "instructions": "Is this remaining choice genuinely the user's — a value, a budget, or an authority boundary — rather than a technical question the evidence can settle?"}}
```

Below ~0.3, settle it yourself from the evidence instead of handing it over; the think skill forbids turning research into a question for the user. Above ~0.7, explain its consequence and wait.

## Confidence section

In the presentation, after the stance, add 「Jev 信心評分」: each bet with its level (0–3, in words) and the stance's level, each beside its verified / 未實查 tag. Say once that these are second opinions from a model outside the deliberation, not verification. The plan file keeps exactly its five sections — do not add a sixth; where a bet scored 0–1, say so inside Approach next to the load-bearing premise.
