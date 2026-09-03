# Vuetify Component Gotchas

---

## v-select / v-combobox / v-autocomplete — Dropdown Won't Open

### Problem

Calling `page.click()` directly on a combobox element usually does nothing — Vuetify's dropdown does not open.

### ✅ Fix

**Method A — click the append icon (most reliable)**:
```javascript
const section = page.locator('.v-input').filter({ hasText: '{field label}' }).first();
await section.locator('.v-input__append .v-icon').first().click({ force: true });
await page.waitForTimeout(500);
await page.getByRole('option', { name: '{option text}' }).click();
```

**Method B — snapshot first, then interact by role**:
```javascript
const snap = await page.snapshotForAI();
console.log(snap.full.substring(0, 3000));
// Find the correct role/name in the snapshot, then:
await page.getByRole('combobox', { name: '{LABEL}' }).click();
await page.waitForTimeout(500);
await page.getByRole('option', { name: '{OPTION}' }).click();
```

---

## v-overlay--active Blocks Clicks

When a Vuetify dialog/menu is open, `v-overlay--active` sits on top and intercepts clicks.

```javascript
// Dismiss the overlay first
await page.keyboard.press('Escape');
// Or force-click through it
await page.locator('{TARGET}').click({ force: true });
```

---

## Animation Timing

Vuetify expand / dialog open / dropdown animations take time. Snapshotting too early captures a mid-transition state.

```javascript
// Wait 1s after any action before snapshotting
await page.waitForTimeout(1000);
const snap = await page.snapshotForAI();
```

---

## Large Page Snapshots

```javascript
// Limit depth to reduce token cost
const snap = await page.snapshotForAI({ depth: 5 });
console.log(snap.full.substring(0, 5000));
```

---

## Filling Vuetify Text Fields

```javascript
// v-text-field wraps a real input inside — target it directly
await page.locator('.v-text-field input').nth(0).fill('{VALUE}');

// Or by label text
await page.getByLabel('{LABEL}').fill('{VALUE}');
```
