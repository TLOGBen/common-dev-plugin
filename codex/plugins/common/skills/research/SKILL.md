---
name: research
description: Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.2.0-codex
---

## Output language

Keep these skill instructions in English. Default user-facing explanations and the research report's authored prose to Traditional Chinese. If the user explicitly requests another language, use it instead. Preserve code, identifiers, commands, source titles, quotations, and cited terminology. Carry the selected output language in the background-agent briefing.

Spin up a **background agent** to do the research, so you keep working while it reads.

Its job:

1. Investigate the question against **primary sources** (official docs, source code, specs, first-party APIs), not a secondary write-up of them. Follow every claim back to the source that owns it.
2. Write the findings to a single Markdown file, citing each claim's source.
3. Save it where the repo already keeps such notes; match the existing convention, and if there is none, put it somewhere sensible and say where.

When the baransu suite is installed in the session (detect first, never assume), fetch sources through `/baransu:read`: it captures a URL, GitHub item, Chrome tab, or local path as offline Markdown under `.claude/read/`, so every cited claim can point at a captured file as well as its URL. Research still owns the question and the answer; read only fetches.
