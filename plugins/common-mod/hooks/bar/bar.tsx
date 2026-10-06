import { atom, read, update } from 'claude-code'
import type { EngineInterface, On } from 'claude-code'

import { SIDE_PANE, SIDE_TOO_NARROW } from '../side/side'
import { actionsFor } from './actions'
import type { Action, Hands } from './actions'
import { drawDesktop } from './desktop'
import {
  absorbUsage,
  advance,
  BRING_BACK,
  folderOf,
  NEXT_QUESTION,
  recordTokens,
  state,
  suggestionsOf,
} from './model'
import type { Next, Suggestion, Usage } from './model'
import { drawTerminal } from './terminal'

export { ESCAPES, TAGS } from './model'

// The status line above the prompt. The model (model.ts), the list of buttons
// (actions.ts) and the two drawings (terminal.tsx, desktop.tsx) are plain
// code; this file is the only one that talks to the engine, since `$` never
// crosses an import. Each surface draws the same model its own way, so the
// terminal's look and the desktop's never touch.

// Recall's band opens and closes on this; the session this one branched from.
const recallQuery = atom({ plugin: 'common-mod', key: 'recallQuery' } as const, null)
const branchParent = atom({ plugin: 'common-mod', key: 'branchParent' } as const, null)

const FRAME_MS = 33
const COUNTDOWN_MS = 30_000

let started = false
// Nerd Font glyphs on the terminal; read from the store on its first drawing.
let nerd: boolean | null = null
// Bumped by every ask and every new turn, so a late answer lands nowhere.
let asking = 0

async function absorb($: EngineInterface, usage: Usage) {
  absorbUsage(usage, Number(await $.env.get('CLAUDE_CODE_AUTO_COMPACT_WINDOW')))
}

async function locate($: EngineInterface) {
  const home = ((await $.env.get('USERPROFILE')) ?? (await $.env.get('HOME')) ?? '').replace(/[\\/]+$/, '')
  state.folder = folderOf(await $.session.cwd(), home)
}

// A failed list draws every button rather than none.
async function learnCommands($: EngineInterface) {
  const commands = await $.command.list().catch(() => null)
  state.known = commands === null ? null : new Set(commands.map(c => c.name))
}

function showNext($: EngineInterface, view: Next) {
  state.nextView = view
  $.ui.invalidate('ui.render')
}

async function askNext($: EngineInterface) {
  const asked = ++asking
  showNext($, { kind: 'loading' })
  let items: Suggestion[] = []
  try {
    await learnCommands($)
    const reply = await $.model.fork({ prompt: NEXT_QUESTION })
    items = reply.isAnswered ? suggestionsOf(reply.text, state.known) : []
  } catch {
    // Said below as no suggestion.
  }
  if (asked !== asking) return
  showNext($, items.length > 0 ? { kind: 'offer', items } : { kind: 'hidden' })
  if (items.length === 0) $.ui.toast('想不到下一步可以做什麼')
}

async function pickNext($: EngineInterface, item: Suggestion) {
  showNext($, { kind: 'hidden' })
  const filled = await $.prompt.fill({ text: item.prompt }).catch(() => null)
  if (!filled?.isFilled) $.ui.toast('沒辦法放進輸入框')
}

async function bringBack($: EngineInterface, to: string) {
  $.ui.toast('正在整理分支的進展…')
  const reply = await $.model.fork({ prompt: BRING_BACK })
  if (!reply.isAnswered) {
    $.ui.toast(reply.reason === 'nothing-to-fork' ? '分支裡還沒有回覆，先聊一輪再帶回' : `沒辦法整理：${reply.reason}`)
    return
  }
  const sent = await $.session.send({ to: { sessionId: to }, text: `[分支回報]\n${reply.text}` })
  $.ui.toast(sent.isDelivered ? '已送回主線' : `送不回主線：${sent.reason}`)
}

async function openSide($: EngineInterface) {
  const opened = await $.ui.open(SIDE_PANE)
  if (!opened.isPlaced) $.ui.toast(SIDE_TOO_NARROW)
}

