---
name: better-prompts
description: Audit or revise agent instructions against their purpose and observed failure modes when the user asks to improve a prompt.
---

# Better Prompts Lab

Make the prompt easier to obey without changing the user's objective.
Default explanations and new human-readable artifacts to Traditional Chinese.

Identify the intended outcome, audience or target model, actual failure, and boundaries from the supplied context. Ask only for a missing choice that changes the rewrite.

Prefer guidance about outcomes and judgment when multiple methods work. For each consequential constraint, distinguish a user-owned purpose or boundary from compensation for a model failure. Name the failure, triggering workload, evidence, enforcement surface, and friction before deciding to keep, change, or remove that compensation. Unknown history is a reason to investigate, not proof that a rule is ceremonial.

Remove duplication and overbroad triggers when their purpose survives. Do not optimize instruction length as a proxy for useful completion. Express completion and authority explicitly; do not replace them with an itinerary.

For skills, make the description a short selection rule. Keep a simple workflow self-contained; route substantial conditional workflows to references. Moving every old instruction into a mandatory reference is not simplification.

Preserve domain invariants and experience-backed failure protections until a replacement is tested under comparable conditions. Long-running drift, unsupported claims, and attention capture are design risks, not assumed cured by a model upgrade. Test model, task scale, context handoffs, concurrency, and mid-task interventions; a short successful run cannot retire a long-horizon safeguard. Re-evaluate its implementation and friction without removing the protected outcome.

Preserve the original explicit approval boundaries unless the user authorizes changing them. Reversible, recoverable, generated, or rebuildable does not mean authorized to delete. Removing repetitive prose must not silently convert "ask before deletion" into permission to clean up.

Use current primary guidance when the request depends on a particular model's behavior. Distinguish official guidance, the user's observed experience, and an experimental hypothesis. Never hard-code a universal model ranking from one benchmark.

Return the usable rewrite, the material tradeoffs, and a small realistic test that could falsify the improvement. Report measured reductions separately from unmeasured quality or token savings.
