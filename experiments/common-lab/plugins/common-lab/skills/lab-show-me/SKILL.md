---
name: lab-show-me
description: Help the user understand the current topic visually with concise diagrams,
  structural sketches, or one focused HTML artifact.
license: See LICENSE
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# Show Me Lab

Help the user see the current discussion. Skip the preamble, keep prose brief, and choose the view that makes the key point clear. Default supporting text to Traditional Chinese unless another language is requested.

Use a form that matches the thing being explained. For example:

- Show logic as pseudocode:

```text
on(save)
  if nothing changed
    return cached result
  write new content
  return fresh result
```

- Show runtime control as a shallow call tree:

```text
submit
  validate
  persist
  notify
```

- Show UI, file, or ownership structure as a labeled tree:

```text
feature/
├── view/       # what the user sees
├── domain/     # rules and state
└── gateway/    # external effects
```

- Show interaction or data flow with Mermaid when arrows carry the explanation.
- Use a focused diff when the point is what changed and the surrounding shape matters.
- For a visual UI, state comparison, or concept too dense for an inline diagram, create one focused HTML page using real labels and data, make it work on desktop and mobile, and open it for the user.

Place each visual next to the short text it supports. Keep only the calls, files, states, boundaries, and choices needed for the user's current question. Use one example, several, or none; use judgment and do not overwhelm the user.

Adapted from HumanLayer's `show-me` skill under the MIT License. See LICENSE.
