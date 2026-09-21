# QuickJS Sandbox Limitations

dev-browser scripts run inside a **QuickJS WASM sandbox** — this is NOT Node.js.

---

## ❌ Not available at script (top) level

| Feature | Why |
|---------|-----|
| `require()` / `import()` | No module system |
| `fetch()` | No direct network access in the sandbox |
| `fs` / `path` / `os` | No Node built-ins |
| `process` | Not available |
| TypeScript syntax (`as Type`, `interface`) | Plain JS only |

## ✅ Available at script level

| API | Description |
|-----|-------------|
| `browser.getPage(nameOrId)` | Get/create a persistent named page, or attach to a `targetId` from `listPages()` |
| `browser.newPage()` | Create an anonymous page; no name argument, cleaned up after the script exits |
| `browser.listPages()` | List named pages and existing tabs as `{id, url, title, name}` |
| `browser.closePage(name)` | Close a named page |
| `console.log/warn/error` | Output to CLI |
| `setTimeout` / `clearTimeout` | Basic timers |
| `saveScreenshot(buf, name)` | Save screenshot to `~/.dev-browser/tmp/` |
| `writeFile(name, data)` | Write text file to tmp |
| `readFile(name)` | Read file from tmp |
| Top-level `await` | ✅ Supported |

---

## `page.evaluate()` — browser context (different rules)

Code inside `page.evaluate()` runs in the **real browser** — browser APIs are fully available:

```javascript
// ✅ fetch works here (it's the browser's fetch)
const result = await page.evaluate(async (apiPath, body) => {
  const token = localStorage.getItem('jwtToken'); // jwtToken 只是範例 key，換成你自己的
  const res = await fetch('http://localhost:8080' + apiPath, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify(body)
  });
  return { status: res.status, body: await res.text() };
}, '/api/path', {});
```

> No TypeScript syntax inside `page.evaluate()` — plain JS only.

---

## File path restriction

`saveScreenshot` / `writeFile` / `readFile` are all restricted to `~/.dev-browser/tmp/` — no path escaping.
