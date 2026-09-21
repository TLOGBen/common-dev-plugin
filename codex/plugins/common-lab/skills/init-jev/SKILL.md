---
name: init-jev
description: Set up TypeSafe Jev access — make TYPESAFE_API_KEY available to the agent's
  shell without exposing the key, then verify with one cheap call. Use before `$jev`
  or `$jev-browser`, or when the user asks to set up Jev.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# Init Jev Lab

Get the user from "no key" to "one verified Jev call". Default user-facing output to Traditional Chinese.

Never print, echo, log, or write the key value anywhere. Report only whether it is set and its length.

Detect the shell first and use the matching column: bash/zsh (Linux, macOS, WSL) or PowerShell 7+ (`pwsh`, native Windows). On WSL, the key must be in the WSL shell's environment; a Windows user variable is not inherited.

1. **Check.** Report only whether the key is set and its length. If set, skip to step 4.
   - bash/zsh: `[ -n "$TYPESAFE_API_KEY" ] && echo "set (${#TYPESAFE_API_KEY} chars)" || echo unset`
   - PowerShell: `if ($env:TYPESAFE_API_KEY) { "set ($($env:TYPESAFE_API_KEY.Length) chars)" } else { 'unset' }`
2. **Get a key.** Ask the user to create one at https://console.typesafe.ai/keys and to say where they keep secrets (password manager, OS keychain, or none).
3. **Load it into the shell.** Propose one line for the user's shell startup file that reads the key from where they keep it. Show the line and let the user add it themselves or confirm before you edit any startup file.
   - bash/zsh (`~/.zshrc` or `~/.bashrc`), 1Password example: `export TYPESAFE_API_KEY=$(op read "op://<vault>/<item>/credential")`
   - PowerShell (`$PROFILE`), 1Password example: `$env:TYPESAFE_API_KEY = op read "op://<vault>/<item>/credential"`
   - PowerShell without a password manager: `Set-Secret TYPESAFE_API_KEY` once (Microsoft.PowerShell.SecretManagement), then `$env:TYPESAFE_API_KEY = Get-Secret TYPESAFE_API_KEY -AsPlainText` in `$PROFILE`. Avoid `[Environment]::SetEnvironmentVariable(..., 'User')`: it stores the key in plain text in the registry.

   Never put the raw key in a startup file, repo, or command the agent runs; if the user must paste it, have them run the command themselves in their own terminal. After changing a startup file, the user must open a new terminal (or `source` / `. $PROFILE`) and restart Codex from it so it inherits the variable.
4. **Verify.** Run one call and report only the HTTP status and latency. `200` means done; `401` means a wrong or revoked key; `402` means billing; `429` means rate limit; `503`/`529` are transient upstream overload — wait a few seconds and retry once before concluding anything.
   - bash/zsh:
     ```bash
     curl -s -o /dev/null -w '%{http_code} %{time_total}s\n' https://api.typesafe.ai/v1/systemone \
       -H "Authorization: Bearer $TYPESAFE_API_KEY" -H 'Content-Type: application/json' \
       -d '{"model":"jev-latest","state":"hello","questions":{"ok":{"type":"noul","instructions":"This text is a greeting"}}}'
     ```
   - PowerShell:
     ```powershell
     $body = '{"model":"jev-latest","state":"hello","questions":{"ok":{"type":"noul","instructions":"This text is a greeting"}}}'
     $sw = [Diagnostics.Stopwatch]::StartNew()
     $r = Invoke-WebRequest https://api.typesafe.ai/v1/systemone -Method Post -SkipHttpErrorCheck -ContentType 'application/json' `
       -Headers @{ Authorization = "Bearer $env:TYPESAFE_API_KEY" } -Body $body
     "$($r.StatusCode) $($sw.ElapsedMilliseconds)ms"
     ```
5. **Data notice.** Tell the user once: everything sent to Jev leaves the machine for TypeSafe (hosted in the U.S.); standard accounts retain input, zero retention is enterprise-only, and TypeSafe does not train on input (https://docs.typesafe.ai/legal.md). Before sending client-project content, check the client contract or company policy.
