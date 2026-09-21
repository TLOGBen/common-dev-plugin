# SPA Login + Basic Debug — Golden Template

> **🔗 現成腳本**：`scripts/case/login.js`（帳號直填模式）
> 跑：先依 `SKILL.md` 的 Codex bundled-path resolution 設定 `$DevBrowserSkillDir`，再執行 `dev-browser --connect http://127.0.0.1:9222 run "$DevBrowserSkillDir\scripts\case\login.js"`。
> 換帳號：改檔頭 `USER_ID`。其他變化（自訂下拉/角色卡登入 / 快速登入面板）見下方內嵌腳本。

---

## Quick Login via Test Data Cards (optional)

有些受測站台的登入頁會提供「快速登入面板」（例如以角色卡 / 測試帳號卡片快速登入），比逐欄輸入帳密更快。
典型流程：**click a role card (filter) → click a member card (actual login)**。
以下為示範，請依目標站台的實際元件調整選擇器與標籤文字。

> ⚠️ **Headless mode gotcha**: `waitForURL` often times out in headless Chromium because the
> member card click doesn't reliably trigger navigation detection. Use `waitForTimeout(6000)`
> instead. If the role card approach still fails, fall back to the **Manual Fill** section below.

```javascript
// === Edit this section （以下標籤皆為範例，請改成你站台實際的文字）===
const ROLE = '<role-label>';     // role card label，例如某個角色名稱
const BU_TAB = '<tab-label>';    // 分頁/分群標籤（若登入頁有分頁切換）
const MEMBER_KEYWORD = '';       // leave empty to pick the first member, or set a name/account substring
// =========================

const page = await browser.getPage("app");
await page.goto("http://localhost:3000/login", { waitUntil: "domcontentloaded" }); // /login 為範例路由，請改成你站台的登入路由
await page.waitForTimeout(1000);

// Switch tab if needed
if (BU_TAB) {
  await page.getByRole('tab', { name: BU_TAB }).click();
  await page.waitForTimeout(500);
}

// Step 1: click role card to filter members
await page.getByRole('button', { name: new RegExp(ROLE) }).first().click();
await page.waitForTimeout(500);

// Step 2: click member card to actually log in
const memberLocator = MEMBER_KEYWORD
  ? page.locator(`text=${MEMBER_KEYWORD}`).first()
  : page.locator('.v-list-item, [cursor=pointer]').filter({ hasText: /\w+\.\w+/ }).first();
await memberLocator.click();

// waitForTimeout instead of waitForURL — more reliable in headless mode
await page.waitForTimeout(6000);

// jwtToken 只是常見的範例 key，請改成你站台實際的 token key
const token = await page.evaluate(() => localStorage.getItem('jwtToken'));
// 有些 SPA (Vue + vuex-persistedstate、Pinia persist 等) 會把整個 store 快照存進 sessionStorage
const store = await page.evaluate(() => {
  const s = sessionStorage.getItem('vuex'); // 'vuex' 為常見範例 key，依你的 persist 設定調整
  return s ? JSON.parse(s) : null;
});

console.log(JSON.stringify({
  url: page.url(),
  hasToken: !!token,
  // 以下取值路徑為範例，請依你站台的 store 結構調整
  userId: store?.auth?.userProfile?.account ?? null,
  dept: store?.auth?.activeDept?.deptName ?? null
}, null, 2));
```

> **Note**: clicking a specific member by account — set `MEMBER_KEYWORD = '<account-substring>'`.
> 若面板分多個群組（例如成員 / 主管），任選一個符合的即可。

---

## Step 1: Login (Manual Fill — headless-safe fallback)

> Use this when the role card approach times out in headless mode.

