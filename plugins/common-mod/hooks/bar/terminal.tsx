import type { ElementTable, RenderElement } from 'claude-code'

import { cells, DEFAULT } from '../raster'
import type { Hands } from './actions'
import { DECODE_FRAMES, gauges, modelText, numberOf, state, tone } from './model'
import type { Gauge } from './model'

// The terminal's bar, drawn in the band above the prompt as two rails hung on
// one neon spine:
//   ▌ telemetry: folder and model, then ctx, 5h and 7d as gauges of one shape
//   ▌ actions: views in Claude Code ╱ asks to Claude
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
const TONES = { ok: OK, warn: WARN, crit: CRIT }
// Button grounds, one per group, all deep enough to keep the default text legible.
const GROUND = { view: 0x0f3640, ask: 0x3d1238, project: 0x2b3512 }

const PULSE_MS = 1200
const SHIMMER_MS = 1800
const FLOW_MS = 2400
const GLITCH = '#%&@$*+=?!0123456789'
// A sent command's spinner, one step every third frame.
const SPINNER = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

// Nerd Font glyphs, drawn only once the person turns them on with the 圖示
// button, since a terminal without a Nerd Font shows boxes for them: Font
// Awesome and Octicons from the long-stable ranges, and the powerline slants
// for the chips' ends. bar.tsx keeps the choice in the store, for every
// session here; only the terminal reads it. Written as escapes, since the
// private-use characters are invisible in most editors.
const ICONS: Record<string, string> = {
  side: '\uf086',
  recall: '\uf1da',
  diff: '\uf440',
  artifacts: '\uf1b2',
  folder: '\uf07c',
  explain: '\uf059',
  draw: '\uf1fc',
  next: '\uf400',
  back: '\uf112',
  project: '\uf15c',
  ctx: '\uf2db',
  five: '\uf017',
  seven: '\uf073',
}
const SLANT_IN = '\ue0ba'
const SLANT_OUT = '\ue0bc'

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
    .map((ch, i) => (i < settled || ch === '%' ? ch : GLITCH[(state.frame * 7 + i * 13) % GLITCH.length]))
    .join('')
}

// How much of the telemetry rail fits, richest first: bar length, how many of
// the ctx extras (tokens, trend), the reset countdowns, the model.
const FITS = [
  { bar: 14, extras: 2, reset: true, model: true },
  { bar: 10, extras: 2, reset: true, model: true },
  { bar: 10, extras: 1, reset: true, model: true },
  { bar: 6, extras: 1, reset: true, model: true },
  { bar: 6, extras: 0, reset: true, model: false },
  { bar: 0, extras: 0, reset: false, model: false },
]
const RAIL = '▌'

export type TerminalHands = Hands & { bodyColumns: number; nerd: boolean; toggleGlyphs: () => void }

