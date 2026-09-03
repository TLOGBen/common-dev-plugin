# delegate: Codex CLI

Load only after Codex CLI is settled as the execution carrier. This document covers the execution mechanism only; it takes no part in the delegation decision.

## Inputs

```text
MODEL=<the actual model chosen from the main skill's model catalog>
EFFORT=<an effort that model supports, as selected>
FAST=<true|false; true only from an explicit --fast parsed by a Codex lead>
PERMISSION=<read-only|workspace-write|danger-full-access; never broader than the parent task>
BRIEFING=<self-contained delegation content, including the strategy-autonomy clause>
WRITE_SET=<none when read-only; an exact list when writing>
```

## Preflight

Run `codex --version` and `codex login status` directly. A restricted sandbox returning `Not logged in` only means the state could not be confirmed — re-check read-only from outside the sandbox, and stop to ask the user for an interactive login only if the outside check also reports not logged in. The carrier still needs writable runtime state to bootstrap even when the delegated thread uses `-s read-only`; `failed to initialize in-process app-server client: Read-only file system` before a `thread_id` exists is an outer-environment failure, not a sidekick failure. Correct the carrier environment while preserving the inner read-only boundary, then launch once. Do not copy credentials into a temporary `CODEX_HOME`. If a model or effort argument is rejected → report backend incompatibility and re-query the model catalog; never retry by dropping the argument.

`WARNING: proceeding` together with `Refusing to create helper binaries under temporary dir` is non-fatal for a temporary `CODEX_HOME`: judge the actual command exit/result and do not retry solely because PATH helper creation was skipped.

### Fast service tier (per-invocation only)

- For `FAST=true`, require the selected model to show Fast eligibility in the filtered live catalog. Remove `--fast` from `BRIEFING`.
- Set `FAST_ARGS=(--enable fast_mode -c 'service_tier="fast"')` and pass it to both execute and resume. Do not run the interactive `/fast` command and do not edit `config.toml`.
- If login type, model metadata, feature support, or CLI argument parsing cannot honor Fast, print `FAST_FALLBACK: Fast unavailable; using standard sidekick.`, set `FAST=false`, clear `FAST_ARGS`, and continue through the standard Codex sidekick flow with the same model and effort. This environment correction does not count as rework.
- Never use a Claude carrier as the fallback, never infer Fast from urgency, and never report Fast active unless the actual invocation carried the override.

### Sandbox-mode parity

Choose `PERMISSION` once from the parent task's live sandbox, before launch:

| Parent task | Delegated task | `PERMISSION` |
|---|---|---|
| Any mode | Read-only | `read-only` |
| `workspace-write` | Authorized writes inside verified roots | `workspace-write` |
| Unrestricted / `danger-full-access` | Authorized writes in the exact declared write set | `danger-full-access` |

Never upgrade beyond the parent task. Equally, do not automatically downgrade an unrestricted parent write task to `workspace-write`: on Windows this creates a new ACL sandbox and can turn an already-authorized writable checkout into `Failed to write file` / `SetNamedSecurityInfoW failed: 5`. Preserve the live parent envelope and narrow the sidekick through the exact write set, working directory, briefing, and lead acceptance.

`-s danger-full-access` is the explicit sandbox mode shown by `codex exec --help`; it is not the forbidden `--dangerously-bypass-approvals-and-sandbox` flag. Use it only when the parent task is already unrestricted and the write is authorized. If the parent mode cannot be observed, stop and inspect it rather than guessing.

## Scratch and reducer

Create a unique `SCRATCHPAD` in writable temp (when temp is not writable, fall back in order: OS temp → a unique scratch directory in the workspace, removing the latter when done). Keep raw, final, `session-id.txt`, stderr, launcher handle, and actual runner identity in the same scratch. A background launcher may yield an empty response while the runner remains active; track the launcher handle separately from the runner PID/session and confirm completion from process state plus exit/final evidence. Always pipe JSONL through the reducer; never read raw JSONL into the lead's context.

## Execute

Always run in the background (Bash `run_in_background: true`):

```bash
FAST_ARGS=()
if [ "$FAST" = "true" ]; then
  FAST_ARGS=(--enable fast_mode -c 'service_tier="fast"')
fi

codex exec --skip-git-repo-check -m "$MODEL" \
  -c "model_reasoning_effort=\"$EFFORT\"" \
  "${FAST_ARGS[@]}" \
  -s "$PERMISSION" --json \
  -o "$SCRATCHPAD/codex-final.txt" \
  "$BRIEFING" < /dev/null 2>"$SCRATCHPAD/stderr.log" \
  | node "${CLAUDE_PLUGIN_ROOT}/skills/delegate/scripts/reduce-cli-events.js" \
      --provider codex \
      --raw "$SCRATCHPAD/codex-events.jsonl" \
      --final "$SCRATCHPAD/codex-final.txt"
```

