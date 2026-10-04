import { expect, mock, test } from 'claude-code/testing'
import type { On, PromptEditResult } from 'claude-code'

// The test runner's timers exist at run time; the environment's typings leave them out.
declare function setTimeout(fn: () => void, ms: number): unknown

const SURFACES = ['terminal', 'desktop'] as const
// Only `hasSurvey` matters to the band; the rest of the site's props are the
// engine's and left to it.
const BAND = { plugin: 'common-mod', component: 'AbovePrompt', props: { hasSurvey: false } } as never

// Beneath the plugin: the engine's own band draws nothing, and its editor
// applies the splice so the plugin sees the draft after each keystroke.
function engine(on: On) {
  mock.clock(on, { now: Date.parse('2026-10-03T12:00:00Z') })
  on('ui.render', ($, e) => {
    const { Box } = $.ui.resolve(e)
    return <Box />
  })
  on('prompt.edit', (_$, e) => {
    const text = e.text.slice(0, e.start) + e.inputText + e.text.slice(e.end)
    return { text, cursor: e.start + e.inputText.length }
  })
}

const type = (draft: string, typed: string) => ({
  origin: { kind: 'composer' } as const,
  text: draft,
  cursor: draft.length,
  start: draft.length,
  end: draft.length,
  inputText: typed,
})

for (const surface of SURFACES) {
  test(`band stays out of the way until @@ is typed (${surface})`, async ($, on) => {
    engine(on)
    const ui = await $.ui.mount({ ...(BAND as object), surface } as never)
    expect(await ui.find({ text: /回想/ })).toBeUndefined()
  })

  test(`typing @@ opens the band and paints the token (${surface})`, async ($, on) => {
    engine(on)
    // prompt.edit is the composer's event; the kit raises it though its noun omits it
    const prompt = $.prompt as unknown as { edit: (e: unknown) => Promise<PromptEditResult> }
    const edited = await prompt.edit(type('上次那個 @@sks', 'e'))
    expect(edited.decorations?.some(d => d.start === 5 && d.end === 11)).toBe(true)

    const ui = await $.ui.mount({ ...(BAND as object), surface } as never)
    expect(await ui.find({ text: /skse/ })).toBeDefined()
    expect(await ui.find({ key: 'strata' })).toBeDefined()
  })
}

test('a prompt without @@ is sent untouched', async ($, on) => {
  let seen = ''
  on('prompt.submit', async (_$, e) => {
    seen = e.text
    return { text: e.text }
  })
  await $.prompt.submit({ text: '幫我看一下 log', wait: false } as never)
  expect(seen).toBe('幫我看一下 log')
})

// An index of two sessions whose last answers are long enough to test the budget.
function indexed(on: On, answerChars: number) {
  mock.env(on, { USERPROFILE: 'C:/Users/me' })
  const session = (id: string, title: string) => ({
    id,
    file: `C:/Users/me/.claude/projects/p/${id}.jsonl`,
    source: 'code',
    project: 'demo',
    title,
    first: '2026-10-01T00:00:00Z',
    last: '2026-10-02T00:00:00Z',
    prompts: ['怎麼修'],
    days: { '2026-10-02': 1 },
    answer: 'x'.repeat(answerChars),
  })
  let loaded = () => {}
  const ready = new Promise<void>(resolve => (loaded = resolve))
  on('process.run', () => ({
    value: { exitCode: 0, stdout: 'C:/Users/me/.claude/recall-index.json', stderr: '', isStdoutTruncated: false, isStderrTruncated: false },
  }))
  on('fs.read', () => {
    setTimeout(loaded, 0)
    return { value: JSON.stringify({ builtAt: 1, sessions: [session('aaaaaaaa-1', '甲對話'), session('bbbbbbbb-2', '乙對話')] }) } as never
  })
  return ready
}

// Beneath the plugin: what reaches the engine once recall has rewritten the prompt.
function captureSubmit(on: On) {
  const sent: { text: string; context?: readonly string[] } = { text: '' }
  on('prompt.submit', async (_$, e) => {
    sent.text = e.text
    sent.context = e.context
    return { text: e.text }
  })
  return async ($: unknown, text: string, context: string[] = []) => {
    const kit = $ as { prompt: { submit: (e: unknown) => Promise<unknown> } }
    await kit.prompt.submit({ text, context, wait: false })
    return sent
  }
}

