import { atom, read, update } from 'claude-code'
import type { EngineInterface, On } from 'claude-code'

import type { SideEntry } from '../../types'

const PANE = 'side'
const entries = atom({ plugin: 'common-mod', key: 'sideEntries' } as const, [])

// What a side question carries of the side chat before it: enough to follow
// up on, little enough that the fork stays cheap.
const HISTORY_TURNS = 6
const HISTORY_ANSWER_CHARS = 1500
const CARRY_BACK_CHARS = 600
const INLINE_ROWS = 24

const FRAME = [
  '[側聊] 使用者暫時離開主線，在旁邊開了一個側邊對話。',
  '主線的工作照舊，這裡不要接續主線、不要規劃下一步、不要使用任何工具，',
  '只就最後的問題回答；簡短直接，用使用者提問的語言。',
].join('')

const WHY: Record<string, string> = {
  'nothing-to-fork': '主對話還沒有任何回覆，等第一輪結束再問',
  'api-error': 'API 回了錯誤',
  'empty-reply': '回覆是空的',
  aborted: '被中斷了',
}

let nextId = 1
// Bumped when the pane closes or the conversation clears, so a reply still
// in flight from before lands nowhere.
let generation = 0

function historyOf(before: SideEntry[]) {
  return before
    .filter(entry => entry.answer?.isAnswered)
    .slice(0, HISTORY_TURNS)
    .reverse()
    .map(entry => {
      const answer = entry.answer?.isAnswered ? entry.answer.text : ''
      return `問：${entry.question}\n答：${answer.slice(0, HISTORY_ANSWER_CHARS)}`
    })
}

function promptOf(question: string, before: SideEntry[]) {
  const history = historyOf(before)
  return [FRAME, ...(history.length ? ['', '先前的側聊：', ...history] : []), '', `問題：${question}`].join('\n')
}

// The newest exchange sits at the bottom: once the pane has scrolled to its
// end it keeps following as the chat grows, until the person scrolls up.
async function followEnd($: EngineInterface) {
  await $.ui.scroll({ in: PANE, to: 'end' }).catch(() => undefined)
}

async function ask($: EngineInterface, question: string) {
  const text = question.trim()
  if (!text) return

  const before = await read($, entries)
  const entry: SideEntry = { id: nextId++, question: text }
  const asked = generation
  await update($, entries, list => [entry, ...list])
  await followEnd($)

  const reply = await $.model.fork({ prompt: promptOf(text, before) })
  if (asked !== generation) return

  const answer: SideEntry['answer'] = reply.isAnswered
    ? { isAnswered: true, text: reply.text }
    : { isAnswered: false, reason: WHY[reply.reason] ?? reply.reason }
  await update($, entries, list => list.map(one => (one.id === entry.id ? { ...one, answer } : one)))
  await followEnd($)
}

async function openPane($: EngineInterface, isDocked: boolean): Promise<string | null> {
  const opened = await $.ui.open({
    id: PANE,
    title: '側聊',
    focus: true,
    closeOnEscape: true,
    ...(isDocked ? {} : { rows: INLINE_ROWS }),
  })
  if (opened.isPlaced) {
    await followEnd($)
    return null
  }
  await $.ui.close({ id: PANE })
  return '終端機太窄，放不下側聊面板；把視窗拉寬一點再試。'
}

async function carryBack($: EngineInterface, entry: SideEntry) {
  if (!entry.answer?.isAnswered) return
  const answer = entry.answer.text.slice(0, CARRY_BACK_CHARS)
  const quoted = `側聊裡問了「${entry.question}」，得到：\n${answer}`
    .split('\n')
    .map(line => `> ${line}`)
    .join('\n')
  const box = await $.prompt.read()
  await $.prompt.fill({ text: `${box.text ? '\n' : ''}${quoted}\n`, mode: 'append' })
  $.ui.toast('已放進輸入框')
}

// A reply still in flight lands nowhere once its chat is gone.
export function retireSideReplies() {
  generation += 1
}

async function forget($: EngineInterface) {
  retireSideReplies()
  await update($, entries, () => [])
}

// Registered by the hooks module's entry, which owns the shared session.start.
export const SIDE_COMMAND = {
  name: 'side',
  description: '開一個側聊：問跟主線無關的事，主線照跑，關掉就消失',
  argumentHint: '[問題]',
}

export function registerSide(on: On) {
  on('command.run', { command: 'side' }, async ($, e) => {
    // From the phone or web remote the pane has no field to type into; /btw
    // already covers it there.
    if (e.origin.kind === 'bridge') {
      return { text: '手機或遠端操作時請直接用 /btw。' }
    }

    const arg = e.args.trim()
    const why = await openPane($, e.presentation.isFullscreen)
    if (why) return { text: why }
    if (arg) void ask($, arg).catch(() => undefined)

    return {}
  })

  // Closing is the end of the side chat: nothing of it outlives the pane.
  on('ui.close', { id: PANE }, async ($, e, next) => {
    const result = await next(e)
    if (result.deny === undefined) await forget($)

    return result
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const els = $.ui.resolve(e)
    const { Box, Text, Button, Markdown } = els
    const list = await read($, entries)
    const isAsking = list.some(entry => !entry.answer)

    const field =
      'Input' in els ? (
        <els.Input
          key={`ask-${nextId}`}
          autoFocus
          placeholder={isAsking ? '上一題還在想，也可以先問下一題' : '問點別的，主線不會被打斷'}
          submitLabel="問"
          onSubmit={(value: string) => void ask($, value).catch(() => undefined)}
        />
      ) : (
        <Text dimColor>這個介面沒有輸入框，請改用 /btw。</Text>
      )

    return (
      <Box flexDirection="column" gap={1} paddingX={1}>
        {list.length === 0 && (
          <Text dimColor>
            答案只看得到主對話到目前為止的內容，不會用工具、不會動檔案，也不會寫進主對話。
          </Text>
        )}

        {[...list].reverse().map(entry => (
          <Box key={`entry-${entry.id}`} flexDirection="column">
            <Text bold>› {entry.question}</Text>
            {!entry.answer && <Text dimColor>正在想…</Text>}
            {entry.answer && !entry.answer.isAnswered && (
              <Text dimColor>沒有回答：{entry.answer.reason}</Text>
            )}
            {entry.answer?.isAnswered && (
              <Box flexDirection="column">
                <Markdown key={`answer-${entry.id}`} text={entry.answer.text} />
                <Box>
                  <Button
                    key={`carry-${entry.id}`}
                    plain
                    dimColor
                    label="帶回主對話"
                    onPress={() => void carryBack($, entry).catch(() => undefined)}
                  />
                </Box>
              </Box>
            )}
          </Box>
        ))}

        {field}

        <Text dimColor>Esc 回到主線；面板一關，這些側聊就不見了。</Text>
      </Box>
    )
  })
}
