import type { EngineInterface, On } from 'claude-code'

import { cells, DEFAULT } from '../raster'

// The status line, drawn in the band above the prompt as two rails hung on
// one neon spine:
//   ▌ telemetry: folder and model, then ctx, 5h and 7d as gauges of one shape
//   ▌ actions: views in Claude Code ╱ apps outside it ╱ asks to Claude
//   below: next-step suggestions, after next-steps, when asked for
// The spine flows while Claude works and a number decodes when it changes;
// the rest holds still.
// A light cyberpunk palette: neon cyan and magenta for the two rails, the
// gauges' green, yellow and red pushed toward neon, steel for everything quiet.
const CYAN = 0x00e5ff
const MAGENTA = 0xff2bd6
const OK = 0x3cf2a0
const WARN = 0xffd23f
const CRIT = 0xff3864
const STEEL = 0x7a83a6
const TRACK = 0x3a3f5a
const WHITE = 0xffffff
// Button grounds, one per group, all deep enough to keep the default text legible.
const VIEW_BG = 0x0f3640
const APP_BG = 0x23283d
const ASK_BG = 0x3d1238

const FRAME_MS = 33
const COUNTDOWN_MS = 30_000
// Share of the distance to the target a value covers each frame.
const EASE = 0.22
const PULSE_MS = 1200
const SHIMMER_MS = 1800
const FLOW_MS = 2400
// Frames a changed number spends decoding before it settles, about 0.4 s.
const DECODE_FRAMES = 12
const GLITCH = '#%&@$*+=?!0123456789'

// `decode` counts down the frames left in a changed number's decode.
type Gauge = { target: number | null; shown: number; resetAt: number | null; decode: number }
const gauge = (): Gauge => ({ target: null, shown: 0, resetAt: null, decode: 0 })
const context = gauge()
const fiveHour = gauge()
const sevenDay = gauge()
const all = [context, fiveHour, sevenDay]

// Nerd Font glyphs, drawn only once the person turns them on with the 圖示
// button, since a terminal without a Nerd Font shows boxes for them: Font
// Awesome and Octicons from the long-stable ranges, and the powerline slants
// for the chips' ends. The choice is kept in $.store, for every session here.
let nerd = false
const ICONS: Record<string, string> = {
  side: '',
  recall: '',
  diff: '',
  artifacts: '',
  folder: '',
  editor: '',
  explain: '',
  draw: '',
  next: '',
}
const SLANT_IN = ''
const SLANT_OUT = ''

let isWorking = false
let started = false
let frame = 0
let cwd = ''
let folder = ''
let model = ''
let effort = ''
let tokens = 0
let windowSize = 0
// Tokens at the end of each main-loop turn, oldest first.
let turns: number[] = []

const css = (c: number) => `#${c.toString(16).padStart(6, '0')}`
const channel = (c: number, shift: number) => (c >> shift) & 255
const mix = (a: number, b: number, t: number) =>
  [16, 8, 0].reduce((out, s) => out | (Math.round(channel(a, s) + (channel(b, s) - channel(a, s)) * t) << s), 0)
const smooth = (from: number, to: number, x: number) => {
  const t = Math.min(1, Math.max(0, (x - from) / (to - from)))
  return t * t * (3 - 2 * t)
}
// The gradient is the thresholds: green to 70, yellow to 90, red past it.
const zone = (percent: number) => mix(mix(OK, WARN, smooth(62, 78, percent)), CRIT, smooth(86, 96, percent))
const tone = (percent: number, crit: number) => (percent >= crit ? CRIT : percent >= 70 ? WARN : OK)
const beat = (now: number) => 0.5 + 0.5 * Math.sin((now / PULSE_MS) * 2 * Math.PI)

// Terminal cells a string takes: CJK and fullwidth characters take two.
const isWide = (cp: number) =>
  (cp >= 0x1100 && cp <= 0x115f) ||
  (cp >= 0x2e80 && cp <= 0xa4cf) ||
  (cp >= 0xac00 && cp <= 0xd7a3) ||
  (cp >= 0xf900 && cp <= 0xfaff) ||
  (cp >= 0xfe30 && cp <= 0xfe4f) ||
  (cp >= 0xff00 && cp <= 0xff60) ||
  (cp >= 0xffe0 && cp <= 0xffe6)
