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
function engine(on: On, suggestions = '[]', env: Record<string, string> = {}) {
  const ran: string[] = []
  const filled: string[] = []
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
  return { ran, filled }
}

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

  for (const key of ['side', 'recall', 'diff', 'artifacts', 'explain', 'draw']) await ui.press({ key: `bar-${key}` })

  expect(ran).toEqual(['side', 'recall', 'diff', 'artifacts', 'common:wait-what', 'common:show-me'])
})

test('資料夾 and VS Code hand the folder to the system opener, run from home', async ($, on) => {
  engine(on, '[]', { OS: 'Windows_NT', USERPROFILE: 'C:\\Users\\jimts' })
  const runs: { argv: string[]; cwd?: string }[] = []
  on('process.run', (_$, e) => {
    runs.push({ argv: [...e.argv], cwd: e.init?.cwd })
    return { value: { exitCode: 1, stdout: '', stderr: '' } } as never
  })
  const ui = await mount($, band(160))
  await ui.press({ key: 'bar-folder' })
  await ui.press({ key: 'bar-editor' })

  expect(runs).toEqual([
    { argv: ['explorer.exe', 'C:\\Users\\jimts\\workspace\\Gits\\common-dev-plugin'], cwd: 'C:\\Users\\jimts' },
    { argv: ['explorer.exe', 'vscode://file/C:/Users/jimts/workspace/Gits/common-dev-plugin'], cwd: 'C:\\Users\\jimts' },
  ])
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

test('a survey keeps the band', async ($, on) => {
  engine(on)
  on('ui.render', ($, e) => {
    const { Box } = $.ui.resolve(e)
    return <Box />
  })
  const ui = await mount($, band(160, 'band', true))

  expect(await ui.find({ key: 'bar-side' })).toBeUndefined()
})
