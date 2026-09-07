# loop-contract — skill behavior under non-interactive drivers

> **Self-declaration**: this is a baransu plugin-level convention, **not an
> official standard**（本慣例非官方標準）. Official Claude Code documentation
> does not cover headless / cron driving scenarios (checked 2026-06-10).

## Contents

- Scope
- 1. Automation field vocabulary
- 2. PAUSE semantics
  - Interactive-capability detection primitive
- 3. Three hard stops — responsibility boundary
- 4. PAUSE classification registry

## Scope

Applies whenever a baransu skill is driven by a non-interactive context:
`/loop`, `/goal`-style external verifiers, cron, Workflow orchestration,
being **hosted as a subagent** (the `AskUserQuestion` tool is simply absent
from the runtime tool list, so there is no way to ask a human anything), or
any automation harness. Human-present sessions follow platform defaults —
including a nested session where the `AskUserQuestion` tool *is* present in
the tool list; presence of that tool, not nesting depth, is what marks a run
as interactive.

---

## 1. Automation field vocabulary

Every skill's Outcome Contract carries
`- **Automation**: ultracode={value}, loop={value}`; per-skill assignments are
pinned by `tests/skills/test-automation-annotation.sh`.

`ultracode=` — how the skill's internal fan-out relates to a Workflow-capable
(ultracode) session:

- **overlap** — own multi-agent dispatch rides Workflow primitives (ships `references/orchestration-interface.md`).
- **assist** — no adapter; specific stages may be accelerated by Workflow fan-out.
- **neutral** — orthogonal; no special handling exists or is needed.

`loop=` — whether a non-interactive driver may iterate the skill:

- **drivable** — safe to re-invoke under §2/§3 obligations.
- **assisted** — drivable only with §4 defaults substituted and annotated.
- **not-drivable** — the interactive dialogue IS the product.

Across all grades, human-present and non-ultracode runs keep current-path
semantics unchanged.

## 2. PAUSE semantics

Two PAUSE classes (defined here, self-contained — the plugin ships with no
external rule dependency):

- **Input PAUSE** — a preference or confirmation checkpoint (typically an
  AskUserQuestion). Platform modes or `--auto`-style flags may skip it by
  taking the recommended default.
- **Authorization PAUSE** — a hard stop requiring explicit human authorization
  (acceptance gates, publishing actions, self-modifying write-backs). Not
  satisfiable by a default substitution. The required authorization may be given
  two ways: interactively at the stop, or as a **standing authorization**
  recorded up-front in the driving context (the loop/cron prompt or an approved
  plan that explicitly authorizes the action) — but only where the skill's own
  `references/loop-pauses.md` marks that PAUSE as standing-authorizable, and only
  with every safety precondition that table names applied.

Platforms map PAUSE *cost* to their own models (free UX stop on Claude Code
vs billed request on Copilot / Claude.ai); that axis stays platform-owned.
This contract adds an orthogonal axis — the *driving context*. When a
non-interactive driver is detected, the skill behaves as follows regardless
of platform:

- **Input PAUSE** — take the recommended default and continue. This trigger
  fires in two shapes that are treated identically: (a) the `AskUserQuestion`
  tool is present but unanswerable (no human to answer, or a platform mode /
  `--auto`-style flag skips it), and (b) the `AskUserQuestion`
  tool is absent from the tool list entirely (the skill is hosted as a
  subagent). An
  absent tool is exactly as non-interactive as an unanswered one — both take
  the recommended default. The final report MUST annotate every substituted
  decision as 「此處採預設：{假設}」. A skill's `references/loop-pauses.md`
  table may bind a specific Input row to a stop-and-report default — report
  `no progress: {reason}` and end the run — when no recommended default can
  exist for that point (the answer requires information only a human holds);
  the per-skill table is the authority for that point's non-interactive
  behavior.
