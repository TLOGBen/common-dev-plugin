// 自包含 Playwright 自動化測試 + 流程期間 API 彙整報告
// ---------------------------------------------------------------------------
// 驅動一段使用者操作流程（見下方 flow()），被動攔截流程期間「所有 API call」，
// 結束後產出 Kami 風 Markdown + HTML 測試報告。
//
// ⭐ 你只需要編輯兩處：
//    1) CONFIG          — 站台網址 / 起始路徑 / 帳密等
//    2) async function flow(page, helpers)  — 實際要測的操作步驟
//    其餘（攔截引擎 + 報告引擎）目標無關，原封不動沿用。
//
// 執行方式：
//   雙擊 run-test.bat（Windows，原生 node）
//   或 macOS/Linux：bash run.sh
//   或直接：node test.mjs
//   只想看報告版型（不開瀏覽器）：PREVIEW=1 node test.mjs
// ---------------------------------------------------------------------------

import { createRequire } from 'node:module';
import { mkdirSync, writeFileSync, existsSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);

// === CONFIG（編輯這裡；可用環境變數覆寫）===
// ⚠️ 以下預設為中性範例值，依受測站台填入實際值；專案沉澱的設定可查 .claude/test-template/
const CONFIG = {
  BASE_URL: process.env.BASE_URL || 'http://localhost:3000', // 前端 dev server（例 http://localhost:3000）
  BACKEND: process.env.BACKEND || 'http://localhost:8080', // 後端 API base（例 http://localhost:8080），用於標記哪些是後端 API
  START_PATH: process.env.START_PATH || '/login', // 流程起始頁路徑（例 /login，換成你自己的路徑）
  TARGET_PATH: process.env.TARGET_PATH || '', // 可選：流程中段要再導航的頁面（留空=不導航）
  HEADLESS: process.env.HEADLESS === '1', // 預設顯示瀏覽器；設 HEADLESS=1 可隱藏（背景跑）
  SETTLE_MS: Number(process.env.SETTLE_MS || 4000), // 流程結束後等網路安靜、收齊 API 的時間
  NAV_TIMEOUT: 30000,

  // 登入無法自動化（圖形驗證碼 / OTP / SSO / 2FA）時用：先 capture-auth.mjs 手動登入
  // 存出 auth.json，引擎偵測到此檔就套用（跳過登入）。flow 收到 helpers.authed=true。
  AUTH_STATE: process.env.AUTH_STATE || 'auth.json', // storageState：localStorage + cookies
  // sessionStorage 快照（storageState 不含）。SPA 把 Vuex/Pinia 存 sessionStorage 時，
  // 缺它冷啟會 boot 崩白頁；引擎用 addInitScript 在頁面載入前還原。
  AUTH_SESSION: process.env.AUTH_SESSION || 'auth.session.json',

  // 選填：authed 跳過登入後，用來判定業務頁已渲染的代表性元素 selector（留空＝以 body 文字長度判定）
  READY_SELECTOR: process.env.READY_SELECTOR || '',

  // 報告標題文案（依流程命名，顯示在 Markdown 與 HTML 報告；不要寫死特定站台）
  REPORT_TITLE: process.env.REPORT_TITLE || '自動化測試報告',
  REPORT_EYEBROW: process.env.REPORT_EYEBROW || 'E2E · API Verification',

  // ↓ 以下是預設 flow（登入範例）用到的參數；依站台填入，換流程時可改或刪
  USER_ID: process.env.USER_ID || 'example.user',
  PASSWORD: process.env.PASSWORD || 'example-password',
};
// =================================

