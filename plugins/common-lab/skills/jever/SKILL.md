---
name: jever
description: Use Jev to strengthen anywhere that only needs a judgment — yes/no, choose one, score. Look at the current target (work in progress, a prompt, a skill, an MCP server, a hook, a script or agent loop) and point out where a TypeSafe Jev call could replace, speed up, or back up a judgment, or where Jev could become the main loop. Use when the user asks where Jev fits, wants to jev-ify something, asks 哪裡可以用 Jev, jev 化, 能不能用 Jev 做, wants to cut LLM calls that only decide something, or is designing a router, gate, classifier, grader, watchdog, or agent loop.
---

Use Jev to strengthen anywhere that only needs a judgment — yes/no, choose one, score.

Jev (TypeSafe) is not a text generator. Given a piece of text (`state`) and typed questions, it returns a probability for every answer you defined: Noul for yes/no, Choice for one of a known list (up to 255), Score for 2–10 ordered levels. Questions on the same state run in parallel, a call takes roughly 0.1–0.8 s, and it cannot reason step by step or see anything outside the state. Default user-facing output to Traditional Chinese.

## Find the target

Work on what the user is looking at now: the task in progress, a prompt or `CLAUDE.md`, a `SKILL.md`, MCP tool definitions, hook configuration, or a script or agent loop. If it is ambiguous, say which one you are assuming and why rather than asking. Read it before judging it; ideas that are not tied to a file, a step, or a line are not useful here.

## Look for judgments hiding in it

A judgment is any point where something reads text and picks from a small set of outcomes. They hide in places like these:

- An LLM call whose output is really a label, a yes/no, or a number, and text is generated only to be parsed back into that decision.
- Regexes, keyword lists, or path rules standing in for meaning, because asking a model seemed too slow or expensive.
- Checks that run only sometimes — sampling, manual review, "check at the end" — because checking every time cost too much.
- Several independent judgments made one after another when they could be asked together.
- Instructions in prompts and skills such as "decide whether", "if the user wants…", "choose the best", "rate", "classify", "is this done".
- Hook matchers and allow/deny logic; MCP tool selection and parameter classification.
- In agent loops, the per-step micro-decisions: which tool, which element, is this done, is the agent stuck or repeating a wrong assumption, is this output still relevant to keep in context.

## Decide whether each one fits

Ask: could an experienced person glance at this text and pick the answer from fixed options in about two seconds, and is a wrong pick cheap or caught downstream? If yes, it fits. It fits better the more of these hold: the options can be listed in advance; everything needed is in the text; it happens often or in a latency-sensitive path; several independent questions apply to the same text; a confidence would let you route certain cases automatically and send uncertain ones on; and the text may leave the machine.

It does not fit when the step must generate content, needs multi-step reasoning or lookahead, needs files or facts outside the state, or makes an irreversible, costly decision with Jev as the only authority. Say so plainly for those, and keep them in a rejected list with the reason.

## Two shapes of integration

Most fits are **additions**: Jev sits beside the existing flow. A gate before an action, a pre-filter before an expensive step, a second-opinion score next to a reviewer, a router in front of an agent.

Sometimes the whole thing is a loop of choices over options that can be listed — routing tables, triage pipelines, browser or computer control, game or control loops. Then consider making Jev **the load-bearing structure**: code owns the control flow and the list of legal actions, Jev picks each step, an LLM is called only when text must be generated, and code verifies the result before trusting it. browser-use/jev-ultrafast is the reference: every observation becomes an indexed element table, one request picks the operation and the target, and model output never becomes a selector or a command directly. Propose this only when the per-step decisions are the bottleneck and the action space is really enumerable; otherwise the rewrite costs more than it saves.

## What people are doing with it

These patterns come from public projects and posts around the September 2026 launch. All numbers are self-reported; there is no independent benchmark yet.

- **Pre-action gate**: before a shell command or edit, ask separate narrow Noul questions (destructive? leaks files or credentials? beyond what the user asked?) because one broad question misses the other angles. Deterministic allow/deny rules run first and Jev cannot override them; the default is shadow mode.
- **Routing**: pick the model, skill, tool, or team for a request with one Choice — including routing Claude Code work to Haiku or Opus, or suggesting one of many installed skills.
- **Checklist fan-out**: ask a dozen independent checks on the same diff, document, or form edit in one request.
- **Cascade**: Jev handles the clear cases and hands low-confidence ones to an LLM or a person; this keeps accuracy while cutting cost.
- **Agent watchdog**: every step, ask whether the agent is progressing, repeating, or retrying on the same wrong assumption; score tool outputs for relevance to drop them from context instead of summarizing.
- **Decision core**: the jev-ultrafast shape above.
- **Shadow judge**: Score questions per rubric dimension, weighted in code, recorded beside an existing reviewer until they have agreed on real data.

## The agent's own decision points

The target can also be how the agent itself works, not only the project's code. Every turn has judgments of the same shape: stop or keep going, ask the user or check first, claim done or verify more, delegate or do it here. They have fixed options, happen every turn, and a wrong call costs one extra question or one extra step — a good fit.

- **Before stopping a turn**: one Choice over a fixed set — goal met and verified; an open point can be answered from existing files, logs, or earlier results; unfinished items need no user input; a decision only the user can make blocks progress; blocked by something outside reach.
- **Before asking the user**: in one request, a Noul "can this be answered from the repo, logs, or earlier conversation?", a Noul "does this need a preference, authorization, or approval of an irreversible action only the user can give?", and a Score for how clearly the user could answer it. Check first when it is answerable locally and not user-only; when it is user-only, ask anyway, and rewrite it first if clarity is low.

Three rules keep this honest. The agent writing the state is the interested party, so the questions and options stay fixed in the skill and the state holds only facts: the goal as stated, what was done, what is unfinished, why it is stopping, and the exact draft question. Jev never replaces the user's say: preferences, authorization, and irreversible choices go to the user whatever the score, and a Jev answer is not a reason to decide on their behalf. And a check every turn sends the working context out every turn, so propose it only where the user has allowed TypeSafe for that project. A skill relies on the model remembering to check; a Stop hook would enforce it, which is a later step once the check has proven useful.

## Present the candidates

Rank the candidates by value, and for the top few give: where it sits (file and step), what happens today, the Jev questions as a short JSON draft with their primitive, who writes the `state` (code, never the party that wants the answer to pass), the threshold and what happens below it, whether a failure passes or blocks, what a wrong answer costs, and what still needs an LLM, code, or a person. Then list what you rejected and why, and name the smallest experiment that would show whether the top candidate is worth building — for example, twenty of the user's own past cases run in shadow mode.

Keep the cautions that matter in view. Rewording a question can move its probability a lot, so the questions belong to whoever is protected by the answer. Treat every answer as a signal whose calibration must be checked on the user's own data, not as evidence or permission. Everything sent to Jev leaves the machine for TypeSafe in the U.S.; do not propose sending client or confidential content unless the user has said TypeSafe is allowed for it.

This skill only points out where Jev fits. Do not edit files or call Jev unless the user asks; when they want to wire one up, the jev-gate, jev-pick, and jev-score skills show the call, and init-jev sets up the key. Hand the list back and wait.
