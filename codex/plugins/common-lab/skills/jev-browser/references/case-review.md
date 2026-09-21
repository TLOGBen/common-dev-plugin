# Page Feature Review — Golden Template

> Prerequisite: page `"app"` must be connected. Only protected pages require authenticated state; public pages can be reviewed directly.

---

## Screenshot + DOM Verification

```javascript
// === Edit this section ===
const TARGET_URL = 'http://localhost:3000/{YOUR_PATH}';  // e.g. /app/list — replace with your own route
// =========================

const page = await browser.getPage("app");
await page.goto(TARGET_URL, { waitUntil: "domcontentloaded" });
await page.waitForTimeout(1000);  // wait for Vuetify animations

// Screenshot
const buf = await page.screenshot();
const shotPath = await saveScreenshot(buf, "review-before.png");
console.log("Screenshot saved: " + shotPath);

// DOM structure
const snap = await page.snapshotForAI();
console.log("=== DOM ===");
console.log(snap.full.substring(0, 4000));
```

---

## Interaction + Verification (fill in actual steps)

```javascript
const page = await browser.getPage("app");

// Actions — fill in as needed:
// await page.getByRole('button', { name: '新增' }).click();
// await page.locator('input[name="{FIELD_NAME}"]').fill('{VALUE}');
// await page.getByRole('combobox', { name: '{LABEL}' }).click();
// await page.waitForTimeout(500);
// await page.getByRole('option', { name: '{OPTION}' }).click();
// await page.getByRole('button', { name: '確認' }).click();
// await page.waitForTimeout(1000);

// Screenshot after action
const buf = await page.screenshot();
const path = await saveScreenshot(buf, "review-after.png");
console.log("Screenshot saved: " + path);

// DOM after action
const snap = await page.snapshotForAI();
console.log("=== DOM after action ===");
console.log(snap.full.substring(0, 3000));
```

---

## How to Find the Right Element

1. Run `page.snapshotForAI()` to see the DOM structure
2. Locate the target element by role / name / label
3. Select it with Playwright:
   - `page.getByRole('button', { name: '...' })` — buttons
   - `page.getByRole('textbox', { name: '...' })` — text inputs
   - `page.locator('.v-combobox input').first()` — combobox (see gotchas-vuetify.md)
   - `page.locator('[data-testid="..."]')` — test IDs
