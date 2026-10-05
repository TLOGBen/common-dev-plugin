import { atom, update } from 'claude-code'
import type { Register } from 'claude-code'

import { registerBar } from './bar/bar'
import { BRANCH_PARENT, isSessionId, PARENT_FRESH_MS } from './branch'
import { registerRecall } from './recall/recall'
import { registerSide, retireSideReplies } from './side/side'

// The same state the mods own, named here by literal reference: the scan reads
// a state ref only where its plugin and key are spelled out.
const recallQuery = atom({ plugin: 'common-mod', key: 'recallQuery' } as const, null)
const sideEntries = atom({ plugin: 'common-mod', key: 'sideEntries' } as const, [])
const branchParent = atom({ plugin: 'common-mod', key: 'branchParent' } as const, null)

// A plugin carries one hooks module, and that module registers an event once,
// so each mod hooks its own events and the shared ones live here. `$` never
// leaves this file: the mods hand over plain data.
export const register: Register = (on, options) => {
  // First: recall draws its band under what the bar draws.
  registerRecall(on, options)
  registerSide(on)
  registerBar(on)

  on('session.start', async ($, e, next) => {
    // A branch window, just opened: the id its opener left, taken once.
    const left = (await $.store.get(BRANCH_PARENT)) as { id?: unknown; at?: unknown } | undefined
    const self = await $.session.id()
    const isFresh = typeof left?.at === 'number' && (await $.clock.now()) - left.at < PARENT_FRESH_MS
    if (left && isFresh && typeof left.id === 'string' && isSessionId(left.id) && left.id !== self) {
      const parent = left.id
      await $.store.set(BRANCH_PARENT, null)
      await update($, branchParent, () => parent)
    }

    return next(e)
  })

  // A new or resumed conversation starts every mod afresh.
  on('command.run', { command: ['clear', 'resume'] }, async ($, e, next) => {
    const result = await next(e)
    retireSideReplies()
    await update($, sideEntries, () => [])
    await update($, recallQuery, () => null)

    return result
  })
}
