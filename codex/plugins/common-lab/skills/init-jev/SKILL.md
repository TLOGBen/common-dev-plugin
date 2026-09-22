---
name: init-jev
description: Set up TypeSafe Jev access — make TYPESAFE_API_KEY available to the agent's
  shell without exposing the key, cached for 30 days by default so the password manager
  is not asked on every shell — then verify with one cheap call. Use when the user
  asks to set up Jev or a TypeSafe key, or when a `$jev-gate`, `$jev-pick`, `$jev-score`,
  or `$jev-browser` call fails because TYPESAFE_API_KEY is unset or rejected (401).
  Also triggers on 設定 Jev, Jev 金鑰, TypeSafe key.
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
3. **Load it into the shell — cached for 30 days by default.** Reading the key from a password manager on every new shell means an unlock prompt (for 1Password, often Windows Hello or Touch ID) every time. The default is to read it once and cache it for `JEV_KEY_TTL_DAYS` days (default 30): new shells load the cached key silently; when the cache is older than that, the key stays unset — Jev skills skip silently — until the user runs the refresh command, which prompts once and restarts the 30 days. Propose the block for the user's startup file, replacing `op read "op://<vault>/<item>/credential"` with however they read their key (on WSL, `op.exe`). Show it and let the user add it themselves or confirm before you edit any startup file.
   - bash/zsh (`~/.zshrc` or `~/.bashrc`). The cache is a plain-text file readable only by the user (directory 700, file 600) under `~/.config/typesafe/`; say so, since Linux has no universal encrypted store to rely on.
     ```bash
     # TypeSafe Jev key — cached for JEV_KEY_TTL_DAYS (default 30) days; refresh with: jev_key_refresh
     jev_key_file="${XDG_CONFIG_HOME:-$HOME/.config}/typesafe/jev-key"
     if [ -n "$(find "$jev_key_file" -mtime -"${JEV_KEY_TTL_DAYS:-30}" 2>/dev/null)" ]; then
       export TYPESAFE_API_KEY="$(cat "$jev_key_file")"
     fi
     jev_key_refresh() {
       local k
       k="$(op read "op://<vault>/<item>/credential" | tr -d '\r\n')"
       [ -n "$k" ] || { echo "jev_key_refresh: could not read the key" >&2; return 1; }
       mkdir -p "${jev_key_file%/*}" && chmod 700 "${jev_key_file%/*}"
       (umask 077; printf %s "$k" > "$jev_key_file")
       export TYPESAFE_API_KEY="$k"
     }
     ```
   - PowerShell (`$PROFILE`). The cache is a DPAPI-encrypted file under `%APPDATA%\typesafe\` that only the same Windows user on the same machine can decrypt.
     ```powershell
     # TypeSafe Jev key — cached for JEV_KEY_TTL_DAYS (default 30) days, DPAPI-encrypted; refresh with: Update-JevKey
     $JevKeyFile = Join-Path $env:APPDATA 'typesafe\jev-key.xml'
     $JevTtlDays = if ($env:JEV_KEY_TTL_DAYS) { [int]$env:JEV_KEY_TTL_DAYS } else { 30 }
     if ((Test-Path $JevKeyFile) -and (Get-Item $JevKeyFile).LastWriteTime -gt (Get-Date).AddDays(-$JevTtlDays)) {
       $env:TYPESAFE_API_KEY = [Net.NetworkCredential]::new('', (Import-Clixml $JevKeyFile)).Password
     }
     function Update-JevKey {
       $k = "$(op read 'op://<vault>/<item>/credential')".Trim()
       if (-not $k) { Write-Error 'Update-JevKey: could not read the key'; return }
       New-Item -ItemType Directory -Force (Split-Path $JevKeyFile) | Out-Null
       ConvertTo-SecureString $k -AsPlainText -Force | Export-Clixml $JevKeyFile
       $env:TYPESAFE_API_KEY = $k
     }
     ```
   After adding the block, the user runs `jev_key_refresh` or `Update-JevKey` once themselves to fill the cache. If they want no cache at all, set `JEV_KEY_TTL_DAYS=0` and read the key directly instead (`export TYPESAFE_API_KEY=$(op read …)` / `$env:TYPESAFE_API_KEY = op read …`). Without a password manager on PowerShell, `Set-Secret TYPESAFE_API_KEY` once (Microsoft.PowerShell.SecretManagement) and read it with `Get-Secret TYPESAFE_API_KEY -AsPlainText` inside `Update-JevKey`. Avoid `[Environment]::SetEnvironmentVariable(..., 'User')`: it stores the key in plain text in the registry.

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
5. **Data notice.** Tell the user once: everything sent to Jev leaves the machine for TypeSafe (hosted in the U.S.); standard accounts retain input, zero retention is enterprise-only, and TypeSafe does not train on input (https://docs.typesafe.ai/legal.md).
