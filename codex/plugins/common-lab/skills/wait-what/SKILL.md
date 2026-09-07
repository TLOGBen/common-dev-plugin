---
name: wait-what
description: Re-explain the last confusing answer for the user's audience without
  advancing the underlying task.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.2.0-codex
---

# Wait What Lab

Pause the underlying task and help the user see what did not land. Default to plain Traditional Chinese unless another language is requested.

Infer the audience from how the user has been talking in this conversation; if that is not possible, treat them as a newcomer and say so rather than asking. Start with the missing connection: what is happening, why it matters, and how it connects to what came before. Preserve the substance the audience needs without speaking down to them.

Pick the explanation shape that repairs the actual confusion. For example:

- If the throughline was lost, show it as `what we wanted → what we learned → what that changes`.
- If two ideas blurred together, put their responsibilities and handoff side by side.
- If a mechanism feels abstract, explain it plainly first. Add an analogy only when one fits exactly and say where it stops matching; a strained analogy or an invented story confuses more than a plain sentence.
- If there are many moving parts, show the whole shape first, then the part that matters to this audience.
- If the earlier answer was wrong or weakly supported, correct it first and separate what is known, inferred, and still unresolved.

Simplify detail, not truth. An explanation must not turn inference into evidence, hide a consequential limitation, invent a decision for the user, or make an unsupported answer more persuasive.

Words only: no HTML, no diagrams, no files. If a picture would carry the point better than prose, say so in one line and leave it there; the user calls show-me when they want one.

Hand understanding back lightly, then wait. Do not resume the underlying task or turn clarification into a test unless the user asks.
