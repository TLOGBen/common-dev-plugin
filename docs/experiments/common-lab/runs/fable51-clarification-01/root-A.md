---
name: wait-what
description: Stop. That last message did not land — re-pitch it in plain Traditional Chinese by default (or another explicitly requested language) as a shallow-to-deep ladder that never assumes prior knowledge, then hand the audience the one part that matters most to their role, with a visuals-first HTML companion under .claude/wait-what/. Flags --as <audience> (-a) and --mode visual|text|auto (-v / -t, default auto).
disable-model-invocation: true
---

Wait — I don't understand where you've got to here, and I'm lost on what you're currently talking about. Stop advancing the task and re-pitch it in plain Traditional Chinese by default, or in another language only when the user explicitly requests it.

## Step 1 — Decide who you are talking to

Audience flag — I may pass `--as <audience>` or `-a <audience>`: a role (`manager`, `pm`, `engineer`, `designer`, `qa`, `newcomer`), an age (`-a 10`), or any free-text description (`-a "my boss who has never seen code"`). No flag: infer my role from how I have been talking in this conversation (what I asked for, what I reacted to, what vocabulary I used). If you cannot infer it, treat me as a complete newcomer and say that is the assumption — never stop to ask.

What each audience cares about, and what to give them:

| Audience | They care about | Frame around | Leave out |
|---|---|---|---|
| Newcomer / outsider (default) | What is going on at all | The situation, one idea at a time, "you" and "your" | Anything that needs prior knowledge to parse |
| Manager / director | Impact, timeline, risk, cost | What changed, what it costs, what decision is now needed — quantify when you can | Implementation detail |
| Product manager | User value, scope, priority | What the user will notice, what to build vs. skip | Mechanism |
| Engineer | How it works, trade-offs | Architecture, the interesting design choice, "like X but with Y difference" | Restating basics they already own |
| Designer | User experience, flow | What the user sees and does, interaction patterns | Server internals |
| QA / tester | What could break, how to check | Inputs, expected outputs, edge cases | Why the code is elegant |
| Age given as a number | Whatever a person that age already knows | Younger: toys, school, games; adult: money, home, daily routines | Jargon, period |

## Step 2 — Re-pitch as a ladder, bottom rung first

The failure this skill exists to fix: you silently guess that I already know some piece, skip it, and I am lost from there. So climb these rungs in order, and every rung must stand on its own — never lean on something that is only explained on a later rung. Use the fixed Traditional Chinese headings below verbatim (translate them only when another output language was explicitly requested) — they name what the reader needs at that rung, never who the rung is "for"; a heading like 「給十歲小孩聽」 reads as talking down and must not appear.

1. **Summary (heading: 摘要).** What this is, in words anyone would follow.
2. **Background (heading: 前情提要).** Written as if for a ten-year-old — analogy only, zero prerequisites — toys, school, games, everyday things. What we were doing, how we got here, and whatever the topic silently assumes. A touch of storytelling is welcome when it serves understanding. **Rungs 1 and 2 are mandatory for every audience, engineers included** — a full rung, not a throwaway line.
3. **Where things stand (heading: 當前概況).** Now the real concepts. Keep technical terms in English and explain each one in plain words on the spot. Go only as deep as the audience from Step 1 can use.
4. **What concerns you (heading: 與你相關的部分).** Pick the single thing this audience most needs from the table above and put it here — the decision a manager must make, the trade-off an engineer must weigh, what a tester should poke. Do not give every audience the same summary.
5. **Rationale (heading: 決策理由).** Why you said what you said, and why you made this decision.

Rules across all rungs: purpose before mechanism — nobody cares how until they know why. One idea per sentence on the low rungs. Simplify ruthlessly: 80% accurate and understood beats 100% accurate and lost. Never talk down — the 前情提要 rung should feel delightful, the manager rung should feel empowering. Don't add new task information — background that orients the listener is not new information.

## Step 3 — Visual companion

Mode flag — I may pass `--mode visual|text|auto`, or the shorthands `-v` (visual) and `-t` (text); no flag means `auto`:

- `visual` (`-v`): always produce the visual companion described below; the only excuse not to is that no available tooling can produce an HTML file at all, and then say so explicitly.
- `text` (`-t`): words only — skip the visual companion entirely.
- `auto` (default): produce it when the tools at hand allow it; skip it only when nothing visual would genuinely help or no tooling can produce it. Whenever you skip in auto, say you skipped and remind me I can force it with `-v` next time.

The visual companion: a self-contained HTML page where pictures and diagrams carry the explanation and text plays a supporting role, laid out in the same ladder order as Step 2, built with whatever visualization capability is available. Save it under `.claude/wait-what/` in the project, then open it for me right away — render it in the conversation or launch it in the browser, whatever the environment supports — rather than only telling me the path.

End by asking me which rung is still unclear (name them by heading: 摘要 / 前情提要 / 當前概況 / 與你相關的部分 / 決策理由), then wait.
