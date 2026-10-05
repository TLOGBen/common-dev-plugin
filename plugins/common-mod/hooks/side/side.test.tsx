import { expect, test } from 'claude-code/testing'
import type { On } from 'claude-code'

// The kit's mount is typed per surface; these tests only find, type and press.
type Drawn = {
  find: (q: { type?: string; key?: string; text?: RegExp }) => Promise<{ key?: string } | undefined>
  findAll: (q: { type?: string }) => Promise<{ key?: string }[]>
  input: (t: { key: string; text: string }) => Promise<unknown>
  press: (t: { key: string }) => Promise<unknown>
}

const SURFACES = ['terminal', 'desktop'] as const

// Only what the drawing reads; the rest of the site's props are the engine's.
const PANE = {
  plugin: 'common-mod',
  component: 'Pane',
  requestId: 'side',
  props: { title: '側聊', isFocused: true, bodyColumns: 80, placement: 'dock', scroll: { bodyRows: 30 } },
} as never

function engine(on: On, reply = '在 src/x.ts 第 12 行') {
  const prompts: string[] = []
  on('ui.scroll', () => ({ value: {} }) as never)
  on('ui.render', ($, e) => {
    const { Box } = $.ui.resolve(e)
    return <Box />
  })
  on('ui.open', () => ({ value: { isPlaced: true } }) as never)
  on('model.fork', (_$, e) => {
    prompts.push(e.prompt)
    return { value: { isAnswered: true, text: reply, usage: {} } } as never
  })
  return prompts
}

const mount = async ($: { ui: { mount: (t: never) => Promise<unknown> } }, target: object) =>
  (await $.ui.mount(target as never)) as unknown as Drawn

for (const surface of SURFACES) {
  test(`an empty side chat says what it can see (${surface})`, async ($, on) => {
    engine(on)
    const ui = await mount($, { ...(PANE as object), surface })
    expect(await ui.find({ text: /不會寫進主對話/ })).toBeDefined()
  })

  test(`a question is answered from a fork (${surface})`, async ($, on) => {
    const prompts = engine(on)
    const ui = await mount($, { ...(PANE as object), surface })
    const field = await ui.find({ type: 'Input' })
    await ui.input({ key: field?.key ?? '', text: '那個 bug 在哪？' })

    expect(await ui.find({ text: /那個 bug 在哪/ })).toBeDefined()
    expect(await ui.find({ text: /第 12 行/ })).toBeDefined()
    expect(prompts[0]).toContain('不要使用任何工具')
    expect(prompts[0]).toContain('問題：那個 bug 在哪？')
  })
}

test('a follow-up carries the earlier side exchange', async ($, on) => {
  const prompts = engine(on)
  const ui = await mount($, { ...(PANE as object), surface: 'terminal' })
  const first = await ui.find({ type: 'Input' })
  await ui.input({ key: first?.key ?? '', text: '第一題' })
  const second = await ui.find({ type: 'Input' })
  await ui.input({ key: second?.key ?? '', text: '第二題' })

  expect(prompts[1]).toContain('問：第一題')
  expect(prompts[1]).toContain('問題：第二題')
})

test('/side from the phone or web remote points to /btw instead of a pane', async ($, on) => {
  let opened = false
  on('ui.open', () => {
    opened = true
    return { value: { isPlaced: true } } as never
  })
  const kit = $ as unknown as { command: { run: (e: unknown) => Promise<{ text?: string }> } }
  const answer = await kit.command.run({
    command: 'side',
    args: '這是什麼',
    origin: { kind: 'bridge' },
    presentation: { isFullscreen: true, columns: 200 },
  })
  expect(answer.text).toBe('手機或遠端操作時請直接用 /btw。')
  expect(opened).toBe(false)
})

const SELF = '11111111-2222-3333-4444-555555555555'

function branching(on: On, turns: number, env: Record<string, string>) {
  const runs: { argv: readonly string[]; cwd?: string }[] = []
  const stored: [string, unknown][] = []
  const toasts: string[] = []
  engine(on)
  on('session.turns', () => ({ value: turns }) as never)
  on('session.id', () => ({ value: SELF }) as never)
  on('session.cwd', () => ({ value: 'C:\\work\\repo' }) as never)
  on('env.get', (_$, e) => ({ value: env[e.name] }) as never)
  on('clock.now', () => ({ value: Date.now() }) as never)
  on('store.set', (_$, e) => {
    stored.push([e.key, e.value])
    return { value: undefined } as never
  })
  on('ui.toast', (_$, e) => {
    toasts.push(e.text)
    return { value: undefined } as never
  })
  on('process.run', (_$, e) => {
    runs.push({ argv: e.argv, cwd: e.init?.cwd })
    return { value: { exitCode: 0, stdout: '', stderr: '', isStdoutTruncated: false, isStderrTruncated: false } }
  })
  return { runs, stored, toasts }
}

test('the pane opens a branch in a new window and leaves its id for it', async ($, on) => {
  const { runs, stored } = branching(on, 2, { OS: 'Windows_NT', USERPROFILE: 'C:\\Users\\me' })
  const ui = await mount($, { ...(PANE as object), surface: 'terminal' })
  await ui.press({ key: 'branch' })

  expect(runs[0]?.argv).toEqual(['wt.exe', '-w', 'new', 'new-tab', '-d', 'C:\\work\\repo', 'claude', '--resume', SELF, '--fork-session'])
  expect(runs[0]?.cwd).toBe('C:\\Users\\me')
  expect(stored[0]?.[0]).toBe('branchParent')
})

// `--resume` finds a session by its transcript, which is written with the
// first prompt: before that the new window would only say it found nothing.
test('before the first prompt there is nothing to branch, and no window opens', async ($, on) => {
  const { runs, stored, toasts } = branching(on, 0, { OS: 'Windows_NT' })
  const ui = await mount($, { ...(PANE as object), surface: 'terminal' })
  await ui.press({ key: 'branch' })

  expect(runs).toEqual([])
  expect(stored).toEqual([])
  expect(toasts[0]).toContain('先聊一輪')
})

test('off Windows, the branch button says what to run instead', async ($, on) => {
  const { runs, toasts } = branching(on, 1, { OS: 'Darwin' })
  const ui = await mount($, { ...(PANE as object), surface: 'terminal' })
  await ui.press({ key: 'branch' })

  expect(runs).toEqual([])
  expect(toasts[0]).toContain(`claude --resume ${SELF} --fork-session`)
})
