import { expect, test } from 'claude-code/testing'
import type { On } from 'claude-code'

type Found = { key?: string; type: string; text: string; props: Record<string, unknown> }
type Drawn = {
  find: (q: { type?: string; key?: string; text?: RegExp }) => Promise<Found | undefined>
  findAll: (q: { type?: string; key?: string; text?: RegExp }) => Promise<Found[]>
  press: (t: { key: string }) => Promise<unknown>
}

const SURFACES = ['terminal', 'desktop'] as const
type Surface = (typeof SURFACES)[number] | 'vscode'

const band = (bodyColumns: number, { requestId = 'band', hasSurvey = false, surface = 'terminal' as Surface } = {}) =>
  ({
    plugin: 'common-mod',
    component: 'AbovePrompt',
    requestId,
    surface,
    props: { hasSurvey, isWorking: false, maxRows: 10, bodyColumns, scroll: { bodyRows: 10 } },
  }) as never

const mount = async ($: { ui: { mount: (t: never) => Promise<unknown> } }, target: never) =>
  (await $.ui.mount(target)) as unknown as Drawn

const COMMANDS = ['diff', 'artifacts', 'common:wait-what', 'common:show-me']

type Options = {
  suggestions?: string
  env?: Record<string, string>
  store?: Record<string, unknown>
  commands?: string[]
  failing?: string
}

// What the session reports; the figures the old statusline showed.
function engine(on: On, { suggestions = '[]', env = {}, store = {}, commands = COMMANDS, failing }: Options = {}) {
  const ran: string[] = []
  const filled: string[] = []
  const stored: [string, unknown][] = []
  const read: string[] = []
  const runs: { argv: readonly string[]; cwd?: string }[] = []
  const sent: { to: unknown; text: string }[] = []
  const toasts: string[] = []
  on('store.get', (_$, e) => {
    read.push(e.key)
    return { value: store[e.key] } as never
  })
  on('store.set', (_$, e) => {
    stored.push([e.key, e.value])
    return { value: undefined } as never
  })
  on('session.usage', () =>
    ({
      value: {
        context: { tokens: 94_000, window: 200_000, percent: 47 },
        rateLimits: [
          { kind: 'five_hour', percentUsed: 23, resetsAt: new Date(Date.now() + 3 * 3_600_000 + 12 * 60_000).toISOString() },
          { kind: 'seven_day', percentUsed: 12 },
        ],
      },
    }) as never,
  )
  on('session.model', () => ({ value: 'claude-sonnet-5-5' }) as never)
  on('session.cwd', () => ({ value: 'C:\\Users\\jimts\\workspace\\Gits\\common-dev-plugin' }) as never)
  on('env.get', (_$, e) => ({ value: env[e.name] }) as never)
  on('clock.now', () => ({ value: Date.now() }) as never)
  on('clock.every', () => ({ value: null }) as never)
  on('ui.toast', (_$, e) => {
    toasts.push(e.text)
    return { value: undefined } as never
  })
  on('command.list', () => ({ value: commands.map(name => ({ name })) }) as never)
  on('model.fork', () => ({ value: { isAnswered: true, text: suggestions, usage: {} } }) as never)
  on('prompt.fill', (_$, e) => {
    filled.push(e.text)
    return { value: { isFilled: true } } as never
  })
  on('command.run', (_$, e) => {
    if (e.command === failing) throw new Error('沒有這個指令')
    ran.push(e.command)
    return { value: {} } as never
  })
  on('session.id', () => ({ value: SELF }) as never)
  on('process.run', (_$, e) => {
    runs.push({ argv: e.argv, cwd: e.init?.cwd })
    return { value: { exitCode: 0, stdout: '', stderr: '', isStdoutTruncated: false, isStderrTruncated: false } }
  })
  on('session.send', (_$, e) => {
    sent.push({ to: e.to, text: e.text })
    return { isDelivered: true } as never
  })
  return { ran, filled, stored, read, runs, sent, toasts }
}

const SELF = '11111111-2222-3333-4444-555555555555'
const PARENT = '99999999-2222-3333-4444-555555555555'

