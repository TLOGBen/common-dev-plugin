---
name: jever
description: Use Jev to strengthen anywhere that only needs a judgment — yes/no, choose one, score. Look at the current target (work in progress, a prompt, a skill, an MCP server, a hook, a script or agent loop) and point out where a TypeSafe Jev call could replace, speed up, or back up a judgment, or where Jev could become the main loop — and say plainly where Jev is the wrong tool and what to use instead. Use when the user asks where Jev fits, wants to jev-ify something, asks 哪裡可以用 Jev, jev 化, 能不能用 Jev 做, wants to cut LLM calls that only decide something, or is designing a router, gate, classifier, grader, watchdog, or agent loop.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

Use Jev to strengthen anywhere that only needs a judgment — yes/no, choose one, score.

Jev (TypeSafe) is not a text generator. Given a piece of text (`state`) and typed questions, it returns a probability for every answer you defined: Noul for yes/no, Choice for one of a known list (up to 255), Score for 2–10 ordered levels. Questions on the same state run in parallel, a call takes roughly 0.1–0.8 s, and it cannot reason step by step or see anything outside the state. Default user-facing output to Traditional Chinese.

## Find the target

Work on what the user is looking at now: the task in progress, a prompt or `CLAUDE.md`, a `SKILL.md`, MCP tool definitions, hook configuration, or a script or agent loop. If it is ambiguous, say which one you are assuming and why rather than asking. Read it before judging it; ideas that are not tied to a file, a step, or a line are not useful here. First understand what the target is for — the outcomes its users care about and where time or money goes today — so the candidates serve those outcomes rather than the tool.

## Look for judgments hiding in it

A judgment is any point where something reads text and picks from a small set of outcomes. They hide in places like these:

- An LLM call whose output is really a label, a yes/no, or a number, and text is generated only to be parsed back into that decision.
- Regexes, keyword lists, or path rules standing in for meaning, because asking a model seemed too slow or expensive.
- Checks that run only sometimes — sampling, manual review, "check at the end", delayed batch jobs — because checking every time cost too much.
- Coverage cut to fit a budget: information discarded, only the top N items looked at, coarse categories where finer ones would help.
- The same context processed again and again to answer different small questions.
- Several independent judgments made one after another when they could be asked together.
- Instructions in prompts and skills such as "decide whether", "if the user wants…", "choose the best", "rate", "classify", "is this done".
- Hook matchers and allow/deny logic; MCP tool selection and parameter classification.
- In agent loops, the per-step micro-decisions: which tool, which element, is this done, is the agent stuck or repeating a wrong assumption, is this output still relevant to keep in context.

## Decide whether each one fits

Ask: could an experienced person glance at this text and pick the answer from fixed options in about two seconds, and is a wrong pick cheap or caught downstream? If yes, it fits. It fits better the more of these hold: the options can be listed in advance; everything needed is in the text; it happens often or in a latency-sensitive path; several independent questions apply to the same text; a confidence would let you route certain cases automatically and send uncertain ones on.

## When Jev is the wrong tool

Say these plainly, keep them in the rejected list with the reason, and name what to use instead. Each comes from something observed while building and testing these skills or from the public cases.