// === FLOW：編輯這個函式成你要測的操作流程 ===
// 收到 page（Playwright Page）與 helpers.step(n, msg)（印階段進度）。
// 用 Playwright API 操作：page.goto / page.locator(sel).click() / .fill(text) ...
// 回傳 { success: boolean, error?: string, summary: [{label, value}] }
//   - success：這次流程是否達成預期（顯示在報告最上方）
//   - summary：要呈現在報告「流程結果」的關鍵資訊（任意鍵值）
//
// 預設範例＝一般 SPA 登入。要測別的流程就改這個函式（其餘程式不用動）。
// 想擴充步驟又懶得手寫 selector：用 `npx playwright codegen <url>` 錄，再把
// 錄到的 page.click/fill 貼進來。
async function flow(page, { step, authed }) {
  const summary = [];

  // authed=true → 引擎已套用 auth.json（capture-auth.mjs 手動登入存下的狀態），
  // 直接跳過登入。適用登入有驗證碼 / OTP / SSO 的站台。
  if (authed) {
    step(2, '已套用 auth.json，跳過登入，直接開啟業務頁');
    await page.goto(CONFIG.BASE_URL + (CONFIG.TARGET_PATH || CONFIG.START_PATH), {
      waitUntil: 'domcontentloaded',
    });
    // 等具體條件而非硬 sleep：有填 READY_SELECTOR 就等該元素出現，
    // 否則等 body 有實際文字內容（auth 不完整時 SPA 會 boot 崩成白頁）。
    if (CONFIG.READY_SELECTOR) {
      await page
        .locator(CONFIG.READY_SELECTOR)
        .first()
        .waitFor({ timeout: CONFIG.NAV_TIMEOUT })
        .catch(() => {});
    } else {
      await page
        .waitForFunction(() => document.body && document.body.innerText.trim().length > 50, {
          timeout: CONFIG.NAV_TIMEOUT,
        })
        .catch(() => {});
    }
    // ⚠️ URL-only 判定會被白頁假綠（白頁的 URL 也不是 /login），必須驗畫面真的 render
    const bodyText = await page.evaluate(() => document.body.innerText);
    const rendered = bodyText.trim().length > 50;
    summary.push({ label: '登入方式', value: 'auth.json（跳過登入）' });
    summary.push({ label: '頁面已渲染', value: rendered ? '是' : '否（疑似白頁）' });
    summary.push({ label: '落地頁面', value: page.url() });
    return { success: rendered && !page.url().includes('/login'), summary };
  }

  step(2, '開啟起始頁並載入');
  await page.goto(CONFIG.BASE_URL + CONFIG.START_PATH, { waitUntil: 'domcontentloaded' });

  // 自訂下拉/登入元件眉角（範例）：帳號可能是 Vuetify v-combobox 的內層 input，
  // 而非單純 <input>；登入按鈕文字依站台而定（此範例為英文 "Login"）。換站台時請調整 selector。
  step(3, `填入帳號（${CONFIG.USER_ID}）`);
  const combo = page.locator('.v-combobox input').first();
  // 等目標欄位真的出現再操作，取代硬 sleep（waitForTimeout 是 flaky 根因）
  await combo.waitFor({ timeout: CONFIG.NAV_TIMEOUT });
  await combo.click();
  await combo.fill(CONFIG.USER_ID);
  await page.locator('input[type="password"]').fill(CONFIG.PASSWORD);

  step(4, '送出登入');
  await page.getByRole('button', { name: 'Login' }).click();

  step(5, '等待流程完成並收集 API（後端較慢時請耐心等候）');
  await page
    .waitForFunction(
      // jwtToken 只是範例 key；換成你站台實際存 token 的 localStorage key
      () => !location.pathname.endsWith('/login') && !!localStorage.getItem('jwtToken'),
      { timeout: CONFIG.NAV_TIMEOUT },
    )
    .catch(() => {});

  // 可選：登入後再導航到要測的頁面，一併納入 API 攔截
  if (CONFIG.TARGET_PATH) {
    await page.goto(CONFIG.BASE_URL + CONFIG.TARGET_PATH, { waitUntil: 'domcontentloaded' });
  }

  // 範例：以 localStorage 的 token 判斷登入成功（jwtToken 只是範例 key，換成你站台實際的 key）
  const token = await page.evaluate(() => localStorage.getItem('jwtToken'));
  summary.push({ label: '登入帳號', value: CONFIG.USER_ID });
  summary.push({ label: 'Token 長度', value: token ? token.length : 0 });
  summary.push({ label: '落地頁面', value: page.url() });

  return { success: !!token && !page.url().endsWith('/login'), summary };
}
// === FLOW 結束 ===

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPORT_DIR = join(__dirname, 'reports');

// --- 載入 playwright（共用 deps / 本地 / 全域，三段解析）---
// 啟動腳本（run-test.bat / run.sh）會用 PW_DEPS 指定相依目錄的絕對路徑，
// 直接 require 該路徑最可靠（Windows 的 NODE_PATH 對 require 不穩，故不依賴它）。
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
    const groot = execSync('npm root -g', { stdio: ['ignore', 'pipe', 'ignore'] })
      .toString()
      .trim();
    return require(join(groot, 'playwright'));
  }
}

// --- 啟動瀏覽器：系統 Chrome → Edge → 內建 chromium 三段 fallback ---
async function launchBrowser(chromium) {
  const headless = CONFIG.HEADLESS;
  const attempts = [
    { label: '系統 Chrome', opts: { headless, channel: 'chrome' } },
    { label: '系統 Edge', opts: { headless, channel: 'msedge' } },
    { label: '內建 chromium', opts: { headless } },
  ];
  let lastErr;
  for (const a of attempts) {
    try {
      const browser = await chromium.launch(a.opts);
      console.log(`▶ 使用瀏覽器：${a.label}`);
      return browser;
    } catch (e) {
      lastErr = e;
    }
  }
  throw new Error(
    '無法啟動任何瀏覽器（已試 Chrome / Edge / 內建 chromium）。\n' +
      '請確認已安裝 Google Chrome，或執行：npx playwright install chromium\n' +
      '原始錯誤：' +
      (lastErr?.message || lastErr),
  );
}

// --- 工具：截斷字串 ---
function truncate(str, n = 500) {
  if (str == null) return '';
  const s = String(str);
  return s.length > n ? s.substring(0, n) + `…(+${s.length - n} chars)` : s;
}