const wide = (s: string) => [...s].reduce((n, ch) => n + (isWide(ch.codePointAt(0) ?? 0) ? 2 : 1), 0)

function until(at: number | null, now: number) {
  if (at === null) return ''
  const minutes = Math.floor((at - now) / 60_000)
  if (minutes <= 0) return ''
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  return days >= 1 ? `${days}d${hours % 24}h` : hours >= 1 ? `${hours}h${minutes % 60}m` : `${minutes}m`
}

// A rule, not a block: ━ for a filled cell, ╸ for a half one, and a dotted ┈
// for the track, so it never reads as a piece of the prompt's own border.
const FULL = 0x2501
const HALF = 0x2578
const DOTS = 0x2508

function barCells(value: number, columns: number, now: number, isShimmering: boolean) {
  const filled = (value / 100) * columns
  const sweep = isShimmering ? ((now % SHIMMER_MS) / SHIMMER_MS) * (filled + 6) - 3 : -99
  const pulse = value >= 90 ? beat(now) : 0
  const grid: [number, number, number][] = []
  for (let i = 0; i < columns; i++) {
    const part = Math.min(1, Math.max(0, filled - i))
    if (part < 0.25) {
      grid.push([DOTS, TRACK, DEFAULT])
      continue
    }
    const head = Math.ceil(filled) - 1
    let color = zone(((i + 0.5) / columns) * 100)
    // The last cells burn brighter, as the lit end of a neon tube.
    color = mix(color, WHITE, Math.max(0, 3 - (head - i)) * 0.08)
    color = mix(color, WHITE, Math.max(0, 1 - Math.abs(i + 0.5 - sweep) / 2.5) * 0.5)
    if (i === head) color = mix(color, WHITE, pulse * 0.4)
    grid.push([part >= 0.75 ? FULL : HALF, color, DEFAULT])
  }
  return cells(grid)
}

// The spine: one cell per row, cyan to magenta. While Claude works the colors
// flow along it; at rest it holds still.
function spineCells(rows: number, now: number, isFlowing: boolean) {
  const phase = isFlowing ? (now % FLOW_MS) / FLOW_MS : 0
  const grid: [number, number, number][] = []
  for (let r = 0; r < rows; r++) {
    const t = rows === 1 ? 0 : r / (rows - 1)
    const wave = isFlowing ? 0.5 + 0.5 * Math.sin((t - phase) * 2 * Math.PI) : t
    grid.push([0x258c, mix(CYAN, MAGENTA, wave), DEFAULT])
  }
  return cells(grid)
}

// A changed number decodes left to right: settled characters stay, the rest
// cycle through glyphs until their turn comes.
function decoded(text: string, left: number) {
  if (left <= 0) return text
  const settled = Math.floor((1 - left / DECODE_FRAMES) * text.length)
  return [...text]
    .map((ch, i) => (i < settled || ch === '%' ? ch : GLITCH[(frame * 7 + i * 13) % GLITCH.length]))
    .join('')
}

// claude-sonnet-5-5 → Sonnet 5.5; a name that is not an id stays as it is.
function modelName(id: string) {
  const m = /^claude-([a-z]+)-(\d+)-(\d+)/.exec(id)
  return m?.[1] ? `${m[1].charAt(0).toUpperCase()}${m[1].slice(1)} ${m[2]}.${m[3]}` : id
}

// The ctx figures follow token-weather (anthropics/claude-code-playground,
// Apache-2.0): tokens used of the window, a chart of the recent turns, and
// what the last one added.
const HISTORY = 12
const BARS = '▁▂▃▄▅▆▇█'

