// selector 診斷工具（gen-e2e-record 復測時用）
// ---------------------------------------------------------------------------
// 登入 → 走到目標頁/狀態 → 對某個文字 LABEL 列出各種 locator 候選的命中數，
// 並列出表格列裡每顆按鈕的 icon class，幫你找到「穩定」的定位方式
// （取代 codegen 那種 hover-tooltip 的 description 脆弱定位）。
//
// 用法（同 test.mjs 的執行環境；headless）：
//   LABEL=明細 CLICK=送出 node inspect.mjs
//   LABEL=匯出 GOTO=/app/list node inspect.mjs   # 路徑為範例，請改成你的站台路徑
//
// 環境變數：
//   LABEL   要找的文字（必填）
//   CLICK   登入後依序要點的按鈕文字，逗號分隔（可選，用來走到目標頁）
//   GOTO    登入後直接導航的路徑（可選，與 CLICK 二擇一或併用）
//   USER_ID/PASSWORD/BASE_URL/START_PATH  同 test.mjs CONFIG
//   PW_DEPS 共用 playwright 路徑（WSL→Windows 必填絕對路徑；同機可省）
// ---------------------------------------------------------------------------

import { createRequire } from 'node:module';
import { join } from 'node:path';
const require = createRequire(import.meta.url);

const C = {
  // 帳密與站台位址以環境變數優先；以下寫死值僅為範例 fallback，
  // 請一律改用環境變數（BASE_URL / START_PATH / USER_ID / PASSWORD）覆寫成你的目標站台
  BASE_URL: process.env.BASE_URL || 'http://localhost:3000', // 前端 dev server（範例）
  START_PATH: process.env.START_PATH || '/login', // 範例登入路徑，請換成你的站台
  USER_ID: process.env.USER_ID || 'test.user',
  PASSWORD: process.env.PASSWORD || '1',
  LABEL: process.env.LABEL || '',
  CLICK: process.env.CLICK || '',
  GOTO: process.env.GOTO || '',
};

function loadPlaywright() {
  const dep = process.env.PW_DEPS;
  if (dep) {
    try {
      return require(join(dep, 'playwright'));
    } catch {
      /* fallthrough */
    }
  }
  try {
    return require('playwright');
  } catch {
    const { execSync } = require('node:child_process');
    const groot = execSync('npm root -g', { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim();
    return require(join(groot, 'playwright'));
  }
}

if (!C.LABEL) {
  console.error('請用 LABEL=<要找的文字> 指定目標，例如 LABEL=詳情 CLICK=送出 node inspect.mjs');
  process.exit(2);
}

const { chromium } = loadPlaywright();
const b = await chromium.launch({ channel: 'chrome', headless: process.env.HEADLESS !== '0' });
const page = await (await b.newContext({ ignoreHTTPSErrors: true })).newPage();

// 登入段 — 此為常見 SPA 登入流程範例（自訂下拉/帳號欄如 v-combobox / Login 按鈕 / token 寫入 localStorage）。
// 請依你站台的 login template（.claude/test-template/）改寫此段。
await page.goto(C.BASE_URL + C.START_PATH, { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(1500);
const combo = page.locator('.v-combobox input').first();
if (await combo.count()) {
  await combo.click();
  await combo.fill(C.USER_ID);
  await page.locator('input[type="password"]').fill(C.PASSWORD);
  await page.getByRole('button', { name: 'Login' }).click();
  await page
    // 'jwtToken' 僅為範例 key，請改成你站台實際的 token 儲存鍵
    .waitForFunction(() => !location.pathname.endsWith('/login') && !!localStorage.getItem('jwtToken'), { timeout: 30000 })
    .catch(() => {});
} else {
  console.warn('[警告] 找不到登入欄位（.v-combobox input），登入段未執行；以下診斷結果可能是「未登入頁面」。請依你站台的 login template 改寫登入段。');
}

if (C.GOTO) {
  await page.goto(C.BASE_URL + C.GOTO, { waitUntil: 'domcontentloaded' });
}
for (const name of C.CLICK.split(',').map((s) => s.trim()).filter(Boolean)) {
  await page.getByRole('button', { name }).first().click().catch((e) => console.log(`  點 "${name}" 失敗: ${e.message}`));
  await page.waitForTimeout(1500);
}
await page.waitForTimeout(2000);

console.log('URL =', page.url());
const L = C.LABEL;
const variants = {
  [`getByRole button name=${L}`]: page.getByRole('button', { name: L }),
  [`getByRole button description=${L}`]: page.getByRole('button', { description: L, exact: true }),
  [`getByRole link name=${L}`]: page.getByRole('link', { name: L }),
  [`getByText ${L}`]: page.getByText(L, { exact: false }),
  [`[title*=${L}]`]: page.locator(`[title*="${L}"]`),
  [`[aria-label*=${L}]`]: page.locator(`[aria-label*="${L}"]`),
};
for (const [k, loc] of Object.entries(variants)) {
  console.log('  ', k, '->', await loc.count().catch(() => 'err'));
}

// 表格列裡每顆按鈕的 icon（找 icon 按鈕的穩定定位）
const rowBtns = await page
  .locator('.v-data-table tbody tr, .v-data-table-server tbody tr')
  .first()
  .locator('button')
  .evaluateAll((els) =>
    els.map((el) => ({
      icon: (el.querySelector('i') || {}).className || '(no i)',
      aria: el.getAttribute('aria-label') || el.getAttribute('aria-describedby') || '',
    })),
  )
  .catch(() => []);
console.log('第一列按鈕（找 icon class 當穩定 selector，例如 button:has(i.mdi-xxx)）:');
for (const x of rowBtns) console.log('   icon=', x.icon, '| aria=', x.aria);

await b.close();
