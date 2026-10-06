import type { ElementTable, RenderElement } from 'claude-code'

import type { Hands } from './actions'
import { gauges, numberOf, state, tone } from './model'
import type { Gauge } from './model'

// The desktop's bar (and the editor's): one row in the app's own look, the
// buttons on the left and the gauges on the right; where the row is too
// narrow the gauges move down together.
//   [側聊] [回想]   [看不懂] [畫給我看] [下一步]        ctx ▬── 26% 263k/1M   5h ▬ 6% 3h42m   7d ▬ 2% 3d17h
// No folder or model: the app shows both already, above and under the prompt.
// Text keeps the theme's own color; the buttons are the app's native ones,
// pressable whole. The gauges are SVG, which the app draws as an image and
// which knows nothing of the theme, so their colors read on light and dark
// alike. No Nerd Font glyphs, no per-frame animation.
const TONES = { ok: '#2a9d5c', warn: '#c0841a', crit: '#d64545' }
const TRACK = '#8a8f98'
const BAR_WIDTH = 56
const BAR_HEIGHT = 7

function barSource(g: Gauge, crit: number) {
  const r = BAR_HEIGHT / 2
  const filled = g.target === null ? 0 : Math.round((Math.min(100, Math.max(0, g.shown)) / 100) * BAR_WIDTH)
  const fill =
    filled > 0 ? `<rect width="${Math.max(filled, BAR_HEIGHT)}" height="${BAR_HEIGHT}" rx="${r}" fill="${TONES[tone(Math.round(g.shown), crit)]}"/>` : ''
  return (
    `<svg xmlns="http://www.w3.org/2000/svg" width="${BAR_WIDTH}" height="${BAR_HEIGHT}" viewBox="0 0 ${BAR_WIDTH} ${BAR_HEIGHT}">` +
    `<rect width="${BAR_WIDTH}" height="${BAR_HEIGHT}" rx="${r}" fill="${TRACK}" fill-opacity="0.28"/>${fill}</svg>`
  )
}

// Three dots that pulse in turn while a sent command waits for its turn. The
// app plays the SMIL itself in its sandboxed frame (`isInteractive`), so the
// bar draws it once and never redraws per frame.
const DOTS =
  '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="8" viewBox="0 0 22 8">' +
  [3, 11, 19]
    .map(
      (x, i) =>
        `<circle cx="${x}" cy="4" r="2.6" fill="${TRACK}">` +
        `<animate attributeName="opacity" values="0.25;1;0.25" dur="1s" begin="${i * 0.2}s" repeatCount="indefinite"/></circle>`,
    )
    .join('') +
  '</svg>'

export function drawDesktop(els: ElementTable<'desktop' | 'vscode'>, hands: Hands & { bodyColumns: number }): RenderElement {
  const { Box, Text, Button, Svg } = els
  // Bars only where there is room for them; the numbers always.
  const hasBars = hands.bodyColumns >= 80

  const groups = (['view', 'ask'] as const).map(key => hands.buttons.filter(a => a.group === key)).filter(g => g.length > 0)
  const buttons = (
    <Box flexDirection="row" flexWrap="wrap" columnGap={3}>
      {groups.map((group, i) => (
        <Box key={`group-${i}`} flexDirection="row" columnGap={1}>
          {group.map(a => (
            <Button
              key={`bar-${a.key}`}
              variant="secondary"
              dimColor={hands.pending !== null && a.command !== undefined}
              label={a.label}
              onPress={a.onPress}
            />
          ))}
        </Box>
      ))}
      {hands.pending ? (
        <Box key="pending" flexDirection="row" columnGap={1} alignItems="center">
          <Svg source={DOTS} alt="送出中" width={22} height={8} isInteractive />
          <Text dimColor>{hands.pending}</Text>
        </Box>
      ) : null}
    </Box>
  )

  const telemetry = (
    <Box flexDirection="row" columnGap={2} alignItems="center">
      {gauges(hands.now).map(g => (
        <Box key={`gauge-${g.key}`} flexDirection="row" columnGap={1} alignItems="center">
          <Text dimColor>{g.label}</Text>
          {hasBars ? (
            <Svg source={barSource(g.g, g.crit)} alt={`${g.label} ${numberOf(g.g)}`} width={BAR_WIDTH} height={BAR_HEIGHT} />
          ) : null}
          {g.g.target === null ? (
            <Text dimColor>{numberOf(g.g)}</Text>
          ) : (
            <Text color={TONES[tone(Math.round(g.g.shown), g.crit)]}>{numberOf(g.g)}</Text>
          )}
          {g.extras
            .filter(x => x.text)
            .map(x => (
              <Text key={`${g.key}-${x.key}`} dimColor>{x.text}</Text>
            ))}
        </Box>
      ))}
    </Box>
  )

  const { nextView } = state
  const nextRows =
    state.isWorking || nextView.kind === 'hidden' ? null : nextView.kind === 'loading' ? (
      <Text dimColor>下一步：想一下…</Text>
    ) : (
      <Box flexDirection="column" rowGap={1}>
        <Text dimColor>下一步</Text>
        {nextView.items.map((item, i) => (
          <Box key={`next-${i}`}>
            <Button key={`next-${i + 1}`} variant="secondary" label={item.label} onPress={() => hands.pick(item)} />
          </Box>
        ))}
        <Box>
          <Button key="next-0" plain dimColor label="收起" onPress={hands.hideNext} />
        </Box>
      </Box>
    )

  return (
    <Box flexDirection="column" rowGap={1}>
      <Box flexDirection="row" flexWrap="wrap" justifyContent="space-between" alignItems="center" columnGap={4} rowGap={1}>
        {buttons}
        {telemetry}
      </Box>
      {nextRows}
    </Box>
  )
}
