---
name: lab-wait-what
description: Re-explain the last confusing answer for the user's audience without advancing the underlying task.
disable-model-invocation: true
---

# Wait What Lab

Pause the underlying task and repair understanding.
Default to plain Traditional Chinese unless another language is requested.

Honor --as <audience> / -a; otherwise infer the audience from context and assume a newcomer only when unknown. Preserve what matters to that audience without speaking down to them.

Start with the point that was missing: what is happening, why it matters, and how it connects to the previous discussion. Explain unfamiliar terms at their first use. Use an analogy only when it illuminates the mechanism, and name any consequential limitation.

Accuracy is not a percentage to trade away. Simplify detail, not truth. Distinguish the original evidence from an illustration, and do not introduce new work or unsupported conclusions.

Do not make an unsupported earlier answer sound more convincing. If the confusion exposes an error, contradiction, or missing evidence, correct or qualify that exact claim before explaining it. Preserve what is known, what was inferred, and what the user still owns; an elegant visual is not new evidence.

Honor --mode text / -t with words only. Honor --mode visual / -v with the smallest useful visual the environment supports; say if the requested medium is unavailable. In auto mode, visualize only when a relationship becomes materially easier to understand. No HTML artifact is required for a one-sentence clarification; if needed, save it under .common-lab/explanations/.

Default to a light handback after the explanation, then wait; do not turn clarification into a comprehension test. Ask for teach-back, a quiz, or a restatement only when the user opts in. Do not resume the underlying task until the user indicates readiness or directs the next action.
