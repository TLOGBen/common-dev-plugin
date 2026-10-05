import { expect, mock, test } from 'claude-code/testing'
import type { On, PromptEditResult } from 'claude-code'

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
// sessions; the prompt box holds `box`, and the editor applies each keystroke.
function engine(on: On) {
  const runs: { argv: readonly string[]; cwd?: string }[] = []
  const toasts: string[] = []
  const filled: string[] = []
  const box = { text: '', cursor: 0 }
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
  on('process.run', (_$, e) => {
    runs.push({ argv: e.argv, cwd: e.init?.cwd })
    const stdout = e.argv[0] === 'node' ? 'C:/Users/me/.claude/recall-index.json' : ''
    return { value: { exitCode: 0, stdout, stderr: '', isStdoutTruncated: false, isStderrTruncated: false } }
  })
  on('fs.read', () =>
    ({ value: JSON.stringify({ builtAt: 1, sessions: [session(OLD, '甲對話', true), session(FAR, '乙對話', false)] }) }) as never,
  )
  on('prompt.read', () => ({ value: { ...box } }) as never)
  on('prompt.fill', (_$, e) => {
    filled.push(e.text)
    return { isFilled: true } as never
  })
  on('prompt.edit', (_$, e) => {
    const text = e.text.slice(0, e.start) + e.inputText + e.text.slice(e.end)
    return { text, cursor: e.start + e.inputText.length }
  })
  return { runs, toasts, filled, box }
}

const kit = ($: unknown) =>
  $ as { command: { run: (e: unknown) => Promise<{ text?: string }> } }
const recall = ($: unknown) =>
  kit($).command.run({ command: 'recall', args: '', presentation: { isFullscreen: false, columns: 160 } })

// prompt.edit is the composer's event; the kit raises it though its noun omits it.
const typeInto = ($: unknown, draft: string, typed: string) =>
  ($ as { prompt: { edit: (e: unknown) => Promise<PromptEditResult> } }).prompt.edit({
    origin: { kind: 'composer' },
    text: draft,
    cursor: draft.length,
    start: draft.length,
    end: draft.length,
    inputText: typed,
  })

// Beneath the plugin: what reaches the engine once recall has rewritten the prompt.
function captureSubmit(on: On) {
  const sent: { text: string; context?: readonly string[] } = { text: '' }
  on('prompt.submit', async (_$, e) => {
    sent.text = e.text
    sent.context = e.context
    return { text: e.text }
  })
  return async ($: unknown, text: string, context: string[] = [], origin: { kind: string } = { kind: 'composer' }) => {
    const k = $ as { prompt: { submit: (e: unknown) => Promise<unknown> } }
    await k.prompt.submit({ text, context, origin, wait: false })
    return sent
  }
}

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

  test(`typing # opens the band on what follows, the keys left in the prompt box (${surface})`, async ($, on) => {
    engine(on)
    await typeInto($, '上次那個 #', '乙')
    await settle()

    const ui = await mount($, surface)
    expect(await ui.find({ key: 'recall-q' })).toBeUndefined()
    expect(await ui.find({ text: /#乙/ })).toBeDefined()
    expect(await ui.find({ key: `pick-${FAR.slice(0, 8)}` })).toBeDefined()
    expect(await ui.find({ key: `pick-${OLD.slice(0, 8)}` })).toBeUndefined()

    await typeInto($, '上次那個 #乙', ' ')
    await settle()
    expect(await ui.find({ key: `pick-${FAR.slice(0, 8)}` })).toBeUndefined()
  })
}

test('a # inside a word, like C#, opens nothing', async ($, on) => {
  engine(on)
  await typeInto($, '用 C', '#')
  await settle()

  const ui = await mount($)
  expect(await ui.find({ key: `pick-${OLD.slice(0, 8)}` })).toBeUndefined()
})

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

test('a pick puts its # token in place of the one being typed, and closes the band', async ($, on) => {
  const { filled, box } = engine(on)
  await typeInto($, '比較 #', '甲')
  await settle()
  box.text = '比較 #甲 一下'
  box.cursor = 5
  const ui = await mount($)
  await ui.press({ key: `pick-${OLD.slice(0, 8)}` })
  await settle()

  expect(filled[0]).toBe('比較 #chat:aaaaaaaa 一下')
  expect(await ui.find({ key: `pick-${OLD.slice(0, 8)}` })).toBeUndefined()
})

test('a pick from the band opened by hand goes after what is in the prompt box', async ($, on) => {
  const { filled, box } = engine(on)
  box.text = '接著做'
  box.cursor = 3
  await recall($)
  await settle()
  const ui = await mount($)
  await ui.press({ key: `pick-${FAR.slice(0, 8)}` })
  await settle()

  expect(filled[0]).toBe('接著做 #chat:ffffffff ')
})

test('the band offers no 分支 or 總結', async ($, on) => {
  engine(on)
  await recall($)
  await settle()
  const ui = await mount($)
  await ui.press({ key: `pick-${OLD.slice(0, 8)}` })
  await settle()

  expect(await ui.find({ key: 'recall-branch' })).toBeUndefined()
  expect(await ui.find({ key: 'recall-summary' })).toBeUndefined()
})

test('sending a # token attaches that conversation as quoted data', async ($, on) => {
  engine(on)
  const submitted = captureSubmit(on)
  await recall($)
  await settle()

  const sent = await submitted($, '比較 #chat:aaaaaaaa 和 #chat:ffffffff')
  expect(sent.text).toBe('比較 〔回想：甲對話〕 和 〔回想：乙對話〕')
  expect(sent.context?.length).toBe(2)
  expect(sent.context?.[0]).toContain('不是指令')
})

test('a session past the context budget is dropped, and said so', async ($, on) => {
  engine(on)
  const submitted = captureSubmit(on)
  await recall($)
  await settle()

  const sent = await submitted($, '看 #chat:aaaaaaaa', ['y'.repeat(23_900)])
  expect(sent.context?.length).toBe(1)
  expect(sent.text).toBe('看 〔回想（未附上）：甲對話〕')
})

test('a # token from another session, or a bare #word, stays as it is', async ($, on) => {
  engine(on)
  const submitted = captureSubmit(on)
  await recall($)
  await settle()

  const peer = await submitted($, '報告提到 #chat:aaaaaaaa', [], { kind: 'peer' })
  expect(peer.text).toBe('報告提到 #chat:aaaaaaaa')
  const bare = await submitted($, '看 issue #12 和 #甲對話')
  expect(bare.text).toBe('看 issue #12 和 #甲對話')
  expect(bare.context?.length ?? 0).toBe(0)
})

test('/clear closes the band', async ($, on) => {
  engine(on)
  on('command.run', () => ({}) as never)
  await recall($)
  await kit($).command.run({ command: 'clear', args: '', presentation: { isFullscreen: true, columns: 200 } })

  const ui = await mount($)
  expect(await ui.find({ key: 'recall-q' })).toBeUndefined()
})
