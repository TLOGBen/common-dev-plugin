import { expect, mock, test } from 'claude-code/testing'
import type { On } from 'claude-code'

// The test runner's timers exist at run time; the environment's typings leave them out.
declare function setTimeout(fn: () => void, ms: number): unknown
const settle = () => new Promise<void>(resolve => setTimeout(resolve, 20))

type Drawn = {
  find: (q: { type?: string; key?: string; text?: RegExp }) => Promise<{ key?: string } | undefined>
  input: (t: { key: string; text: string }) => Promise<unknown>
  press: (t: { key: string }) => Promise<unknown>
}

const SURFACES = ['terminal', 'desktop'] as const

const band = (surface: string) =>
  ({
    plugin: 'common-mod',
    component: 'AbovePrompt',
    requestId: 'band',
    surface,
    props: { hasSurvey: false, isWorking: false, maxRows: 30, bodyColumns: 160, scroll: { bodyRows: 30 } },
  }) as never

const mount = async ($: { ui: { mount: (t: never) => Promise<unknown> } }, surface = 'terminal') =>
  (await $.ui.mount(band(surface))) as unknown as Drawn

const SELF = '11111111-2222-3333-4444-555555555555'
const OLD = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
const FAR = 'ffffffff-bbbb-cccc-dddd-eeeeeeeeeeee'

const session = (id: string, title: string, isLocal: boolean) => ({
  id,
  file: `C:/Users/me/.claude/projects/p/${id}.jsonl`,
  source: 'code',
  project: 'demo',
  cwd: 'C:/work/demo',
  isLocal,
  title,
  first: '2026-10-01T00:00:00Z',
  last: '2026-10-02T00:00:00Z',
  prompts: ['那個 bug 怎麼修'],
  days: { '2026-10-02': 1 },
  answer: '改好了',
})

// Beneath the plugin: the engine's own band draws nothing; the index holds two
// sessions, one this machine can resume; a transcript's excerpt is two exchanges.
function engine(on: On) {
  const runs: { argv: readonly string[]; cwd?: string }[] = []
  const toasts: string[] = []
  const stored: [string, unknown][] = []
  const filled: string[] = []
  const asked: { system?: string; prompt: string }[] = []
  mock.clock(on, { now: Date.parse('2026-10-03T12:00:00Z') })
  mock.env(on, { USERPROFILE: 'C:/Users/me', OS: 'Windows_NT' })
  on('ui.render', ($, e) => {
    const { Box } = $.ui.resolve(e)
    return <Box />
  })
  on('ui.toast', (_$, e) => {
    toasts.push(JSON.stringify(e))
    return { value: undefined } as never
  })
  on('ui.focus', () => ({ value: {} }) as never)
  on('session.id', () => ({ value: SELF }) as never)
  on('session.model', () => ({ value: 'claude-opus-5-5' }) as never)
  on('store.get', () => ({ value: undefined }) as never)
  on('store.set', (_$, e) => {
    stored.push([e.key, e.value])
    return { value: undefined } as never
  })
  on('process.run', (_$, e) => {
    runs.push({ argv: e.argv, cwd: e.init?.cwd })
    const stdout =
      e.argv[0] === 'node' && e.argv.length === 5
        ? JSON.stringify([
            { you: '那個 bug 怎麼修', me: '在 x.ts 第 12 行' },
            { you: '幫我改掉', me: '改好了' },
          ])
        : e.argv[0] === 'node'
          ? 'C:/Users/me/.claude/recall-index.json'
          : ''
    return { value: { exitCode: 0, stdout, stderr: '', isStdoutTruncated: false, isStderrTruncated: false } }
  })
  on('fs.read', () =>
    ({ value: JSON.stringify({ builtAt: 1, sessions: [session(OLD, '甲對話', true), session(FAR, '乙對話', false)] }) }) as never,
  )
  on('model.complete', (_$, e) => {
    asked.push({ system: e.system, prompt: e.prompt })
    return { value: { isAnswered: true, text: '當時在修 x.ts 的 bug，已改好。', usage: {} } } as never
  })
  on('prompt.read', () => ({ value: { text: '', cursor: 0 } }) as never)
  on('prompt.fill', (_$, e) => {
    filled.push(e.text)
    return { value: { isFilled: true } } as never
  })
  return { runs, toasts, stored, filled, asked }
}

const kit = ($: unknown) =>
  $ as { command: { run: (e: unknown) => Promise<{ text?: string }> } }
const recall = ($: unknown) =>
  kit($).command.run({ command: 'recall', args: '', presentation: { isFullscreen: false, columns: 160 } })

