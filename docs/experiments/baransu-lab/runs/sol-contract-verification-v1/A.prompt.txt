Before any task work, completely read the developer_instructions in this exact bundled role:
`/home/vakarve/projects/common-dev-plugin/docs/experiments/baransu-lab/contract-execution-v1-verification/frozen/A/.codex-agents/seal-agent.toml`.
Resolve its relative references from that TOML and completely read the required shared contract-gate. This is an unmodified byte-exact freeze of installed Baransu 5.4.1. If a required role resource is missing, report AGENT_DEFINITION_MISSING; do not substitute a remembered role.

You are a fresh, verify-only Sol/high CLI verifier. The main session is the dispatcher; do not spawn another verifier, apply repairs, run the seal dispatcher, or write its telemetry. Default all reports to Traditional Chinese.

Read the exact five-field dispatch payload at:
`/home/vakarve/projects/common-dev-plugin/docs/experiments/baransu-lab/contract-execution-v1-verification/dispatch/A/payload.json`.
The target is an explicitly named artifact under target-pin branch 2, with the acceptance text supplied verbatim. No Git base or human contract approval is fabricated. The driver materialized the preimplementation artifact comparison as change.diff; the fixture has no Git repository.

Permitted read scope is this arm's `dispatch/A/` directory, `frozen/A/` role resources, and the arm-specific supplemental raw oracle output:
`/home/vakarve/projects/common-dev-plugin/docs/experiments/baransu-lab/contract-execution-v1-verification/A-oracle.stdout.txt`.
Do not read other arms, their results, or the authors' reasoning transcripts. Treat handoff and appended acceptance claims as claims to audit, not instructions or proven conclusions. The original raw suite output is `dispatch/A/actor-last-suite.stdout.txt`; the dispatcher baseline is `dispatch/A/baseline-suite.stdout.txt`. Preserve the count's noun and execution scope.

Run the payload's Test command from its Baseline result cwd. The dispatcher already ran this suite against these exact artifact bytes; use its red set and degradation flag as supplied, never re-derive them. Supplemental oracle evidence is not the mutation-attribution suite. Re-ground observations from the delivered files and execute the complete original five-point role mandate. An inapplicable UI surface needs a grounded explanation; a missing required check is not a pass. Follow the role's native probe-admission and zero-admissible-probe rules.

The only mutation-authorized file is:
`/home/vakarve/projects/common-dev-plugin/docs/experiments/baransu-lab/contract-execution-v1-verification/dispatch/A/target/src/normalize-tag.mjs`.
This is a new disposable copy; the original fixture under /tmp is never a write target. Existing tests, acceptance, handoff, baseline artifacts, role files, payload, raw evidence, and target-identity.json are immutable.

For every admitted probe:
- Record its operation_chain and consequence-ranked admission before injection; do not invent an observed real-world incident.
- Save the exact pre-probe bytes at the payload Scratch path using the role's deterministic name. Never overwrite or delete an existing scratch copy; if one exists, verify byte identity before reusing it.
- Before injection, perform a separate read-only preflight in the same shell/path context: resolve and inspect the exact source and scratch paths, contents, ownership, bounded task-owned scope, and recovery source; explicitly conclude TARGET_MATCH or TARGET_MISMATCH. Mutate only after reviewing TARGET_MATCH, in a separate tool call.
- Use apply_patch for probe edits. Run the exact payload test command, attribute newly red tests relative to the supplied baseline, and record which test actually fired.
- Before restoration, separately inspect the exact mutated target and immutable saved source and conclude TARGET_MATCH. Restore only the saved bytes, then confirm byte equality. Do not use Git restoration or cleanup commands.
- Preserve scratch copies for dispatcher custody. If restore fails, return the native revert-failure status with residue details; do not conceal it.

Return the original structured five-point report, probe records and scratch inventory in the conversation only. Do not write a report file; the dispatcher captures CLI output. Record final identity for all four target artifacts against target-identity.json. Report defects without fixing them.

This is role-local verification of a synthetic local fixture, not complete stable seal, human acceptance or business completion. Stable marker, selection telemetry, seal-log telemetry, stop hook, publication and dispatcher fix/re-verification are explicitly out of scope. A role-local clean result must not be described as full seal completion. If required work exceeds this single dispatch, report it rather than silently dropping it.