// --- 工具：遮蔽 body 內的機敏值，避免寫進落地報告（reports/*.html|md）---
// 與 header 遮蔽同一原則：body 常含 JWT / 密碼 / 金鑰。先試 JSON 依「鍵名」遞迴遮值，
// 再對 JWT / Bearer 形狀字串做正則清除（涵蓋非 JSON body）。於攔截當下就遮，存進報告的即為已遮版本。
const SENSITIVE_KEY = /token|jwt|password|passwd|secret|authorization|refresh|api[-_]?key|credential|cookie|session/i;
function scrubTokenShapes(s) {
  return String(s)
    .replace(/eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}/g, '***jwt-redacted***')
    .replace(/(bearer\s+)[A-Za-z0-9._~+/=-]{16,}/gi, '$1***redacted***');
}
function redactBody(text) {
  if (!text) return '';
  let s = String(text);
  try {
    const walk = (v) => {
      if (Array.isArray(v)) return v.map(walk);
      if (v && typeof v === 'object') {
        const o = {};
        for (const k of Object.keys(v)) o[k] = SENSITIVE_KEY.test(k) ? '***redacted***' : walk(v[k]);
        return o;
      }
      return v;
    };
    s = JSON.stringify(walk(JSON.parse(s)));
  } catch {
    /* 非 JSON → 落到形狀遮蔽 */
  }
  return scrubTokenShapes(s);
}

// --- 工具：從 response body 嘗試抽出常見 API 包封欄位（isSuccess / returnCode）---
// 多數後端會用統一的回應包封（success 旗標 + 錯誤碼）；此處抓常見命名，換站台可調整。
function summarizeBody(text) {
  if (!text) return { isSuccess: null, returnCode: null, preview: '' };
  let json;
  try {
    json = JSON.parse(text);
  } catch {
    return { isSuccess: null, returnCode: null, preview: truncate(redactBody(text), 200) };
  }
  return {
    isSuccess: json?.isSuccess ?? json?.IsSuccess ?? null,
    returnCode: json?.returnCode ?? json?.ReturnCode ?? null,
    preview: truncate(redactBody(text), 200),
  };
}

// --- 進度輔助 ---
const TOTAL_STEPS = 6;
function step(n, msg) {
  process.stdout.write(`\n[${n}/${TOTAL_STEPS}] ${msg}\n`);
}
function bar(pct) {
  const w = 24;
  const filled = Math.round((pct / 100) * w);
  return '[' + '#'.repeat(filled) + '-'.repeat(w - filled) + `] ${String(pct).padStart(3)}%`;
}
// 在固定等待期間顯示進度條（同時持續收集 API）
async function waitWithBar(page, ms, label, getCount) {
  const start = Date.now();
  const tick = 250;
  while (Date.now() - start < ms) {
    const elapsed = Date.now() - start;
    const pct = Math.min(100, Math.round((elapsed / ms) * 100));
    process.stdout.write(`\r    ${label} ${bar(pct)}  已攔截 ${getCount()} 支 API`);
    await page.waitForTimeout(tick);
  }
  process.stdout.write(`\r    ${label} ${bar(100)}  已攔截 ${getCount()} 支 API\n`);
}