// What each button does. Most run the command a person would type, so each
// opens what that command opens, the way it does. 側聊 and 回想 are this
// plugin's own, which its `$.command.run` does not reach, so they act here.
async function act($: EngineInterface, action: Action, parent: string | null) {
  switch (action.key) {
    case 'side':
      return openSide($)
    case 'recall':
      return update($, recallQuery, q => (q === null ? '' : null))
    case 'next':
      return askNext($)
    case 'back':
      return parent === null ? undefined : bringBack($, parent)
    default:
      if (action.command !== undefined) await $.command.run({ command: action.command })
  }
}

// A press that fails says so, rather than doing nothing.
function press($: EngineInterface, action: Action, parent: string | null) {
  void act($, action, parent).catch(err => $.ui.toast(`${action.label}：${err instanceof Error ? err.message : String(err)}`))
}

async function toggleGlyphs($: EngineInterface) {
  nerd = !nerd
  $.ui.invalidate('ui.render')
  await $.store.set('barGlyphs', nerd)
}

// Loaded on the first drawing, not at session.start: that event is the entry
// module's, and a mod that fails to read here still draws what it has.
async function start($: EngineInterface) {
  if (started) return
  started = true
  try {
    await absorb($, await $.session.usage())
    state.model = await $.session.model()
    await locate($)
    await learnCommands($)
  } catch {
    // Figures arrive with the next session.measure.
  }
  $.clock.every(FRAME_MS, () => {
    if (advance()) $.ui.invalidate('ui.render')
  })
  $.clock.every(COUNTDOWN_MS, () => $.ui.invalidate('ui.render'))
}

// One reading per main-loop turn; the command list too, since a turn can
// install or reload plugins.
async function recordTurn($: EngineInterface) {
  await learnCommands($)
  try {
    await absorb($, await $.session.usage())
  } catch {
    return
  }
  if (recordTokens()) $.ui.invalidate('ui.render')
}

export function registerBar(on: On) {
  on('session.measure', async ($, e, next) => {
    await absorb($, e)
    $.ui.invalidate('ui.render')

    return next(e)
  })

  // The effort rides on each model request; the model's name, as /model shows it.
  on('turn.step', async function* ($, e, next) {
    const was = `${state.model}|${state.effort}`
    state.effort = e.effort === undefined ? '' : String(e.effort)
    state.model = await $.session.model().catch(() => state.model)
    if (`${state.model}|${state.effort}` !== was) $.ui.invalidate('ui.render')

    yield* next(e)
  })

  // A new turn puts away suggestions made for the last one.
  on('turn.start', async ($, e, next) => {
    asking += 1
    if (state.nextView.kind !== 'hidden') showNext($, { kind: 'hidden' })

    return next(e)
  })

  // One reading per main-loop turn; a subagent's turns are not the session's.
  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    if (!e.agentId) await recordTurn($)

    return result
  })

  // Registered after recall's, which draws its band under this one.
  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey) return next(e)
    await start($)
    state.isWorking = e.props.isWorking
    state.seen.add(e.surface)
    const parent = await read($, branchParent)
    const hands: Hands = {
      now: await $.clock.now(),
      buttons: actionsFor(e.surface, state.known, parent !== null).map(a => ({ ...a, onPress: () => press($, a, parent) })),
      pick: item => void pickNext($, item).catch(() => undefined),
      hideNext: () => showNext($, { kind: 'hidden' }),
    }

    if (e.surface === 'terminal') {
      if (nerd === null) nerd = (await $.store.get('barGlyphs').catch(() => false)) === true
      const glyphs = nerd
      return drawTerminal($.ui.resolve(e), {
        ...hands,
        bodyColumns: e.props.bodyColumns,
        nerd: glyphs,
        toggleGlyphs: () => void toggleGlyphs($).catch(() => undefined),
      })
    }
    if (e.surface === 'desktop' || e.surface === 'vscode') {
      return drawDesktop($.ui.resolve(e), { ...hands, bodyColumns: e.props.bodyColumns })
    }
    return next(e)
  })
}
