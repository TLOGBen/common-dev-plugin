import type { ElementTable, RenderElement } from 'claude-code'

import type { Hands } from './actions'
import { gauges, modelText, numberOf, state, tone } from './model'
import type { Gauge } from './model'

// The desktop's bar (and the editor's): two rows in the app's own look.
//   folder · model   ctx ▬▬▬── 47% 94k/200k   5h ▬──── 23% 3h12m   7d ...
//   [側聊] [回想]  │  [看不懂] [畫給我看] [下一步]
// Text keeps the theme's own color; the buttons are the app's native ones,
// pressable whole. The gauges are SVG, which the app draws as an image and
// which knows nothing of the theme, so their colors read on light and dark
// alike. No Nerd Font glyphs, no per-frame animation.
const TONES = { ok: '#2a9d5c', warn: '#c0841a', crit: '#d64545' }
const TRACK = '#8a8f98'
const BAR_HEIGHT = 8

// The SVG's width in CSS pixels for the band's width in cells; none when narrow.
const barWidth = (columns: number) => (columns >= 120 ? 96 : columns >= 80 ? 64 : 0)

function barSource(g: Gauge, crit: number, width: number) {
  const r = BAR_HEIGHT / 2
  const filled = g.target === null ? 0 : Math.round((Math.min(100, Math.max(0, g.shown)) / 100) * width)
  const fill =
    filled > 0 ? `<rect width="${Math.max(filled, BAR_HEIGHT)}" height="${BAR_HEIGHT}" rx="${r}" fill="${TONES[tone(Math.round(g.shown), crit)]}"/>` : ''
  return (
    `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${BAR_HEIGHT}" viewBox="0 0 ${width} ${BAR_HEIGHT}">` +
    `<rect width="${width}" height="${BAR_HEIGHT}" rx="${r}" fill="${TRACK}" fill-opacity="0.28"/>${fill}</svg>`
  )
}

export function drawDesktop(els: ElementTable<'desktop' | 'vscode'>, hands: Hands & { bodyColumns: number }): RenderElement {
  const { now } = hands
  const { Box, Text, Button, Svg } = els
  const width = barWidth(hands.bodyColumns)
  const model = modelText()

  const telemetry = (
    <Box flexDirection="row" flexWrap="wrap" columnGap={3}>
      <Box flexDirection="row" columnGap={2}>
        {state.folder ? <Text bold>{state.folder}</Text> : null}
        {model ? <Text dimColor>{model}</Text> : null}
      </Box>
      {gauges(now).map(g => (
        <Box key={`gauge-${g.key}`} flexDirection="row" columnGap={1} alignItems="center">
          <Text dimColor>{g.label}</Text>
          {width > 0 ? (
            <Svg
              source={barSource(g.g, g.crit, width)}
              alt={`${g.label} ${numberOf(g.g)}`}
              width={width}
              height={BAR_HEIGHT}
            />
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

  const groups = (['view', 'ask'] as const).map(key => hands.buttons.filter(a => a.group === key)).filter(g => g.length > 0)
  const buttons = (
    <Box flexDirection="row" flexWrap="wrap" columnGap={1} alignItems="center">
      {groups.flatMap((group, i) => [
        ...(i > 0 ? [<Text key={`split-${i}`} dimColor>│</Text>] : []),
        ...group.map(a => <Button key={`bar-${a.key}`} variant="secondary" label={a.label} onPress={a.onPress} />),
      ])}
    </Box>
  )

  const { nextView } = state
  const nextRows =
    state.isWorking || nextView.kind === 'hidden' ? null : nextView.kind === 'loading' ? (
      <Text dimColor>下一步：想一下…</Text>
    ) : (
      <Box flexDirection="column" rowGap={1}>
        <Text dimColor>下一步：</Text>
        {nextView.items.map((item, i) => (
          <Box key={`next-${i}`}>
            <Button key={`next-${i + 1}`} label={item.label} onPress={() => hands.pick(item)} />
          </Box>
        ))}
        <Box>
          <Button key="next-0" dimColor label="收起" onPress={hands.hideNext} />
        </Box>
      </Box>
    )

  return (
    <Box flexDirection="column" rowGap={1}>
      {telemetry}
      {buttons}
      {nextRows}
    </Box>
  )
}
