// A branch is a conversation forked into a new terminal window:
// `claude --resume <id> --fork-session`, in the folder it ran in. The copy
// gets a new id and the original is left as it was. The session that opens
// one leaves its own id in the store; the branch picks it up at start, so its
// 帶回主線 knows where to send.

// Store key: `{ id, at }`, the opener's session id and when it was left.
export const BRANCH_PARENT = 'branchParent'
// A branch window starts within seconds; anything older was left by a launch
// that never came up.
export const PARENT_FRESH_MS = 60_000

const SESSION_ID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

export const isSessionId = (id: string) => SESSION_ID.test(id)

// Windows Terminal, which takes the command after its own options. A `;` is
// its command separator, so one in the folder is escaped. Elsewhere there is
// no one terminal to ask, and the caller says what to run instead.
export function branchArgv(isWindows: boolean, sessionId: string, folder: string): string[] | null {
  if (!isWindows || !isSessionId(sessionId)) return null
  return ['wt.exe', '-w', 'new', 'new-tab', '-d', folder.replace(/;/g, '\\;'), 'claude', '--resume', sessionId, '--fork-session']
}

export const branchCommand = (sessionId: string, folder: string) =>
  `cd "${folder}" && claude --resume ${sessionId} --fork-session`