for (const surface of SURFACES) {
  test(`the telemetry rail names the folder and model, then ctx, 5h and 7d (${surface})`, async ($, on) => {
    engine(on)
    const ui = await mount($, band(160, { surface }))

    expect(await ui.find({ text: /common-dev-plugin/ })).toBeDefined()
    expect(await ui.find({ text: /Sonnet 5\.5/ })).toBeDefined()
    expect(await ui.find({ text: /^ctx$/ })).toBeDefined()
    expect(await ui.find({ text: /^47%$/ })).toBeDefined()
    expect(await ui.find({ text: /^94k\/200k$/ })).toBeDefined()
    expect(await ui.find({ text: /^23%$/ })).toBeDefined()
    expect(await ui.find({ text: /^3h1\dm$/ })).toBeDefined()
    expect(await ui.find({ text: /^12%$/ })).toBeDefined()
  })

  test(`看不懂 and 畫給我看 run the commands a person would type (${surface})`, async ($, on) => {
    const { ran } = engine(on)
    const ui = await mount($, band(160, { surface }))

    for (const key of ['explain', 'draw']) await ui.press({ key: `bar-${key}` })

    expect(ran).toEqual(['common:wait-what', 'common:show-me'])
  })

  test(`a button whose command fails says why (${surface})`, async ($, on) => {
    const { toasts } = engine(on, { failing: 'common:wait-what' })
    const ui = await mount($, band(160, { surface }))

    await ui.press({ key: 'bar-explain' })

    expect(toasts.some(t => t.startsWith('看不懂：'))).toBe(true)
  })

  test(`a command the session lacks draws no button (${surface})`, async ($, on) => {
    engine(on, { commands: ['diff', 'artifacts'] })
    const ui = await mount($, band(160, { surface }))

    expect(await ui.find({ key: 'bar-explain' })).toBeUndefined()
    expect(await ui.find({ key: 'bar-draw' })).toBeUndefined()
    expect(await ui.find({ key: 'bar-side' })).toBeDefined()
  })

  // This plugin's own commands never reach its command.run hooks through
  // `$.command.run`, so 側聊 opens the side pane itself.
  test(`側聊 opens the side pane, docked where the surface docks panes (${surface})`, async ($, on) => {
    const { ran, runs } = engine(on)
    const opened: unknown[] = []
    on('ui.open', (_$, e) => {
      opened.push(e)
      return { value: { isPlaced: true } } as never
    })
    on('ui.scroll', () => ({ value: {} }) as never)
    const ui = await mount($, band(160, { surface }))

    await ui.press({ key: 'bar-side' })

    expect(ran).toEqual([])
    expect(runs).toEqual([])
    expect((opened[0] as { id: string }).id).toBe('side')
  })

  test(`a branch window takes the id its opener left, and 帶回主線 sends a summary there (${surface})`, async ($, on) => {
    const { sent } = engine(on, { suggestions: '查到了：x.ts 第 12 行', store: { branchParent: { id: PARENT, at: Date.now() } } })
    // No slash commands any more: 側聊 and 回想 live on the bar alone.
    const registered: string[] = []
    on('command.register', (_$, e) => {
      registered.push(e.name)
      return { value: { command: e.name } } as never
    })
    on('session.start', (_$, e) => ({ cwd: e.cwd }) as never)
    const kit = $ as unknown as { session: { start: (e: unknown) => Promise<unknown> } }
    await kit.session.start({ cwd: 'C:\\work', surface, isInteractive: true })
    expect(registered).toEqual([])

    const ui = await mount($, band(160, { surface }))
    await ui.press({ key: 'bar-back' })

    expect(sent[0]?.to).toBe(PARENT)
    expect(sent[0]?.text).toBe('[分支回報]\n查到了：x.ts 第 12 行')
  })

  test(`a window that is no branch has no 帶回主線 (${surface})`, async ($, on) => {
    engine(on)
    const ui = await mount($, band(160, { surface }))
    expect(await ui.find({ key: 'bar-back' })).toBeUndefined()
  })

  test(`下一步 offers the forked suggestions, drops unknown commands, and fills the pick as a draft (${surface})`, async ($, on) => {
    const { filled } = engine(on, {
      suggestions: JSON.stringify([
        { label: '跑測試', prompt: '跑一下 bar 的測試' },
        { label: '不存在', prompt: '/no-such-command now' },
        { label: '看變更', prompt: '/diff' },
      ]),
    })
    const ui = await mount($, band(160, { surface }))
    await ui.press({ key: 'bar-next' })

    expect(await ui.find({ key: 'next-1' })).toBeDefined()
    expect(await ui.find({ key: 'next-2' })).toBeDefined()
    expect(await ui.find({ key: 'next-3' })).toBeUndefined()

    await ui.press({ key: 'next-1' })
    expect(filled).toEqual(['跑一下 bar 的測試'])
    expect(await ui.find({ key: 'next-1' })).toBeUndefined()
  })

  test(`a survey keeps the band (${surface})`, async ($, on) => {
    engine(on)
    on('ui.render', ($, e) => {
      const { Box } = $.ui.resolve(e)
      return <Box />
    })
    const ui = await mount($, band(160, { hasSurvey: true, surface }))

    expect(await ui.find({ key: 'bar-side' })).toBeUndefined()
  })
}

