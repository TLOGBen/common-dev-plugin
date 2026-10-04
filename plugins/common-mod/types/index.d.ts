export type RecallSource = 'code' | 'desktop' | 'cowork' | 'ssh'

export type RecallSession = {
  id: string
  file: string
  source: RecallSource
  project: string
  title: string
  first: string | null
  last: string | null
  prompts: string[]
  days: Record<string, number>
  answer: string
}

export type SideEntry = {
  id: number
  /** What the row shows: the typed question, or 「看不懂：…」／「畫給我看：…」. */
  question: string
  /** The reply, or why there is none; absent while it is being asked. */
  answer?: { isAnswered: true; text: string } | { isAnswered: false; reason: string }
}

declare module 'claude-code' {
  interface PluginState {
    'common-mod': {
      /** recall: the text after `@@` at the caret while one is being typed. */
      recallQuery: string | null
      /** recall: the session the pane previews. */
      recallPicked: string | null
      /** recall: when the index was last loaded, 0 before the first scan. */
      recallBuiltAt: number
      /** side: newest first; gone when the pane closes. */
      sideEntries: SideEntry[]
    }
  }
}