test('a session past the context budget is cut, the cut said in the block', async ($, on) => {
  engine(on)
  const ready = indexed(on, 20_000)
  const submitted = captureSubmit(on)
  const prompt = $.prompt as unknown as { edit: (e: unknown) => Promise<PromptEditResult> }
  await prompt.edit(type('@@', 'x'))
  await ready
  await new Promise<void>(resolve => setTimeout(resolve, 10))

  const sent = await submitted($, '比較 @@chat:aaaaaaaa 和 @@chat:bbbbbbbb')
  const blocks = sent.context ?? []
  expect(blocks.length).toBe(2)
  expect(blocks.reduce((n, b) => n + b.length, 0) <= 24_000).toBe(true)
  expect(blocks[1]?.includes('超過長度上限，已截斷')).toBe(true)
  expect(sent.text).toBe('比較 〔回想：甲對話〕 和 〔回想：乙對話〕')
})

test('a session with no room left is not attached, and its token says so', async ($, on) => {
  engine(on)
  const ready = indexed(on, 2_000)
  const submitted = captureSubmit(on)
  const prompt = $.prompt as unknown as { edit: (e: unknown) => Promise<PromptEditResult> }
  await prompt.edit(type('@@', 'x'))
  await ready
  await new Promise<void>(resolve => setTimeout(resolve, 10))

  const sent = await submitted($, '看 @@chat:aaaaaaaa', ['y'.repeat(23_600)])
  expect(sent.context?.length).toBe(1)
  expect(sent.text).toBe('看 〔回想（未附上）：甲對話〕')
})

test('/clear empties the band of the last conversation', async ($, on) => {
  engine(on)
  on('command.run', () => ({}) as never)
  const prompt = $.prompt as unknown as { edit: (e: unknown) => Promise<PromptEditResult> }
  await prompt.edit(type('@@sks', 'e'))
  const kit = $ as unknown as { command: { run: (e: unknown) => Promise<unknown> } }
  await kit.command.run({ command: 'clear', args: '', presentation: { isFullscreen: true, columns: 200 } })

  const ui = await $.ui.mount({ ...(BAND as object), surface: 'terminal' } as never)
  expect(await ui.find({ text: /回想/ })).toBeUndefined()
})

for (const isPlaced of [true, false]) {
  test(`/recall outside the fullscreen layout opens a dialog${isPlaced ? '' : ', withdrawn when it cannot seat'}`, async ($, on) => {
    engine(on)
    let opened: { rows?: number } = {}
    let closed = false
    on('ui.open', (_$, e) => {
      opened = e as { rows?: number }
      return { value: { isPlaced } } as never
    })
    on('ui.close', () => {
      closed = true
      return { value: undefined } as never
    })
    const kit = $ as unknown as { command: { run: (e: unknown) => Promise<{ text?: string }> } }
    const answer = await kit.command.run({ command: 'recall', args: '', presentation: { isFullscreen: false, columns: 90 } })

    expect(opened.rows).toBe(30)
    expect(closed).toBe(!isPlaced)
    expect(answer.text).toBe(isPlaced ? '回想面板已開啟。' : '終端機太窄，放不下回想面板；把視窗拉寬一點再試。')
  })
}

test('the indexer runs from home with the extra roots from the settings', { options: { recallExtraRoots: 'D:/a ; //wsl/b' } }, async ($, on) => {
  engine(on)
  mock.env(on, { USERPROFILE: 'C:/Users/me' })
  let argv: readonly string[] = []
  let cwd: string | undefined
  let ran = () => {}
  const indexed = new Promise<void>(resolve => (ran = resolve))
  on('process.run', (_$, e) => {
    argv = e.argv
    cwd = e.init?.cwd
    ran()
    return { value: { exitCode: 1, stdout: '', stderr: 'stub', isStdoutTruncated: false, isStderrTruncated: false } }
  })
  const prompt = $.prompt as unknown as { edit: (e: unknown) => Promise<PromptEditResult> }
  await prompt.edit(type('@@', 'x'))
  await indexed
  expect(argv).toEqual(['node', '-', 'D:/a', '//wsl/b'])
  expect(cwd).toBe('C:/Users/me')
})
