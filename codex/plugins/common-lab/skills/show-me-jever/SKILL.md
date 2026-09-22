---
name: show-me-jever
description: Lab overlay on common:show-me that checks the visual with TypeSafe Jev before showing it — would this user actually understand it — and, when not, lets Jev pick among a few candidate views (pseudocode, call tree, component or file tree, Mermaid, diff, focused HTML) before redrawing. Use when the user asks for show-me-jever or a Jev-checked visual; use show-me for ordinary visuals.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# Show Me (Jev overlay)

Use Jev to strengthen anywhere that only needs a judgment — yes/no, choose one, score.

Load and run `$show-me` exactly as written: pick the smallest view that makes the key point clear, keep prose brief, and follow its Mermaid and HTML rules. This overlay adds one check between drafting the view and showing it. Default user-facing output to Traditional Chinese.

## Check before showing

State: who the user is as far as the conversation shows, the question the visual answers, and the draft view as text (the pseudocode, tree, diff, or Mermaid source; for an HTML page, its section outline and labels).

```json
{"understood": {"type": "score", "instructions": "How well would this user understand the key point from this view on first look?",
  "criteria": ["They would be lost", "They would get the gist but miss the key point", "They would understand the key point with some effort", "They would understand it clearly"]}}
```

At about 2 or above, show it. Below that, write two to four candidate views — each a one-line description of what you would draw, drawn from show-me's own list (pseudocode, call tree, component tree, file tree, Mermaid flow, diff, whole block, one focused HTML page) — and ask Jev to pick:

```json
{"view": {"type": "choice", "instructions": "Which view would make the key point clearest for this user?",
  "criteria": {"<a>": "<one-line candidate view>", "<b>": "<one-line candidate view>", "<c>": "<one-line candidate view>"}}}
```

Redraw in the chosen view and check `understood` once more; then show whichever version scored higher. Do not loop further. Jev reads the view as text, not pixels, so a rendered HTML page still gets show-me's own look before it is opened.

## Calling Jev

`POST https://api.typesafe.ai/v1/systemone` with `{"model": "jev-latest", "state": "<facts>", "questions": {...}}` and `Authorization: Bearer $TYPESAFE_API_KEY`. If the key is unset (`$init-jev`) or the call fails, show the view as show-me would. The view leaves the machine for TypeSafe in the U.S.; skip the check for client or confidential content unless the user has said TypeSafe is allowed.
