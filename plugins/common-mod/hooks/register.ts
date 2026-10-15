import { atom, update } from 'claude-code'
import type { Register } from 'claude-code'

import { registerBar } from './bar/bar'
import { registerRecall } from './recall/recall'

// The same state the mods own, named here by literal reference: the scan reads
// a state ref only where its plugin and key are spelled out.
const recallQuery = atom({ plugin: 'common-mod', key: 'recallQuery' } as const, null)

// A plugin carries one hooks module, and that module registers an event once,
// so each mod hooks its own events and the shared ones live here. `$` never
// leaves this file: the mods hand over plain data.
export const register: Register = (on, options) => {
  // First: recall draws its band under what the bar draws.
  registerRecall(on, options)
  registerBar(on)

  // A new or resumed conversation starts every mod afresh.
  on('command.run', { command: ['clear', 'resume'] }, async ($, e, next) => {
    const result = await next(e)
    await update($, recallQuery, () => null)

    return result
  })
}
