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

declare module 'claude-code' {
  interface PluginState {
    'common-lab': {
      /** recall: the text after `@@` at the caret while one is being typed. */
      recallQuery: string | null
      /** recall: the session the pane previews. */
      recallPicked: string | null
      /** recall: when the index was last loaded, 0 before the first scan. */
      recallBuiltAt: number
    }
  }
}
