---
name: delegate
description: 'Delegates a bounded, independently-verifiable execution slice to a cheaper
  sidekick model — use when the user says 派工, 派給, 委派, 丟給 codex, delegate this, hand
  this off, asks for Luna Max, wants to run it in the background with a cheaper model,
  or when a scan / log sweep / test run would burn the lead''s context. Runs over
  native sub-agents, Codex CLI, or Claude CLI: judges whether delegating pays off,
  scores the task into lightweight, full, or supervised execution, and queries the
  live model catalog for the lowest viable model + effort. Codex users may explicitly
  request --fast to run the sidekick with Codex Fast service tier; Claude must not
  enable it. Supervised long tasks use an auditable progress ledger, periodic diff
  patrols, and checkpoint resume. Briefings fix goal, permissions, and acceptance
  — never the execution path; the lead keeps analysis, decisions, and acceptance.
  Not for plain discussion or second opinions.'
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# delegate — goal-oriented delegation

## Codex Port Adapter - Bundled Agent Resolution

This plugin does not assume package-local TOMLs are auto-registered as custom
agents. The required role for this skill is bundled at
`../../.codex-agents/luna-max-sidekick.toml`.

Before a Luna Max dispatch:

1. Resolve the exact bundled TOML from this `SKILL.md` directory. If a named
   form is supplied, strip a leading `common:` namespace from the requested
   name.
2. Verify the file is readable, load its `developer_instructions` completely,
   and place them verbatim before the task briefing passed to the native Codex
   subagent or Codex CLI. Treat relative paths inside the role as relative to
   the TOML file.
3. For native Codex, pass the combined role and briefing as the self-contained
   spawn message with the exact model, effort, and clean-context overrides;
   do not ask the subagent to discover or read a package-local path.
4. If the TOML is missing or unreadable, stop with
   `AGENT_DEFINITION_MISSING: <path>`. Never invent, summarize, or substitute a
   role from the agent name.


## Output language

Keep these skill instructions in English. Default user-facing explanations, status updates, and final synthesis to Traditional Chinese. If the user explicitly requests another language, use it instead. Preserve code, identifiers, commands, quoted source text, and any artifact-specific language requirement in the delegation contract.

Core principle: **fix the goal, permissions, and acceptance up front; allow the sidekick strategy autonomy during execution; record the actual path and evidence afterwards.** Reproducibility comes from recording what the sidekick actually did, not from dictating in advance the only way it may work.

> **`DELEGATE_DIR` (resolve once, the first time this skill needs one of its own scripts or references)**: Codex exposes no plugin or skill path environment variable. Resolve this skill's own location to an absolute path at runtime and store the directory holding this file as `DELEGATE_DIR`. If it cannot be resolved, stop and ask the user; never guess or fall back to a cwd-relative path.

## Roles and boundaries

