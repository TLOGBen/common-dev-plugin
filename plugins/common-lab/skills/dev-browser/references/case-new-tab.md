# 新分頁偵測與操作

> 每次先看 `dev-browser --help`；目前 API 可用 `browser.listPages()` 找出真實 tab，再用 `browser.getPage(targetId)` 接手，不需呼叫外部 `/json` endpoint。

---

## 方法選擇

| 方法 | 場景 | Chrome 真的開分頁？ | 可操作分頁內容？ |
|------|------|--------------------|-----------------|
| **Method A** — 攔截 window.open | 不需要使用者看到分頁、要保留 named page 時 | ❌ 被攔截，不開 | ✅ `getPage(name)` |
| **Method B** — listPages target diff（推薦） | 需要真實 Chrome tab 時 | ✅ 真實開分頁 | ✅ `getPage(targetId)` |
| **Method C** — waitForEvent('page') | 已在單一 script 內持有 opener page 時 | ✅ 真實開分頁 | ✅ Playwright event handle |

---

## Live API contract

| API | 用途 |
|-----|------|
| `browser.listPages()` | 列出 named pages 與既有 Chrome tabs；回傳 `{id, url, title, name}` |
| `browser.getPage(name)` | 建立或重取可跨 script 保存的 named page |
| `browser.getPage(targetId)` | 接手 `listPages()` 找到的既有 Chrome tab |
| `browser.newPage()` | 建匿名 page；script 結束後自動清理，不接受 name 參數 |
| `browser.closePage(name)` | 關閉 named page |

---

## Method C — waitForEvent('page')：真實開分頁並取 handle（推薦用於「使用者需目視」情境）

> ✅ `page.context()` 與 `waitForEvent` 在 dev-browser QuickJS sandbox **已確認可用**。
>
> **SPA 時序關鍵**：SPA 的 `window.open` 是同步 JS 呼叫——必須在點擊「之前」就建好 promise，
> 否則事件先觸發，listener 才後來才註冊，永遠等不到。
> **絕對不要用 `Promise.all`** — 兩個 async 在 QuickJS 執行順序不保證，容易漏接。

```javascript
const page = await browser.getPage("app");   // ← 換成你自己命名的 tab

// ① 先建 promise（不 await），此時 listener 已就位
const newPagePromise = page.context().waitForEvent('page');

// ② 再觸發點擊（window.open 在這裡發生）
await page.evaluate((keyword) => {
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
  let node;
  while ((node = walker.nextNode())) {
    if (getComputedStyle(node).cursor === 'pointer' && node.textContent.includes(keyword)) {
      node.click();
      return;
    }
  }
}, 'YOUR-KEYWORD');   // ← 換成目標關鍵字

// ③ 現在才 await，取得新分頁 handle
const newPage = await newPagePromise;
await newPage.waitForLoadState('domcontentloaded');
await newPage.waitForTimeout(2000);

console.log('新分頁 URL:', newPage.url());
const snap = await newPage.snapshotForAI();
```

**優點**：
- Chrome 真的開了一個新分頁，使用者可以看到
- `newPage` 是完整 Playwright Page 物件，可正常 evaluate / snapshot / click
- sessionStorage（部分 SPA 把 store 快照存於此）由 Chrome 自動複製，不需手動注入

**注意**：
- `waitForEvent` 預設 timeout 30s；若 30s 內沒觸發（例如元素未找到）就 timeout
- 確認目標元素存在後再執行，避免白等

---

## Method A — 點擊前攔截 window.open（推薦用於「不需使用者目視」情境）

在點擊前把 `window.open` 換掉，改為記錄目標 URL，再用 `browser.getPage(name)` 建持久可控分頁。

```javascript
const page = await browser.getPage("app");   // ← 換成你自己命名的 tab

// ① 攔截：換掉 window.open，記錄 URL（不實際開分頁）
await page.evaluate(() => {
  window._newTabUrl = null;
  window.open = (url) => { window._newTabUrl = url; };
});

// ② 點擊觸發元素（evaluate 比 locator 更不容易 timeout）
await page.evaluate((keyword) => {
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
  let node;
  while ((node = walker.nextNode())) {
    if (getComputedStyle(node).cursor === 'pointer' && node.textContent.includes(keyword)) {
      node.click();
      return;
    }
  }
}, 'YOUR-KEYWORD');   // ← 換成目標關鍵字

await page.waitForTimeout(300);

// ③ 取得攔截到的 URL
const targetUrl = await page.evaluate(() => window._newTabUrl);
console.log('攔截到 URL:', targetUrl);

// ④ 用 getPage(name) 建持久可控分頁並導航
const fullUrl = targetUrl.startsWith('http')
  ? targetUrl
  : 'http://localhost:3000' + targetUrl;   // ← 換成你的前端 dev server

const newTab = await browser.getPage("new-tab");
await newTab.goto(fullUrl, { waitUntil: "domcontentloaded" });
await newTab.waitForTimeout(2000);
```

**收工時記得關掉**：
```javascript
// 這個 tab 不會自動關，之後的 script 用 browser.getPage("new-tab") 還能拿到
// 若想明確關閉：await browser.closePage("new-tab")
```

---

## Method B — 不攔截，讓真實 tab 開，用 listPages() 接手

適合需要讓使用者看到真實 Chrome 新分頁的情境。先記錄現有 target IDs，觸發 `window.open`，再用差集找出新 tab。

```javascript
const page = await browser.getPage("app");
const beforeIds = new Set((await browser.listPages()).map((p) => p.id));

// 觸發會呼叫 window.open 的操作
await page.getByRole('link', { name: 'Open detail' }).click(); // 換成真實 selector

let opened = null;
for (let i = 0; i < 20 && !opened; i++) {
  await page.waitForTimeout(250);
  opened = (await browser.listPages()).find((p) => !beforeIds.has(p.id)) ?? null;
}
if (!opened) throw new Error('未偵測到 window.open 新分頁');

const newTab = await browser.getPage(opened.id);
await newTab.waitForLoadState('domcontentloaded');
console.log(JSON.stringify({ id: opened.id, url: newTab.url(), title: await newTab.title() }));
```

---

## 注意：新分頁的 sessionStorage

`browser.getPage("new-tab")` 新建的 named page 有獨立的 sessionStorage；真實 `window.open` tab 通常會複製 opener 的 sessionStorage。

> 有些 SPA（Vue + vuex-persistedstate、Pinia persist 等）會把整個 store 快照存進 sessionStorage。

| 儲存 | window.open 真實 tab | 新建 named page |
|------|---------------------|-------------------|
| localStorage（token）| ✅ 繼承 | ✅ 共用同 profile |
| sessionStorage（store 快照）| ✅ Chrome 複製一份 | ❌ 空的 |

→ 若目標頁面依賴 store 內的 auth state 才能渲染，新建 named page 可能顯示空白。
→ 解法：導航到該頁前先確認 token 存在，或在目標頁等待 API 回應後再取 snapshot。

```javascript
// 確認新分頁有 token 再繼續
// 'jwtToken' 只是範例 key，換成你自己的 token 儲存鍵
const hasToken = await newTab.evaluate(() => !!localStorage.getItem('jwtToken'));
if (!hasToken) {
  console.log('⚠️ 新分頁無 token，可能需要重新登入');
}
```
