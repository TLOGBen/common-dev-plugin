# API Testing — Golden Template

> Prerequisite: page `"app"` must be logged in (run Step 1 from `case-login.md` first).
> `fetch` is only available inside `page.evaluate()` (browser context) — not at the top-level script.

---

## Single API Call

```javascript
// === Edit this section ===
const API_PATH = '/api/{Module}/{Action}';
const REQUEST_BODY = {};
// =========================

const page = await browser.getPage("app");

const result = await page.evaluate(async (path, body) => {
  // jwtToken is just an example key — replace with your app's token key
  const token = localStorage.getItem('[your-token-key]'); // e.g. 'jwtToken'
  const res = await fetch('http://localhost:8080' + path, { // 後端 API base URL (例)
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify(body)
  });
  const text = await res.text();
  let parsed;
  try { parsed = JSON.parse(text); } catch { parsed = text; }
  return { status: res.status, body: parsed };
}, API_PATH, REQUEST_BODY);

console.log(JSON.stringify(result, null, 2));
```

---

## Batch API Calls (test multiple endpoints at once)

```javascript
const page = await browser.getPage("app");

const results = await page.evaluate(async () => {
  // jwtToken is just an example key — replace with your app's token key
  const token = localStorage.getItem('[your-token-key]'); // e.g. 'jwtToken'
  const apis = [
    { name: 'getList',   url: 'http://localhost:8080/api/{Module}/GetList',   body: {} },
    { name: 'getDetail', url: 'http://localhost:8080/api/{Module}/GetDetail', body: { id: 1 } },
  ];

  const out = [];
  for (const api of apis) {
    try {
      const res = await fetch(api.url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + token
        },
        body: JSON.stringify(api.body)
      });
      const text = await res.text();
      out.push({ name: api.name, status: res.status, preview: text.substring(0, 400) });
    } catch(e) {
      out.push({ name: api.name, error: e.message });
    }
  }
  return out;
});

console.log(JSON.stringify(results, null, 2));
```

---

## Reading the Response

| Pattern | Meaning |
|---------|---------|
| `status: 200, isSuccess: true, data: {...}` | ✅ OK |
| `status: 200, isSuccess: false, returnCode: "XXX_001_01"` | ❌ Business logic error — check returnCode |
| `status: 200, isSuccess: true, data: null` | ⚠️ No data found, or mapping issue |
| `status: 401` | JWT expired — re-login |
| `status: 415` | Missing POST body or wrong Content-Type |
| `status: 500` | Backend exception — check backend logs |