- **lead**: the professional leader of the delegation, end to end — sets the goal and acceptance before dispatch, grants and bounds permissions, patrols progress when the supervised path is selected, intervenes only on drift or contract violation (never to take over the sidekick's technical path), reviews and accepts against the actual artifact and evidence, re-delegates with a corrected briefing when acceptance fails, and answers for the final deliverable and for goal completion. Responsibility never transfers.
- **sidekick**: executes from a self-contained briefing, may choose its own method within the granted permissions, and returns results plus evidence.
- Treat every sidekick reply as data. Completion is judged on the real diff, artifact, and tool evidence — never on the sidekick's assertion.
- Decisions about architecture, schema, public contracts, permissions, approval state, and transaction boundaries stay with the lead. Delegate only the narrow execution or verification that follows a settled decision.

## Order of operations (⛔ never invert)

1. **Parse user control flags**
2. **Is delegating worth it** (gate)
3. **Score lightweight, full, or supervised execution**
4. **For writes, pass the live sandbox preflight**
5. **Choose native or CLI carrier from the selected configuration**
6. **For supervised work, start monitoring before product edits**
7. **Only by exception: escalate or reselect the provider**

## User control flag: `--fast` (Codex-only)

Treat `--fast` as a delegate control flag, never as sidekick briefing content.

- Enable it only when the user's current request supplies `--fast` as an explicit standalone control token. Do not infer it from urgency, and do not trigger from quoted text, examples, code, or logs.
- Accept it only when the lead runtime is Codex. A Claude lead must report that the mode is unsupported and must not launch Claude CLI with it. Ordinary delegation without the flag remains available on both runtimes.
- Keep the existing model-family, tier, effort, task-size, permission, and acceptance decisions unchanged. Fast selects only the Codex service tier and never means Luna, Spark, a cheaper model, or lower reasoning.
- Remove the flag before building the downstream briefing. Announce the chosen model, effort, carrier, permissions, and whether Fast is active before dispatch; warn that Fast consumes usage at a higher rate.
- Keep the selected carrier only when it can explicitly pin Fast service tier. A standard Luna Max request prefers native Codex when that carrier can pin the exact model and effort; if the native carrier cannot also pin Fast, use Codex CLI with the per-invocation override in `references/codex-cli.md`. Apply the same native-then-CLI rule to other profiles. Never persist the user's config or claim Fast from prompt wording alone.
- If the current Codex login, model, feature, or carrier cannot honor Fast, state `FAST_FALLBACK: Fast unavailable; using standard sidekick.` and fall back visibly to the existing standard sidekick flow with the same selected model and effort. Never fall back to Claude, and never claim Fast was active.

## Delegation gate

A task becomes a candidate if any of these hold: the user explicitly asked for delegation; the work is self-contained and only its summary is needed; a search / log / test sweep would consume a large share of the lead's context; several tasks are genuinely parallel with non-overlapping write sets.

The benefit must exceed the total cost of briefing + launch + acceptance + rework. Do not delegate when the task would finish faster than its briefing takes to write, when it is tightly coupled to the main line of work, or when the result is hard to spot-check. **When in doubt, do not delegate.** If the user names a specific model or tool, comply; if it is clearly not worth it, say so in one sentence and proceed.

**Split exploration in two before judging.** Exploration = scanning (gathering facts) + understanding (forming design judgment). **Delegate the scanning, never the understanding.** Decide by the shape of the output: work that can be written as a list or table plus coordinates (`file:line`, table name, position) is scanning — delegable and spot-checkable. Work whose output is narrative, interpretation, or recommendation is understanding — the lead does it. Interpretation the sidekick volunteers alongside its report may inform the lead but must never be used directly as a basis for a decision. The lead personally spot-checks load-bearing points and every negative claim ("not found", "does not exist"); for the rest, trusting the summary is enough.

## Lightweight path (default)

All of these must hold: single-shot; clearly bounded and independently verifiable; no human decision or long monitoring required; no sensitive data leaves the machine; read-only or a very small write set.

How: pick the lowest viable configuration against the model catalog (next section), announce the delegation in one sentence (what, to whom, which configuration and permissions), and send it. Do not write a full status narrative.

If any condition fails → take the full path: same catalog-driven model selection, plus a complete briefing and acceptance narrative.

## Task size and path selection

Do not decide from vague impressions or file count alone. Score each dimension from 0–2 before dispatch: `0–2` uses the lightweight path, `3–5` the full path, and `6–8` the supervised path. When the estimate is genuinely uncertain, choose the higher path; do not pretend wall time is predictable. The score decides the path; the lightweight-path conditions above are extra guards, not a second selector — if any of them fails (including sensitive data leaving the machine), a `0–2` score still takes the full path.

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Execution stages | Single verification or artifact | 2–3 stages | 4+ stages or iterative repair |
| Write surface | Read-only or one non-code artifact | 1–3 files in one module | 4+ files, cross-module/repo, or shared worktree |
| Execution / validation time | Expected under 2 minutes | About 2–10 minutes | Over 10 minutes or highly uncertain |
| Cost of drift | Easy rerun, directly comparable result | Reversible local code change | Workflow, transaction, schema, public contract, or external side effect |

Hard overrides:

- A user request for periodic monitoring, a progress ledger, or intervention on drift → supervised.
- One deterministic long-running command, such as a fixed test suite, does not justify delegation by duration alone; the lead uses the runtime's wait or monitoring mechanism directly.
- Irreversible or external side effects retain a human checkpoint. Supervision never expands the original authorization.

## Model catalog (query once, live, per session)

Selection is driven by a **candidate catalog** — the candidate models per carrier, the efforts each supports, and their tier — not by a fixed default. Do not maintain a persistent cache file: the query costs one command, a few seconds, and a few lines of output. Query it **live** the first time a session passes the delegation gate and actually needs to pick a model; later delegations in the same session reuse that result.

- Codex native sub-agents: inspect the live native spawn tool schema for its advertised model overrides and reasoning-effort values. Treat those entries as native candidates and use a successful launch as the availability check; do not use the CLI catalog as proof of native support.
- Codex CLI: `codex debug models` **must be piped through the `$DELEGATE_DIR/scripts/parse-cli-json.js models` filter**, keeping only model names, descriptions, supported reasoning levels, and Fast eligibility. The raw output exceeds 200 KB and must never be read into context in full.
- Claude CLI: the aliases listed by `claude --help` (usable directly as the `--model` argument).
- Claude native sub-agents: the aliases the native spawn tool accepts (or the agent definition's `model:`) — no query needed.

If the query fails (no network, CLI error) → use a configuration already known to work in this session, or ask the user. Never guess a model name from memory.

**Pin model and effort on every dispatch.** Both runtimes let an unpinned sub-agent inherit the parent's model, and Codex also inherits the parent's effort — a lead running the top tier at high effort silently hands the same cost to a grep sweep. Prefer current-generation catalog entries; one the catalog describes as older or previous generation needs a reason.

**Selection has two axes, in this order — family fit first, then tier.** A model is not simply stronger or weaker than another; families think differently, and a bad fit does not improve by paying for a bigger model in the same family.

1. **Family fit** — match the family to the *shape* of the work, never to a version number. Resolve concrete model IDs from the live catalog above; never hardcode a version, because families outlive their releases. The table is a working heuristic from observed runs, not vendor documentation — re-check it when a generation changes.

   | Work shape | Family | Why |
   |---|---|---|
   | Bounded execution from a stated goal; autonomous multi-file exploration; deep single-problem digging with no hand-holding | **GPT family** | Principle-driven: give the goal and the decision criteria, and it finds its own mechanics. |
   | Long multi-step procedures that must be followed exactly; structured or templated output; work whose value is in compliance with a checklist | **Claude family** | Mechanics-driven: follows detailed step-by-step instructions closely and reproduces required structure. |
   | Mechanical scanning, single-shot verification, grep-shaped inventory | **either — take the cheapest tier available** | Fit barely matters at this size; cost does. |

2. **Tier** — inside the chosen family, start at the lowest viable tier and effort. Escalate only after a failure or on concrete evidence that the configuration is too weak, and **raise exactly one dimension at a time** — model or effort, never both. **Raise effort first** (up to `high`), after confirming the briefing already states the goal and success criteria — a missing completion bar fails more often than a low effort; move to a larger model only when the current one still falls short at `high`. Anthropic's guidance names effort tuning as often the cheaper lever than switching models.

   | Work | Claude side | GPT side |
   |---|---|---|
   | Scanning, summaries, compaction, classification, no-judgment writing | Haiku line at `medium` (`low` on a long agent prompt tends to skip searches and stop early) | Luna line (Codex suggests `high` as the start for explicit settings) |
   | Well-scoped implementation, everyday bug fixes | Sonnet line, `medium`; `high` for hard bugs | Sol line |
   | Independent review of a diff | Opus line at `high`, fresh context | Sol line at `high` |
   | Hardest problems, high-risk final review | Fable line, only after the Opus line at `high` falls short | Astra line, same condition |

   Read the rows as starting points inside a family, not as a fixed roster. For long-context bulk work compare long-prompt pricing: the cheapest per-token model may not stay cheapest past its long-prompt threshold. A cross-family second opinion is worth its cost for high-risk review; routine review is not.

**Before escalating tier, re-check family fit.** A sidekick that produced confident-but-wrong structure, drifted off the goal, or ignored parts of the briefing is usually a family mismatch, not an under-powered tier; escalating within the wrong family spends more and still fails.

`xhigh` / `max` / `ultra` require an explicit user request. Codex `ultra` is maximum reasoning plus proactive delegation: the sidekick may spawn sub-agents of its own, which breaks the bounded-slice contract, so even on request confirm the user wants that before using it. Claude Code's `ultracode` is a setting, not an effort level. If a user-specified model does not support the specified effort, stop and report; do not silently substitute a different model.

### Bundled Luna Max sidekick role

When the user explicitly requests **Luna Max**, require the current-generation Luna model from the live Codex catalog — the Luna entry not described as older or previous generation — with `max` effort, and name the resolved ID when announcing the dispatch. If more than one candidate remains, list them and ask the user; never pick by guess. A Codex lead must prefer a native Codex sub-agent when the live spawn schema exposes both model and effort overrides. Load the complete bundled role at `$DELEGATE_DIR/../../.codex-agents/luna-max-sidekick.toml` and place its `developer_instructions` verbatim before the task briefing for either carrier; never infer support from this file alone.

- For native Codex, call the native spawn tool with `model="<resolved Luna ID>"`, `reasoning_effort="max"`, and `fork_turns="none"`; the briefing is self-contained, so the clean context is intentional. The bundled agent file supplies role instructions but is not an auto-registered native agent.
- A Claude lead cannot launch this GPT profile through a Claude native sub-agent. Use Codex CLI with the same exact model, effort, role, and briefing. A Codex lead also crosses to Codex CLI when its native schema or launch cannot pin the exact profile.
- If the same request supplies `--fast` and the native carrier cannot pin Fast, apply Fast to the Codex CLI invocation per `references/codex-cli.md`; it changes only the service tier.
- If neither Codex carrier can provide the exact model, effort, and bundled role, report the precise incompatibility. Never silently substitute another model, effort, carrier family, or improvised role.

## Execution carrier

Prefer a native sub-agent when it can launch the chosen configuration; cross to another CLI only when it cannot. This includes Luna Max on a Codex lead when native spawn can pin the exact model and effort. Read the matching reference only after the carrier is settled — never pre-read the other provider's:

| CLI | Required reference |
|---|---|
| Codex | `$DELEGATE_DIR/references/codex-cli.md` |
| Claude | `$DELEGATE_DIR/references/claude-cli.md` |

Use explicit native model and effort overrides when the live schema exposes them. A package-local bundled role is not an auto-registered custom agent: load its complete instructions into the native briefing instead of naming an agent that the runtime cannot discover. If the selected native carrier cannot pin the exact configuration, cross to the matching CLI. For Fast alone, switch to Codex CLI only when the selected native carrier cannot honor the service tier, then use the visible standard-sidekick fallback if Fast is unavailable. Keep explicit profiles fail-closed unless their own contract says otherwise.

## Supervised long tasks

Enable this only when the score or a hard override selects the supervised path. Do not impose its coordination cost on short work.

### Progress ledger

- Give the sidekick one self-contained HTML ledger and include it in the write set. Default to `<repo>/.codex/impl.html`; parallel tasks use distinct `.codex/impl-<task>.html` files and never share one ledger.
- Record the current stage, files read, evidence summary, decisions and tradeoffs, actual changes, failures/retries, blockers, risks, validation, and unrun checks. Require auditable rationale summaries, never private chain-of-thought.
- Create the ledger before editing product files. Update it after each meaningful analysis, implementation, or validation milestone, not after every small tool call.
- Treat the ledger as a progress signal, not completion evidence. Acceptance still depends on the actual artifact, diff, and tool output.

### Patrol and intervention

- Patrol every 5 minutes by default; a user-specified interval wins. Completion, failure, or an explicit checkpoint may wake the lead early. Avoid high-frequency polling with no decision value.
- Inspect the runner process, ledger freshness and contents, declared write set, `git status --porcelain` (untracked out-of-scope files never appear in `git diff`), `git diff --name-only`, `git diff --stat`, load-bearing diff hunks, stderr, and final output together. Raw JSONL remains reducer-only scratch and never enters lead context wholesale.
- High/max reasoning can produce no new reducer summary for several minutes. An empty launcher or poll response is not completion and is not by itself a stall while the exact runner is alive and at least one corroborating liveness signal (event file, ledger, CPU, stderr, or process state) is moving. Declare a stall only after a full patrol interval with no new events and corroborating stale signals; never restart from one empty poll.
- No product diff while the sidekick reads required rules is not drift. Intervene only for out-of-scope writes, contract violations, unnecessary expansion, or multiple substantive events with a stale ledger.
- Before intervention, take a read-only state snapshot. Stop the exact runner process tree and confirm no writer remains. Put observed facts, drift, and passing conditions into a checkpoint; do not seize control of the sidekick's technical path.
- Resume by explicit session ID only when model, effort, permissions, and useful context remain unchanged. Start a new session after permission escalation or context pollution. Never use `--last`, and never let old and new runners write the same worktree concurrently.
- Sandbox, login, argument, and runner-start failures are environment corrections, not rework. Content drift counts as rework and is limited to two rounds; then the lead takes the task back or reports the failure honestly.

## Briefing contract (⛔ goal-oriented)

> **Principle: describe the goal and the boundaries, not the execution path.** Unless a specific method is itself a security, permission, or contractual requirement (list it as MUST with the reason), never write a tool, command, SQL statement, or step as the only permitted path. Known resources and approaches are always offered as MAY — non-binding hints.

**Keep the three required fields identical; vary only their density to fit the sidekick's family.** The contract above is what changes never — what may change is how much scaffolding sits inside it:

- **GPT family** — stay lean. State the goal, the boundary, and the decision criteria, then stop. Extra rules are extra contradiction surface: past a point, more instruction produces *more* drift, not less.
- **Claude family** — afford more structure. Spell the acceptance out as an explicit checklist and make required output shape literal; under-specifying is the failure mode here, not over-specifying.

This is a density dial on the same contract, never a licence to write the execution path back in for either family.

Three required fields:

```text
Goal and acceptance: <what result is wanted + what counts as passing + the required output language; default Traditional Chinese unless the user explicitly requested another language>
Permission boundary:
  - Read scope and write set (parallel delegations must not overlap; write "none" when read-only)
  - MUST NOT: <forbidden actions>
  - MUST: <externally imposed constraints, with the reason; omit when none>
Background (MAY): <context the lead has confirmed, known resources and leads — all non-binding>
```

Optional, only when needed: report format (default = result + actual evidence + unfinished items), a human checkpoint (only for high risk or a genuine human decision), API contracts.

For supervised work also include the absolute ledger path, update milestones, and patrol interval. The ledger must be in the exact write set and must not be shared with another sidekick.

**Acceptance for exploratory tasks**: when the answer is not known in advance (explore, inventory, find similar implementations, open-ended investigation), acceptance does not state an expected answer. It verifies **coverage and report quality** instead: which areas or angles to explore, the report structure (what was found, what was not, and the basis for each), and the stopping condition (for example, two consecutive rounds with no new findings). Never invent a fake expected result just to fill the field, and never narrow the exploration scope to make one fit.

**Strategy-autonomy clause** (embed verbatim in every briefing):

```text
You may change tools, commands, and technical approaches at will,
within the granted permissions and write set.
A single tool or approach being unavailable means only that this
strategy failed — switch approaches and retry. Report blocked only
when the acceptance goal is genuinely unreachable, or when you need
permissions or scope beyond what was granted.
```

A briefing must be self-contained. Never require the sidekick to go looking for rules that live outside it.

## Permissions

- Search, analysis, review, planning, reporting only → readonly.
- Creating or modifying workspace artifacts → write, with an exact write set declared.
- Destructive operations, external publishing, writing to shared environments, and credential handling still require the authorization they would normally require.

### Live sandbox preflight for write tasks (⛔ before dispatch)

- A sidekick inherits the parent task's current sandbox, approval policy, and writable roots. A model, effort, agent name, or redelegation never raises permissions. The briefing may narrow permissions but cannot grant writes the parent does not have.
- For a CLI carrier, derive its sandbox mode from the parent task's live envelope, not from the word "write" alone. A read-only task stays `read-only`; a write task under `workspace-write` stays `workspace-write`; an authorized write task under an unrestricted / `danger-full-access` parent uses `danger-full-access` plus the exact write set. Never upgrade beyond the parent, and do not create a narrower Windows ACL sandbox merely by habit.
- Resolve every write-set item to an absolute path and verify it is inside the current runtime's writable roots. A readable sibling repo or an `additionalDirectories` entry is not proof of write access.
- If a target is outside the writable roots, select the correct workspace root or obtain the required parent-task permission before dispatch. `Ask for approval` and auto-review change approval routing, not sandbox boundaries.
- If writable roots are not explicit or Windows ACL behavior is uncertain, perform one minimal reversible write probe inside the authorized target. For supervised tasks, creating the ledger may serve as the probe. A failed probe stops dispatch and preserves the error and target path.
- Treat `SetNamedSecurityInfoW failed: 5`, workspace sandbox denial, or an unavailable approval prompt as environment failures. Inspect the actual workspace, permission mode, and sandbox log where available. Do not resume or redelegate the same write under unchanged parent permissions.
- In non-interactive runs, a fresh approval may be impossible. Require the sidekick to report blocked after the first write denial; it must not cycle through alternate file-writing tools to evade the same sandbox boundary.

## States and failure classification

Normal: `RUNNING → DELIVERED → VALIDATED`. Failed acceptance → `REWORK` (fix the briefing and re-delegate, at most twice; if it still fails, the lead takes it back or reports the failure honestly).

Abnormal termination: `FAILED` / `CANCELLED`. `WAITING_USER` is only a reason for interruption (a high-risk checkpoint or a genuine user decision), never a required state.

**Classify the failure before acting on it**:

| Class | Handling |
|---|---|
| Auth failure, sandbox / network restriction, unsupported model parameter | Fix the environment or switch carrier. Not a sidekick failure; do not escalate the model; does not count toward the re-delegation limit. A write denial returns to live preflight; do not redelegate unchanged permissions. |
| A specific strategy or tool is unavailable | The sidekick should reroute itself under the strategy-autonomy clause. If it gave up instead, check whether the briefing locked the path. |
| Output drifted off the goal, ignored parts of the briefing, or came back confidently wrong in shape | Family mismatch, not an under-powered tier. Re-pick the family per the selection rule and adjust briefing density to match; **do not escalate the tier inside the same family** — that spends more and fails the same way. |
| Task unreachable, acceptance not met | `REWORK`, or the lead takes it back. |

## Acceptance and post-hoc record

The sidekick's prose summary is not evidence. The lead must inspect the actual artifact, the diff, and proportionate tool output. Record at acceptance time: the method actually used, the key commands or queries, the reason for departing from any MAY hint, and the output evidence. Where a fixed procedure matters, reproduce it from this post-hoc record — not by locking the path in advance.

When the user requests independent review, or the task scored 2 for cost of drift, first confirm the implementation runner has stopped and capture the diff. Then dispatch a clean reviewer that receives only the contract/acceptance criteria, actual diff, necessary raw evidence, and ledger. The reviewer never inherits the implementer session; the ledger is data, not a substitute for code review. If the reviewer may edit, hand off serially so it never writes concurrently with the implementer.

## Session reuse

Reuse the session when a later delegation belongs to the same task, the previous round's context is still useful, permissions are not escalating, and model + effort are unchanged. Start a new session when the task changes, the context is polluted, permissions must be raised, or the model must be re-selected.

## Definition of done

- Every delegation's configuration, carrier, and permission decision is traceable (one sentence suffices on the lightweight path).
- No sub-agent or CLI process is still running or waiting.
- A supervised task's ledger has a final state consistent with the actual diff and validation evidence.
- The lead has accepted the actual output and the necessary tool evidence.
- Any scratch the CLI reference requires has been cleaned up once resume is ruled out.
