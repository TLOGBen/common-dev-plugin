import type { RenderSurface } from 'claude-code'

// What the bar shows, whatever draws it: the gauges, the session's figures,
// the next-step offer. One model for every surface, since a session may draw
// on the terminal and the desktop at once and both should read the same.
// Plain data and pure functions only: `$` stays in bar.tsx.

// Share of the distance to the target a value covers each frame.
const EASE = 0.22
// Frames a changed number spends decoding before it settles, about 0.4 s.
export const DECODE_FRAMES = 12

// `decode` counts down the frames left in a changed number's decode.
export type Gauge = { target: number | null; shown: number; resetAt: number | null; decode: number }
const gauge = (): Gauge => ({ target: null, shown: 0, resetAt: null, decode: 0 })
export const context = gauge()
export const fiveHour = gauge()
export const sevenDay = gauge()
const all = [context, fiveHour, sevenDay]

export type Suggestion = { label: string; prompt: string }
export type Next = { kind: 'hidden' } | { kind: 'loading' } | { kind: 'offer'; items: Suggestion[] }

export const state = {
  isWorking: false,
  frame: 0,
  folder: '',
  model: '',
  effort: '',
  tokens: 0,
  windowSize: 0,
  // Tokens at the end of each main-loop turn, oldest first.
  turns: [] as number[],
  nextView: { kind: 'hidden' } as Next,
  // The session's command names; null until read, or when the list fails.
  known: null as ReadonlySet<string> | null,
  // Surfaces that have drawn the bar: only the terminal's animates per frame.
  seen: new Set<RenderSurface>(),
  // A command a button sent and its turn has not reached the model yet: said
  // on the bar at once, since the app can take seconds to show the turn.
  // `isQueued` while a turn was running at the press; `isDispatched` once the
  // engine took the command, so the next model request is its own.
  pending: null as { label: string; at: number; isQueued: boolean; isDispatched: boolean } | null,
}

// Pending past this is put away whatever happened.
export const PENDING_MS = 30_000

export const pendingText = () => {
  const { pending } = state
  if (!pending) return null
  return pending.isQueued && !pending.isDispatched ? `排隊中：${pending.label}（等這一輪結束）` : `已送出：${pending.label}…`
}

export const tone = (percent: number, crit: number) => (percent >= crit ? 'crit' : percent >= 70 ? 'warn' : 'ok')
export const numberOf = (g: Gauge) => (g.target === null ? '--' : `${Math.round(g.shown)}%`)

export function until(at: number | null, now: number) {
  if (at === null) return ''
  const minutes = Math.floor((at - now) / 60_000)
  if (minutes <= 0) return ''
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  return days >= 1 ? `${days}d${hours % 24}h` : hours >= 1 ? `${hours}h${minutes % 60}m` : `${minutes}m`
}

// claude-sonnet-5-5 → Sonnet 5.5; a name that is not an id stays as it is.
export function modelName(id: string) {
  const m = /^claude-([a-z]+)-(\d+)-(\d+)/.exec(id)
  return m?.[1] ? `${m[1].charAt(0).toUpperCase()}${m[1].slice(1)} ${m[2]}.${m[3]}` : id
}

export const modelText = () => {
  const name = modelName(state.model)
  return state.model ? (state.effort ? `${name} [${state.effort}]` : name) : ''
}

// The ctx figures follow token-weather (anthropics/claude-code-playground,
// Apache-2.0): tokens used of the window and what the last turn added.
const HISTORY = 12

