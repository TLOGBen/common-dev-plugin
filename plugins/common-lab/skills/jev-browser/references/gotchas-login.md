# Custom Login Component Gotchas

> dev-browser quick reference for login gotchas with custom/dynamic login components.

---

## Account field may be a dynamic dropdown component (not a plain input)

許多 UI 框架的自訂下拉/登入元件（例如 Vuetify v-combobox、自訂 autocomplete）並非單純的 `<input>`，
直接 fill 外層元素可能打不到真正的輸入框。改成填內層 input。

```javascript
// ✅ Correct: fill the inner input of the combobox/autocomplete
await page.locator('.v-combobox input').first().fill('[example-account]');

// ❌ Wrong: may not target the right element
await page.fill('input[type="text"]', '[example-account]');
```

> 動態下拉元件的 selector 通常較脆弱（class 隨框架版本變動、選項由 JS 動態渲染）。
> 盡量用內層 input 或 stable 的 `role` / `aria` 屬性定位，避免錄製出易碎的 selector。

---

## Login button text may be in any language

按鈕文字依站台而定，可能是英文也可能是其他語系。請依受測站台實際文字調整。

```javascript
await page.getByRole('button', { name: 'Login' }).click();  // ✅ 範例，依站台調整
// 例如本地化站台可能是 '登入'
```

---

## Password — dev env may skip validation

部分 dev 環境會略過密碼驗證，任意字串即可登入；請依目標站台實際行為確認。

```javascript
await page.locator('input[type="password"]').fill('any');
```

---

## Auth Token Location

驗證 token 常見儲存位置因站台而異。最常見是 JWT 存在 `localStorage`，
但也可能在 `sessionStorage`、cookie 或記憶體中。請依受測站台實際情況確認。

```javascript
// 範例：許多 SPA 把 JWT 存在 localStorage（不一定是 sessionStorage）
// jwtToken 只是範例 key，請換成你站台實際使用的 key
const token = await page.evaluate(() => localStorage.getItem('[your-token-key]'));
```

> 注意：有些 SPA（Vue + vuex-persistedstate、Pinia persist 等）會把整個 store 快照
> 存進 `sessionStorage`，token 可能藏在序列化的 store JSON 內，而非單一 key。

---

## Account Reference

依受測站台的測試帳號自行填寫。常見的一個陷阱是：某些帳號需要手動輸入（不在下拉選單中），
其餘可從下拉選單選取。以下為範例格式。

| Account | Role | How to enter |
|---------|------|--------------|
| `[admin-account]` | System admin | **Must type manually** — not in dropdown |
| `[user-account-1]` | Manager | Available in dropdown |
| `[user-account-2]` | Operator | Available in dropdown |
| `[user-account-3]` | Manager | Available in dropdown |

---

## Post-login Behavior

- 登入後通常會 redirect 到首頁路由（範例 `/app/list`，請換成你站台實際路由）
- Wait for it: `await page.waitForURL('**/app/**', { timeout: 10000 })`  // 範例 glob，依站台調整
- token 通常持續存在 `localStorage` 直到分頁關閉
- Named page（例 `"app"`）keeps login state across script runs (until the daemon restarts)

---

## Common Login Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Stuck on login page | 後端 API not running | Start the backend (例 http://localhost:8080) |
| Blank page | 前端 dev server not running | `npm run dev` (例 http://localhost:3000) |
| API 401 | token expired | Re-login |
