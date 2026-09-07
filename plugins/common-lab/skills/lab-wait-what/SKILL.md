---
name: lab-wait-what
description: Re-explain the last confusing answer for the user's audience without advancing the underlying task.
disable-model-invocation: true
---

# Wait What Lab

Pause the underlying task and help the user see what did not land. Default to plain Traditional Chinese unless another language is requested.

Honor --as <audience> / -a; otherwise infer the audience from context. Start with the missing connection: what is happening, why it matters, and how it connects to what came before. Preserve the substance the audience needs without speaking down to them.

Pick the explanation shape that repairs the actual confusion. For example:

- If the throughline was lost, show it as `what we wanted → what we learned → what that changes`.
- If two ideas blurred together, put their responsibilities and handoff side by side.
- If a mechanism feels abstract, use a familiar analogy and say where the analogy stops matching.
- If there are many moving parts, show the whole shape first, then the part that matters to this audience.
- If the earlier answer was wrong or weakly supported, correct it first and separate what is known, inferred, and still unresolved.

Simplify detail, not truth. An explanation or visual must not turn inference into evidence, hide a consequential limitation, invent a decision for the user, or make an unsupported answer more persuasive.

Honor --mode text / -t with words only. Honor --mode visual / -v by helping the user see the explanation. In auto mode, visualize when a view makes the key point clearer. A sequence may be a short flow, a distinction may be a comparison, and a dense concept may become one focused HTML artifact. These are examples, not required formats; use judgment and do not overwhelm the user. Save durable visuals under .common-lab/explanations/ and open them for the user.

Hand understanding back lightly, then wait. Do not resume the underlying task or turn clarification into a test unless the user asks.