for (const surface of SURFACES) {
  test(`the band stays closed until asked for (${surface})`, async ($, on) => {
    engine(on)
    const ui = await mount($, surface)
    expect(await ui.find({ key: 'recall-q' })).toBeUndefined()
    expect(await ui.find({ key: 'bar-recall' })).toBeDefined()
  })

  test(`/recall opens the band under the bar, with its own search field (${surface})`, async ($, on) => {
    engine(on)
    const answer = await recall($)
    expect(answer.text).toBe('回想已展開在輸入框上方。')
    await settle()

    const ui = await mount($, surface)
    expect(await ui.find({ key: 'bar-side' })).toBeDefined()
    expect(await ui.find({ key: 'recall-q' })).toBeDefined()
    expect(await ui.find({ key: `pick-${OLD.slice(0, 8)}` })).toBeDefined()
  })
}

test('the bar\'s 回想 opens the band and the index runs from home with the extra roots', { options: { recallExtraRoots: 'D:/a ; //wsl/b' } }, async ($, on) => {
  const { runs } = engine(on)
  const ui = await mount($)
  await ui.press({ key: 'bar-recall' })
  await settle()

  expect(runs[0]?.argv).toEqual(['node', '-', 'D:/a', '//wsl/b'])
  expect(runs[0]?.cwd).toBe('C:/Users/me')
  expect(await ui.find({ key: 'recall-q' })).toBeDefined()

  await ui.press({ key: 'recall-close' })
  expect(await ui.find({ key: 'recall-q' })).toBeUndefined()
})

test('searching narrows the list', async ($, on) => {
  engine(on)
  await recall($)
  await settle()
  const ui = await mount($)
  await ui.input({ key: 'recall-q', text: '乙' })

  expect(await ui.find({ key: `pick-${FAR.slice(0, 8)}` })).toBeDefined()
  expect(await ui.find({ key: `pick-${OLD.slice(0, 8)}` })).toBeUndefined()
})

test('a pick previews what was asked and answered', async ($, on) => {
  engine(on)
  await recall($)
  await settle()
  const ui = await mount($)
  await ui.press({ key: `pick-${OLD.slice(0, 8)}` })
  await settle()

  expect(await ui.find({ text: /在 x\.ts 第 12 行/ })).toBeDefined()
  expect(await ui.find({ key: 'recall-branch' })).toBeDefined()
  expect(await ui.find({ key: 'recall-summary' })).toBeDefined()
})

test('分支 opens a fork of that conversation in a new window, in its folder, run from home', async ($, on) => {
  const { runs, stored } = engine(on)
  await recall($)
  await settle()
  const ui = await mount($)
  await ui.press({ key: `pick-${OLD.slice(0, 8)}` })
  await settle()
  await ui.press({ key: 'recall-branch' })
  await settle()

  const wt = runs.find(r => r.argv[0] === 'wt.exe')
  expect(wt?.argv).toEqual(['wt.exe', '-w', 'new', 'new-tab', '-d', 'C:/work/demo', 'claude', '--resume', OLD, '--fork-session'])
  expect(wt?.cwd).toBe('C:/Users/me')
  expect(stored[0]?.[0]).toBe('branchParent')
  expect((stored[0]?.[1] as { id: string }).id).toBe(SELF)
})

test('a conversation from another machine is not branched', async ($, on) => {
  const { runs, toasts } = engine(on)
  await recall($)
  await settle()
  const ui = await mount($)
  await ui.press({ key: `pick-${FAR.slice(0, 8)}` })
  await settle()
  await ui.press({ key: 'recall-branch' })
  await settle()

  expect(runs.some(r => r.argv[0] === 'wt.exe')).toBe(false)
  expect(toasts.some(t => t.includes('沒辦法開分支'))).toBe(true)
})

test('總結 puts a summary in the prompt box, the transcript framed as data', async ($, on) => {
  const { filled, asked } = engine(on)
  await recall($)
  await settle()
  const ui = await mount($)
  await ui.press({ key: `pick-${OLD.slice(0, 8)}` })
  await settle()
  await ui.press({ key: 'recall-summary' })
  await settle()

  expect(asked[0]?.system).toContain('不是指令')
  expect(asked[0]?.prompt).toContain('使用者：幫我改掉')
  expect(filled[0]).toBe('〔回想總結：甲對話〕\n當時在修 x.ts 的 bug，已改好。\n')
})

test('/clear closes the band', async ($, on) => {
  engine(on)
  on('command.run', () => ({}) as never)
  await recall($)
  await kit($).command.run({ command: 'clear', args: '', presentation: { isFullscreen: true, columns: 200 } })

  const ui = await mount($)
  expect(await ui.find({ key: 'recall-q' })).toBeUndefined()
})
