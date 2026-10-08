---
name: jever
description: Use Jev to strengthen anywhere that only needs a judgment — yes/no, choose one, score. Look at the current target (work in progress, a prompt, a skill, an MCP server, a hook, a script or agent loop) and point out where a TypeSafe Jev call could replace, speed up, or back up a judgment, or where Jev could become the main loop — and say plainly where Jev is the wrong tool and what to use instead. Use when the user asks where Jev fits, wants to jev-ify something, asks 哪裡可以用 Jev, jev 化, 能不能用 Jev 做, wants to cut LLM calls that only decide something, or is designing a router, gate, classifier, grader, watchdog, or agent loop.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

Use Jev to strengthen anywhere that only needs a judgment — yes/no, choose one, score.

Jev (TypeSafe) is not a text generator. Given a piece of text (`state`) and typed questions, it returns a probability for every answer you defined: Noul for yes/no, Choice for one of a known list (up to 255), Score for 2–10 ordered levels. Questions on the same state run in parallel, a call takes roughly 0.1–0.8 s, and it cannot reason step by step or see anything outside the state. It takes text only — no images, audio, or binaries — with at most 32k tokens for the state plus the longest question (64k per request). English is its strongest language; other languages, including Chinese, work less well, so candidates for a non-English workload must be tested in that language. Default user-facing output to Traditional Chinese.

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
- **The deciding facts are not in the state.** Jev sees nothing but the text you send: not the repository, not the page, not the history. A `console.log` line is user-facing in a CLI and not in a server; without the file path in the state, Jev can only guess. The same holds when fitting the state limit means cutting the content that decides the answer: a public attempt at Claude Code context compaction truncated each tool output down to its tool name and length and did no better than a stub that always answered 0, and a disk cleanup judged by file name found 0 deletable videos where plain rules found 7. Images, audio, and binaries must become text first. If you cannot put the facts in the state cheaply, look them up first or do not ask.
- **Code can decide it exactly.** Set membership, path comparison, blocking graphs, cycle detection, schema validation, counting — a regex or a set difference is exact, free, and auditable. Jev belongs where meaning is involved, not where a rule already works.
- **Exact numbers or calculations.** A Score is an expected level (for example 1.45), not a measurement. Compute numbers in code; use Jev only to judge the text around them. Dates are read as text too: which comes first, how far apart, whether one falls in a window are all unreliable. Extract the parts (a Choice per part, with a "not stated" option, when extraction itself is a judgment) and compare in code.
- **Jev would be the only authority on something irreversible or costly.** Moving money, deleting data, merging to production, approving on someone's behalf. A public bot trading real money at 5× leverage hit its daily stop. Keep a deterministic rule or a person as the authority and let Jev flag.
- **The party who wants a particular answer writes the question or the state.** Rewording moved one "is this authorized" probability from 6% to 80%. If the questions cannot be fixed in advance and the state cannot be built from facts by code, the answer is not trustworthy.
- **Untrusted content fills the state and the answer gates something.** Web pages, emails, issues, tool output, and command arguments can carry injected instructions or text that argues for its own classification; the vendor's docs say the state is not treated as hostile and such content can move the answer. A guard reading an agent's tool call reads exactly the text an attacker would write. Keep a deterministic rule as the authority, and test with adversarial cases before relying on it.
- **The only gain would be money the user does not pay.** In a subscription harness (Claude Code, Codex) a judgment the agent already makes has zero marginal cost; adding Jev adds a round trip and a failure point. A public attempt to route Codex through a Jev proxy to save quota cost 59–184% more and 1–2 s per step, because the proxy made each request 2.5× heavier and broke prompt caching. There, justify a candidate only by a better outcome — a caught premature stop, a question not asked — never by cost.
- **It spends resources on a count.** Jev over-estimated how many subagents trivial tasks need; counts and budgets need conservative thresholds and a person or rule on top.
- **The goal or the options are vague.** Compaction against a vague goal makes everything look relevant; a Choice whose options overlap spreads its probability thin. Sharpen the goal or the options first, or do not ask.
- **The decision is rare.** Once per project, once per map: an integration (key, state building, thresholds, evaluation) costs more than it saves. Let the agent or a person decide.
- **A simpler alternative already solves it.** Before proposing Jev, compare with the process already in place, a cache, an index or embedding search, a small classifier trained on existing labels, or a small LLM with a constrained output. Choose Jev only when it wins on the whole path — accuracy, latency, cost, and maintenance. A public "AI-flavor" sentence checker flagged 22 of 62 sentences falsely and caught nothing the author's own line-by-line review missed: fast and cheap, net value zero. Against a light LLM (Qwen 3.8 Flash, 300 Chinese judgments) one public test found accuracy (94.7% vs 93.0%) and cost ($0.003 each) about even; Jev won only on tail latency (worst 1.5 s vs 32 s) and on a confidence usable for routing. On a LangChain agent, try the ready-made `langchain-typesafe` middleware (`ModelRouterMiddleware`, `AutoModeMiddleware`, both experimental) before a hand-built integration.
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