async function run() {
  const { chromium } = loadPlaywright();
  const startedAt = new Date();
  const calls = []; // 攔截到的所有請求
  const byUrl = new Map(); // url+method -> call 物件，用於配對 request/response
  let barActive = false; // 進度條顯示期間，改由進度條呈現計數，不逐筆印
  const doneCount = () => calls.filter((c) => c.status != null || c.failed).length;

  step(1, '啟動瀏覽器');
  const browser = await launchBrowser(chromium);
  // 偵測 auth.json：存在就套用登入狀態（localStorage + cookies），flow 跳過登入
  const authPath = CONFIG.AUTH_STATE ? join(__dirname, CONFIG.AUTH_STATE) : '';
  const hasAuth = !!authPath && existsSync(authPath);
  if (hasAuth) console.log(`▶ 偵測到 ${CONFIG.AUTH_STATE}，已套用登入狀態（flow 將跳過登入）`);
  const context = await browser.newContext({
    ignoreHTTPSErrors: true,
    ...(hasAuth ? { storageState: authPath } : {}),
  });
  // 還原 sessionStorage（storageState 不含）。SPA 把 Vuex/Pinia 存 sessionStorage 時，
  // 沒這步冷啟會因 store 為空而 boot 崩白頁。addInitScript 在每個頁面載入前先塞回去。
  const sessPath = CONFIG.AUTH_SESSION ? join(__dirname, CONFIG.AUTH_SESSION) : '';
  if (hasAuth && sessPath && existsSync(sessPath)) {
    const sessJson = readFileSync(sessPath, 'utf8');
    await context.addInitScript((data) => {
      try {
        const o = JSON.parse(data);
        for (const k in o) window.sessionStorage.setItem(k, o[k]);
      } catch {
        /* 還原失敗就讓 app 自行 boot */
      }
    }, sessJson);
    console.log(`▶ 已還原 sessionStorage（${CONFIG.AUTH_SESSION}）`);
  }
  const page = await context.newPage();

  function keyOf(req) {
    return req.method() + ' ' + req.url() + ' #' + req.timing?.()?.startTime;
  }

  // --- 被動攔截：對任一頁面掛 request/response 監聽（只收 xhr/fetch）---
  function attachCapture(p, pageTag) {
    p.on('request', (req) => {
      const rt = req.resourceType();
      if (rt !== 'xhr' && rt !== 'fetch') return; // 排除靜態資源
      const call = {
        pageTag, // 來源頁：主頁 / popup（多視窗流程用來分辨）
        method: req.method(),
        url: req.url(),
        resourceType: rt,
        isBackend: req.url().startsWith(CONFIG.BACKEND) || /\/api\//i.test(req.url()),
        requestHeaders: req.headers(),
        requestBody: truncate(redactBody(req.postData() || ''), 4000),
        startMs: Date.now(),
        status: null,
        statusText: '',
        durationMs: null,
        responseHeaders: null,
        responseBodyFull: '',
        responseSummary: null,
        failed: false,
        failureText: '',
      };
      calls.push(call);
      byUrl.set(req, call);
    });

    p.on('response', async (res) => {
      const call = byUrl.get(res.request());
      if (!call) return;
      call.status = res.status();
      call.statusText = res.statusText();
      call.durationMs = Date.now() - call.startMs;
      try {
        call.responseHeaders = res.headers();
      } catch {
        call.responseHeaders = null;
      }
      try {
        const text = await res.text();
        call.responseBodyFull = truncate(redactBody(text), 8000);
        call.responseSummary = summarizeBody(text);
      } catch (e) {
        call.responseBodyFull = '(body unavailable)';
        call.responseSummary = { isSuccess: null, returnCode: null, preview: '(body unavailable)' };
      }
      if (!barActive) {
        const tag = call.status >= 200 && call.status < 300 ? '✓' : '✗';
        process.stdout.write(`    ${tag} ${call.status} ${call.method} ${call.url.replace(CONFIG.BACKEND, '')}\n`);
      }
    });

    p.on('requestfailed', (req) => {
      const call = byUrl.get(req);
      if (!call) return;
      call.failed = true;
      call.failureText = req.failure()?.errorText || 'request failed';
      call.durationMs = Date.now() - call.startMs;
    });
  }

  attachCapture(page, '主頁');
  // popup / window.open 開的新分頁也一併攔截（流程圖、明細等常開新視窗）
  context.on('page', (p) => attachCapture(p, 'popup'));

  page.setDefaultTimeout(CONFIG.NAV_TIMEOUT);

  let flowResult = { success: false, error: '', summary: [] };
  try {
    // 執行使用者定義的操作流程
    const r = await flow(page, { step, authed: hasAuth });
    if (r) flowResult = { success: !!r.success, error: r.error || '', summary: r.summary || [] };

    // 流程後等網路安靜，收齊期間的 API（進度條呈現）
    await page.waitForLoadState('networkidle').catch(() => {});
    barActive = true;
    await waitWithBar(page, CONFIG.SETTLE_MS, '收集 API 中', doneCount);
    barActive = false;
  } catch (e) {
    flowResult.error = e.message;
  } finally {
    await page.waitForTimeout(500); // 收尾，讓最後的 response 配對完成
    await browser.close();
  }

  const finishedAt = new Date();
  const durationMs = finishedAt - startedAt;

  // --- 產出報告 ---
  step(6, '產生報告（Markdown + HTML）');
  const report = buildReport({ calls, flowResult, startedAt, finishedAt, durationMs });
  mkdirSync(REPORT_DIR, { recursive: true });
  const stamp = startedAt.toISOString().replace(/[:.]/g, '-').replace('T', '_').slice(0, 19);
  const base = `api-report_${stamp}`;
  const mdPath = join(REPORT_DIR, base + '.md');
  const htmlPath = join(REPORT_DIR, base + '.html');
  writeFileSync(mdPath, report.md, 'utf8');
  writeFileSync(htmlPath, report.html, 'utf8');

  // --- CLI 摘要 ---
  console.log('');
  console.log('==================== 測試完成 ====================');
  console.log(`流程結果 : ${flowResult.success ? '✅ 成功' : '❌ 失敗'}${flowResult.error ? '（' + flowResult.error + '）' : ''}`);
  for (const s of flowResult.summary) console.log(`${String(s.label).padEnd(8, '　')}: ${s.value}`);
  console.log(`API 總數 : ${report.stats.total}（成功 ${report.stats.ok} / 失敗 ${report.stats.fail}）`);
  console.log(`總耗時   : ${(durationMs / 1000).toFixed(1)}s`);
  console.log('--------------------------------------------------');
  console.log(`Markdown : ${mdPath}`);
  console.log(`HTML     : ${htmlPath}`);
  console.log('==================================================');

  process.exit(flowResult.success ? 0 : 1);
}

