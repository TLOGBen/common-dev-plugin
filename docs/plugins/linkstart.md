# `linkstart` — HTML／App 回連 Origin Session（Preview）

回到 [文件索引](../README.md)。

<img src="../images/plugin-linkstart.png" alt="linkstart" width="320">

**LinkStart v1 Preview：Stable core + Preview platform adapters** 讓互動式 HTML 或 localhost App 在原 turn 結束後，仍能透過每位 OS 使用者一個的本機 Daemon，把事件送回產出它的同一條 Origin Session，並在同一個 App 收到 Agent Feedback；不靠 `claude -p`、`codex -p`、Agent SDK subprocess 或替代 session。預設啟用（`defaultEnabled: true`）。

- Claude source：`plugins/linkstart/`
- Codex 移植：`codex/plugins/linkstart/`（不含 monitors；Codex 沒有 monitors）
- 版本：見 `plugins/linkstart/.claude-plugin/plugin.json` 與 [CHANGELOG](../../CHANGELOG.md)。舊版 README 記載當時 plugin version 是 `0.2.2`、內嵌 Runtime `0.1.3`。

## Skill：`link-start`

唯一 public skill 是 `link-start`。它在內部依序處理 Runtime／Daemon、Origin attach/rebind、App Manifest 註冊／launch，以及 private context 驅動的 `arm`／`respond` monitor flow；先辨識目前 host，再只讀對應的 `claude-code.md` 或 `codex.md` reference。

Claude Code 使用 `/linkstart:link-start <manifest.json>`；Codex 使用 `$link-start <manifest.json>`。App 回答仍只是 untrusted input，不會變成 tool approval、permission 或 scope expansion。

## Monitor flow

Monitor compatibility 不再要求模型手工串 `wait → ack → feedback → wait`。Attach 後把 state dir、`connectionId` 與 connection capability 注入 `0600` private context；`arm` 只讀 context 並等待一則 Event，`respond --payload <json>` 自動推導 pending Event/App identities、送 Delivery Ack、以 stable generated `feedbackId` 寫入 Feedback，接著進入下一次 bounded wait。Claude 用 attached background tool call 讓 completion 喚醒同一 session；Codex 用同一 wrapper 做 bounded foreground wait。

```console
printf '%s' "$CONNECTION_CAPABILITY" | runtime.py context create \
  --context "$CONTEXT" --state-dir "$STATE_DIR" \
  --connection-id "$CONNECTION_ID" --capability-stdin --json
runtime.py arm --context "$CONTEXT" --timeout-seconds 300 --json
runtime.py respond --context "$CONTEXT" --payload '{"message":"已收到"}' \
  --timeout-seconds 300 --json
runtime.py close --context "$CONTEXT" --json
```

Capability 不出現在 stdout；`close` 刪除本機 ephemeral secret，但不冒稱已完成 Runtime-side revoke。完整 attach/register/launch schemas 以 bundled Runtime `help --json` 為準，兩份 host reference 已提供 exact examples，模型不需讀 Rust source。

## 平台 adapter 分級

Claude Channel 是 Research Preview，通過 live self-test 的 Monitor 是 Experimental compatibility；Codex 只 allowlist 經完整 MOP／MOE 驗證的 LinkStart-owned app-server（初始為 `0.149.1`），standalone embedded TUI 不支援 hot takeover。未知版本、schema drift、Origin process offline 或同 session 證據不足都 fail closed。

## Runtime 來源

Runtime 不從網路下載，也不從 `PATH` 猜測；plugin 只直接執行並驗證這三個 release artifact：

```text
plugins/linkstart/skills/link-start/assets/
├── checksums.json
└── bin/
    ├── linux-x64-musl/linkstart
    ├── windows-x64/linkstart.exe
    └── macos-universal/linkstart
```

舊版 README 記載當時內嵌 GitHub Release `v0.1.3`（workflow run `33049940902`）；目前內嵌版本以 `checksums.json` 與 `scripts/validate_linkstart_release.py` 的版本釘選為準。缺少 exact binary、SHA-256、size、release tag provenance 或 Unix executable mode 時會回 `runtime_binary_missing`／`runtime_binary_invalid`，不得下載或使用系統安裝版本頂替。

## 發布驗收

發布驗收把 MOP（機制確實執行）與 MOE（真 App Event 回到同一 Origin Session，真 Feedback 回到同一 App Instance）分開；build、mock、health response 都不能替代 MOE。發布前執行 `python3 scripts/validate_linkstart_release.py`，見 [開發指南](../development.md#驗證)。
