// 登入 — 帳號直填模式（headless / connected 都可靠）
// 完整說明 + 其他變化（自訂下拉/登入元件 / 快速登入面板）：references/case-login.md
//
// 用法：
//   PowerShell（Windows native，先跑 setup-chrome-debug.ps1 啟動 Chrome）：
//     dev-browser --connect http://127.0.0.1:9222 run "$DevBrowserSkillDir\scripts\case\login.js"
//
//   WSL2（先跑 setup-wsl2-chrome-debug.sh）：
//     HOST_IP=$(ip route show default | awk '/default/ {print $3; exit}')
//     dev-browser --connect http://${HOST_IP}:9333 run "$DEV_BROWSER_SKILL_DIR/scripts/case/login.js"
//
// PowerShell：現成 template 用 `run <file>`；臨時多行腳本可依 `dev-browser --help` 使用 here-string pipe。
//
// 換帳號：直接改下方 USER_ID。dev env 通常任何密碼都可，欄位不可空（依你的站台而定）。
// 帳號參考：以下皆為範例，換成你站台的測試帳號（例：admin、user1、user2）

const USER_ID = 'admin';  // ← 範例帳號，換成你站台的測試帳號

const page = await browser.getPage("app");
// ↓ 範例路由，換成你站台的登入頁網址（前端 dev server，例 http://localhost:3000）
await page.goto("http://localhost:3000/login", { waitUntil: "domcontentloaded" });
await page.waitForTimeout(1500);

// 範例：帳號是自訂下拉/組合框元件（如 v-combobox），填內層 input
// 換成你站台實際的帳號/密碼/登入按鈕選擇器
await page.locator('.v-combobox input').first().click();
await page.locator('.v-combobox input').first().fill(USER_ID);
await page.locator('input[type="password"]').fill('1');
await page.getByRole('button', { name: 'Login' }).click();  // 注意：按鈕文字依站台而定

await page.waitForTimeout(6000);  // waitForURL 在 headless 下不可靠

// localStorage.getItem('jwtToken')：jwtToken 只是範例 key，換成你站台的 token key
const token = await page.evaluate(() => localStorage.getItem('jwtToken'));
// 有些 SPA（Vue + vuex-persistedstate、Pinia persist 等）會把整個 store 快照存進 sessionStorage
// 'vuex' 與下方欄位路徑皆為範例，換成你站台的 store key 與欄位結構
const vuex = await page.evaluate(() => {
  const s = sessionStorage.getItem('vuex');
  return s ? JSON.parse(s) : null;
});

console.log(JSON.stringify({
  url: page.url(),
  hasToken: !!token,
  tokenLen: token ? token.length : 0,
  userId: vuex?.auth?.userProfile?.empAuthList?.[0]?.empAccount ?? null,
  dept: vuex?.auth?.activeEmpDept?.deptName ?? null
}, null, 2));