export function short(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(n % 1_000_000 === 0 ? 0 : 1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(n % 1_000 === 0 ? 0 : 1)}k`
  return String(n)
}

function trend() {
  const [before, last] = state.turns.slice(-2)
  if (before === undefined || last === undefined || last === before) return ''
  return last > before ? `▲+${short(last - before)}` : `▼${short(before - last)}`
}

export function recordTokens() {
  if (state.tokens === 0) return false
  state.turns = [...state.turns, state.tokens].slice(-HISTORY)
  return true
}

// The three gauges of one shape: label, value, the threshold it turns red at,
// and its extras (ctx: tokens and trend; the windows: time to reset).
export function gauges(now: number) {
  return [
    {
      key: 'ctx',
      label: 'ctx',
      g: context,
      crit: 85,
      extras: [
        { key: 'tokens', text: state.windowSize ? `${short(state.tokens)}/${short(state.windowSize)}` : '' },
        { key: 'trend', text: trend() },
      ],
    },
    ...[
      { key: 'five', label: '5h', g: fiveHour },
      { key: 'seven', label: '7d', g: sevenDay },
    ].map(w => {
      const left = w.g.target !== null ? until(w.g.resetAt, now) : ''
      return { ...w, crit: 90, extras: [{ key: 'reset', text: left }] }
    }),
  ]
}

function aim(g: Gauge, value: number | undefined) {
  if (value === undefined) return
  if (g.target === null) g.shown = value
  else if (Math.round(value) !== Math.round(g.target)) g.decode = DECODE_FRAMES
  g.target = value
}

export type Usage = {
  context: { tokens?: number; window: number; percent?: number }
  rateLimits: { kind: string; percentUsed: number; resetsAt?: string }[]
}

// Compaction can come before the model's whole window; the old statusline
// measured against it when it is set (`compact`, 0 when not).
export function absorbUsage(usage: Usage, compact: number) {
  state.tokens = usage.context.tokens ?? 0
  state.windowSize = compact > 0 ? compact : usage.context.window
  aim(context, compact > 0 ? Math.trunc((state.tokens / compact) * 100) : (usage.context.percent ?? 0))
  for (const limit of usage.rateLimits) {
    const g = limit.kind === 'five_hour' ? fiveHour : limit.kind === 'seven_day' ? sevenDay : null
    if (!g) continue
    aim(g, limit.percentUsed)
    g.resetAt = limit.resetsAt ? Date.parse(limit.resetsAt) : null
  }
}

export function folderOf(cwd: string, home: string) {
  const dir = cwd.replace(/[\\/]+$/, '')
  return home && dir.toLowerCase() === home.toLowerCase() ? '~' : (dir.split(/[\\/]/).pop() || dir).replace(/[\x00-\x1f]/g, '')
}

// One frame: values ease toward their readings. True while the bar should
// redraw: a value moving on every surface; on the terminal also Claude
// working and a gauge past 90 pulsing, which only its drawing animates.
export function advance() {
  state.frame += 1
  let moving = false
  for (const g of all) {
    if (g.decode > 0) {
      g.decode -= 1
      moving = true
    }
    if (g.target === null) continue
    const gap = g.target - g.shown
    if (Math.abs(gap) > 0.05) {
      g.shown += gap * EASE
      moving = true
    } else {
      g.shown = g.target
    }
  }
  const isHot = all.some(g => (g.target ?? 0) >= 90)
  const isSpinning = state.pending !== null && state.frame % 3 === 0
  return moving || (state.seen.has('terminal') && (state.isWorking || isSpinning || (isHot && state.frame % 2 === 0)))
}

// Next steps follow next-steps (anthropics/claude-plugins-community, MIT), on
// a button press rather than after every turn: the session is forked for up
// to three prompts the person is likely to type next, and a pick goes into
// the prompt box as a draft. Nothing is submitted.
const NEXT_MAX = 3
const NEXT_LABEL = 48
const NEXT_PROMPT_CHARS = 600
export const NEXT_QUESTION =
  'Do not continue the task. Instead, predict what the user is most likely to ask you next, ' +
  `as up to ${NEXT_MAX} concrete prompts written in the user's voice and language (imperative, specific to ` +
  'this conversation: name the file, test, PR, or follow-up they would actually type). Prefer the obvious ' +
  'next action (run the tests, commit, fix the thing you flagged, do the same for X) over generic ones. A ' +
  "prompt may start with one of the session's slash commands, spelled exactly; never invent one. If the " +
  'conversation is clearly finished or nothing useful comes to mind, return an empty list.\n\n' +
  'Answer with ONLY a JSON array, no prose, no code fence: ' +
  `[{"label": "<≤${NEXT_LABEL} chars shown on a button>", "prompt": "<full prompt text>"}]`

// Suggestions are model output, and the model reads untrusted text. Before
// any of it reaches the screen or the prompt box, keep only what a person can
// see; text carrying Unicode tag characters is refused outright.
export const ESCAPES = /\x1b\[[0-?]*[ -/]*[@-~]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)|\x1b[@-Z\\-_]/g
export const TAGS = /[\u{E0000}-\u{E007F}]/u
const UNSEEN = /[\p{Cc}\p{Cf}\p{Cn}\p{Co}\p{Cs}\p{Variation_Selector}ᅟᅠㅤﾠ]/gu

function clean(text: string, max: number) {
  if (TAGS.test(text)) return ''
  const safe = text.replace(ESCAPES, '').replace(/\s+/g, ' ').replace(UNSEEN, '').replace(/ {2,}/g, ' ').trim()
  const points = [...safe]
  return points.length > max ? `${points.slice(0, max - 1).join('')}…` : safe
}

export function suggestionsOf(reply: string, known: ReadonlySet<string> | null): Suggestion[] {
  const from = reply.indexOf('[')
  const to = reply.lastIndexOf(']')
  if (from === -1 || to <= from) return []
  let parsed: unknown
  try {
    parsed = JSON.parse(reply.slice(from, to + 1))
  } catch {
    return []
  }
  if (!Array.isArray(parsed)) return []
  const items: Suggestion[] = []
  for (const entry of parsed as { label?: unknown; prompt?: unknown }[]) {
    if (typeof entry?.prompt !== 'string') continue
    const prompt = clean(entry.prompt, NEXT_PROMPT_CHARS)
    // A prompt that starts with a slash runs a command: one the session does
    // not have is dropped rather than offered.
    const command = prompt.startsWith('/') ? (prompt.slice(1).split(' ', 1)[0] ?? '') : null
    if (prompt === '' || (command !== null && known !== null && !known.has(command))) continue
    const label = typeof entry.label === 'string' ? clean(entry.label, NEXT_LABEL) : ''
    items.push({ label: label || clean(prompt, NEXT_LABEL), prompt })
    if (items.length === NEXT_MAX) break
  }
  return items
}

export const BRING_BACK =
  '不要接續工作。這個對話是從主對話分出來的分支；把分出來之後的進展寫成一份給主對話看的精簡回報：' +
  '問了什麼、查到或做了什麼、結論是什麼、主線要接手的事。用繁體中文，只寫回報本身。'