export function drawTerminal(els: ElementTable<'terminal'>, hands: TerminalHands): RenderElement {
  const { now, nerd } = hands
  const { Box, Text, Button } = els
  const Raster = 'Raster' in els ? els.Raster : null
  const room = hands.bodyColumns - 2

  // ── telemetry rail. Three gauges of one shape: label, bar, number, extras.
  const { folder } = state
  const folderText = folder && nerd ? `${ICONS.folder} ${folder}` : folder
  const model = modelText()
  const fitted = (fit: (typeof FITS)[number]) =>
    gauges(now).map(g => ({
      ...g,
      extras: (g.key === 'ctx' ? g.extras.slice(0, fit.extras) : fit.reset ? g.extras : []).filter(x => x.text),
      isShimmering: g.key === 'ctx' && state.isWorking,
    }))
  const railWide = (fit: (typeof FITS)[number]) => {
    const identity = wide(folderText) + (fit.model && model ? 2 + wide(model) : 0)
    const parts = fitted(fit).map(
      g => wide(g.label) + (nerd ? 2 : 0) + 1 + (fit.bar ? fit.bar + 1 : 0) + wide(numberOf(g.g)) + g.extras.reduce((n, x) => n + 1 + wide(x.text), 0),
    )
    return 2 + identity + parts.reduce((n, w) => n + 3 + w, 0)
  }
  const usable = FITS.filter(f => Raster || f.bar === 0)
  const fit = usable.find(f => railWide(f) <= room) ?? usable[usable.length - 1]!
  const color = (g: Gauge, crit: number) => css(g.target === null ? TRACK : TONES[tone(Math.round(g.shown), crit)])

  const telemetry = (
    <Box flexDirection="row" columnGap={3}>
      <Box flexDirection="row" columnGap={2}>
        {folder ? <Text color={css(CYAN)} bold>{folderText}</Text> : null}
        {fit.model && model ? <Text color={css(STEEL)}>{model}</Text> : null}
      </Box>
      {fitted(fit).map(g => (
        <Box key={`gauge-${g.key}`} flexDirection="row" columnGap={1}>
          <Text color={css(STEEL)}>{nerd && ICONS[g.key] ? `${ICONS[g.key]} ${g.label}` : g.label}</Text>
          {Raster && fit.bar > 0 ? (
            <Raster
              key={`bar-${g.key}`}
              columns={fit.bar}
              rows={1}
              cells={barCells(g.g.target === null ? 0 : g.g.shown, fit.bar, now, g.isShimmering)}
            />
          ) : null}
          <Text color={color(g.g, g.crit)}>{decoded(numberOf(g.g), g.g.decode)}</Text>
          {g.extras.map(x => (
            <Text key={`${g.key}-${x.key}`} dimColor>{x.text}</Text>
          ))}
        </Box>
      ))}
    </Box>
  )

  // ── action rail. Up to three groups (the project's own last), each its own
  // ground, split by ╱.
  const groups = (['view', 'ask', 'project'] as const)
    .map(key => ({ key, bg: GROUND[key], buttons: hands.buttons.filter(a => a.group === key) }))
    .filter(g => g.buttons.length > 0)
  const iconOf = (key: string, own?: string) => ICONS[key] ?? (key.startsWith('project-') ? (own ?? ICONS.project) : undefined)

  // Each chip is cut on the slant: a triangle in its own ground at each end,
  // the powerline ones once Nerd Font glyphs are on. The chip's padding is in
  // the label, so it presses too. The last button turns the glyphs on and off.
  const chips = (
    <Box flexDirection="row" flexWrap="wrap" columnGap={1}>
      {groups.flatMap((group, i) => [
        ...(i > 0 ? [<Text key={`slash-${group.key}`} color={css(TRACK)}>╱</Text>] : []),
        ...group.buttons.map(a => (
          <Box key={`chip-${a.key}`} flexDirection="row">
            <Text color={css(group.bg)}>{nerd ? SLANT_IN : '◢'}</Text>
            <Box backgroundColor={css(group.bg)}>
              <Button
                key={`bar-${a.key}`}
                plain
                dimColor={hands.pending !== null && a.command !== undefined && !a.fill}
                label={nerd && iconOf(a.key, a.icon) ? ` ${iconOf(a.key, a.icon)} ${a.label} ` : ` ${a.label} `}
                hover={{ color: css(WHITE), bold: true }}
                onPress={a.onPress}
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
          onPress={hands.toggleGlyphs}
        />
      </Box>
      {hands.pending ? (
        <Box key="pending" marginLeft={2}>
          <Text color={css(CYAN)}>{SPINNER[Math.floor(state.frame / 3) % SPINNER.length]}</Text>
          <Text dimColor> {hands.pending}</Text>
        </Box>
      ) : null}
    </Box>
  )

  // The spine runs down both rails; without a Raster, a plain mark per row.
  const spine = Raster ? (
    <Raster key="spine" columns={1} rows={2} cells={spineCells(2, now, state.isWorking)} />
  ) : (
    <Box flexDirection="column">
      <Text color={css(CYAN)}>{RAIL}</Text>
      <Text color={css(MAGENTA)}>{RAIL}</Text>
    </Box>
  )

  const { nextView } = state
  const nextRows =
    state.isWorking || nextView.kind === 'hidden' ? null : nextView.kind === 'loading' ? (
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
              onPress={() => hands.pick(item)}
            />
          </Box>
        ))}
        <Box marginLeft={2}>
          <Button key="next-0" hotkey="0" plain dimColor label="收起" onPress={hands.hideNext} />
        </Box>
      </Box>
    )

  return (
    <Box flexDirection="column" paddingX={1}>
      <Box flexDirection="row">
        {spine}
        <Box flexDirection="column" marginLeft={1}>
          {telemetry}
          {chips}
        </Box>
      </Box>
      {nextRows}
    </Box>
  )
}
