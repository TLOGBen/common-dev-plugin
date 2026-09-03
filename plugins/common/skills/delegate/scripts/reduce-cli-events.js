// Keep the delegation CLI's JSONL in local scratch; emit only low-frequency milestone
// summaries and exceptional control signals. What reaches the lead context is the
// milestone message itself (sidekick self-report, in-progress todo, changed filenames,
// failed verification command, stall notice) — never an action label.
const fs = require('fs');
const path = require('path');
const readline = require('readline');

function readArg(name) {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] : undefined;
}

const provider = readArg('--provider');
const rawPath = readArg('--raw');
const finalPath = readArg('--final');
const cleanup = process.argv.includes('--cleanup');
const heartbeatMs = Math.max(10, Number(readArg('--heartbeat-ms')) || 60000);
// Replay verification: ignore the wall clock and treat every N events as one heartbeat.
const replayTick = Math.max(0, Number(readArg('--replay-tick')) || 0);

// Only this many consecutive event-free heartbeats counts as a stall.
const STALL_FLUSHES = 5;

if (!rawPath || !finalPath) {
  console.error('delegate: --raw <path> and --final <path> are required');
  process.exit(2);
}

const rawFile = path.resolve(rawPath);
const finalFile = path.resolve(finalPath);
const scratchDir = path.dirname(rawFile);
const markerPath = path.join(scratchDir, '.delegate-cli-scratch');
const sessionPath = path.join(scratchDir, 'session-id.txt');

if (scratchDir !== path.dirname(finalFile)) {
  console.error('delegate: --raw and --final must live in the same dedicated scratch directory');
  process.exit(2);
}

if (cleanup) {
  if (!fs.existsSync(markerPath)) {
    console.error('delegate: refusing to clean an unmarked directory');
    process.exit(2);
  }
  fs.rmSync(scratchDir, { recursive: true, force: true });
  process.exit(0);
}

if (!['codex', 'claude'].includes(provider)) {
  console.error('delegate: --provider <codex|claude> is required');
  process.exit(2);
}

fs.mkdirSync(scratchDir, { recursive: true });
fs.writeFileSync(markerPath, 'delegate\n', 'utf8');
fs.writeFileSync(rawFile, '', 'utf8');

let terminal = false;
let pendingSummary = '';
let lastPrintedSummary = '';
let todoSignature = '';
let eventsSinceFlush = 0;
let idleFlushes = 0;

const startedAt = Date.now();
let replayEvents = 0;
let replayFlushes = 0;

function elapsed() {
  const ms = replayTick ? replayFlushes * heartbeatMs : Date.now() - startedAt;
  const total = Math.floor(ms / 1000);
  const mm = Math.floor(total / 60);
  const ss = total % 60;
  return `${String(mm).padStart(2, '0')}:${String(ss).padStart(2, '0')}`;
}

