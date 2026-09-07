---
name: lab-domain-modeling
description: Clarify domain terms, rules, and architectural decisions when ambiguity is blocking shared understanding.
---

# Domain Modeling Lab

Create the smallest shared model that resolves the current ambiguity.
Default user-facing output and new artifacts to Traditional Chinese.

Use the project's existing domain documentation if it covers the issue. Model the relevant actors, concepts, relationships, lifecycle, and invariants from concrete examples; omit categories that add no understanding.

Distinguish observed behavior, desired rules, disputed terms, and open questions. Code is evidence of implementation, not automatic authority for business intent.

When a term has competing meanings, show the collision using an example and resolve only the decision the user can actually make. Do not remodel unrelated domains.

Record durable findings in the existing canonical document, or a focused file under .common-lab/domain/ if none exists. For a consequential architectural choice, capture the context, chosen option, alternatives, consequences, and evidence without forcing a template onto a vocabulary clarification.

Finish with the ambiguity removed, unresolved decisions, and what downstream work can now proceed. Do not implement the modeled system unless requested.
