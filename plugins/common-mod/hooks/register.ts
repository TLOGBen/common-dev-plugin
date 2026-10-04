import { atom, update } from 'claude-code'
import type { Register } from 'claude-code'

import { RECALL_COMMAND, registerRecall } from './recall/recall'
import { registerSide, retireSideReplies, SIDE_COMMAND } from './side/side'

// The same state the mods own, named here by literal reference: the scan reads
// a state ref only where its plugin and key are spelled out.
const recallQuery = atom({ plugin: 'common-mod', key: 'recallQuery' } as const, null)
const recallPicked = atom({ plugin: 'common-mod', key: 'recallPicked' } as const, null)
const sideEntries = atom({ plugin: 'common-mod', key: 'sideEntries' } as const, [])

// A plugin carries one hooks module, and that module registers an event once,
// so each mod hooks its own events and the shared ones live here. `$` never
// leaves this file: the mods hand over plain data (command specs).
export const register: Register = (on, options) => {
  registerRecall(on, options)
  registerSide(on)

  on('session.start', async ($, e, next) => {
    await $.command.register(RECALL_COMMAND)
    await $.command.register(SIDE_COMMAND)

    return next(e)
  })

  // A new or resumed conversation starts every mod afresh.
  on('command.run', { command: ['clear', 'resume'] }, async ($, e, next) => {
    const result = await next(e)
    retireSideReplies()
    await update($, sideEntries, () => [])
    await update($, recallQuery, () => null)
    await update($, recallPicked, () => null)

    return result
  })
}
