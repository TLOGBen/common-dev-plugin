---
name: research
description: Researches a question against high-trust primary sources and captures the findings as a Markdown file in the repo. Use when the user wants a topic researched, says "research this" or "look into" something, or wants docs or API facts gathered or reading legwork delegated to a background agent.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

## Output language

Keep these skill instructions in English. Default user-facing explanations and the research report's authored prose to Traditional Chinese. If the user explicitly requests another language, use it instead. Preserve code, identifiers, commands, source titles, quotations, and cited terminology.

Spin up a **background agent** to do the research, so you keep working while it reads.

Its job:

1. Investigate the question against **primary sources** — official docs, source code, specs, first-party APIs — not a secondary write-up of them. Follow every claim back to the source that owns it.
2. Write the findings to a single Markdown file, citing each claim's source. Carry the selected output language in the background-agent briefing: Traditional Chinese by default, or the user's explicitly requested language.
3. Save it where the repo already keeps such notes; match the existing convention, and if there is none, put it somewhere sensible and say where.
