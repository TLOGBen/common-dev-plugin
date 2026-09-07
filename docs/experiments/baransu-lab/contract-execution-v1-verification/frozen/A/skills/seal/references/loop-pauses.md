# loop-pauses — $seal PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Target-pin off-ramp (no materializable diff / contract / named artifact) | Authorization | Hard stop: report `needs-input`（「無可審工件」）upward; never fabricate a target, never seal from conversation memory |
| In-band fix loop (agent-reported findings: unpinned surface, constant drift, minimal criteria-violation fix) | Input | Standing-authorized on the dispatcher side: the agent only reports — the main session applies the fix, pairs it with a pinning test, re-runs to green, re-dispatches for re-verification (cap 2), and annotates 「此處採預設：帶內修正已直接套用」 in the report |
| Out-of-band findings (architectural rework, redesign, files outside the diff) | Authorization | Never apply; list in the report as pending and route to $review or $hunt |
| 複驗超限 (re-verification cap exhausted: 2 re-dispatches used, findings still open) | Authorization | Stop the loop, write no sealed marker, append seal-log `unresolved`, and report the uncleared findings upward verbatim（「複驗上限已達（2 次）…未蓋章」） |
| 指紋不符/探針殘留 (post-dispatch fingerprint mismatch, or agent self-reports a failed probe restore) | Authorization | Dispatcher restores from the scratch pre-image copies and records the incident as a finding; restoration impossible → hard stop: report the dirty state verbatim, never commit or continue over probe residue |