function short(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(n % 1_000_000 === 0 ? 0 : 1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(n % 1_000 === 0 ? 0 : 1)}k`
  return String(n)
}

// Bars scale to the busiest turn shown, so growth shows at any fill.
function chart() {
  const top = Math.max(...turns, 1)
  return turns.map(t => BARS[Math.min(BARS.length - 1, Math.floor((t / top) * (BARS.length - 1)))]).join('')
}

function trend() {
  const [before, last] = turns.slice(-2)
  if (before === undefined || last === undefined || last === before) return ''
  return last > before ? `▲+${short(last - before)}` : `▼${short(before - last)}`
}

function aim(g: Gauge, value: number | undefined) {
  if (value === undefined) return
  if (g.target === null) g.shown = value
  else if (Math.round(value) !== Math.round(g.target)) g.decode = DECODE_FRAMES
  g.target = value
}

type Usage = {
  context: { tokens?: number; window: number; percent?: number }
  rateLimits: { kind: string; percentUsed: number; resetsAt?: string }[]
}

async function absorb($: EngineInterface, usage: Usage) {
  // Compaction can come before the model's whole window; the old statusline
  // measured against it when this is set.
  const compact = Number(await $.env.get('CLAUDE_CODE_AUTO_COMPACT_WINDOW'))
  tokens = usage.context.tokens ?? 0
  windowSize = compact > 0 ? compact : usage.context.window
  aim(context, compact > 0 ? Math.trunc((tokens / compact) * 100) : (usage.context.percent ?? 0))
  for (const limit of usage.rateLimits) {
    const g = limit.kind === 'five_hour' ? fiveHour : limit.kind === 'seven_day' ? sevenDay : null
    if (!g) continue
    aim(g, limit.percentUsed)
    g.resetAt = limit.resetsAt ? Date.parse(limit.resetsAt) : null
  }
}

async function homeOf($: EngineInterface) {
  return ((await $.env.get('USERPROFILE')) ?? (await $.env.get('HOME')) ?? '').replace(/[\\/]+$/, '')
}

async function locate($: EngineInterface) {
  cwd = (await $.session.cwd()).replace(/[\\/]+$/, '')
  const home = await homeOf($)
  folder =
    home && cwd.toLowerCase() === home.toLowerCase() ? '~' : (cwd.split(/[\\/]/).pop() || cwd).replace(/[\x00-\x1f]/g, '')
}

// Hands a folder or a URL to the system's opener. It runs from home with the
// target as an argument, never through a shell and never from the session's
// folder: Windows looks for a program in the working directory before PATH,
// so an untrusted repo could ship one. Explorer exits 1 even when it opened.
async function openOutside($: EngineInterface, target: string) {
  const home = await homeOf($)
  const options = { cwd: home || undefined, timeoutMs: 10_000 }
  if ((await $.env.get('OS')) === 'Windows_NT') {
    await $.process.run(['explorer.exe', target], options)
    return
  }
  const ran = await $.process.run(['xdg-open', target], options).catch(() => null)
  if (ran === null || ran.exitCode !== 0) await $.process.run(['open', target], options)
}

async function openFolder($: EngineInterface) {
  if (cwd) await openOutside($, cwd)
}

// VS Code answers its own URL scheme, so no `code` launcher is looked up.
async function openEditor($: EngineInterface) {
  if (cwd) await openOutside($, `vscode://file/${encodeURI(cwd.replace(/\\/g, '/'))}`)
}

// Next steps follow next-steps (anthropics/claude-plugins-community, MIT), on
// a button press rather than after every turn: the session is forked for up
// to three prompts the person is likely to type next, and a pick goes into
// the prompt box as a draft. Nothing is submitted.
type Suggestion = { label: string; prompt: string }
type Next = { kind: 'hidden' } | { kind: 'loading' } | { kind: 'offer'; items: Suggestion[] }
let nextView: Next = { kind: 'hidden' }
// Bumped by every ask and every new turn, so a late answer lands nowhere.
let asking = 0

const NEXT_MAX = 3
const NEXT_LABEL = 48
const NEXT_PROMPT_CHARS = 600
const NEXT_QUESTION =
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
const ESCAPES = /\x1b\[[0-?]*[ -/]*[@-~]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)|\x1b[@-Z\\-_]/g
const TAGS = /[\u{E0000}-\u{E007F}]/u
const UNSEEN = /[\p{Cc}\p{Cf}\p{Cn}\p{Co}\p{Cs}\p{Variation_Selector}ᅟᅠㅤﾠ]/gu

