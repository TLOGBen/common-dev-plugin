# One acceptance record

The task has one current statement of acceptance, not a separate contract at every skill boundary. Reuse an adequate user-provided record. Otherwise use .baransu-lab/acceptance/<task>.md and keep unrelated or historical artifacts intact.

The record needs only information that changes implementation or acceptance:

- Outcome and scope, including explicit user choices and relevant authority limits.
- Premises: verified with a source, inferred, or awaiting evidence; identify which criteria actually depend on each uncertainty.
- Stable criterion IDs: an observable expected result, a consequential counterexample or exclusion, and the real evidence path that can accept or reject it.
- Required versus optional status, and the real impact of a violation when that changes verification or sequencing. Do not silently downgrade a user requirement to optional because it is low impact. A test plan is a method, not an extra product requirement.
- Requirement constants exactly as supplied, when any exist.
- Material decisions or corrections, with their evidence and authority, without rewriting unrelated criteria.

Do not invent numeric targets to fill the form. An unknown premise never waives adjacent independent criteria. A proposed test name is a plan, not a test result. Evidence that mocks out the claimed layer cannot establish that layer's behavior.

An evidence-backed premise correction is a narrow revision, not a new goal. When the correction changes a user-owned value, scope, or authority decision, pause for that decision. When it only corrects an observed implementation fact, record the evidence and continue within the original authorization.

## Experimental receipt

A new receipt under .baransu-lab/receipts/<task>-<run>.md records:

- Target: exact paths plus commit or content hashes; include uncommitted and relevant untracked artifact bytes, not just filenames.
- Acceptance: record path/revision or explicit criteria; each ID is supported, violated, or unverified with concrete evidence.
- Independence: verifier identity/context and whether it authored the target; unavailable independence stays unavailable.
- Observations: actual commands or read-only observations and their results, including relevant pre-existing failures and verification limits.
- Outcome: supported within the stated scope, incomplete, or needs a user decision; what remains and where to continue.

Observe target identity again before claiming the receipt applies to the current artifact. A changed hash means recheck affected criteria, not blindly reuse the old result. Hashes identify bytes; they do not prove semantic quality or independence.

Do not label an author-only check independent. Do not mark a required observation unneeded merely because it cannot run. Unrelated baseline failures may be scoped out with evidence; changed required behavior cannot.

The receipt is an experimental artifact only. It neither writes the stable sealed marker nor feeds the original plugin's telemetry or Stop hook. It gives no permission to publish, archive, delete, or change external state.

For an extended verification cycle, also retain the check/repair allowance, actual rounds, unresolved required gaps, and the evidence-based reason for any extension. This belongs in the same task's receipt or working notes, not a new approval system.