- **Pre-action gate**: before a shell command or edit, ask separate narrow Noul questions (destructive? leaks files or credentials? beyond what the user asked?) because one broad question misses the other angles. Deterministic allow/deny rules run first and Jev cannot override them; the default is shadow mode. LangChain's `AutoModeMiddleware` blocks outright with no published threshold or fallback — measure its false blocks on your own traffic before trusting it.
- **Routing**: pick the model, skill, tool, or team for a request with one Choice — including routing Claude Code work to Haiku or Opus, or suggesting one of many installed skills. Say how often it routes: LangChain's `ModelRouterMiddleware` picks once per run from the latest user message; routing every step follows a task that turns hard but costs a call per step and can switch models mid-run.
- **Checklist fan-out**: ask a dozen independent checks on the same diff, document, or form edit in one request.
- **Cascade**: Jev handles the clear cases and hands low-confidence ones to an LLM or a person; this keeps accuracy while cutting cost. In one public test on 300 simple, templated Chinese judgments, all 255 answers at confidence 0.9 or above were right and a 0.8 auto-pass line passed 89% with one error — but the 0.8–0.9 band held only 11 samples.
- **Agent watchdog**: every step, ask whether the agent is progressing, repeating, or retrying on the same wrong assumption; score tool outputs for relevance to drop them from context instead of summarizing.
- **Decision core**: the jev-ultrafast shape above.
- **Shadow judge**: Score questions per rubric dimension, weighted in code, recorded beside an existing reviewer until they have agreed on real data.
- **Context compaction**: judge each tool output against the current goal — keep verbatim, keep a one-line summary, or drop — instead of summarizing the whole context with an LLM.

Before drafting questions for a target, read `references/examples.md` in this skill's directory. It holds the integrations already built and tested in this plugin — the agent's own ask check, request routing, context compaction, grilling order, goal and contract checks, MOE tagging, browser element picking, estimation basis — each with the exact question, a test result, and the question-writing lessons learned (split combined questions, one Noul per option, wording effects). Reuse a shape that matches before inventing a new one, and cite it in the candidate you present.

## The agent's own decision points

The target can also be how the agent itself works, not only the project's code. Every turn has judgments of the same shape: stop or keep going, ask the user or check first, claim done or verify more, delegate or do it here. They have fixed options, happen every turn, and a wrong call costs one extra question or one extra step — a good fit on shape. Under a subscription the agent already makes these calls for free, so the case rests only on catching what the agent gets wrong (stopping early, asking what it could look up); measure that, not cost.

- **Before stopping a turn**: one Choice over a fixed set — goal met and verified; an open point can be answered from existing files, logs, or earlier results; unfinished items need no user input; a decision only the user can make blocks progress; blocked by something outside reach.
- **Before asking the user**: in one request, a Noul "can this be answered from the repo, logs, or earlier conversation?", a Noul "does this need a preference, authorization, or approval of an irreversible action only the user can give?", and a Score for how clearly the user could answer it. Check first when it is answerable locally and not user-only; when it is user-only, ask anyway, and rewrite it first if clarity is low.

Two rules keep this honest. The agent writing the state is the interested party, so the questions and options stay fixed in the skill and the state holds only facts: the goal as stated, what was done, what is unfinished, why it is stopping, and the exact draft question. Jev never replaces the user's say: preferences, authorization, and irreversible choices go to the user whatever the score, and a Jev answer is not a reason to decide on their behalf. A skill relies on the model remembering to check; a Stop hook would enforce it, which is a later step once the check has proven useful.