function clean(text: string, max: number) {
  if (TAGS.test(text)) return ''
  const safe = text.replace(ESCAPES, '').replace(/\s+/g, ' ').replace(UNSEEN, '').replace(/ {2,}/g, ' ').trim()
  const points = [...safe]
  return points.length > max ? `${points.slice(0, max - 1).join('')}…` : safe
}

function suggestionsOf(reply: string, known: ReadonlySet<string> | null): Suggestion[] {
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

function showNext($: EngineInterface, view: Next) {
  nextView = view
  $.ui.invalidate('ui.render')
}

async function askNext($: EngineInterface) {
  const asked = ++asking
  showNext($, { kind: 'loading' })
  let items: Suggestion[] = []
  try {
    const commands = await $.command.list().catch(() => null)
    const known = commands === null ? null : new Set(commands.map(c => c.name))
    const reply = await $.model.fork({ prompt: NEXT_QUESTION })
    items = reply.isAnswered ? suggestionsOf(reply.text, known) : []
  } catch {
    // Said below as no suggestion.
  }
  if (asked !== asking) return
  showNext($, items.length > 0 ? { kind: 'offer', items } : { kind: 'hidden' })
  if (items.length === 0) $.ui.toast('想不到下一步可以做什麼')
}

async function pickNext($: EngineInterface, item: Suggestion) {
  showNext($, { kind: 'hidden' })
  const filled = await $.prompt.fill({ text: item.prompt }).catch(() => null)
  if (!filled?.isFilled) $.ui.toast('沒辦法放進輸入框')
}

// Ticks run all the time but redraw only while something moves: a value
// easing to a new reading, Claude working, or a gauge past 90 pulsing.
function tick($: EngineInterface) {
  frame += 1
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
  if (moving || isWorking || (isHot && frame % 2 === 0)) $.ui.invalidate('ui.render')
}

// Loaded on the first drawing, not at session.start: that event is the entry
// module's, and a mod that fails to read here still draws what it has.
async function start($: EngineInterface) {
  if (started) return
  started = true
  try {
    await absorb($, await $.session.usage())
    model = await $.session.model()
    await locate($)
    nerd = (await $.store.get('barGlyphs')) === true
  } catch {
    // Figures arrive with the next session.measure.
  }
  $.clock.every(FRAME_MS, () => tick($))
  $.clock.every(COUNTDOWN_MS, () => $.ui.invalidate('ui.render'))
}

async function toggleGlyphs($: EngineInterface) {
  nerd = !nerd
  $.ui.invalidate('ui.render')
  await $.store.set('barGlyphs', nerd)
}

async function recordTurn($: EngineInterface) {
  try {
    await absorb($, await $.session.usage())
  } catch {
    return
  }
  if (tokens === 0) return
  turns = [...turns, tokens].slice(-HISTORY)
  $.ui.invalidate('ui.render')
}

// How much of the telemetry rail fits, richest first: bar length, how many of
// the ctx extras (tokens, chart, trend), the reset countdowns, the model.
const FITS = [
  { bar: 14, extras: 3, reset: true, model: true },
  { bar: 10, extras: 3, reset: true, model: true },
  { bar: 10, extras: 1, reset: true, model: true },
  { bar: 6, extras: 1, reset: true, model: true },
  { bar: 6, extras: 0, reset: true, model: false },
  { bar: 0, extras: 0, reset: false, model: false },
]
const RAIL = '▌'

export function registerBar(on: On) {
  on('session.measure', async ($, e, next) => {
    await absorb($, e)
    $.ui.invalidate('ui.render')

    return next(e)
  })

  // The effort rides on each model request; the model's name, as /model shows it.
  on('turn.step', async function* ($, e, next) {
    const was = `${model}|${effort}`
    effort = e.effort === undefined ? '' : String(e.effort)
    model = await $.session.model().catch(() => model)
    if (`${model}|${effort}` !== was) $.ui.invalidate('ui.render')

    yield* next(e)
  })

  // A new turn puts away suggestions made for the last one.
  on('turn.start', async ($, e, next) => {
    asking += 1
    if (nextView.kind !== 'hidden') showNext($, { kind: 'hidden' })

    return next(e)
  })

  // One chart bar per main-loop turn; a subagent's turns are not the session's.
  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    if (!e.agentId) await recordTurn($)

    return result
  })

  // Registered after recall's, so its @@ results take the band first.
  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey) return next(e)
    await start($)
    isWorking = e.props.isWorking

    const now = await $.clock.now()
    const els = $.ui.resolve(e)
    const { Box, Text, Button } = els
    const Raster = e.surface === 'terminal' && 'Raster' in els ? els.Raster : null
    // Most buttons run the commands a person would type, so each opens what
    // that command opens, the way it does.
    const run = (command: string) => void $.command.run({ command }).catch(() => undefined)
    const room = e.props.bodyColumns - 2

    // ── telemetry rail. Three gauges of one shape: label, bar, number, extras.
    const folderText = folder && nerd ? `${ICONS.folder} ${folder}` : folder
    const name = modelName(model)
    const modelText = model ? (effort ? `${name} [${effort}]` : name) : ''
    const numberOf = (g: Gauge) => (g.target === null ? '--' : `${Math.round(g.shown)}%`)
    const ctxExtras = [
      { key: 'tokens', text: windowSize ? `${short(tokens)}/${short(windowSize)}` : '', color: null },
      { key: 'chart', text: turns.length > 0 ? chart() : '', color: CYAN },
      { key: 'trend', text: trend(), color: null },
    ]
    const gauges = (fit: (typeof FITS)[number]) => [
      {
        key: 'ctx',
        label: 'ctx',
        g: context,
        crit: 85,
        extras: ctxExtras.slice(0, fit.extras).filter(x => x.text),
        isShimmering: isWorking,
      },
      ...[
        { key: 'five', label: '5h', g: fiveHour },
        { key: 'seven', label: '7d', g: sevenDay },
      ].map(w => {
        const left = fit.reset && w.g.target !== null ? until(w.g.resetAt, now) : ''
        return { ...w, crit: 90, extras: left ? [{ key: 'reset', text: left, color: null }] : [], isShimmering: false }
      }),
    ]
    const railWide = (fit: (typeof FITS)[number]) => {
      const identity = wide(folderText) + (fit.model && modelText ? 2 + wide(modelText) : 0)
      const parts = gauges(fit).map(
        g => wide(g.label) + 1 + (fit.bar ? fit.bar + 1 : 0) + wide(numberOf(g.g)) + g.extras.reduce((n, x) => n + 1 + wide(x.text), 0),
      )
      return 2 + identity + parts.reduce((n, w) => n + 3 + w, 0)
    }
    const usable = FITS.filter(f => Raster || f.bar === 0)
    const fit = usable.find(f => railWide(f) <= room) ?? usable[usable.length - 1]!

    const telemetry = (
      <Box flexDirection="row" columnGap={3}>
        <Box flexDirection="row" columnGap={2}>
          {folder ? <Text color={css(CYAN)} bold>{folderText}</Text> : null}
          {fit.model && modelText ? <Text color={css(STEEL)}>{modelText}</Text> : null}
        </Box>
        {gauges(fit).map(g => (
          <Box key={`gauge-${g.key}`} flexDirection="row" columnGap={1}>
            <Text color={css(STEEL)}>{g.label}</Text>
            {Raster && fit.bar > 0 ? (
              <Raster
                key={`bar-${g.key}`}
                columns={fit.bar}
                rows={1}
                cells={barCells(g.g.target === null ? 0 : g.g.shown, fit.bar, now, g.isShimmering)}
              />
            ) : null}
            <Text color={css(g.g.target === null ? TRACK : tone(Math.round(g.g.shown), g.crit))}>
              {decoded(numberOf(g.g), g.g.decode)}
            </Text>
            {g.extras.map(x =>
              x.color === null ? (
                <Text key={`${g.key}-${x.key}`} dimColor>{x.text}</Text>
              ) : (
                <Text key={`${g.key}-${x.key}`} color={css(x.color)}>{x.text}</Text>
              ),
            )}
          </Box>
        ))}
      </Box>
    )

    // ── action rail. Three groups, each its own ground, split by ╱.
    const groups = [
      {
        key: 'view',
        bg: VIEW_BG,
        buttons: [
          { key: 'side', label: '側聊', press: () => run('side') },
          { key: 'recall', label: '回想', press: () => run('recall') },
          { key: 'diff', label: 'diff', press: () => run('diff') },
          { key: 'artifacts', label: 'artifacts', press: () => run('artifacts') },
        ],
      },
      {
        key: 'app',
        bg: APP_BG,
        buttons: [
          { key: 'folder', label: '資料夾', press: () => void openFolder($).catch(() => $.ui.toast('沒辦法開資料夾')) },
          { key: 'editor', label: 'VS Code', press: () => void openEditor($).catch(() => $.ui.toast('沒辦法開 VS Code')) },
        ],
      },
      {
        key: 'ask',
        bg: ASK_BG,
        buttons: [
          { key: 'explain', label: '看不懂', press: () => run('common:wait-what') },
          { key: 'draw', label: '畫給我看', press: () => run('common:show-me') },
          { key: 'next', label: '下一步', press: () => void askNext($).catch(() => undefined) },
        ],
      },
    ]

    // Each chip is cut on the slant: a triangle in its own ground at each end,
    // the powerline ones once Nerd Font glyphs are on. The last button turns
    // them on and off.
    const actions = (
      <Box flexDirection="row" flexWrap="wrap" columnGap={1}>
        {groups.flatMap((group, i) => [
          ...(i > 0 ? [<Text key={`slash-${group.key}`} color={css(TRACK)}>╱</Text>] : []),
          ...group.buttons.map(b => (
            <Box key={`chip-${b.key}`} flexDirection="row">
              <Text color={css(group.bg)}>{nerd ? SLANT_IN : '◢'}</Text>
              <Box backgroundColor={css(group.bg)} paddingX={1}>
                <Button
                  key={`bar-${b.key}`}
                  plain
                  label={nerd && ICONS[b.key] ? `${ICONS[b.key]} ${b.label}` : b.label}
                  hover={{ color: css(WHITE), bold: true }}
                  onPress={b.press}
                />
              </Box>
              <Text color={css(group.bg)}>{nerd ? SLANT_OUT : '◤'}</Text>
            </Box>
          )),
        ])}
        <Box key="glyphs" marginLeft={2}>
          <Button
            key="bar-glyphs"
            plain
            dimColor={!nerd}
            label={nerd ? '● 圖示' : '○ 圖示'}
            onPress={() => void toggleGlyphs($).catch(() => undefined)}
          />
        </Box>
      </Box>
    )

    // The spine runs down both rails; without a Raster, a plain mark per row.
    const spine = Raster ? (
      <Raster key="spine" columns={1} rows={2} cells={spineCells(2, now, isWorking)} />
    ) : (
      <Box flexDirection="column">
        <Text color={css(CYAN)}>{RAIL}</Text>
        <Text color={css(MAGENTA)}>{RAIL}</Text>
      </Box>
    )

    const nextRows =
      isWorking || nextView.kind === 'hidden' ? null : nextView.kind === 'loading' ? (
        <Box marginLeft={2}>
          <Text dimColor>下一步：想一下…</Text>
        </Box>
      ) : (
        <Box flexDirection="column" marginLeft={2}>
          <Text dimColor>下一步：</Text>
          {nextView.items.map((item, i) => (
            <Box key={`next-${i}`} marginLeft={2}>
              <Button
                key={`next-${i + 1}`}
                hotkey={String(i + 1)}
                plain
                label={item.label}
                onPress={() => void pickNext($, item).catch(() => undefined)}
              />
            </Box>
          ))}
          <Box marginLeft={2}>
            <Button key="next-0" hotkey="0" plain dimColor label="收起" onPress={() => showNext($, { kind: 'hidden' })} />
          </Box>
        </Box>
      )

    return (
      <Box flexDirection="column" paddingX={1}>
        <Box flexDirection="row">
          {spine}
          <Box flexDirection="column" marginLeft={1}>
            {telemetry}
            {actions}
          </Box>
        </Box>
        {nextRows}
      </Box>
    )
  })
}