function buildReport({ calls, flowResult, startedAt, finishedAt, durationMs }) {
  // 統計
  const stats = {
    total: calls.length,
    backend: calls.filter((c) => c.isBackend).length,
    ok: calls.filter((c) => c.status != null && c.status >= 200 && c.status < 300).length,
    fail: calls.filter((c) => c.failed || (c.status != null && c.status >= 400)).length,
    pending: calls.filter((c) => c.status == null && !c.failed).length,
    bizFail: calls.filter((c) => c.responseSummary?.isSuccess === false).length,
  };
  const statusCount = {};
  for (const c of calls) {
    const k = c.failed ? 'FAILED' : c.status ?? 'PENDING';
    statusCount[k] = (statusCount[k] || 0) + 1;
  }

  const fmt = (d) => (d == null ? '-' : `${d}ms`);
  const shortUrl = (u) => u.replace(CONFIG.BACKEND, '').replace(CONFIG.BASE_URL, '');
  const statusBadge = (c) => {
    if (c.failed) return '❌ FAILED';
    if (c.status == null) return '⏳ PENDING';
    if (c.status >= 200 && c.status < 300) {
      if (c.responseSummary?.isSuccess === false) return `⚠️ ${c.status}`;
      return `✅ ${c.status}`;
    }
    return `❌ ${c.status}`;
  };

  // === Markdown ===
  let md = '';
  md += `# ${CONFIG.REPORT_TITLE}\n\n`;
  md += `## 環境\n\n`;
  md += `| 項目 | 值 |\n|------|----|\n`;
  md += `| 登入帳號 | \`${CONFIG.USER_ID}\` |\n`;
  md += `| 起始頁 | ${CONFIG.BASE_URL}${CONFIG.START_PATH} |\n`;
  md += `| 後端 API | ${CONFIG.BACKEND} |\n`;
  md += `| 目標頁面 | ${CONFIG.TARGET_PATH || '（預設首頁）'} |\n`;
  md += `| 開始時間 | ${startedAt.toLocaleString('zh-TW')} |\n`;
  md += `| 結束時間 | ${finishedAt.toLocaleString('zh-TW')} |\n`;
  md += `| 總耗時 | ${(durationMs / 1000).toFixed(1)}s |\n\n`;

  md += `## 流程結果\n\n`;
  md += `- 結果：${flowResult.success ? '✅ 成功' : '❌ 失敗'}\n`;
  for (const s of flowResult.summary) md += `- ${s.label}：${s.value}\n`;
  if (flowResult.error) md += `- 錯誤：\`${flowResult.error}\`\n`;
  md += `\n`;

  md += `## API 統計\n\n`;
  md += `| 指標 | 數量 |\n|------|------|\n`;
  md += `| API 呼叫總數 | ${stats.total} |\n`;
  md += `| 後端 API | ${stats.backend} |\n`;
  md += `| 成功 (2xx) | ${stats.ok} |\n`;
  md += `| 失敗 (4xx/5xx/連線) | ${stats.fail} |\n`;
  md += `| 業務失敗 (isSuccess=false) | ${stats.bizFail} |\n`;
  md += `| 未完成 | ${stats.pending} |\n\n`;
  md += `### 狀態碼分布\n\n`;
  md += `| 狀態 | 數量 |\n|------|------|\n`;
  for (const [k, v] of Object.entries(statusCount)) md += `| ${k} | ${v} |\n`;
  md += `\n`;

  md += `## API 呼叫明細\n\n`;
  md += `| # | 狀態 | 來源 | Method | URL | 耗時 | returnCode | isSuccess |\n`;
  md += `|---|------|------|--------|-----|------|-----------|-----------|\n`;
  calls.forEach((c, i) => {
    const rs = c.responseSummary || {};
    md += `| ${i + 1} | ${statusBadge(c)} | ${c.pageTag ?? '主頁'} | ${c.method} | \`${shortUrl(c.url)}\` | ${fmt(c.durationMs)} | ${rs.returnCode ?? '-'} | ${rs.isSuccess ?? '-'} |\n`;
  });
  md += `\n`;

  // 失敗 / 異常明細
  const problems = calls.filter((c) => c.failed || (c.status != null && c.status >= 400) || c.responseSummary?.isSuccess === false);
  if (problems.length) {
    md += `## ⚠️ 失敗 / 異常明細\n\n`;
    problems.forEach((c, i) => {
      md += `### ${i + 1}. ${c.method} ${shortUrl(c.url)}\n\n`;
      md += `- 狀態：${statusBadge(c)}\n`;
      if (c.failureText) md += `- 連線錯誤：\`${c.failureText}\`\n`;
      if (c.requestBody) md += `- Request：\`${c.requestBody}\`\n`;
      if (c.responseSummary?.preview) md += `- Response：\`${c.responseSummary.preview}\`\n`;
      md += `\n`;
    });
  } else {
    md += `## ⚠️ 失敗 / 異常明細\n\n（無）\n\n`;
  }

  // === HTML ===
  const html = buildHtml({ stats, statusCount, calls, flowResult, startedAt, finishedAt, durationMs, statusBadge, fmt, shortUrl, problems });

  return { md, html, stats };
}

