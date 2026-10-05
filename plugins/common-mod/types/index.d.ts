export type RecallSource = 'code' | 'desktop' | 'cowork' | 'ssh'

export type RecallSession = {
  id: string
  file: string
  source: RecallSource
  project: string
  /** The folder it ran in, where a branch of it starts. */
  cwd: string | null
  /** Whether this machine's Claude Code can resume it. */
  isLocal: boolean
  title: string
  first: string | null
  last: string | null
  prompts: string[]
  days: Record<string, number>
  answer: string
}

export type SideEntry = {
  id: number
  /** What the row shows: the typed question. */
  question: string
  /** The reply, or why there is none; absent while it is being asked. */
  answer?: { isAnswered: true; text: string } | { isAnswered: false; reason: string }
}

declare module 'claude-code' {
  interface PluginState {
    'common-mod': {
      /** recall: the search text while the band is open; null when it is closed. */
      recallQuery: string | null
      /** recall: the session the band previews. */
      recallPicked: string | null
      /** recall: when the index was last loaded, 0 before the first scan. */
      recallBuiltAt: number
      /** side: newest first; gone when the pane closes. */
      sideEntries: SideEntry[]
      /** bar: the session this branch was opened from; null when it is no branch. */
      branchParent: string | null
    }
  }
}
