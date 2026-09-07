---
name: lab-review
description: Independently review a concrete artifact or claim when the user requests a second opinion, without editing it.
---

# Review Lab

Find consequential defects in the user's actual target; a clean review is a valid result.
Default user-facing output to Traditional Chinese.

Pin the supplied artifact, diff, or directly quoted claim and the review question. Inspect the real target and relevant upstream/downstream context. Do not invent a diff base, target, or claim from an author's completion statement.

Review-only means no target, test, contract, configuration, or working-tree edits, including obvious typos and automatic formatting. A proposed fix remains a finding. Creating a requested separate review report does not authorize changing the reviewed material.

Reuse acceptance criteria when present; a contract is not a prerequisite for an ordinary review. Select the evidence and perspectives by causal risk, not fixed line-count tiers or automatic five-perspective fan-out.

For independent review, load ${CLAUDE_PLUGIN_ROOT}/agents/lab-verifier.md completely and dispatch a fresh, narrow-context verifier with the target, question, acceptance, permitted read/probe scope, and raw evidence. Do not supply the author's defense or desired verdict. Use additional independent perspectives only for distinct consequential risks.

If independent execution is unavailable or the current reviewer authored the target, disclose the limitation. A same-context self-check can still find defects, but cannot earn an independent pass. Never assume a tool or model exists because it worked in another session.

Verify consequential counts against the exact noun and scope claimed, and coverage against real executed paths. Mocking the claimed layer does not test that layer. For business behavior, distinguish upstream-reachable states and authoritative requirements from what the target happens to accept.

Retain findings with a concrete location, triggering condition, supported consequence, and relevant evidence. Test a plausible disconfirming explanation for a severe claim; do not inflate confidence or severity from repeated agreement.

Consolidate against the review goal. Separate defects, unknowns, and optional improvements; do not recommend a new mechanism without explaining what consequential failure it addresses. Do not suppress a contradiction to your own authoring decision by declaring it off-goal.

If reviewing a workflow or skill, distinguish human-owned purpose from compensation for a model failure. Evaluate the actual failure conditions and enforcement surface; shorter instructions or a stronger model are not evidence that a long-run protection is obsolete. Do not promote a short scenario probe into a reliability claim for an hours-long coupled task.

Before extending a review into repeated probes, use ${CLAUDE_PLUGIN_ROOT}/skills/lab-seal/references/verification-effort.md. A finding's validity does not itself authorize extra rounds, fixes, or a broader target. Preserve fresh-context judgment and source evidence; shared model agreement is not an independent ground truth.

Report examined scope, findings, evidence, independence, and remaining limits. No findings is not universal correctness; no tests is not an exempt layer. An absent required observation is unverified, not passed. Use a new report under .baransu-lab/reviews/ only when persistence is useful or requested.
