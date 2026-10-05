// The indexer runs under the host's node (fed on stdin), because a session log
// can be tens of MB and the hooks module only reads whole files. It keeps a
// cache keyed by size + mtime so a rescan touches only the sessions that grew,
// writes the index next to the cache and prints that path on stdout.

// What the script reads a transcript line by.
const COMMON = String.raw`
const fs = require('fs')
const os = require('os')
const path = require('path')
const readline = require('readline')

const clip = (s, n) => {
  const one = s.replace(/\s+/g, ' ').trim()
  return one.length > n ? one.slice(0, n - 1) + '…' : one
}

const promptText = msg => {
  if (!msg || msg.role !== 'user') return null
  const c = msg.content
  const text = typeof c === 'string'
    ? c
    : Array.isArray(c) ? c.filter(b => b && b.type === 'text').map(b => b.text).join(' ') : ''
  if (!text || text.startsWith('<') || text.startsWith('[Request interrupted')) return null
  return text
}

const answerText = msg =>
  msg && Array.isArray(msg.content)
    ? msg.content.filter(b => b.type === 'text').map(b => b.text).join('\n').trim()
    : ''
`

export const INDEXER = String.raw`
${COMMON}
const HOME_ROOT = path.join(os.homedir(), '.claude', 'projects')
const ROOTS = [HOME_ROOT, ...process.argv.slice(2)]
const OUT = path.join(os.homedir(), '.claude', 'recall-index.json')
const MAX_PROMPTS = 60
const CLIP = 160

// Cowork and desktop scratch sessions live beside the CLI ones; the folder
// name is the only thing that tells them apart.
const sourceOf = dir =>
  dir.includes('scratch-workspaces') ? 'cowork' : dir.startsWith('ssh-') ? 'ssh' : 'code'

const projectOf = (dir, cwd) => {
  if (sourceOf(dir) === 'cowork') return 'Cowork'
  if (cwd) return path.basename(cwd.replace(/[\\/]+$/, '')) || cwd
  return dir
}

async function scan(file, dir, root) {
  const s = { prompts: [], days: {}, title: null, cwd: null, first: null, last: null, answer: '' }
  const rl = readline.createInterface({ input: fs.createReadStream(file), crlfDelay: Infinity })
  for await (const line of rl) {
    if (!line) continue
    let r
    try { r = JSON.parse(line) } catch { continue }
    if (r.type === 'custom-title' && r.customTitle) s.title = r.customTitle
    if (r.cwd && !s.cwd) s.cwd = r.cwd
    if (r.entrypoint && !s.entry) s.entry = r.entrypoint
    if (r.isSidechain) continue
    if (r.type === 'user' && !r.isMeta) {
      const t = promptText(r.message)
      if (t) {
        if (s.prompts.length < MAX_PROMPTS) s.prompts.push(clip(t, CLIP))
        if (r.timestamp) {
          s.first = s.first || r.timestamp
          s.last = r.timestamp
          const day = r.timestamp.slice(0, 10)
          s.days[day] = (s.days[day] || 0) + 1
        }
      }
    }
    if (r.type === 'assistant') {
      const t = answerText(r.message)
      if (t) s.answer = t
    }
  }
  // SDK runs are other tools driving Claude (reviews, graders), not your chats
  if (!s.prompts.length || (s.entry || '').startsWith('sdk')) return null
  const source = sourceOf(dir) === 'code' && s.entry === 'claude-desktop' ? 'desktop' : sourceOf(dir)
  return {
    id: path.basename(file, '.jsonl'),
    file,
    source,
    project: projectOf(dir, s.cwd),
    cwd: s.cwd,
    // Only this machine's own Claude Code can resume it: not an extra root
    // (another machine's or WSL's copy) and not a Cowork scratch session.
    isLocal: root === HOME_ROOT && source !== 'cowork',
    title: clip(s.title || s.prompts[0], 60),
    first: s.first,
    last: s.last,
    prompts: s.prompts,
    days: s.days,
    answer: s.answer.length > 900 ? s.answer.slice(-900) : s.answer,
  }
}

;(async () => {
  let cache = {}
  try { for (const e of JSON.parse(fs.readFileSync(OUT, 'utf8')).sessions) cache[e.file] = e } catch {}
  const sessions = []
  const files = []
  for (const root of ROOTS) {
    let dirs = []
    try { dirs = fs.readdirSync(root) } catch { continue }
    for (const dir of dirs) {
      let names = []
      try { names = fs.readdirSync(path.join(root, dir)).filter(n => n.endsWith('.jsonl')) } catch { continue }
      for (const name of names) files.push({ file: path.join(root, dir, name), dir, root })
    }
  }
  for (const { file, dir, root } of files) {
    const st = fs.statSync(file)
    const old = cache[file]
    // An entry from before isLocal was kept is read again.
    if (old && old.size === st.size && old.mtimeMs === st.mtimeMs && 'isLocal' in old) { sessions.push(old); continue }
    const e = await scan(file, dir, root).catch(() => null)
    if (e) sessions.push({ ...e, size: st.size, mtimeMs: st.mtimeMs })
  }
  sessions.sort((a, b) => (b.last || '').localeCompare(a.last || ''))
  // Same contents as the transcripts it reads, so the same owner-only reach
  fs.writeFileSync(OUT, JSON.stringify({ builtAt: Date.now(), sessions }), { mode: 0o600 })
  process.stdout.write(OUT)
})()
`

