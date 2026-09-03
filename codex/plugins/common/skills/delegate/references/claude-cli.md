# delegate: Claude CLI

Load only after Claude CLI is settled as the execution carrier. This document covers the execution mechanism only; it takes no part in the delegation decision.

## Inputs

```text
MODEL=<an alias listed by claude --help, or a full model ID>
EFFORT=<an effort that model supports>
FAST=<must be false>
PERMISSION=<plan|acceptEdits>
BRIEFING=<self-contained delegation content, including the strategy-autonomy clause>
WRITE_SET=<none when read-only; an exact list when writing>
DISALLOWED_TOOLS=<tools forbidden under acceptEdits; write "none" when there are none>
```

`--fast` is Codex-only. `FAST=true` or a standalone `--fast` still present in `BRIEFING` is an upstream contract violation: report that Fast is unavailable on Claude and must not launch Claude CLI. Do not silently ignore it or substitute a Claude model or effort. Ordinary delegation with `FAST=false` remains valid.

## Preflight

Resolve `DELEGATE_DIR` per the rule at the top of the main skill. Run `claude --version` and `claude auth status`, confirming `loggedIn`; if not logged in, stop and ask the user for an interactive login. Aliases listed by `--help` are usable directly as arguments — do not send a probe prompt first to resolve the full ID. If an argument is rejected → report the incompatibility and refresh the main skill's model catalog; never retry by dropping the argument and falling back to a default.

- Treat Markdown backticks inside a double-quoted shell command as executable command substitution, not inert text. Keep briefings in quoted variables or stdin and use single-quoted search patterns when they contain backticks. A shell quoting failure before the session exists is a launch correction, not re-delegation.
- A multi-file patch may fail atomically because one target has stale context. After any patch failure, verify whether nothing was applied, re-read every target, and retry with smaller hunks; never assume the earlier files succeeded.
- A multi-command validation shell normally returns only the last command's status. Use fail-fast mode or capture and aggregate every required status; never let a later successful status/diff command mask an earlier failed assertion.
- For source/generated parity checks, normalize only documented adapter differences. When the assertion fails, inspect the precise diff before editing either side; a faulty normalization rule is not product drift.

## Permission-mode mapping

`PERMISSION` is the tool-execution envelope; it is not the write set:

| The task needs | `PERMISSION` | Additional restriction |
|---|---|---|
| Only the read / search / planning tools plan mode allows | `plan` | `WRITE_SET=none` |
| MCP, read-only shell, or other tools plan mode will not execute | `acceptEdits` | `WRITE_SET=none` + `--disallowedTools` blocking `Write,Edit,NotebookEdit` and any non-essential shell |
| To modify workspace artifacts | `acceptEdits` | Declare an exact `WRITE_SET`; enable only the necessary tools |

Never start on `plan` and escalate mid-run.

## Private content and network

Crossing to another CLI means content may be sent to a different model service. Send only the minimum necessary; strip accounts, credentials, and unrelated data. When the briefing contains internal organizational information (source code, logs, customer data), tell the user what will be sent and obtain explicit consent before the first call — "use Claude" is not informed authorization. When Codex is the lead, its sandbox may block the Claude API: request scoped network permission on the first real call rather than running a test you expect to fail.

## Scratch and output

Generate a UUID for every new session and pass it via `--session-id`; never guess results from "the latest session". Create a unique `SCRATCHPAD` in writable temp, and always write stderr and runner identity into the scratch (they are required for argument-failure diagnosis and precise intervention).

Short tasks: pipe a single JSON object into `parse-cli-json.js fields result`. Tasks expected to exceed 60 seconds: use `stream-json --verbose` piped into `reduce-cli-events.js --provider claude`, run in the background. Do not use `--include-partial-messages`. For supervised work, inspect the ledger, reducer summary, stderr, and actual diff according to the main skill. Never read raw JSONL into the lead's context.

## Execute

Short task (Git Bash):

```bash
claude -p --session-id "<uuid>" --model "$MODEL" --effort "$EFFORT" \
  --output-format json --permission-mode "$PERMISSION" \
  "$BRIEFING" < /dev/null 2>"$SCRATCHPAD/claude-stderr.log" \
  | node "$DELEGATE_DIR/scripts/parse-cli-json.js" fields result
```

Long task: switch to `--output-format stream-json --verbose`, pipe into the reducer, use `run_in_background: true`, and preserve the runner PID/process-tree identity. Follow the main skill's supervised patrol and report status at least once before completion.

### PowerShell argument order (⛔)

`--allowedTools` / `--disallowedTools` / `--add-dir` accept multiple values, so the positional prompt must come **before** them — otherwise the briefing is swallowed as a tool name and the CLI only answers "Input must be provided":

```powershell
claude -p "$BRIEFING" `
  --session-id "$SESSION_ID" --model "$MODEL" --effort "$EFFORT" `
  --output-format json --permission-mode "$PERMISSION" `
  --disallowedTools "Write,Edit,NotebookEdit,Bash" `
  2> "$SCRATCHPAD/claude-stderr.log" |
  node "$DELEGATE_DIR/scripts/parse-cli-json.js" fields result
```

PowerShell does not use `< /dev/null`.

## Resume

```bash
claude -p --resume "<session-id>" --model "$MODEL" --effort "$EFFORT" \
  --output-format json --permission-mode "$PERMISSION" \
  "<checkpoint answer or corrected briefing>" < /dev/null 2>"$SCRATCHPAD/claude-stderr.log" \
  | node "$DELEGATE_DIR/scripts/parse-cli-json.js" fields result
```

Raising `plan` to `acceptEdits` requires a new session.

Before resume, confirm the prior runner process tree has stopped. Use only the session ID created for this task; never use `--continue` to guess the latest session.

## Empty output and failures

Empty stdout → read stderr first, then check the local record for that session ID to verify the prompt and cwd:

- stderr shows an argument-parsing error **and** the session does not exist → fix the command and resend (a launch correction; does not count toward re-delegation).
- The session already exists → do not resend the prompt. If there is an assistant message, take the last result; if there are only user messages, poll once.

Classify failures per the main skill: CLI missing / not logged in / argument rejected / `ConnectionRefused` (a network restriction — diagnose it separately from "not logged in") are environment-class and do not count toward re-delegation. When the sidekick returns `WAITING_USER`, keep the session and scratch, hand the question over, then resume.

If the runtime rejects the scratch cleanup primitive before execution, do not rerun the delegated task. Use an allowed exact-target cleanup mechanism, or preserve and report the scratch path when no safe mechanism is available.

## Accepting external tool results

The sidekick's prose summary is not tool evidence. Using the session ID, the lead inspects the local transcript: the actual tool calls (tool name, key arguments, target scope), their matching `tool_result`, and the resolved model ID when one is returned. Only when these agree with the summary does the delegation move `DELIVERED → VALIDATED`.

## Cleanup

In stream-json mode, once resume, retry, and waiting are all ruled out, clear the scratch with the reducer's `--cleanup`. Never clean up while running or while in `WAITING_USER`.
