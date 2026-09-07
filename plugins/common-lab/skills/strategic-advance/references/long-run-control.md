# Long-run control, not a universal itinerary

Use this control for an admitted coupled campaign. The outcome ledger remains the source of objective, criteria, evidence, and unresolved operations. Keep ordinary bounded work outside this protocol.

## Roles and independent facts

The lead owns the campaign, priorities, acceptance, and the human handoff. Implementation workers own bounded write sets; they do not expand a failed slice into a compound rescue task. The lead may inspect evidence and maintain the small control record, but routes substantial implementation and repairs to workers.

A fresh calibrator outside those execution contexts compares the original objective with actual evidence. Give it the current acceptance source, ledger, raw observations, relevant changed artifacts, and the proposed next increment. Label the lead's interpretation as a claim, not fact; let the calibrator inspect counterevidence. Record the actual runtime context identities. Different role names or self-declared IDs are not proof of isolation. Select a capable judgment model from the available runtime; the cheapest executor need not be an adequate calibrator. No model is assumed immune to shared errors.

A scribe is optional for collecting bulky traces into source-linked facts. It never decides acceptance. If the control packet grows too large to independently understand, delegate fact collection rather than copying the entire execution conversation into the calibrator.

## Bounded increment

Reuse the campaign's work-order or notes artifact. Before dispatch, record only what governs this increment:

- Remaining criterion gaps and the expected observable outcome change.
- Concurrent slices, named owners, permitted write sets, shared dependencies, and join condition.
- A finite repair allowance and the next checkpoint, chosen for the actual risk and workload. Count failed attempts and repeated hypotheses; more commands, tests, or edits alone do not renew the allowance.
- The latest time to reassess, earlier event triggers, and a safe handback point.

One main effort can involve many APIs and pages in parallel. Bound coupling and goal changes, not arbitrary worker counts. Do not set a checkpoint only at the end of the entire campaign.

Dispatch the independent calibrator before the increment. Its result identifies goal progress (MOE), work performed (MOP), the causal link or gap between them, and a disposition: continue this bounded increment, replan, hold, or ready for completion checks. The lead resolves conflicting evidence rather than treating the report as a vote or rubber stamp. A changed proposal requires a new review; the lead cannot self-approve a rejected continuation.

## Checkpoints that do not depend on feeling confused

Recalibrate at the earlier of the named checkpoint/deadline and these events:

- A new user requirement or intervention that changes priority, scope, or acceptance.
- A growing write set, repeated failed hypothesis, exhausted repair allowance, or activity without the expected outcome change.
- A material cross-worker integration failure, uncertain external mutation, context compaction, handoff, or resumed campaign.
- Proposed completion or reduction of campaign controls.

On compaction or resumption, first recover objective, original decisions, unresolved operations, current write ownership, and the last accepted evidence. Keep workers within their already bounded safe handback while control is being restored; do not overlap replacement writers. If a deadline cannot interrupt an active tool, stop at the next safe tool boundary and report the delay. This skill does not install a scheduler, intercept all tools, or claim that prose can force a sleeping agent to wake.

## A mid-campaign style correction

Preserve the existing criteria and uncommitted work. Establish whether the correction enforces an existing requirement or adds a new one; do not use that classification to dismiss an explicit user request. Suspend the affected conflicting slice at a safe boundary and send the original goal, actual style rule, diff, build failures, and bounded options to the calibrator before more implementation.

Decide whether a minimal style change is a prerequisite to the current increment, a separately sequenced required slice, or a scope/priority choice for the user. Do not silently combine remaining features, global formatting, shared refactoring, and build repair. Unrelated valid slices may continue. Revalidate only the old acceptance evidence that the change could invalidate; neither reset all progress nor assume all earlier passes still hold.

## Artifact-bound calibration

The bundled read-only check detects missing/stale control evidence; it does not prove semantic truth, actual agent identity, or universal tool enforcement. Use the actual runtime identity and observe the calibrator's returned artifact, not a receipt the lead wrote on its behalf.

Prepare a new packet from the existing state, work-order, and relevant raw evidence or changed source files:

    python3 ${CLAUDE_PLUGIN_ROOT}/skills/strategic-advance/scripts/calibration.py prepare <state.json> --brief <existing-work-order.md> --source <raw-evidence-or-source-file> --lead <runtime-context-id> --worker <runtime-context-id> --expires <ISO-8601-with-timezone> --output <new-packet.json>

Repeat --source and --worker as needed. Keep the lifetime within the next meaningful checkpoint. Sources must be separate files from the ledger and work-order, and should allow the calibrator to challenge the lead's story, not merely repeat it. Different files alone do not establish different evidence. For a large diff, use a reproducible target manifest with content hashes and verify its entries against actual files; a manifest file's own hash does not prove the listed files stayed unchanged.

The calibrator writes a new JSON decision with these fields:

    {"schema":"lab-calibration-decision/1", "packet_sha256":"<actual packet digest>",
     "reviewer_context":"<actual fresh runtime context>", "verdict":"continue",
     "observed_moe":"<supported outcome delta or explicit absence>",
     "observed_mop":"<activity and its cost>",
     "reason":"<evidence-based disposition>", "next_action":"<bounded move or recovery>",
     "evidence_paths":["<absolute inspected source path>"]}

Verdicts are continue, replan, hold, or ready-to-complete. Before dispatch/renewal or final completion checks:

    python3 ${CLAUDE_PLUGIN_ROOT}/skills/strategic-advance/scripts/calibration.py check <packet.json> <decision.json> --purpose continue

Use --purpose complete for a ready-to-complete disposition. The check rejects expired packets, changed state/brief/sources, stale accepted evidence, source aliases of control files, missing source inspection, same-context reviewers, non-active campaign status, and a decision for another packet. Reconcile a blocked campaign's actual cause and update its bounded focus before preparing a new continuation packet; do not toggle status merely to pass this check. Neither an accepted packet nor a ready-to-complete verdict overrides the ledger's completion checks or the user's authority. Any material event above invalidates continuation even if the files still hash the same.

If independent execution is unavailable, disclose degraded control and hold the affected next increment. Do not claim independent success from an author-only check. Safe read-only reconciliation may continue; missing independence is not permission to weaken acceptance or create a new external service.

## Handback and control reduction

Show the person what changed in the real outcome, what remains, what detour was stopped and why, and the next bounded move or actual choice. Do not make them parse the event stream or approve routine internal checkpoints.

Reduce control only when independent calibration establishes that the remaining work is genuinely bounded and coupled risks are reconciled. A model upgrade, a quiet interval, elapsed time, or a short successful trial is not that evidence. The purpose is recoverable progress despite fallibility, not a promise that drift can never occur.
