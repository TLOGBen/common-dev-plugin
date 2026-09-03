// 登入狀態擷取器（Part 1）——給「登入無法自動化」的站台用
// ---------------------------------------------------------------------------
// 適用：登入有圖形驗證碼 / OTP / 簡訊驗證 / SSO 跳轉 / 2FA 等「機器過不了或不該自動過」
// 的關卡。做法是：開一個「看得到的」瀏覽器，讓你**親手登入一次**（驗證碼你自己填），
// 登入完成後在這個 console 按 Enter，工具就把整個登入狀態
// （localStorage + sessionStorage + cookies）存成 auth.json。
//
// 之後跑 test.mjs（Part 2）時，引擎偵測到 auth.json 會自動套用、**跳過登入**，
// 直接從業務頁開始測。token 過期（API 開始回 401）就重跑本工具重抓即可。
//
// ⚠️ auth.json 內含活的登入憑證＝等同帳密，務必 gitignore，不可外流 / 進版控。
//
// 用法（headed，必須看得到瀏覽器才能手動登入）：
//   BASE_URL=http://host START_PATH=/login PW_DEPS=<abs> node capture-auth.mjs
//   （或雙擊 capture-auth.bat）
//   AUTH_STATE=auth.json   # 輸出檔名，預設 auth.json
// ---------------------------------------------------------------------------

import { createRequire } from 'node:module';
import { writeFileSync, chmodSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const __dirname = dirname(fileURLToPath(import.meta.url));

const CONFIG = {
  BASE_URL: process.env.BASE_URL || 'http://localhost:3000',
  START_PATH: process.env.START_PATH || '/login', // 例：請改成你站台的登入路由
  AUTH_STATE: process.env.AUTH_STATE || 'auth.json', // storageState：localStorage + cookies
  AUTH_SESSION: process.env.AUTH_SESSION || 'auth.session.json', // sessionStorage（storageState 不含）
  LOGIN_HINT: process.env.LOGIN_HINT || '/login', // URL 含此字串視為仍在登入頁
};

function loadPlaywright() {
  const dep = process.env.PW_DEPS;
  if (dep) {
    try {
      return require(join(dep, 'playwright'));
    } catch {
      /* 落到下一段 */
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

async function launchHeaded(chromium) {
  // 必須 headed：你要親眼看著畫面手動登入
  const attempts = [
    { label: '系統 Chrome', opts: { headless: false, channel: 'chrome' } },
    { label: '系統 Edge', opts: { headless: false, channel: 'msedge' } },
    { label: '內建 chromium', opts: { headless: false } },
  ];
  let lastErr;
  for (const a of attempts) {
    try {
      const b = await chromium.launch(a.opts);
      console.log(`▶ 使用瀏覽器：${a.label}`);
      return b;
    } catch (e) {
      lastErr = e;
    }
  }
  throw new Error('無法啟動瀏覽器（Chrome / Edge / chromium 都失敗）：' + (lastErr?.message || lastErr));
}

function waitForEnter(promptMsg) {
  return new Promise((resolve) => {
    process.stdout.write(promptMsg);
    process.stdin.resume();
    process.stdin.setEncoding('utf8');
    const onData = () => {
      process.stdin.removeListener('data', onData);
      process.stdin.pause();
      resolve();
    };
    process.stdin.on('data', onData);
  });
}

async function main() {
  const { chromium } = loadPlaywright();
  const outPath = join(__dirname, CONFIG.AUTH_STATE);
  const sessOutPath = join(__dirname, CONFIG.AUTH_SESSION);

  console.log('==================================================');
  console.log(' 登入狀態擷取器（Part 1）');
  console.log('==================================================');
  console.log(` 起始頁：${CONFIG.BASE_URL}${CONFIG.START_PATH}`);
  console.log(` 輸出檔：${outPath}`);
  console.log('--------------------------------------------------');

  const browser = await launchHeaded(chromium);
  const context = await browser.newContext({ ignoreHTTPSErrors: true });
  const page = await context.newPage();
  await page.goto(CONFIG.BASE_URL + CONFIG.START_PATH, { waitUntil: 'domcontentloaded' }).catch(() => {});

  // 輔助提示：偵測 URL 離開登入頁就提醒一次（僅提示，存檔仍以你按 Enter 為準）
  let hinted = false;
  const poll = setInterval(() => {
    if (!hinted && page.url && !page.url().includes(CONFIG.LOGIN_HINT)) {
      hinted = true;
      console.log(`\n   （偵測到已離開登入頁：${page.url()}　看起來登入成功了，可回此視窗按 Enter）`);
    }
  }, 1500);

  console.log('\n👉 請在剛開出來的瀏覽器裡「手動登入」（驗證碼 / OTP / SSO 都你自己操作）。');
  await waitForEnter('👉 登入完成後，回到這個視窗按 Enter 存檔（直接 Enter 即可）...\n');
  clearInterval(poll);

  // 1) storageState：localStorage + cookies
  await context.storageState({ path: outPath });
  try { chmodSync(outPath, 0o600); } catch { /* 非 POSIX 檔系統（如 Windows）忽略 */ }

  // 2) sessionStorage（⚠️ storageState 不含它）：另存一份。
  //    很多 SPA 把 Vuex / Pinia 狀態用 persistedstate 存進 sessionStorage；
  //    少了它，Part 2 冷啟會因 store 為空而 boot 崩（白頁），即使 token 在也沒用。
  let ssBytes = 0;
  try {
    const ss = await page.evaluate(() => JSON.stringify(sessionStorage));
    writeFileSync(sessOutPath, ss, { mode: 0o600 });
    try { chmodSync(sessOutPath, 0o600); } catch { /* 非 POSIX 檔系統忽略 */ }
    ssBytes = ss.length;
  } catch {
    /* 取不到就算了，Part 2 沒 session 檔時自然降級 */
  }

  // 簡單回報抓到什麼（不印出敏感值本身）
  const state = await context.storageState();
  const lsCount = (state.origins || []).reduce((n, o) => n + (o.localStorage?.length || 0), 0);
  const ckCount = (state.cookies || []).length;
  console.log('\n==================================================');
  console.log(` ✅ 已存登入狀態：${outPath}`);
  console.log(`    localStorage 項目：${lsCount}　cookies：${ckCount}`);
  console.log(`    sessionStorage：${ssBytes} bytes → ${CONFIG.AUTH_SESSION}`);
  console.log(`    當前頁面：${page.url()}`);
  console.log('--------------------------------------------------');
  console.log(' 接下來：直接跑 test.mjs（或雙擊 run-test.bat），');
  console.log(' 引擎會自動套用 auth.json + auth.session.json、跳過登入，從業務頁開始測。');
  console.log(' ⚠️ auth.json / auth.session.json 含活憑證，已被 .gitignore，請勿外流 / 進版控。');
  console.log(' （token 過期、API 開始回 401 → 重跑本工具重抓。）');
  console.log('==================================================');

  await browser.close();
  process.exit(0);
}

main().catch((e) => {
  console.error('擷取失敗：', e);
  process.exit(2);
});