test('a wide terminal draws a bar for every gauge, a narrow one only the numbers', async ($, on) => {
  engine(on)
  const wide = await mount($, band(160))
  for (const key of ['spine', 'bar-ctx', 'bar-five', 'bar-seven']) expect(await wide.find({ key })).toBeDefined()

  const narrow = await mount($, band(40, { requestId: 'band-narrow' }))
  expect(await narrow.find({ key: 'bar-ctx' })).toBeUndefined()
  expect(await narrow.find({ text: /^23%$/ })).toBeDefined()
})

test('diff and artifacts are the terminal’s, and run its commands', async ($, on) => {
  const { ran } = engine(on)
  const ui = await mount($, band(160))
  expect(await ui.find({ key: 'chip-side' })).toBeDefined()

  for (const key of ['diff', 'artifacts']) await ui.press({ key: `bar-${key}` })
  expect(ran).toEqual(['diff', 'artifacts'])

  const desk = await mount($, band(160, { requestId: 'band-desktop', surface: 'desktop' }))
  expect(await desk.find({ key: 'bar-diff' })).toBeUndefined()
  expect(await desk.find({ key: 'bar-artifacts' })).toBeUndefined()
})

test('a terminal chip carries its padding in the label, so all of it presses', async ($, on) => {
  engine(on)
  const ui = await mount($, band(160))
  expect(await ui.find({ key: 'bar-side', text: /^ 側聊 $/ })).toBeDefined()
})

test('圖示 turns the Nerd Font glyphs on and keeps the choice for later sessions', async ($, on) => {
  const { stored } = engine(on)
  const ui = await mount($, band(160))
  expect(await ui.find({ text: /^○ 圖示$/ })).toBeDefined()
  expect(await ui.find({ text: /^ 側聊 $/ })).toBeDefined()

  await ui.press({ key: 'bar-glyphs' })

  expect(stored).toEqual([['barGlyphs', true]])
  expect(await ui.find({ text: /^● 圖示$/ })).toBeDefined()
  expect((await ui.find({ key: 'bar-side' }))?.text).toBe('  側聊 ')
  expect(await ui.find({ text: /^$/ })).toBeDefined()
})

test('the desktop draws native buttons, SVG gauges, and no glyph toggle', async ($, on) => {
  const { read } = engine(on, { store: { barGlyphs: true } })
  const ui = await mount($, band(160, { surface: 'desktop' }))

  expect((await ui.find({ key: 'bar-side' }))?.props.variant).toBe('secondary')
  expect(await ui.find({ key: 'bar-side', text: /^側聊$/ })).toBeDefined()
  expect(await ui.find({ key: 'bar-glyphs' })).toBeUndefined()
  expect(read).not.toContain('barGlyphs')
  expect(await ui.find({ text: /◢/ })).toBeUndefined()
  expect(await ui.findAll({ type: 'Raster' })).toEqual([])
  const bars = await ui.findAll({ type: 'Svg' })
  expect(bars.map(b => b.props.alt)).toEqual(['ctx 47%', '5h 23%', '7d 12%'])
})

test('a narrow desktop keeps only the numbers', async ($, on) => {
  engine(on)
  const ui = await mount($, band(60, { surface: 'desktop' }))
  expect(await ui.findAll({ type: 'Svg' })).toEqual([])
  expect(await ui.find({ text: /^47%$/ })).toBeDefined()
})

test('VS Code takes the desktop’s drawing', async ($, on) => {
  engine(on)
  const ui = await mount($, band(160, { surface: 'vscode' }))
  expect((await ui.find({ key: 'bar-side' }))?.props.variant).toBe('secondary')
  expect(await ui.find({ key: 'bar-diff' })).toBeUndefined()
})

test('資料夾 and VS Code are gone from the bar', async ($, on) => {
  engine(on)
  const ui = await mount($, band(160))
  expect(await ui.find({ key: 'bar-folder' })).toBeUndefined()
  expect(await ui.find({ key: 'bar-editor' })).toBeUndefined()
})
