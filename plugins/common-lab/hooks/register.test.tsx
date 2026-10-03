import { expect, mock, test } from 'claude-code/testing'
import type { On, PromptEditResult } from 'claude-code'

const SURFACES = ['terminal', 'desktop'] as const
// Only `hasSurvey` matters to the band; the rest of the site's props are the
// engine's and left to it.
const BAND = { plugin: 'common-lab', component: 'AbovePrompt', props: { hasSurvey: false } } as never

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
