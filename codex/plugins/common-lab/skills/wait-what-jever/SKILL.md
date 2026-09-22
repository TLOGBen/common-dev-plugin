---
name: wait-what-jever
description: Lab overlay on common:wait-what that checks the re-explanation with TypeSafe Jev before sending it — would this audience actually understand it — and, when not, lets Jev pick among a few candidate explanation shapes before rewriting.
disable-model-invocation: true
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# Wait What (Jev overlay)

Use Jev to strengthen anywhere that only needs a judgment — yes/no, choose one, score.

Load and run `$wait-what` exactly as written: pause the task, infer the audience, repair the actual confusion, simplify detail not truth, words only. This overlay adds one check between drafting the re-explanation and sending it. Default user-facing output to Traditional Chinese.

## Check before sending

State: the audience as you inferred it, what confused them (the earlier answer or the phrase that did not land), and your draft.

```json
{"understood": {"type": "score", "instructions": "How well would this audience actually understand this explanation on first read?",
  "criteria": ["They would be lost", "They would get the gist but miss the key point", "They would understand the key point with some effort", "They would understand it clearly"]}}
```

At about 2 or above, send the draft. Below that, write two to four candidate shapes — each a one-line description of how you would re-explain it, drawn from wait-what's own list (throughline, side by side, plain mechanism, whole shape first, correct the earlier answer first) or another shape that fits — and ask Jev to pick:

```json
{"shape": {"type": "choice", "instructions": "Which explanation shape would best repair this audience's confusion?",
  "criteria": {"<a>": "<one-line candidate>", "<b>": "<one-line candidate>", "<c>": "<one-line candidate>"}}}
```

Rewrite in the chosen shape and check `understood` once more; then send whichever version scored higher. Do not loop further — the user's reaction is the real test. A higher score never justifies dropping a limitation or turning inference into evidence; wait-what's truthfulness rules come first.

## Calling Jev

`POST https://api.typesafe.ai/v1/systemone` with `{"model": "jev-latest", "state": "<facts>", "questions": {...}}` and `Authorization: Bearer $TYPESAFE_API_KEY`. If the key is unset (`$init-jev`) or the call fails, send the re-explanation as wait-what would. The explanation leaves the machine for TypeSafe in the U.S.; skip the check for client or confidential content unless the user has said TypeSafe is allowed.

Tested (one run each), audience a project manager with no programming background: a jargon-heavy explanation of a stale git lock scored 0.17; a "do not disturb sign" explanation of the same thing scored 2.55; Jev picked `plain_mechanism` for both.