```javascript
// === Edit this section ===
const USER_ID = '<your-test-account>';  // 你站台的測試帳號
// =========================

const page = await browser.getPage("app");
await page.goto("http://localhost:3000/login", { waitUntil: "domcontentloaded" }); // /login 為範例路由
await page.waitForTimeout(1500);

// 若帳號欄是自訂下拉/組合框元件（如 Vuetify v-combobox），填內層的 input 而非外層元件（見 gotchas-login.md）
await page.locator('.v-combobox input').first().click();
await page.locator('.v-combobox input').first().fill(USER_ID);
await page.locator('input[type="password"]').fill('<your-test-password>');
await page.getByRole('button', { name: 'Login' }).click();  // 按鈕文字依站台而定（可能是 'Login' 或 '登入'）

// waitForTimeout instead of waitForURL — reliable in both headless and connected mode
await page.waitForTimeout(6000);

const token = await page.evaluate(() => localStorage.getItem('jwtToken')); // jwtToken 為範例 key
console.log(JSON.stringify({ url: page.url(), hasToken: !!token }));
```

**Account reference**（依你站台的 dev 環境填寫；以下為範例格式）：

| Account | Role | Notes |
|---------|------|-------|
| `<account-a>` | System admin | 例如：不在下拉清單中，需手動輸入 |
| `<account-b>` | Manager | 例如：可從下拉清單選取 |
| `<account-c>` | Operator | 例如：可從下拉清單選取 |

---

## Step 2: Navigate + DOM Snapshot

```javascript
// page "app" retains login state — no re-login needed
const page = await browser.getPage("app");
await page.goto("{TARGET_URL}", { waitUntil: "domcontentloaded" });
await page.waitForTimeout(1000);  // wait for UI framework animations (e.g. Vuetify transitions)

const snap = await page.snapshotForAI();
console.log("=== DOM ===");
console.log(snap.full.substring(0, 3000));
```

---

## Step 3: Console Errors + Persisted Store State

```javascript
const page = await browser.getPage("app");

const errors = [];
page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
await page.reload({ waitUntil: "domcontentloaded" });
await page.waitForTimeout(1500);

// 有些 SPA 會把 store 快照存進 sessionStorage（vuex-persistedstate / Pinia persist 等）
const store = await page.evaluate(() => {
  const s = sessionStorage.getItem('vuex'); // 'vuex' 為範例 key
  return s ? JSON.parse(s) : null;
});

console.log(JSON.stringify({
  url: page.url(),
  errors,
  storeUserId: store?.auth?.userId ?? 'N/A'
}, null, 2));
```

---

## All-in-One Template (most common — copy and edit)

```javascript
// === Edit this section （路由與帳號皆為範例，請改成你站台實際的值）===
const USER_ID = '<your-test-account>';
const TARGET_URL = 'http://localhost:3000/app/detail';  // /app/detail 為範例路由
// =========================

const page = await browser.getPage("app");

// Login
await page.goto("http://localhost:3000/login", { waitUntil: "domcontentloaded" }); // /login 為範例路由
await page.waitForTimeout(1500);
await page.locator('.v-combobox input').first().click();   // 自訂下拉/組合框：填內層 input
await page.locator('.v-combobox input').first().fill(USER_ID);
await page.locator('input[type="password"]').fill('<your-test-password>');
await page.getByRole('button', { name: 'Login' }).click();
await page.waitForTimeout(6000);  // waitForURL unreliable in headless mode

// Navigate
await page.goto(TARGET_URL, { waitUntil: "domcontentloaded" });
await page.waitForTimeout(1000);

// Collect console errors
const errors = [];
page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
await page.waitForTimeout(500);

// DOM snapshot
const snap = await page.snapshotForAI();
const token = await page.evaluate(() => localStorage.getItem('jwtToken')); // jwtToken 為範例 key

console.log(JSON.stringify({
  url: page.url(),
  hasToken: !!token,
  errors,
  snapshot: snap.full.substring(0, 3000)
}, null, 2));
```

---

## Symptom → First Check

| Symptom | What to look at |
|---------|-----------------|
| Blank page | Console errors — JS init failure |
| 載入失敗 / error toast | Which API returned `data: null` |
| Button not responding | Snapshot for `disabled` + console errors |
| Empty table | Check if list API returned `data` |
| 401 Unauthorized | JWT expired — re-login |