- When the task needs network access and `PERMISSION=workspace-write`, add `-c "sandbox_workspace_write.network_access=true"`. Some crypto and network components inside the Codex sandbox differ from the host, so a sidekick connection failure is a "sandbox restriction" class failure — the briefing's strategy-autonomy clause should let it switch approaches.
- When the write set spans multiple workspace roots, choose the narrowest common workdir or add only the required paths with `--add-dir`; never make an entire drive writable for convenience. The ledger must also be inside a real writable root.
- The reducer writes `thread_id` into `session-id.txt`; it never enters the lead's context.
- After background launch, preserve the runner PID and process-tree identity. Intervention stops only that tree, never every process named `codex`.
- Success is judged on the exit code **and** the final output together.
- Read-only shells may reject heredocs or other inline forms that need temporary backing files. That is a strategy failure: use direct reads, `jq`, `python -c`, or another no-temp method in the same thread. Do not relaunch or count rework when the goal remains reachable.
- Treat Markdown backticks inside a double-quoted shell command as executable command substitution, not inert text. Keep prompts in quoted variables or stdin and use single-quoted search patterns when they contain backticks; a shell quoting correction before a `thread_id` exists is a launch correction, not re-delegation.
- A multi-file patch may fail atomically because one target has stale context. After any patch failure, verify whether nothing was applied, re-read every target, and retry with smaller hunks; never assume the earlier files succeeded.
- A multi-command validation shell normally returns only the last command's status. Use fail-fast mode or capture and aggregate every required status; never let a later successful status/diff command mask an earlier failed assertion.
- For source/generated parity checks, normalize only documented adapter differences. When the assertion fails, inspect the precise diff before editing either side; a faulty normalization rule is not product drift.

Progress reporting: for supervised work, inspect the ledger, reducer summary, stderr, and actual diff according to the main skill. Raw JSONL is reducer-only. Short tasks just wait for the result. Report status at least once before completion.

## Resume

```bash
FAST_ARGS=()
if [ "$FAST" = "true" ]; then
  FAST_ARGS=(--enable fast_mode -c 'service_tier="fast"')
fi

codex exec resume "$(tr -d '\r\n' < "$SCRATCHPAD/session-id.txt")" \
  --skip-git-repo-check -m "$MODEL" \
  -c "model_reasoning_effort=\"$EFFORT\"" --json \
  "${FAST_ARGS[@]}" \
  -o "$SCRATCHPAD/codex-resume-final.txt" \
  "<checkpoint answer or corrected briefing>" < /dev/null 2>"$SCRATCHPAD/codex-resume-stderr.log" \
  | node "${CLAUDE_PLUGIN_ROOT}/skills/delegate/scripts/reduce-cli-events.js" \
      --provider codex \
      --raw "$SCRATCHPAD/codex-resume-events.jsonl" \
      --final "$SCRATCHPAD/codex-resume-final.txt"
```

Before resume, confirm the prior runner process tree has stopped and use the explicit session ID saved in scratch; never use `--last`. Resume does not accept `-s`; changing sandbox mode requires a new thread.

## Failures and MCP

Handle failures per the main skill's classification: CLI missing / not logged in / argument rejected / sandbox restriction are environment-class — fix the environment or switch carrier, and do not count them toward re-delegation. On an empty result, inspect stderr, runner state, `session-id.txt`, and the final file before acting: no session ID plus a launch error permits one corrected launch; an existing session forbids resending the original briefing. `Reading additional input from stdin...` means stdin was left open; keep `< /dev/null` on non-interactive execute/resume. A non-zero exit code or a missing final → classify by the actual cause; do not blanket-label everything `FAILED`. Never use `--dangerously-bypass-approvals-and-sandbox`. On `user cancelled MCP tool call` → fix the approval mode first, then resume. When the sidekick returns `WAITING_USER`, keep the scratch, hand the question over, then resume.

## Cleanup

Once resume, retry, and waiting on the user are all ruled out:

```bash
node "${CLAUDE_PLUGIN_ROOT}/skills/delegate/scripts/reduce-cli-events.js" \
  --cleanup --raw <raw-path> --final <final-path>
```

Never clean up while running or while in `WAITING_USER`.

If the runtime rejects the cleanup primitive before execution, do not rerun the delegated task. Treat it as a cleanup-environment failure: use an allowed exact-target cleanup mechanism, or preserve and report the scratch path when no safe mechanism is available.
