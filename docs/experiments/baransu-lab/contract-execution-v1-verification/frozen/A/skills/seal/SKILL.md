---
name: seal
description: 'Post-implementation seal, run as a dispatcher: assembles the verification
  payload, runs the baseline, dispatches a verify-only seal-agent in a clean context
  (criteria audit / unpinned-surface scan / cross-UI / constants byte-diff / mutation
  spot-check), fixes findings in the main session with capped re-verification, and
  stamps the sealed marker on a clean pass. Use to close out a /contract-banded task.
  Trigger On ''$seal'', ''封緘'', ''收尾驗收'', ''驗收剛做完的'', ''seal it''. Not for cross-perspective
  re-verification of any model output (use $review) or pre-work criteria pinning (use
  $contract). 繁體中文輸出。'
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# seal — one cold-eyed pass before you call it done

## Codex Port Adapter - Bundled Agent Resolution

This plugin does not assume package-local TOMLs are auto-registered as custom
agents. The required definitions for this skill are bundled at
`../../.codex-agents/<agent-name>.toml`: `seal-agent`.

Before every named-agent dispatch:

1. Resolve the exact bundled TOML from this `SKILL.md` directory (strip a
   leading `baransu:` namespace from the requested name).
2. Verify the file exists, then pass its absolute path and the task input to a
   generic Codex subagent. The first instruction to that subagent is to read
   the TOML's `developer_instructions` completely before doing any task work
   and to treat relative paths as relative to the TOML file.
3. If the TOML is missing or unreadable, stop with
   `AGENT_DEFINITION_MISSING: <path>`. Never invent, summarize, or substitute a
   role from the agent name.


Teeth live in the criteria and the mandate, not in the reviewer's model: the
same reviewer that waves a defect through under a loose contract rejects it
under an assertable one. The main session is a DISPATCHER — it assembles the
payload, dispatches a verify-only seal-agent into a clean context, applies
fixes itself, and stamps the seal. All user-visible output is
**Traditional Chinese (繁體中文)**.

## Outcome Contract

- **Outcome**: Narrow-scope verification of a finished implementation against its contract (or user-named criteria), executed by a dispatched verify-only seal-agent; findings fixed in the main session and pinned by tests; a clean dispatch stamps the sealed marker onto CONTRACT.md.
- **Done when**: The agent's five-point report is in hand with per-point evidence; every applied fix carries a pinning test that runs green in-session; the post-dispatch fingerprint comparison matches (no probe residue); and either the sealed marker is written (clean dispatch, branch 1) or the over-cap/branch-2/branch-3 closing path has been reported.
- **Evidence**: The agent's structured five-point report (each point: finding or 「乾淨」), the fix list (each with pinning test name and green-run tail), the fingerprint record (pre-dispatch vs post-return), the mutation probe record, and the seal-log JSONL line.
- **Output**: A Traditional Chinese seal report in the conversation (dispatcher-assembled: 五點結果＋修正清單＋突變抽查記錄); fixes land as working-tree edits with their pinning tests; on a clean branch-1 dispatch, the sealed marker on CONTRACT.md line 2.
- **Automation**: ultracode=neutral, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）
- **Telemetry**: on invocation, append one selection record per `../_shared/selection-telemetry.md`.
- **Seal evidence**: on completion, append one JSON line `{"ts":"<ISO8601>","skill":"seal","result":"pass|fixed|unresolved","target":"<one-phrase>"}` to `~/.codex/baransu/telemetry/{project}/seal-log-{YYYY-MM}.jsonl` ({project} = git-root basename, or the cwd folder name when there is no git) — written by the main session ONLY, never by the agent. This is the evidence the shipped seal-guard Stop hook checks; skipping it causes a false block at session end.

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## Target-pin off-ramp (hard rule)