function buildHtml({ stats, statusCount, calls, flowResult, startedAt, finishedAt, durationMs, statusBadge, fmt, shortUrl, problems }) {
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>]/g, (m) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[m]));
  const badgeClass = (c) => {
    if (c.failed || (c.status != null && c.status >= 400)) return 'bad';
    if (c.responseSummary?.isSuccess === false) return 'warn';
    if (c.status == null) return 'pend';
    return 'ok';
  };
  const rows = calls
    .map((c, i) => {
      const rs = c.responseSummary || {};
      return `<tr class="${badgeClass(c)}">
        <td>${i + 1}</td>
        <td>${esc(statusBadge(c))}</td>
        <td>${esc(c.pageTag ?? '主頁')}</td>
        <td>${esc(c.method)}</td>
        <td class="url">${esc(shortUrl(c.url))}</td>
        <td>${esc(fmt(c.durationMs))}</td>
        <td>${esc(rs.returnCode ?? '-')}</td>
        <td>${esc(rs.isSuccess ?? '-')}</td>
      </tr>`;
    })
    .join('\n');

  const problemRows = problems
    .map((c, i) => `<div class="prob">
        <h3>${i + 1}. ${esc(c.method)} ${esc(shortUrl(c.url))}</h3>
        <p>狀態：${esc(statusBadge(c))}</p>
        ${c.failureText ? `<p>連線錯誤：<code>${esc(c.failureText)}</code></p>` : ''}
        ${c.requestBody ? `<p>Request：<code>${esc(c.requestBody)}</code></p>` : ''}
        ${c.responseSummary?.preview ? `<p>Response：<code>${esc(c.responseSummary.preview)}</code></p>` : ''}
      </div>`)
    .join('\n');

  const statusRows = Object.entries(statusCount).map(([k, v]) => `<tr><td>${esc(k)}</td><td>${v}</td></tr>`).join('');

  // 可展開明細：headers / body
  const fmtHeaders = (h) => {
    if (!h || !Object.keys(h).length) return '（無）';
    return Object.entries(h)
      .map(([k, v]) => {
        let val = String(v);
        // 遮蔽機敏值：Authorization / cookie / token，只留前後幾碼
        if (/authorization|cookie|token/i.test(k) && val.length > 24) {
          val = val.slice(0, 16) + '…(' + val.length + ' chars)…' + val.slice(-6);
        }
        return `${k}: ${val}`;
      })
      .join('\n');
  };
  const prettyBody = (s) => {
    if (!s) return '（無）';
    try {
      return JSON.stringify(JSON.parse(s), null, 2);
    } catch {
      return s;
    }
  };
  const block = (title, content) => `<div class="blk"><div class="blk-t">${esc(title)}</div><pre>${esc(content)}</pre></div>`;
  const detailItems = calls
    .map((c, i) => {
      return `<details class="api ${badgeClass(c)}">
        <summary>
          <span class="st">${esc(statusBadge(c))}</span>
          <span class="mt">${esc(c.method)}</span>
          <span class="su">${esc(shortUrl(c.url))}</span>
          <span class="du">${esc(fmt(c.durationMs))}</span>
        </summary>
        <div class="api-body">
          ${block('Request Headers', fmtHeaders(c.requestHeaders))}
          ${block('Request Body', prettyBody(c.requestBody))}
          ${block('Response Headers', fmtHeaders(c.responseHeaders))}
          ${block('Response Body', c.failed ? c.failureText : prettyBody(c.responseBodyFull))}
        </div>
      </details>`;
    })
    .join('\n');

  return `<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(CONFIG.REPORT_TITLE)} — ${esc(CONFIG.USER_ID)}</title>
<style>
  /* ── Kami design tokens（紙色 / 靛藍 / 朱色，全 solid hex）── */
  :root {
    --parchment: #f5f4ed;
    --ivory: #faf9f5;
    --warm-sand: #e8e6dc;
    --brand: #1B365D;
    --brand-light: #2D5A8A;
    --brand-tint: #EEF2F7;
    --brand-tint-strong: #E4ECF5;
    --near-black: #141413;
    --olive: #504e49;
    --stone: #6b6a64;
    --charcoal: #4d4c48;
    --line: #e5e3d8;
    --warm-bg: #f1ece4;
    --vermilion: #b05c28;
    --crimson: #8a2f2f;
  }
  * { box-sizing: border-box; }
  body {
    background: var(--parchment);
    color: var(--near-black);
    font-family: 'Noto Serif TC','Source Han Serif TC', Charter, Georgia, 'Palatino Linotype', serif;
    margin: 0; padding: 48px 24px; line-height: 1.7;
  }
  .wrap { max-width: 920px; margin: 0 auto; }
  .eyebrow { font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 12px; letter-spacing: .22em;
    text-transform: uppercase; color: var(--stone); margin-bottom: 6px; }
  h1 { font-size: 30px; font-weight: 700; margin: 0 0 4px; color: var(--near-black); letter-spacing: .01em; }
  h1 .seal { color: var(--vermilion); }
  h2 { font-size: 19px; font-weight: 700; color: var(--brand); margin: 40px 0 14px;
    padding-bottom: 8px; border-bottom: 1px solid var(--line); }
  .rule { height: 2px; background: var(--brand); width: 56px; margin: 14px 0 28px; }

  .result { font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 16px; font-weight: 600;
    padding: 16px 22px; border-radius: 2px; border-left: 4px solid; background: var(--ivory); }
  .result.success { border-color: var(--brand); color: var(--brand); background: var(--brand-tint); }
  .result.fail { border-color: var(--crimson); color: var(--crimson); background: var(--warm-bg); }
  .result small { font-family: 'Noto Serif TC', serif; font-weight: 400; color: var(--charcoal); }

  .cards { display: flex; gap: 14px; flex-wrap: wrap; margin: 18px 0; }
  .card { flex: 1; min-width: 130px; background: var(--ivory); border: 1px solid var(--line);
    border-radius: 2px; padding: 18px 20px; }
  .card .n { font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 32px; font-weight: 700;
    color: var(--near-black); line-height: 1; }
  .card .lbl { font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 12px; color: var(--stone);
    margin-top: 8px; letter-spacing: .04em; }
  .card.ok .n { color: var(--brand); }
  .card.bad .n { color: var(--crimson); }
  .card.warn .n { color: var(--vermilion); }

  table { border-collapse: collapse; width: 100%; background: var(--ivory);
    font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 13.5px; border: 1px solid var(--line); }
  th, td { padding: 9px 12px; text-align: left; border-bottom: 1px solid var(--line); }
  th { background: var(--brand); color: #fff; font-weight: 600; letter-spacing: .03em; }
  tbody tr:last-child td { border-bottom: none; }
  tbody tr:nth-child(even) { background: var(--parchment); }
  td.url { font-family: 'SFMono-Regular', Consolas, monospace; word-break: break-all; max-width: 420px; color: var(--charcoal); }
  tr.bad td { background: var(--warm-bg); }
  tr.warn td { background: #f6efe6; }
  tr.bad td.url, tr.warn td.url { color: var(--near-black); }

  table.meta td:first-child { font-weight: 600; width: 140px; background: var(--warm-bg);
    color: var(--olive); font-family: 'Noto Serif TC', serif; }
  table.meta td { font-family: 'Noto Serif TC', serif; }

  code { background: var(--brand-tint); color: var(--brand); padding: 2px 6px; border-radius: 2px;
    font-family: 'SFMono-Regular', Consolas, monospace; font-size: 12.5px; word-break: break-all; }
  .prob { background: var(--ivory); border-left: 3px solid var(--vermilion); padding: 12px 20px;
    margin: 12px 0; border-radius: 0 2px 2px 0; }
  .prob h3 { margin: 0 0 8px; font-size: 15px; color: var(--vermilion); font-family: 'Noto Serif TC', serif; }
  .prob p { margin: 4px 0; font-size: 13.5px; font-family: 'Helvetica Neue', Arial, sans-serif; color: var(--charcoal); }
  .foot { margin-top: 44px; padding-top: 16px; border-top: 1px solid var(--line);
    font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 11.5px; color: var(--stone); letter-spacing: .04em; }
  .muted { font-family: 'Noto Serif TC', serif; color: var(--stone); }

  /* 可展開明細 */
  details.api { background: var(--ivory); border: 1px solid var(--line); border-left: 3px solid var(--stone);
    border-radius: 2px; margin: 8px 0; overflow: hidden; }
  details.api.ok { border-left-color: var(--brand); }
  details.api.bad { border-left-color: var(--crimson); }
  details.api.warn { border-left-color: var(--vermilion); }
  details.api > summary { list-style: none; cursor: pointer; padding: 11px 16px;
    display: flex; align-items: center; gap: 14px;
    font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 13.5px; }
  details.api > summary::-webkit-details-marker { display: none; }
  details.api > summary::before { content: '▸'; color: var(--stone); font-size: 12px; transition: transform .15s; }
  details.api[open] > summary::before { transform: rotate(90deg); }
  details.api > summary:hover { background: var(--warm-bg); }
  summary .st { min-width: 70px; font-weight: 600; }
  summary .mt { min-width: 48px; color: var(--brand); font-weight: 600; }
  summary .su { flex: 1; font-family: 'SFMono-Regular', Consolas, monospace; color: var(--charcoal); word-break: break-all; }
  summary .du { color: var(--stone); font-size: 12px; }
  .api-body { padding: 6px 16px 14px; border-top: 1px solid var(--line); background: var(--parchment); }
  .blk { margin: 12px 0; }
  .blk-t { font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 11px; letter-spacing: .12em;
    text-transform: uppercase; color: var(--stone); margin-bottom: 5px; }
  .blk pre { margin: 0; background: var(--ivory); border: 1px solid var(--line); border-radius: 2px;
    padding: 10px 12px; font-family: 'SFMono-Regular', Consolas, monospace; font-size: 12.5px;
    line-height: 1.55; color: var(--near-black); white-space: pre-wrap; word-break: break-word;
    max-height: 360px; overflow: auto; }
</style>
</head>
<body>
<div class="wrap">

<div class="eyebrow">${esc(CONFIG.REPORT_EYEBROW)}</div>
<h1><span class="seal">朱</span> ${esc(CONFIG.REPORT_TITLE)}</h1>
<div class="rule"></div>

<div class="result ${flowResult.success ? 'success' : 'fail'}">
  流程${flowResult.success ? '成功' : '失敗'}${flowResult.error ? '（' + esc(flowResult.error) + '）' : ''}
  ${flowResult.summary.length ? '<br><small>' + flowResult.summary.map((s) => esc(s.label) + ' ' + esc(s.value)).join('　·　') + '</small>' : ''}
</div>

<h2>環境</h2>
<table class="meta">
  <tr><td>登入帳號</td><td><code>${esc(CONFIG.USER_ID)}</code></td></tr>
  <tr><td>起始頁</td><td>${esc(CONFIG.BASE_URL + CONFIG.START_PATH)}</td></tr>
  <tr><td>後端 API</td><td>${esc(CONFIG.BACKEND)}</td></tr>
  <tr><td>目標頁面</td><td>${esc(CONFIG.TARGET_PATH || '（預設首頁）')}</td></tr>
  <tr><td>開始時間</td><td>${esc(startedAt.toLocaleString('zh-TW'))}</td></tr>
  <tr><td>結束時間</td><td>${esc(finishedAt.toLocaleString('zh-TW'))}</td></tr>
  <tr><td>總耗時</td><td>${(durationMs / 1000).toFixed(1)}s</td></tr>
</table>

<h2>API 統計</h2>
<div class="cards">
  <div class="card"><div class="n">${stats.total}</div><div class="lbl">API 總數</div></div>
  <div class="card ok"><div class="n">${stats.ok}</div><div class="lbl">成功 2xx</div></div>
  <div class="card bad"><div class="n">${stats.fail}</div><div class="lbl">失敗 4xx/5xx</div></div>
  <div class="card warn"><div class="n">${stats.bizFail}</div><div class="lbl">業務失敗</div></div>
  <div class="card"><div class="n">${stats.backend}</div><div class="lbl">後端 API</div></div>
</div>
<table>
  <thead><tr><th>狀態碼</th><th>數量</th></tr></thead>
  <tbody>${statusRows}</tbody>
</table>

<h2>API 呼叫總覽</h2>
<table>
  <thead><tr><th>#</th><th>狀態</th><th>來源</th><th>Method</th><th>URL</th><th>耗時</th><th>returnCode</th><th>isSuccess</th></tr></thead>
  <tbody>${rows}</tbody>
</table>

<h2>API 明細（點擊展開 Header / Body）</h2>
${detailItems}

<h2>失敗 / 異常明細</h2>
${problems.length ? problemRows : '<p class="muted">（無）</p>'}

<div class="foot">由 test.mjs 自動產生　·　Kami preset</div>
</div>
</body>
</html>`;
}