- **Authorization PAUSE** — if the driving context carries a **standing
  authorization** for this action (per the skill's `references/loop-pauses.md`),
  proceed under that authorization, applying every safety precondition the table
  names (e.g. structure gate, blind-judge bar, file-level snapshot, audit log),
  and record the standing-authorized decision in the run's audit trail.
  Otherwise it is an unconditional hard stop: report `needs input` to the driver;
  never substitute a default. Tool absence does not weaken this: a missing
  `AskUserQuestion` tool (subagent hosting) never downgrades an Authorization
  PAUSE to a default substitution. It remains a hard stop reported to the
  upper layer, satisfiable only by a standing authorization where the skill's
  `references/loop-pauses.md` permits it. "Cannot ask" is not "may assume" —
  only Input PAUSE takes a default under tool absence; Authorization PAUSE
  does not.

**Override precedence (explicit)**:

> Driving context overrides the platform default. An Authorization PAUSE is never satisfied by a default substitution — only by explicit human authorization, given interactively at the stop or as a standing authorization recorded in the driving context where the skill's loop-pauses table permits it.

An Authorization PAUSE is never satisfied by `--auto`, driver flags, or platform
mode alone — those are default substitutions, not authorization. A standing
authorization is explicit human authorization given up-front (not a default), so
it is the one sanctioned way a non-interactive run may proceed past such a PAUSE.

### Interactive-capability detection primitive

The detection primitive is a **tool-list inspection**: at the start of a run
the skill inspects its own available tool list and checks whether
`AskUserQuestion` is present. Present means the interaction axis is live and
platform defaults govern PAUSE cost; absent means every Input PAUSE takes its
recommended default (annotated) and every Authorization PAUSE hard-stops per
the rules above.

The tool-list check covers the hosted-as-subagent case (tool hard-absent).
It does not — and cannot — detect `/loop`, cron, or Workflow driving, where
the tool is present: those are **declared by the driving context itself** (the
loop/cron prompt, Workflow script, or a system reminder stating non-interactive
drive), not detected. The two signals are independent, and either one alone
marks the run non-interactive.

This detection MUST be a direct tool-list check, **not** an attempt-and-catch.
Tool absence means the tool does not exist in this runtime — there is no call
to attempt and no error to catch, so invoking a missing tool "to see if it
fails" is forbidden and would simply be a no-op or an undefined reference, not
a signal. Inspect the tool list directly.

The detection gates the **interaction axis only** (Input and Authorization
PAUSE). It does **not** gate worker fan-out: subagent dispatch relies on the
Task/Agent tool, which is always present, so fan-out stays unconditionally
allowed whether or not `AskUserQuestion` is in the tool list. A skill hosted
as a subagent still fans out its own worker layer exactly as it would when
driven interactively — only its PAUSE handling degrades, never its dispatch.

---

## 3. Three hard stops — responsibility boundary

Loop control belongs to the driver; reentrancy and reporting belong to the
skill. Three driver-owned hard stops, explicitly:

| # | Hard stop | Owner | Mechanism |
|---|-----------|-------|-----------|
| 1 | Iteration cap | Driver | `/loop` / Workflow script counts rounds |
| 2 | No-progress detection | Driver | Workflow script compares consecutive outputs |
| 3 | Budget cap | Driver (harness) | harness budget mechanism |

Skill-side obligations (all mandatory):

1. **Re-entrant** — re-invocation must resume or redo safely; repetition never
   corrupts state.
2. **State on disk** — persist working artifacts under `.codex/<skill>/` so
   the driver and the next invocation can observe progress.
3. **Explicit no-progress reporting** — when the skill detects it cannot
   advance, report `no progress: {reason}` instead of silently retrying.
4. **Machine-checkable outcome signal** — every loop-driven run's final
   message MUST end with the single line
   `LOOP_OUTCOME: ok | blocked | no progress: {reason}`.
   Drivers grep this line for go/no-go instead of trusting the process exit
   code (a mid-run kill can still return rc=0 — documented false green,
   2026-06-29). `blocked` covers §2 `needs input` hard stops; `no progress`
   carries the same reason as obligation 3 — one literal, space form, in both
   the in-report phrase and this terminal token. No line means the run did
   not complete.

---

## 4. PAUSE classification registry

Each loop-classified skill owns its PAUSE classification table in its own
`references/loop-pauses.md`, enumerated from that skill's live SKILL.md and
re-verified when that SKILL.md changes. A skill absent from this registry has
no PAUSE checkpoints beyond the shared semantics — its `loop=` value in the
Outcome Contract still applies.

| Skill | PAUSE classification |
|---|---|
| $review | `../review/references/loop-pauses.md` |
| $contract | `../contract/references/loop-pauses.md` |
| $seal | `../seal/references/loop-pauses.md` |
| $hunt | `../hunt/references/loop-pauses.md` |
| $learn | `../learn/references/loop-pauses.md` |
| $ship | `../ship/references/loop-pauses.md` |
| $evolve | `../evolve/references/loop-pauses.md` |
| $think | `../think/references/loop-pauses.md` |
| $write | `../write/references/loop-pauses.md` |
| $read | `../read/references/loop-pauses.md` |
| $book | `../book/references/loop-pauses.md` |
| $design | `../design/references/loop-pauses.md` |
| $health | `../health/references/loop-pauses.md` |
| $codex-skill-transfer | `../codex-skill-transfer/references/loop-pauses.md` |