Materialize the target from disk BEFORE anything else, in this order:
1. A `CONTRACT.md` (project root or user-named path) → its criteria are the audit baseline; the diff is `git diff <base>` when the user names a base, else uncommitted + branch-local changes. This is the ONLY branch that can end with a sealed marker.
2. No contract but user-named criteria / artifact → use those verbatim as the baseline. A clean result on this branch closes with the report + seal-log line only — **no sealed marker is written** (there is no contract file to stamp, and nothing enters $ship's archive loop).
3. Neither a materializable diff nor a named artifact → **stop and report** `needs-input`（「無可審工件：請指名 diff 基準或合約」）. **No sealed marker is written.** Never fabricate a target and never seal from conversation memory.

Seal is designed for cold eyes: the five points run in a dispatched clean
context that has never seen this session's implementation reasoning. What this
session remembers is a claim, not evidence — the agent re-grounds every claim
from disk.

## Baseline suite pre-flight (dispatcher-run)

After the target is pinned and BEFORE the first dispatch, the dispatcher runs
the project's full test suite once and records the result as the baseline. The
red set and the degradation flag travel in the payload (field 4); the agent
never re-derives them.

- **No runnable suite** → set the degradation flag: the agent's mandate point 5
  degrades to a static pin-audit (surface → pinning-test mapping check, no
  probe injection), and 「無可執行測試套件」 is itself a top-level finding; in
  the fix loop, fixes narrow to constant-drift corrections — an in-band finding
  that cannot be paired with a pinning test is reported, not fixed.
- **Baseline already red** → record the pre-existing red tests in the payload;
  mutation-probe attribution counts only tests that turn red RELATIVE to the
  baseline, and "green" for applied fixes means green relative to the baseline
  (the pre-existing red set unchanged, listed in the report).

Both branches keep the report template and seal-log JSONL unchanged — the
degraded path records 突變 0/0（靜態核對）in the closing line.

## Dispatch payload (five fields)

Every dispatch of seal-agent carries exactly these five fields; a dispatch
missing any field is malformed — fix the payload, do not send it:

1. **Contract** — the `CONTRACT.md` path, or (branch 2) the user-named criteria verbatim.
2. **Diff base** — the base ref the user named, else uncommitted + branch-local changes.
3. **Test command** — the exact suite command the agent runs for probe attribution.
4. **Baseline result** — the pre-dispatch suite outcome: pre-existing red set + degradation flag.
5. **Scratch path** — a dispatcher-chosen directory where the agent saves byte-exact pre-probe copies; this is the dispatcher's restore source if the agent leaves residue.

## The five-point mandate (executed by seal-agent)

All five points are EXECUTED BY seal-agent in a dispatched clean context —
this file defines the dispatch; the execution rules (probe protocol, restore
semantics, structured report format) live in the agent definition under
`plugins/baransu/agents/` (file `../../.codex-agents/seal-agent.toml`). The agent is verify-only: it reports
findings and never applies a fix. The gate rules are the shared single
implementation in `../_shared/contract-gate.md` (G1–G4 + Loose-Criterion
Escalation) — the agent judges against it; the dispatcher re-judges disputed
findings against it. The mandate, point by point:

1. **Criteria audit** — walk the contract criteria one by one against the
   implementation; each gets 符合 / 違反 / 條文太鬆 (G1 judgment).
2. **Unpinned-surface scan** — enumerate every user-facing output the diff
   touches (CLI println, TUI toast, error path); flag each surface no test
   pins at rejection strength (G4 judgment, including the cross-UI shared-helper rule).
   **Zero-test layers are the PRIMARY scan target, never an exempt zone** — a
   layer with no tests (DAO SQL, controller parameter mapping) is where unpinned
   defects live, and the mutation spot-check (point 5) can only fire where tests
   exist, so at least one probe or manual line-by-line check goes into a
   zero-test layer. Two mechanical sub-checks whenever the diff contains
   parameterized queries: (a) **parameter-usage reconciliation** — the set of
   parameters added to the command equals the set referenced in the SQL text
   (an added-but-unreferenced parameter is a correctness finding: the filter
   silently does not filter); (b) **condition-effectiveness** — every query
   condition the contract names (vendor / date-range / permission scopes) is
   confirmed present in the WHERE clause; "the parameter is passed" never
   substitutes for "the condition takes effect", and a criterion resting on an
   unverified premise does not exempt its adjacent verifiable conditions.
3. **Cross-UI consistency** — when two UIs express the same outcome, confirm a
   single shared helper pinned on BOTH real call paths; mirror tests do not count.
4. **Verbatim constants byte-diff** — diff every constant in the implementation
   against the contract's `## Verbatim Constants` block (G3), byte for byte.
5. **Mutation spot-check** — deliberately break 1-2 user-facing surfaces, run
   the payload's test command, and record which test fired (or that none did);
   degrades to a static pin-audit when the payload's degradation flag is set.
   Every probe MUST first pay the entry fee and be ranked by the selection
   standard in **Probe admission** below — an unpaid probe is never injected.
   Before injecting each probe the agent saves the target file's exact
   pre-probe content byte for byte to the payload's scratch path; the only
   permitted revert is writing that saved copy back, confirmed by byte-for-byte
   comparison (full protocol in the agent definition). A probe that no test
   catches is a finding, never a shrug.

## Probe admission (verbatim-shared clause — SKILL.md and ../../.codex-agents/seal-agent.toml MUST match word for word)

**Entry fee (per probe, paid in writing BEFORE injection)** — list the real
operation chain the probe replays: which future real actor, under what normal
operation, and step by step which step walks through the existing process
discipline (diff review, self-verification, first-hand handover data) without
being caught. A chain that does not walk through end to end is a paper exercise
and that probe is NOT admitted. An arbitrary character mutation with no
corresponding real operator is inadmissible; "it could happen" is not an entry
fee. The chain travels in the probe record as `operation_chain`, so the
dispatcher can audit the fee that was paid.

**Selection standard** — rank admissible probes by the consequence severity of
the DEFENCE BREACH each one would expose. A probe that would expose a whole
family of hollow assertions of one shape (e.g. the bare-value `includes` form)
is ranked at the heaviest surface that family of judges guards — never at the
surface consequence of the mutated object itself, and never by adjacency to the
previous round's finding (streetlight ban).

**Zero-probe exit clause** (the same shape as the existing "no runnable suite"
degradation path) — when the slice offers NO admissible probe target at all,
point 5 is recorded as 未執行, and that fact is ITSELF a top-level finding;
silently judging 符合 is forbidden.

## Fix loop (dispatcher side)

The agent returns structured findings; it never fixes. In the main session:

1. **Apply in-band fixes**, graded per **Findings grading** below — an unpinned
   surface, a constant drift, a criteria
   violation with an obvious minimal fix: fix directly, pair each fix with a
   pinning test, re-run the suite to green (relative to the baseline red set).
2. **Re-dispatch for re-verification** with a refreshed payload and a fresh
   fingerprint. **A re-verification dispatch is NOT a second five-point
   excavation.** Its mandate is exactly these three mechanical replays, and the
   dispatch payload names them in place of the five-point mandate:
   (a) **Regression on fixed findings** — every finding from the previous round,
   one by one, re-checked at its own citation.
   (b) **Re-fire every probe that already bit in the first dispatch** — those
   probes produced no finding and appear nowhere in the fix list, and the fix
   round is the single most likely step to hollow them out (recorded case: a fix
   round's stub isolation passed handover review and was caught only by
   re-firing those probes during re-verification).
   (c) **Hollowness spot-check on judges newly created in the fix round** — an
   implementer's self-proof of "exactly one red" certifies ONLY the one
   discriminating branch that actually went red, never the whole protected
   surface the judge claims for itself; the re-verifier issues every newborn
   judge its own red (its birth certificate).
   **Findings newly discovered during re-verification are report-only** — logged
   in the report, not fixed. The ONE exception: an irreversible / data-destroying
   class is fixed immediately, and that fix does NOT count against the
   re-verification cap. **Re-verification cap: 2** — the initial dispatch plus at
   most 2 re-verification dispatches (total dispatches ≤3). The fingerprint
   comparison rule is unchanged.
3. **Over the cap with findings still open** → stop the loop, write NO sealed
   marker, append seal-log `unresolved`, and report:
   「複驗上限已達（2 次）：{N} 項未清 findings 如下，未蓋章（seal-log: unresolved）。」

**Findings grading — one axis only: consequence severity.** Rank is never taken
from which mandate point found it, how cheap the fix looks, or how visible the
mutated object is. When the contract's Surface Inventory carries an impact
class (G4 impact grammar), that class is the severity source of truth — the
grading below applies on its own only to surfaces the contract never
classified.

- **Must-fix**: irreversible consequences (data corruption / data loss) and
  broken shipped contracts (an already-published behavioral contract, a
  licensing or compliance breach). These are fixed in-band.
- **Surface assets** (styling, copy, color tokens, letter-spacing) carry a
  low-severity DEFAULT PRIOR — a prior, not a verdict. First-hand evidence (an
  actual probe result, or a whole family of hollow assertions exposed by a
  judge's shape) overturns the prior and raises the severity.
- **Low-rank findings default to logged, not fixed** — the report leaves them to
  the user's discretion.
- A surface-asset judge receives EXACTLY ONE round of probes in its lifetime
  (its birth certificate); later rounds do not re-fire probes at it. The round
  is counted per seal ENGAGEMENT, not per dispatch: within one engagement,
  re-verification replay (b) re-fires every probe that already bit regardless
  of the judge's asset class — a probe that bit is evidence, not a prior. What
  the cap forbids is fresh probes at that judge in later seal engagements.

Per the shared Loose-Criterion Escalation rule: a real defect the criteria are
too loose to reject is a SPEC BUG — fix the defect AND record the criteria
patch; "the contract doesn't forbid it" is never grounds to pass.

**Evidence-backed dissent (R10, 大膽包 A)** — governs how the DISPATCHER judges
agent findings against contract premises: if the implementation DEVIATED from
a contract premise or clause AND carries first-hand evidence (a DB query result,
actual code at file:line, an SA-doc citation) that the premise was wrong, judge
the deviation on that EVIDENCE — a correct evidence-backed deviation is 符合,
never 違反 on literal contract wording; record a premise/criteria patch. In a prior
harness experiment, seal rejected an implementer's evidence-backed correct
data-source switch on literal contract wording (seal 字面誤判率 baseline 1) —
R10 forbids that pushback.
A bare assertion WITHOUT first-hand evidence does not qualify (evidence gate).

Out of band — architectural rework, behavior redesign, anything touching files
the diff never touched — is reported, not fixed: route to `$review`
(independent re-verification) or `$hunt` (root-cause diagnosis).

Each dispatch is exactly one pass on the agent side — no seal-of-a-seal inside
a dispatch; iteration lives only in this fix loop, and the sealed marker stamps
only the latest clean dispatch. A clean first dispatch — five points executed,
zero findings, fingerprint matched — is a complete, valid deliverable.

## Fingerprint and probe custody (dispatcher evidence chain)

- **Fingerprint definition**: the tracked diff (`git diff`) plus the
  untracked-file list difference (`git status --porcelain`, existing ignores
  excluded). Record it immediately BEFORE each dispatch; compare immediately
  after each return.
- **Probe custody**: pre-probe copies live at the dispatcher-chosen scratch
  path (payload field 5), so the dispatcher can restore without the agent. On
  fingerprint mismatch (probe residue — e.g. the agent died mid-probe), restore
  from the scratch copies and record the incident as a finding; restoration
  impossible → hard stop per `references/loop-pauses.md`.
- **Ordering**: the sealed marker write is ordered strictly AFTER the
  fingerprint comparison of the clean dispatch — never before, never in
  parallel. A mismatch means there is no clean dispatch to stamp.
- The seal-log JSONL line is written by the main session only.

## Sealed marker (on clean)

Written ONLY on target-pin branch 1 (a CONTRACT.md exists), ONLY after the
clean dispatch's fingerprint comparison matches (ordering rule above).
Branches 2 and 3 never write a marker.

The grammar authority is the contract template in `../contract/SKILL.md`
Step 2 (sealed-marker grammar: single authority) — cite it, do not restate its
rules here. Write this exact line (write-target format) at line 2 of
CONTRACT.md, immediately after the H1:

```
> STATUS: sealed（{ISO 日期}）— {五點結果一行摘要}
```

Idempotent overwrite — detect an existing marker first (never grep the whole
file):

```bash
head -3 "$f" | grep -qF '> STATUS: sealed'
```

On a hit, overwrite the existing marker line in place; never append a second
line. The marker stamps only the latest clean dispatch — it certifies clean at
seal time, nothing later.

## Report shape (Traditional Chinese)

The dispatcher assembles the report from the agent's structured findings plus
its own fix and fingerprint records.
「封緘結果」：五點逐一（符合/發現＋處置）、修正清單（每筆附釘死測試名與綠燈證據）、
突變抽查記錄（弄壞了什麼→哪個測試叫了/沒叫→已還原）、以及（若有）條文補丁建議。
Close with: 「封緘完成：{N} 條條文核對、{M} 個表面掃描、{K} 處修正（各附釘死測試）、
突變 {X}/{Y} 被測試攔截。」

## Not-for boundaries

- Cross-perspective independent re-verification of any model output（跨視角重驗證、四層回應、無預設修正權）→ `$review`.
- Pre-work criteria pinning（開工前釘條文）→ `$contract`（contract 開工前、seal 收工後——同一頻段的一對）.
- Large-band work is sealed one slice at a time: seal audits a single slice against its own contract. A multi-module effort MUST be sliced and each slice sealed separately — never one seal pass over the whole effort.
- Symptom/error debugging（報錯排查）→ `$hunt`.