## Check the economics

Estimate the whole path, not one request: building the state, the network round trip (about 0.6–0.9 s from Taiwan in this plugin's tests), question tokens, retries, fallbacks, and the extra work a wrong answer creates. Lower latency per request is not lower end-to-end latency — find the critical path.

Price runs per request, not per question: Jev charges $0.042 per million input tokens, output is free, and the state is charged once however many questions ride on it (rate limits 250k tokens/s and 1,200 requests/min, adjusted without notice). So fan out: put every question you might need — the speculative ones too — in one request and route in code afterwards. One call per question is the classic mistake; the vendor's own example batched a 13-question briefing 12.2× cheaper and 10× faster with the same answers (vendor claim). The limit is the 64k budget per request, not cost.

Ask who pays the marginal cost. Under a subscription (Claude Code, Codex) the agent's own judgments are already paid for, so saving money is not a benefit (see "When Jev is the wrong tool"). When Jev sits in the middle of an existing call, count what the insertion breaks: request size, prompt-cache hits, an extra hop on every step.

Vendor comparison numbers need discounting: "up to 200× faster and 400× cheaper" compares against frontier LLMs writing a full answer, not answering one letter, and the vendor's accuracy benchmark (about 68%) uses the average answer of two frontier models as ground truth. Compare against the current implementation and the simpler alternatives above. When nothing is measured yet, give assumptions, a plausible range, and the break-even condition: what would have to be true for this to be worth building.

## Design an evaluation that could prove it wrong

For the strongest candidates, define representative inputs including held-out and ambiguous cases, and a task-level success criterion. Compare against two baselines: a stub that always gives the same answer (or the majority class) — if Jev does no better, the state is missing what decides it — and the process already in place, since beating nothing is not beating what the user does today. Log the response's `model` and `usage` on every call; when the model behind the alias changes, re-run the evaluation — thresholds and known weaknesses belong to the model that was tested, and a new one may not share them. Also define the asymmetric cost of a false yes versus a false no; latency and cost as distributions, not averages; tests for missing evidence, adversarial input, and sensitivity to question wording; how thresholds, abstention, and fallback will be validated, with enough samples in the 0.7–0.9 confidence band where routing decisions actually happen; and a go/no-go rule. Treat returned probabilities as signals whose calibration must be checked on the user's own data. If the key, suitable data, and a small budget are available and the user asks, run a bounded experiment; otherwise hand over a runnable plan and say what remains unmeasured. Never invent results.

## Present the candidates

Start with a short assessment of how much Jev could matter for this target. Then give a ranked table that separates direct savings, better outcomes, and new capabilities. For the top few (fewer if fewer survive), give: where it sits (file and step), what happens today, the Jev questions as a short JSON draft with their primitive, which questions share one request and which truly depend on an earlier answer, who writes the `state` (code, never the party that wants the answer to pass) and how code filters it to only the fields the question needs — a whole document as state costs accuracy, since irrelevant detail distracts; the evidence goes in fields separate from the original request, as evidence rather than a summary; for a Choice, options rebuilt from what exists at this step plus a `none` option, since the answer is always one of the options even when all are wrong; the threshold and what happens below it — start from about 0.9 confidence for anything destructive or auto-approved and about 0.5 for read-only actions, then move with data — whether a failure passes or blocks, what a wrong answer costs, and what still needs an LLM, code, retrieval, or a person. Add a short first-principles sketch of how the relevant part would be designed today with cheap judgments available. Then list what you rejected and why — citing the "wrong tool" reasons above — and name the smallest experiment that would settle the most important uncertainty, for example twenty of the user's own past cases run in shadow mode. Throughout, mark what is a vendor claim, what someone measured, and what is your hypothesis.

Keep the questions and thresholds together in one file, and expect to revise the wording with the user: agents write these questions poorly on the first try.

Keep the cautions that matter in view. Rewording a question can move its probability a lot, so the questions belong to whoever is protected by the answer. A Noul of 0.5 means "as likely yes as no", not "medium". Treat every answer as a signal whose calibration must be checked on the user's own data, not as evidence or permission.

This skill only points out where Jev fits. Do not edit files or call Jev unless the user asks; when they want to wire one up, the jev-gate, jev-pick, and jev-score skills show the call, and init-jev sets up the key. Hand the list back and wait.
