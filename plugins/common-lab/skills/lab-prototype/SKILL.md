---
name: lab-prototype
description: Build a disposable prototype when a design or logic question needs concrete experience to answer.
---

# Prototype Lab

Answer a design question with the cheapest convincing artifact.
Default user-facing output to Traditional Chinese.

State the uncertainty and the observation that would resolve it. Reuse the project's tooling when practical; choose fidelity according to the question, not a fixed stack.

Put a new throwaway artifact under .common-lab/prototypes/ unless the user provides another location. Label simulated data and unavailable integrations. Do not replace production code or silently promote a mock into delivered functionality.

For logic, exercise the state transitions and counterexample that matter. For UI, make the relevant interaction inspectable at a representative size. Skip unrelated features and ornamental polish.

For asynchronous logic, distinguish a command that can be rejected before execution from an event reporting a side effect that already happened. Rejecting a late successful-payment event does not undo the charge. Represent the observed external effect and the unresolved reconciliation or compensation separately; never imply that ignoring an event restores consistency or authorizes a refund.

Inspect the result using available runtime or rendering tools and fix failures that prevent answering the question. Report what was actually observed, what remains hypothetical, and whether to keep, revise, or discard the idea.

When iterations stop changing the answer, hand back the result instead of pursuing polish or a production rewrite. A promising demo supports only the question it exercised, not reliability at production scale or over a long run. Show the relevant interaction or state transition alongside the simulation boundaries so the person can judge the result without mistaking appearance for completion.

Creating a disposable artifact does not authorize deleting it or the user's existing files. Preserve it unless cleanup is explicitly authorized.