function cleanText(text, max = 60) {
  const clean = String(text == null ? '' : text)
    .replace(/[\r\n|｜]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  return clean.length > max ? `${clean.slice(0, max)}…` : clean;
}

function saveSessionId(value) {
  const sessionId = String(value || '').trim();
  if (sessionId) fs.writeFileSync(sessionPath, sessionId, 'utf8');
}

function setSummary(text) {
  const summary = cleanText(text, 80);
  if (summary) pendingSummary = summary;
}

// Exceptional signals bypass throttling and must not overwrite throttle state,
// otherwise a pending summary would be reprinted.
function emitNow(text) {
  if (terminal) return;
  process.stdout.write(`[${elapsed()}] ${cleanText(text, 80)}\n`);
}

function emitSummary() {
  if (replayTick) replayFlushes += 1;
  const hadEvents = eventsSinceFlush > 0;
  eventsSinceFlush = 0;

  if (!terminal && pendingSummary && pendingSummary !== lastPrintedSummary) {
    process.stdout.write(`[${elapsed()}] ${pendingSummary}\n`);
    lastPrintedSummary = pendingSummary;
    idleFlushes = 0;
    return;
  }

  // A stall means no new events at all — events that were merely filtered out do not count.
  if (hadEvents) {
    idleFlushes = 0;
    return;
  }
  idleFlushes += 1;
  if (idleFlushes % STALL_FLUSHES === 0) {
    const minutes = Math.round((idleFlushes * heartbeatMs) / 60000);
    emitNow(`⏸ no activity for ${minutes} min · last: ${lastPrintedSummary || 'no summary yet'}`);
  }
}

function emitControl(kind, detail) {
  const summary = cleanText(detail, 60);
  process.stdout.write(`${kind}${summary ? `｜${summary}` : ''}\n`);
}

function extractQuestion(text) {
  const match = String(text || '').match(/(?:^|\r?\n)question:\s*(.+)/i);
  return match ? match[1] : 'user decision required';
}

function isWaiting(text) {
  return /(^|\r?\n)status:\s*WAITING_USER\b/m.test(String(text || ''));
}

// Strip the pwsh/bash wrapper and leftover nested quotes, leaving only the real command.
function stripShell(command) {
  let value = String(command || '').trim();
  const shell = value.match(/^"?[^"]*(?:pwsh|powershell|bash|sh|cmd)(?:\.exe)?"?\s+(?:-Command|-c|\/c)\s+([\s\S]+)$/i);
  if (shell) value = shell[1].trim();
  const quoted = value.match(/^(['"])([\s\S]*)\1$/);
  if (quoted) value = quoted[2].trim();
  value = value.replace(/^['"]\s*/, '').replace(/\s*['"]$/, '');
  return value.replace(/'"'/g, "'").replace(/"'/g, "'");
}

// For a multi-line inline script, print only the first line plus a line count, so the
// whole script never floods the summary.
function shortCommand(command) {
  const lines = String(command || '').split(/\r?\n/).map(item => item.trim()).filter(Boolean);
  if (lines.length <= 1) return lines[0] || '';
  return `${lines[0]} …(${lines.length}-line script)`;
}

function isVerifyCommand(command) {
  return /\b(dotnet\s+(test|build)|eslint|npm\s+run|pytest|node\s+--check)\b/i.test(String(command || ''));
}

// Process commands (file reads, searches, git) never reach the lead context;
// verification commands are reported only when they fail.
function describeCommand(command, exitCode, status) {
  const failed = Boolean(exitCode) || status === 'failed';
  if (!failed || !isVerifyCommand(command)) return '';
  return `✗(${exitCode == null ? '?' : exitCode}) ${shortCommand(command)}`;
}

function fileNames(changes) {
  const list = [];
  const entries = Array.isArray(changes)
    ? changes
    : Object.keys(changes || {}).map(key => ({ path: key }));
  for (const entry of entries) {
    const target = typeof entry === 'string' ? entry : entry && entry.path;
    if (target) list.push(path.basename(String(target).replace(/\\/g, '/')));
  }
  if (!list.length) return '';
  // ± is the one file-change marker kept: without it filenames blur into surrounding prose.
  if (list.length <= 2) return `± ${list.join(', ')}`;
  return `± ${list[0]} (${list.length} files)`;
}

// Todos are queued only when the in-progress item changes, so the same list never spams;
// an all-complete list prints nothing.
function todoSummary(items) {
  const list = Array.isArray(items) ? items : [];
  if (!list.length) return '';
  const done = list.filter(item => item && item.completed).length;
  const current = list.find(item => item && !item.completed);
  const signature = `${done}/${list.length}|${current ? current.text : 'done'}`;
  if (signature === todoSignature) return '';
  todoSignature = signature;
  return current ? cleanText(current.text, 80) : '';
}

function firstSentence(text) {
  const value = String(text || '');
  return value.split(/(?<=[。！？!?])\s*/)[0] || value;
}

function describeCodexItem(item) {
  switch (item.type) {
    case 'agent_message':
      return firstSentence(item.text);
    case 'command_execution':
      return describeCommand(stripShell(item.command), item.exit_code, item.status);
    case 'file_change':
      return fileNames(item.changes);
    case 'todo_list':
      return todoSummary(item.items);
    default:
      return '';
  }
}

function finishResult(result, isError) {
  terminal = true;
  if (isError) {
    emitControl('FAIL', 'CLI returned an error');
    process.exitCode = 1;
  } else if (isWaiting(result)) {
    emitControl('WAIT', extractQuestion(result));
  }
}

function handleCodex(event) {
  if (terminal) return;
  const type = String(event.type || 'unknown');
  const item = event.item || {};
  if (type === 'thread.started') {
    saveSessionId(event.thread_id);
  } else if (type.includes('failed') || type === 'error') {
    terminal = true;
    emitControl('FAIL', 'CLI execution failed');
    process.exitCode = 1;
  } else if (type === 'item.completed') {
    setSummary(describeCodexItem(item));
  } else if ((type === 'item.started' || type === 'item.updated') && item.type === 'todo_list') {
    // Todos already carry progress meaning at started/updated; every other type is taken
    // only at completed, to avoid duplicates.
    setSummary(todoSummary(item.items));
  }
}

function claudeToolDetail(block) {
  const name = String(block.name || '');
  const input = block.input && typeof block.input === 'object' ? block.input : {};
  const base = value => path.basename(String(value).replace(/\\/g, '/'));
  if (name === 'Write' || name === 'Edit' || name === 'NotebookEdit') {
    const target = base(input.file_path || input.notebook_path || '');
    return target ? `± ${target}` : '';
  }
  if (name === 'TodoWrite') {
    return todoSummary((input.todos || []).map(todo => ({
      text: todo.content || todo.activeForm,
      completed: todo.status === 'completed',
    })));
  }
  // Bash is reported only on a failed verification, as judged by tool_result;
  // no other tool ever reaches the lead context.
  return '';
}

function handleClaude(event) {
  if (terminal) return;
  const type = String(event.type || 'unknown');
  const subtype = String(event.subtype || '');
  if (type === 'system' && subtype === 'init') {
    saveSessionId(event.session_id);
  } else if (type === 'result') {
    saveSessionId(event.session_id);
    const result = typeof event.result === 'string' ? event.result : '';
    fs.writeFileSync(finalFile, result, 'utf8');
    finishResult(result, event.is_error || subtype === 'error');
  } else if (type === 'assistant') {
    for (const block of (event.message && event.message.content) || []) {
      if (block.type === 'tool_use') {
        if (block.name === 'Bash') lastBashCommand = stripShell((block.input || {}).command);
        setSummary(claudeToolDetail(block));
      } else if (block.type === 'text' && block.text) {
        setSummary(firstSentence(block.text));
      }
    }
  } else if (type === 'user') {
    for (const block of (event.message && event.message.content) || []) {
      if (block.type === 'tool_result' && block.is_error && isVerifyCommand(lastBashCommand)) {
        setSummary(`✗ ${shortCommand(lastBashCommand)}`);
      }
    }
  } else if (type === 'error') {
    terminal = true;
    emitControl('FAIL', 'CLI execution failed');
    process.exitCode = 1;
  }
}

let lastBashCommand = '';

const heartbeat = replayTick ? null : setInterval(emitSummary, heartbeatMs);
const rawStream = fs.createWriteStream(rawFile, { flags: 'a' });
const input = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });

input.on('line', line => {
  if (!line.trim()) return;
  rawStream.write(`${line}\n`);
  eventsSinceFlush += 1;
  try {
    const event = JSON.parse(line);
    if (provider === 'codex') handleCodex(event);
    else handleClaude(event);
  } catch {
    // The raw content is already preserved; invalid JSON never reaches the lead context.
  }
  if (replayTick && ++replayEvents % replayTick === 0) emitSummary();
});

input.on('close', () => {
  if (heartbeat) clearInterval(heartbeat);
  rawStream.end();
  if (terminal) return;

  const result = fs.existsSync(finalFile) ? fs.readFileSync(finalFile, 'utf8').trim() : '';
  if (result) {
    finishResult(result, false);
    return;
  }

  terminal = true;
  emitControl('FAIL', 'process ended with no result');
  process.exitCode = 1;
});