// --- 預覽模式（PREVIEW=1）：用假資料直接產報告，驗證版型，不開瀏覽器 ---
function previewRun() {
  const now = new Date();
  const mk = (method, url, status, dur, isSuccess, returnCode, failed, pageTag = '主頁') => ({
    pageTag, method, url, resourceType: 'fetch', isBackend: true,
    requestHeaders: {
      'content-type': 'application/json',
      authorization: 'Bearer eyJhbGciOiJIUzI1NiJ9.' + 'x'.repeat(7600) + '.sig123',
      accept: 'application/json',
    },
    requestBody: method === 'POST' ? '{"userId":"sample.user","sample":true}' : '',
    startMs: 0, status: failed ? null : status, statusText: '', durationMs: dur,
    responseHeaders: { 'content-type': 'application/json; charset=utf-8', server: 'Kestrel' },
    responseBodyFull: failed
      ? '(body unavailable)'
      : JSON.stringify({ isSuccess, returnCode, data: { count: 3, items: [1, 2, 3] } }),
    responseSummary: { isSuccess, returnCode, preview: '{"isSuccess":' + isSuccess + '}' },
    failed: !!failed, failureText: failed ? 'net::ERR_CONNECTION_REFUSED' : '',
  });
  const calls = [
    mk('GET', CONFIG.BACKEND + '/health', 200, 21917, true, null, false),
    mk('POST', CONFIG.BACKEND + '/api/auth/login', 200, 475, true, null, false),
    mk('POST', CONFIG.BACKEND + '/api/auth/getLoginUser', 200, 607, true, 'SYS_001', false),
    mk('POST', CONFIG.BACKEND + '/api/home/getTodoData', 200, 664, false, 'TODO_003_01', false),
    mk('POST', CONFIG.BACKEND + '/api/flow/getFlowChart', 200, 540, true, null, false, 'popup'),
    mk('POST', CONFIG.BACKEND + '/api/common/foo', 500, 1200, null, null, false),
  ];
  const flowResult = {
    success: true,
    error: '',
    summary: [
      { label: '登入帳號', value: CONFIG.USER_ID },
      { label: 'Token 長度', value: 7645 },
      { label: '落地頁面', value: CONFIG.BASE_URL + '/app/list' },
    ],
  };
  const report = buildReport({ calls, flowResult, startedAt: now, finishedAt: now, durationMs: 25000 });
  mkdirSync(REPORT_DIR, { recursive: true });
  const p = join(REPORT_DIR, 'preview.html');
  writeFileSync(p, report.html, 'utf8');
  writeFileSync(join(REPORT_DIR, 'preview.md'), report.md, 'utf8');
  console.log('預覽報告已產生：' + p);
}

// 防呆：flow 裡懸空的 promise（如未 await 的 waitForEvent('popup')）若 reject，
// 預設會讓 Node 直接 crash、連報告都來不及寫。攔下來只記錄，不終止程序，
// 讓 run() 的 try/catch + 報告產出一定跑完。
process.on('unhandledRejection', (reason) => {
  console.warn('    [warn] 未捕捉的 promise rejection（已忽略，不影響報告）:', reason?.message || reason);
});

if (process.env.PREVIEW === '1') {
  previewRun();
} else {
  run().catch((e) => {
    console.error('測試執行失敗：', e);
    process.exit(2);
  });
}
