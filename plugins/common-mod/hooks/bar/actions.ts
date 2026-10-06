import type { RenderSurface } from 'claude-code'

import type { Suggestion } from './model'

// The bar's buttons, for every surface. Each says where it is drawn: diff and
// artifacts open terminal dialogs, which the desktop does not show (it has
// its own diff entry). One that runs a command is drawn only while the
// session has that command. What a press does lives in bar.tsx, with `$`.
export type Action = {
  key: string
  label: string
  group: 'view' | 'ask'
  surfaces: readonly RenderSurface[]
  command?: string
}

const ALL: readonly RenderSurface[] = ['terminal', 'desktop', 'vscode']

export const ACTIONS: readonly Action[] = [
  { key: 'side', label: '側聊', group: 'view', surfaces: ALL },
  { key: 'recall', label: '回想', group: 'view', surfaces: ALL },
  { key: 'diff', label: 'diff', group: 'view', surfaces: ['terminal'], command: 'diff' },
  { key: 'artifacts', label: 'artifacts', group: 'view', surfaces: ['terminal'], command: 'artifacts' },
  { key: 'explain', label: '看不懂', group: 'ask', surfaces: ALL, command: 'common:wait-what' },
  { key: 'draw', label: '畫給我看', group: 'ask', surfaces: ALL, command: 'common:show-me' },
  { key: 'next', label: '下一步', group: 'ask', surfaces: ALL },
  { key: 'back', label: '帶回主線', group: 'ask', surfaces: ALL },
]

// The buttons a surface draws now; a failed command list draws them all, and
// 帶回主線 shows only in a branch window.
export function actionsFor(surface: RenderSurface, known: ReadonlySet<string> | null, isBranch: boolean) {
  return ACTIONS.filter(
    a =>
      a.surfaces.includes(surface) &&
      (a.command === undefined || known === null || known.has(a.command)) &&
      (a.key !== 'back' || isBranch),
  )
}

// What a drawing gets besides the model: the time, the buttons with their
// presses already bound, and what picking or putting away a next step does.
export type Pressable = Action & { onPress: () => void }
export type Hands = {
  now: number
  buttons: readonly Pressable[]
  // What a press just sent, while its turn has not started answering.
  pending: string | null
  pick: (item: Suggestion) => void
  hideNext: () => void
}