- **The step produces content** — code, copy, a summary, an explanation, a plan. Jev returns probabilities over options you wrote; it cannot write. Use an LLM, and let Jev judge the result if a judgment follows.
- **The answer needs multi-step reasoning or lookahead.** Jev judges in one pass. In a public chess match it moved in about 2.6 s while Fable 5.1 took 6–15 s per move and was far ahead on material — Fable lost on time, not on judgment. Break the problem into questions that each take one glance, or use a reasoning model.
- **The deciding facts are not in the state.** Jev sees nothing but the text you send: not the repository, not the page, not the history. A `console.log` line is user-facing in a CLI and not in a server; without the file path in the state, Jev can only guess. If you cannot put the facts in the state cheaply, look them up first or do not ask.
- **Code can decide it exactly.** Set membership, path comparison, blocking graphs, cycle detection, schema validation, counting — a regex or a set difference is exact, free, and auditable. Jev belongs where meaning is involved, not where a rule already works.
- **Exact numbers or calculations.** A Score is an expected level (for example 1.45), not a measurement. Compute numbers in code; use Jev only to judge the text around them.
- **Jev would be the only authority on something irreversible or costly.** Moving money, deleting data, merging to production, approving on someone's behalf. A public bot trading real money at 5× leverage hit its daily stop. Keep a deterministic rule or a person as the authority and let Jev flag.
- **The party who wants a particular answer writes the question or the state.** Rewording moved one "is this authorized" probability from 6% to 80%. If the questions cannot be fixed in advance and the state cannot be built from facts by code, the answer is not trustworthy.
- **It spends resources on a count.** Jev over-estimated how many subagents trivial tasks need; counts and budgets need conservative thresholds and a person or rule on top.
- **The goal or the options are vague.** Compaction against a vague goal makes everything look relevant; a Choice whose options overlap spreads its probability thin. Sharpen the goal or the options first, or do not ask.
- **The decision is rare.** Once per project, once per map: an integration (key, state building, thresholds, evaluation) costs more than it saves. Let the agent or a person decide.
- **A simpler alternative already solves it.** Before proposing Jev, compare with a cache, an index or embedding search, a small classifier trained on existing labels, or a small LLM with a constrained output. Choose Jev only when it wins on the whole path — accuracy, latency, cost, and maintenance.
- **Nothing downstream can catch a wrong answer and there is no fallback.** Jev's probabilities are not independently calibrated yet. Without a check after it, or a path for low-confidence cases, a confident wrong answer goes straight through.

## Two shapes of integration

Most fits are **additions**: Jev sits beside the existing flow. A gate before an action, a pre-filter before an expensive step, a second-opinion score next to a reviewer, a router in front of an agent.

Sometimes the whole thing is a loop of choices over options that can be listed — routing tables, triage pipelines, browser or computer control, game or control loops. Then consider making Jev **the load-bearing structure**: code owns the control flow and the list of legal actions, Jev picks each step, an LLM is called only when text must be generated, and code verifies the result before trusting it. browser-use/jev-ultrafast is the reference: every observation becomes an indexed element table, one request picks the operation and the target, and model output never becomes a selector or a command directly. Propose this only when the per-step decisions are the bottleneck and the action space is really enumerable; otherwise the rewrite costs more than it saves.

## Reconsider from first principles

