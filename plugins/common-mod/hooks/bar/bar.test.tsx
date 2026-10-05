import { expect, test } from 'claude-code/testing'
import type { On } from 'claude-code'

type Drawn = {
  find: (q: { type?: string; key?: string; text?: RegExp }) => Promise<{ key?: string } | undefined>
  press: (t: { key: string }) => Promise<unknown>
}

const band = (bodyColumns: number, requestId = 'band', hasSurvey = false) =>
  ({
    plugin: 'common-mod',
    component: 'AbovePrompt',
    requestId,
    surface: 'terminal',
    props: { hasSurvey, isWorking: false, maxRows: 10, bodyColumns, scroll: { bodyRows: 10 } },
  }) as never

const mount = async ($: { ui: { mount: (t: never) => Promise<unknown> } }, target: never) =>
  (await $.ui.mount(target)) as unknown as Drawn

// What the session reports; the figures the old statusline showed.
function engine(
  on: On,
  suggestions = '[]',
  env: Record<string, string> = {},
  store: Record<string, unknown> = {},
  usageFails = false,
) {
  const ran: string[] = []
  const filled: string[] = []
  const stored: [string, unknown][] = []
  const runs: { argv: readonly string[]; cwd?: string }[] = []
  const sent: { to: unknown; text: string }[] = []
  on('store.get', (_$, e) => ({ value: store[e.key] }) as never)
  on('store.set', (_$, e) => {
    stored.push([e.key, e.value])
    return { value: undefined } as never
  })
  on('session.usage', () => {
    if (usageFails) throw new Error('no figures yet')
    return {
      value: {
        context: { tokens: 94_000, window: 200_000, percent: 47 },
        rateLimits: [
          { kind: 'five_hour', percentUsed: 23, resetsAt: new Date(Date.now() + 3 * 3_600_000 + 12 * 60_000).toISOString() },
          { kind: 'seven_day', percentUsed: 12 },
        ],
      },
    } as never
  })
  on('session.model', () => ({ value: 'claude-sonnet-5-5' }) as never)
  on('session.cwd', () => ({ value: 'C:\\Users\\jimts\\workspace\\Gits\\common-dev-plugin' }) as never)
  on('env.get', (_$, e) => ({ value: env[e.name] }) as never)
  on('clock.now', () => ({ value: Date.now() }) as never)
  on('clock.every', () => ({ value: null }) as never)
  on('ui.toast', () => ({ value: undefined }) as never)
  on('command.list', () => ({ value: [{ name: 'diff' }, { name: 'common:show-me' }] }) as never)
  on('model.fork', () => ({ value: { isAnswered: true, text: suggestions, usage: {} } }) as never)
  on('prompt.fill', (_$, e) => {
    filled.push(e.text)
    return { value: { isFilled: true } } as never
  })
  on('command.run', (_$, e) => {
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
  return { ran, filled, stored, runs, sent }
}

const SELF = '11111111-2222-3333-4444-555555555555'
const PARENT = '99999999-2222-3333-4444-555555555555'

test('the telemetry rail names the folder and model, then ctx, 5h and 7d', async ($, on) => {
  engine(on)
  const ui = await mount($, band(160))

  expect(await ui.find({ text: /common-dev-plugin/ })).toBeDefined()
  expect(await ui.find({ text: /Sonnet 5\.5/ })).toBeDefined()
  expect(await ui.find({ text: /^ctx$/ })).toBeDefined()
  expect(await ui.find({ text: /^47%$/ })).toBeDefined()
  expect(await ui.find({ text: /^94k\/200k$/ })).toBeDefined()
  expect(await ui.find({ text: /^23%$/ })).toBeDefined()
  expect(await ui.find({ text: /^3h1\dm$/ })).toBeDefined()
  expect(await ui.find({ text: /^12%$/ })).toBeDefined()
})

test('a wide terminal draws a bar for every gauge, a narrow one only the numbers', async ($, on) => {
  engine(on)
  const wide = await mount($, band(160))
  for (const key of ['spine', 'bar-ctx', 'bar-five', 'bar-seven']) expect(await wide.find({ key })).toBeDefined()

  const narrow = await mount($, band(40, 'band-narrow'))
  expect(await narrow.find({ key: 'bar-ctx' })).toBeUndefined()
  expect(await narrow.find({ text: /^23%$/ })).toBeDefined()
})

test('the buttons run the commands a person would type', async ($, on) => {
  const { ran } = engine(on)
  const ui = await mount($, band(160))
  expect(await ui.find({ key: 'chip-side' })).toBeDefined()

  for (const key of ['diff', 'artifacts', 'explain', 'draw']) await ui.press({ key: `bar-${key}` })

  expect(ran).toEqual(['diff', 'artifacts', 'common:wait-what', 'common:show-me'])
})

// This plugin's own commands never reach its command.run hooks through
// `$.command.run`, so 側聊 opens the side pane itself.
test('側聊 opens the side pane, docked where the surface docks panes', async ($, on) => {
  const { ran, runs } = engine(on)
  const opened: unknown[] = []
  on('ui.open', (_$, e) => {
    opened.push(e)
    return { value: { isPlaced: true } } as never
  })
  on('ui.scroll', () => ({ value: {} }) as never)
  const ui = await mount($, band(160))

  await ui.press({ key: 'bar-side' })

  expect(ran).toEqual([])
  expect(runs).toEqual([])
  expect((opened[0] as { id: string }).id).toBe('side')
})

test('a branch window takes the id its opener left, and 帶回主線 sends a summary there', async ($, on) => {
  const { sent } = engine(on, '查到了：x.ts 第 12 行', {}, { branchParent: { id: PARENT, at: Date.now() } })
  on('command.register', (_$, e) => ({ value: { command: e.name } }) as never)
  on('session.start', (_$, e) => ({ cwd: e.cwd }) as never)
  const kit = $ as unknown as { session: { start: (e: unknown) => Promise<unknown> } }
  await kit.session.start({ cwd: 'C:\\work', surface: 'terminal', isInteractive: true })

  const ui = await mount($, band(160))
  await ui.press({ key: 'bar-back' })

  expect(sent[0]?.to).toBe(PARENT)
  expect(sent[0]?.text).toBe('[分支回報]\n查到了：x.ts 第 12 行')
})

test('a window that is no branch has no 帶回主線', async ($, on) => {
  engine(on)
  const ui = await mount($, band(160))
  expect(await ui.find({ key: 'bar-back' })).toBeUndefined()
})

test('資料夾 and VS Code hand the folder to the system opener, run from home', async ($, on) => {
  const { runs } = engine(on, '[]', { OS: 'Windows_NT', USERPROFILE: 'C:\\Users\\jimts' })
  const ui = await mount($, band(160))
  await ui.press({ key: 'bar-folder' })
  await ui.press({ key: 'bar-editor' })

  expect(runs).toEqual([
    { argv: ['explorer.exe', 'C:\\Users\\jimts\\workspace\\Gits\\common-dev-plugin'], cwd: 'C:\\Users\\jimts' },
    { argv: ['explorer.exe', 'vscode://file/C:/Users/jimts/workspace/Gits/common-dev-plugin'], cwd: 'C:\\Users\\jimts' },
  ])
})

// The folder used to be read only after the usage figures, so a failed read
// of those left 資料夾 doing nothing at all.
test('資料夾 still opens when the usage figures could not be read', async ($, on) => {
  const { runs } = engine(on, '[]', { OS: 'Windows_NT', USERPROFILE: 'C:\\Users\\jimts' }, {}, true)
  const ui = await mount($, band(160))
  await ui.press({ key: 'bar-folder' })

  expect(runs[0]?.argv).toEqual(['explorer.exe', 'C:\\Users\\jimts\\workspace\\Gits\\common-dev-plugin'])
})

test('下一步 offers the forked suggestions, drops unknown commands, and fills the pick as a draft', async ($, on) => {
  const { filled } = engine(
    on,
    JSON.stringify([
      { label: '跑測試', prompt: '跑一下 bar 的測試' },
      { label: '不存在', prompt: '/no-such-command now' },
      { label: '看變更', prompt: '/diff' },
    ]),
  )
  const ui = await mount($, band(160))
  await ui.press({ key: 'bar-next' })

  expect(await ui.find({ key: 'next-1' })).toBeDefined()
  expect(await ui.find({ key: 'next-2' })).toBeDefined()
  expect(await ui.find({ key: 'next-3' })).toBeUndefined()

  await ui.press({ key: 'next-1' })
  expect(filled).toEqual(['跑一下 bar 的測試'])
  expect(await ui.find({ key: 'next-1' })).toBeUndefined()
})

test('圖示 turns the Nerd Font glyphs on and keeps the choice for later sessions', async ($, on) => {
  const { stored } = engine(on)
  const ui = await mount($, band(160))
  expect(await ui.find({ text: /^○ 圖示$/ })).toBeDefined()
  expect(await ui.find({ text: /^側聊$/ })).toBeDefined()

  await ui.press({ key: 'bar-glyphs' })

  expect(stored).toEqual([['barGlyphs', true]])
  expect(await ui.find({ text: /^● 圖示$/ })).toBeDefined()
  expect(await ui.find({ text: /^ 側聊$/ })).toBeDefined()
})

test('a survey keeps the band', async ($, on) => {
  engine(on)
  on('ui.render', ($, e) => {
    const { Box } = $.ui.resolve(e)
    return <Box />
  })
  const ui = await mount($, band(160, 'band', true))

  expect(await ui.find({ key: 'bar-side' })).toBeUndefined()
})
