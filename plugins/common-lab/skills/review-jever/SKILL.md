---
name: review-jever
description: Lab overlay on baransu:review that adds a TypeSafe Jev confidence section — for each retained finding, how well the cited evidence supports its claimed consequence and whether it is a defect, an unknown, or an optional improvement — as a second opinion shown beside the review's own judgment. Use when the user asks for review-jever or a review with Jev confidence scores; use /baransu:review for ordinary reviews.
---

# Review (Jev overlay)

Use Jev to strengthen anywhere that only needs a judgment — yes/no, choose one, score.

Load and run `/baransu:review` exactly as written; pinning the target and question, the fresh verifier, the evidence rules, and the report are unchanged. This overlay adds one reading per retained finding, in the main session after the verifier returns, and one extra section in the report. The reading is a second opinion on the finding as written: it cannot add a fact the evidence has not established, cannot turn an unknown into a defect, and does not replace the report's scope / findings / evidence / independence / limits. Default user-facing output to Traditional Chinese.

## Calling Jev

`POST https://api.typesafe.ai/v1/systemone` with `{"model": "jev-latest", "state": "<facts>", "questions": {...}}` and `Authorization: Bearer $TYPESAFE_API_KEY`. If the key is unset (`/common-lab:init-jev`) or the call fails, skip the section and report as written. Findings quote the target, which leaves the machine for TypeSafe in the U.S.; skip the reading for client or confidential targets unless the user has said TypeSafe is allowed. Keep the questions as written — the reviewer has a stake in its own findings.

## Confidence per finding

State: one retained finding exactly as the report will present it — location, trigger, claimed consequence, and the evidence with its quoted output.

```json
{"support": {"type": "score", "instructions": "How well does the cited evidence support the claimed consequence of this finding?",
  "criteria": ["No evidence; the consequence is speculation", "Evidence is related but does not show the consequence happens",
               "Evidence shows the trigger, but the consequence is inferred", "Evidence directly shows the trigger and the consequence"]},
 "kind": {"type": "choice", "instructions": "What is this finding?",
  "criteria": {"defect": "A demonstrated defect against the review question", "unknown": "A plausible issue that the evidence has not settled",
               "improvement": "An optional improvement, not a defect"}}}
```

Act on disagreement, not on the number alone:

- `support` below ~1 on a finding you called a defect → re-read its evidence; either add the missing observation (within the review's allowance) or move it to unknowns. For a severe claim, test the plausible disconfirming explanation the review already asks for.
- `kind` differs from your own classification → keep your classification only if you can say in one line why the evidence supports it; otherwise take the weaker of the two (unknown over defect, improvement over unknown).
- A high `support` never upgrades a finding past what its evidence shows, and never authorizes extra rounds, fixes, or a broader scope.

## Report section

After the review's own findings, add 「Jev 信心評分」: one line per retained finding with its ID, `support` as a number out of 3 with the level in words, Jev's `kind` next to yours, and — only where they differ — what you did about it. Say once that these are second opinions from a model outside the review, not additional evidence.

Tested (one run each): a finding with a reproduced output and a cited spec line scored support 1.99 (trigger shown, consequence inferred from the spec) and `defect` 1.0; "the module might be slow because the file is 600 lines" scored 0.75 and `unknown` 0.99.
