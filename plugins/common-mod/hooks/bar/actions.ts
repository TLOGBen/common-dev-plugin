import type { RenderSurface } from 'claude-code'

import type { Suggestion } from './model'

// The bar's buttons, for every surface. Each says where it is drawn: diff and
// artifacts open terminal dialogs, which the desktop does not show (it has
// its own diff entry). One that runs a command names the commands that can
// serve it, first choice first, and runs the first the session has: the
// plugin's own skill, else a project's skill of the same name. With none of
// them it is not drawn. `fill` puts `/command ` in the prompt box instead of
// running it, for a command that needs words after it. What a press does
// lives in bar.tsx, with `$`.
export type Action = {
  key: string
  label: string
  group: 'view' | 'ask' | 'project'
  surfaces: readonly RenderSurface[]
  commands?: readonly string[]
  fill?: boolean
  // A project button's own icon (an emoji, say); the built-in ones have theirs
  // in each drawing.
  icon?: string
}

// An action as drawn: `command` is the one of its commands the session has.
export type Drawn = Action & { command?: string }

const ALL: readonly RenderSurface[] = ['terminal', 'desktop', 'vscode']

export const ACTIONS: readonly Action[] = [
  { key: 'side', label: '側聊', group: 'view', surfaces: ALL },
  { key: 'recall', label: '回想', group: 'view', surfaces: ALL },
  { key: 'diff', label: 'diff', group: 'view', surfaces: ['terminal'], commands: ['diff'] },
  { key: 'artifacts', label: 'artifacts', group: 'view', surfaces: ['terminal'], commands: ['artifacts'] },
  { key: 'explain', label: '看不懂', group: 'ask', surfaces: ALL, commands: ['common:wait-what', 'wait-what'] },
  { key: 'draw', label: '畫給我看', group: 'ask', surfaces: ALL, commands: ['common:show-me', 'show-me'] },
  { key: 'next', label: '下一步', group: 'ask', surfaces: ALL },
  { key: 'back', label: '帶回主線', group: 'ask', surfaces: ALL },
]

// A project's own buttons, from its .claude/common-mod.json:
//   { "buttons": [{ "label": "SA 怎麼說", "command": "sa-align", "fill": true, "icon": "📄" }] }
// Anything malformed is left out; a label is kept short enough for a button,
// an icon to a few visible characters.
const LABEL_MAX = 12
const ICON_MAX = 8
const COMMAND = /^[\w.-]+(:[\w.-]+)?$/
const CONTROL = /[\p{Cc}\p{Cf}]/u

export function projectActions(text: string): Action[] {
  let parsed: unknown
  try {
    parsed = JSON.parse(text)
  } catch {
    return []
  }
  const buttons = (parsed as { buttons?: unknown })?.buttons
  if (!Array.isArray(buttons)) return []
  const actions: Action[] = []
  for (const b of buttons as { label?: unknown; command?: unknown; fill?: unknown; icon?: unknown }[]) {
    if (typeof b?.label !== 'string' || typeof b.command !== 'string') continue
    const label = b.label.trim()
    const command = b.command.trim().replace(/^\//, '')
    if (!label || [...label].length > LABEL_MAX || CONTROL.test(label) || !COMMAND.test(command)) continue
    const icon = typeof b.icon === 'string' ? b.icon.trim() : ''
    actions.push({
      key: `project-${actions.length}`,
      label,
      group: 'project',
      surfaces: ALL,
      commands: [command],
      fill: b.fill === true,
      ...(icon && icon.length <= ICON_MAX && !/[\p{Cc}]/u.test(icon) ? { icon } : {}),
    })
  }
  return actions
}

// The buttons a surface draws now; a failed command list draws them all (on
// their first choice), and 帶回主線 shows only in a branch window.
export function actionsFor(
  surface: RenderSurface,
  known: ReadonlySet<string> | null,
  isBranch: boolean,
  project: readonly Action[] = [],
): Drawn[] {
  const drawn: Drawn[] = []
  for (const a of [...ACTIONS, ...project]) {
    if (!a.surfaces.includes(surface) || (a.key === 'back' && !isBranch)) continue
    if (a.commands === undefined) {
      drawn.push(a)
      continue
    }
    const command = known === null ? a.commands[0] : a.commands.find(c => known.has(c))
    if (command !== undefined) drawn.push({ ...a, command })
  }
  return drawn
}

// What a drawing gets besides the model: the time, the buttons with their
// presses already bound, and what picking or putting away a next step does.
export type Pressable = Drawn & { onPress: () => void }
export type Hands = {
  now: number
  buttons: readonly Pressable[]
  // What a press just sent, while its turn has not started answering.
  pending: string | null
  pick: (item: Suggestion) => void
  hideNext: () => void
}