This section and the two after it follow the investigation prompt in ryana/jevify (https://github.com/ryana/jevify). Ask: if many small semantic judgments were affordable inside this target's time budget, what would it do differently? Name the assumptions that exist only because judging meaning used to be slow or expensive, and look for three kinds of opportunity, giving the third real attention:

- **Direct savings** — the same work at lower cost or latency and acceptable quality.
- **Better outcomes** — more coverage, relevance, reliability, or responsiveness within the same budget: every event instead of a sample, every candidate instead of the top ten.
- **New capabilities** — behavior not attempted today: reacting while the user is still typing, continuously reassessing changing state, many dimensions judged at once, fast judgments feeding a slower reasoning step.

Keep these ideas specific to the target, not a generic feature list. Do not hide a reasoning task inside a vaguely worded classification question: show that the questions keep the information the decision needs.

## What people are doing with it

These patterns come from public projects and posts around the September 2026 launch. All numbers are self-reported; there is no independent benchmark yet.

- **Pre-action gate**: before a shell command or edit, ask separate narrow Noul questions (destructive? leaks files or credentials? beyond what the user asked?) because one broad question misses the other angles. Deterministic allow/deny rules run first and Jev cannot override them; the default is shadow mode.
- **Routing**: pick the model, skill, tool, or team for a request with one Choice — including routing Claude Code work to Haiku or Opus, or suggesting one of many installed skills.
- **Checklist fan-out**: ask a dozen independent checks on the same diff, document, or form edit in one request.
- **Cascade**: Jev handles the clear cases and hands low-confidence ones to an LLM or a person; this keeps accuracy while cutting cost.
- **Agent watchdog**: every step, ask whether the agent is progressing, repeating, or retrying on the same wrong assumption; score tool outputs for relevance to drop them from context instead of summarizing.
- **Decision core**: the jev-ultrafast shape above.
- **Shadow judge**: Score questions per rubric dimension, weighted in code, recorded beside an existing reviewer until they have agreed on real data.
- **Context compaction**: judge each tool output against the current goal — keep verbatim, keep a one-line summary, or drop — instead of summarizing the whole context with an LLM.

Before drafting questions for a target, read `references/examples.md` in this skill's directory. It holds the integrations already built and tested in this plugin — the agent's own stop and ask checks, request routing, context compaction, grilling order, goal and contract checks, mutation-probe triage, MOE tagging, delegation sizing, UI plan fit and element choice, estimation basis — each with the exact question, a test result, and the question-writing lessons learned (split combined questions, one Noul per option, wording effects). Reuse a shape that matches before inventing a new one, and cite it in the candidate you present.

## The agent's own decision points

The target can also be how the agent itself works, not only the project's code. Every turn has judgments of the same shape: stop or keep going, ask the user or check first, claim done or verify more, delegate or do it here. They have fixed options, happen every turn, and a wrong call costs one extra question or one extra step — a good fit.

- **Before stopping a turn**: one Choice over a fixed set — goal met and verified; an open point can be answered from existing files, logs, or earlier results; unfinished items need no user input; a decision only the user can make blocks progress; blocked by something outside reach.
- **Before asking the user**: in one request, a Noul "can this be answered from the repo, logs, or earlier conversation?", a Noul "does this need a preference, authorization, or approval of an irreversible action only the user can give?", and a Score for how clearly the user could answer it. Check first when it is answerable locally and not user-only; when it is user-only, ask anyway, and rewrite it first if clarity is low.

Two rules keep this honest. The agent writing the state is the interested party, so the questions and options stay fixed in the skill and the state holds only facts: the goal as stated, what was done, what is unfinished, why it is stopping, and the exact draft question. Jev never replaces the user's say: preferences, authorization, and irreversible choices go to the user whatever the score, and a Jev answer is not a reason to decide on their behalf. A skill relies on the model remembering to check; a Stop hook would enforce it, which is a later step once the check has proven useful.

## Check the economics

Estimate the whole path, not one request: building the state, the network round trip (about 0.6–0.9 s from Taiwan in this plugin's tests), question tokens, retries, fallbacks, and the extra work a wrong answer creates. Lower latency per request is not lower end-to-end latency — find the critical path. More questions in one request are cheap but not free, and batching does not scale forever. Compare against the current implementation and the simpler alternatives above. When nothing is measured yet, give assumptions, a plausible range, and the break-even condition: what would have to be true for this to be worth building.

## Design an evaluation that could prove it wrong

For the strongest candidates, define representative inputs including held-out and ambiguous cases, the baseline, and a task-level success criterion; the asymmetric cost of a false yes versus a false no; latency and cost as distributions, not averages; tests for missing evidence, adversarial input, and sensitivity to question wording; how thresholds, abstention, and fallback will be validated; and a go/no-go rule. Treat returned probabilities as signals whose calibration must be checked on the user's own data. If the key, suitable data, and a small budget are available and the user asks, run a bounded experiment; otherwise hand over a runnable plan and say what remains unmeasured. Never invent results.

## Present the candidates

Start with a short assessment of how much Jev could matter for this target. Then give a ranked table that separates direct savings, better outcomes, and new capabilities. For the top few (fewer if fewer survive), give: where it sits (file and step), what happens today, the Jev questions as a short JSON draft with their primitive, which questions share one request and which truly depend on an earlier answer, who writes the `state` (code, never the party that wants the answer to pass), the threshold and what happens below it, whether a failure passes or blocks, what a wrong answer costs, and what still needs an LLM, code, retrieval, or a person. Add a short first-principles sketch of how the relevant part would be designed today with cheap judgments available. Then list what you rejected and why — citing the "wrong tool" reasons above — and name the smallest experiment that would settle the most important uncertainty, for example twenty of the user's own past cases run in shadow mode. Throughout, mark what is a vendor claim, what someone measured, and what is your hypothesis.

Keep the cautions that matter in view. Rewording a question can move its probability a lot, so the questions belong to whoever is protected by the answer. Treat every answer as a signal whose calibration must be checked on the user's own data, not as evidence or permission.

This skill only points out where Jev fits. Do not edit files or call Jev unless the user asks; when they want to wire one up, the jev-gate, jev-pick, and jev-score skills show the call, and init-jev sets up the key. Hand the list back and wait.
