// 逐步視覺勘查工具（gen-e2e-record Stage 4 用）
// ---------------------------------------------------------------------------
// 逐行「重播」recording.js 的每個動作，每執行一步就：
//   1) 截圖到 reports/walk_<n>.png（截「該動作所在的視窗」，popup 也截得到）
//   2) 印出當下 URL + 動作 + 目標元素真實樣貌（tag / chip? / icon class /
//      aria-expanded / 命中數）
// 某一步定位失敗（脆弱 selector 已壞）→ 自動 dump 候選 selector。
//
// ⭐ 支援多視窗 / popup：codegen 對「從錄製視窗點出來的子 popup」會錄成
//    `const page1 = await page.waitForEvent('popup')` + 一串 `page1.*` 動作。
//    本工具保留這些行原樣重播，並對正確的視窗（page / page1 / …）截圖，
//    這樣 popup 裡的步驟（簽辦流程圖 / 表單流程圖之類）也看得到、不會被漏掉。
//
// 目的：把「轉換前先看畫面」自動化，取代每次手寫探測腳本。看完逐步輸出，
//       就能在寫 flow 前把每步 selector 與畫面現實（預設展開的面板、chip vs
//       button、icon class、帳號有沒有資料、popup 視窗）全部定案。
//
// 用法（同 test.mjs 執行環境；headless）：
//   PW_DEPS=<abs> node walk.mjs
//   RECORDING=other.js PW_DEPS=<abs> node walk.mjs
//   STOP_ON_FAIL=1 ...                          # 第一個失敗步就停
//
// 環境變數：RECORDING / PW_DEPS / STOP_ON_FAIL / HEADLESS（=0 顯示瀏覽器）
//
// ⚠️ 信任邊界：用 new Function 重播 recording.js 的動作行。recording.js 是使用者
//    自己用 codegen 錄出的檔案（與雙擊 record.bat 同信任層級、在本機跑），屬可信
//    輸入。本機開發診斷工具，**不可**拿去重播來路不明 / 外部來源的腳本。
// ---------------------------------------------------------------------------

import { createRequire } from 'node:module';
import { readFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
const require = createRequire(import.meta.url);

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

const RECORDING = process.env.RECORDING || 'recording.js';
const STOP_ON_FAIL = process.env.STOP_ON_FAIL === '1';

// 抽出 recording IIFE 裡的「動作 / popup 綁定」行，排除 browser/context 建置與收尾、close()
const raw = readFileSync(RECORDING, 'utf8')
  .split('\n')
  .map((l) => l.trim())
  .filter(Boolean)
  .filter((l) => !l.startsWith('//') && !l.startsWith('/*') && !l.startsWith('*'));

const SETUP = /chromium|browser\s*=|context\s*=|newContext|newPage|require\(|async\s*\(\)|\}\)\(\)|^\{|^\}/;
const lines = raw.filter(
  (l) =>
    !SETUP.test(l) &&
    !/\.close\(\)/.test(l) && // 不重播 close，留著視窗好截圖
    (/^await\s+\w+\./.test(l) || // 動作：await page.* / await page1.*
      /^const\s+\w+\s*=\s*\w+\.waitForEvent\(/.test(l) || // popup 綁定 promise
      /^const\s+\w+\s*=\s*await\s+/.test(l)), // popup 取得
);

if (!lines.length) {
  console.error(`[walk] ${RECORDING} 裡找不到可重播的動作行`);
  process.exit(2);
}

mkdirSync('reports', { recursive: true });
const actionCount = lines.filter((l) => /^await\s+\w+\./.test(l)).length;
console.log(`[walk] 重播 ${RECORDING}，動作 ${actionCount} 步（含 popup 綁定行）\n`);

const { chromium } = loadPlaywright();
const browser = await chromium.launch({ channel: 'chrome', headless: process.env.HEADLESS !== '0' });
const context = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1600, height: 900 } });
const page = await context.newPage();
context.on('page', (p) => console.log('   >> 偵測到新 popup 視窗:', p.url()));

function targetText(line) {
  const m =
    line.match(/getByText\(\s*['"`]([^'"`]+)['"`]/) ||
    line.match(/name:\s*['"`]([^'"`]+)['"`]/) ||
    line.match(/description:\s*['"`]([^'"`]+)['"`]/) ||
    line.match(/hasText:\s*['"`]([^'"`]+)['"`]/);
  return m ? m[1] : '';
}

// 失敗時 dump 候選 selector（對指定視窗 pg）
async function diag(label, pg) {
  if (!label || !pg) {
    console.log('   （無法解析目標文字或視窗，略過候選 dump）');
    return;
  }
  const variants = {
    [`getByRole button name=${label}`]: pg.getByRole('button', { name: label }),
    [`getByRole button description=${label}`]: pg.getByRole('button', { description: label, exact: true }),
    [`getByRole tab name=${label}`]: pg.getByRole('tab', { name: label }),
    [`getByText ${label}`]: pg.getByText(label, { exact: false }),
    [`.v-chip hasText=${label}`]: pg.locator('.v-chip', { hasText: label }),
  };
  for (const [k, loc] of Object.entries(variants)) {
    console.log('     候選', k, '->', await loc.count().catch(() => 'err'));
  }
  const icons = await pg
    .locator('.v-data-table tbody tr, .v-data-table-server tbody tr')
    .first()
    .locator('button')
    .evaluateAll((els) => els.map((el) => (el.querySelector('i') || {}).className || '(no i)'))
    .catch(() => []);
  if (icons.length) console.log('     第一列按鈕 icon:', JSON.stringify(icons));
}

let snapN = 0;
// 對「動作所在視窗 pg」截圖 + dump 目標元素
async function snap(line, pg) {
  const i = snapN++;
  if (!pg || pg.isClosed?.()) {
    console.log(`[${i + 1}] （視窗不存在/已關，可能前一步觸發 popup 的點擊失敗）動作: ${line}`);
    return;
  }
  const which = pg === page ? 'page(主)' : 'popup';
  const png = `reports/walk_${String(i).padStart(2, '0')}.png`;
  await pg.screenshot({ path: png, fullPage: true }).catch(() => {});
  const label = targetText(line);
  let info = '';
  if (label) {
    const probe = await pg
      .evaluate((t) => {
        const hit = [...document.querySelectorAll('*')].find(
          (e) => e.children.length === 0 && (e.innerText || '').trim() === t,
        );
        if (!hit) return null;
        const btn = hit.closest('button,[role=button],[role=tab]');
        return {
          tag: hit.tagName,
          chip: !!hit.closest('.v-chip'),
          ctrl: btn ? btn.getAttribute('role') || 'button' : '',
          icon: (btn && btn.querySelector('i') && btn.querySelector('i').className) || '',
          ariaExpanded: hit.closest('[aria-expanded]')
            ? hit.closest('[aria-expanded]').getAttribute('aria-expanded')
            : '',
        };
      }, label)
      .catch(() => null);
    info = probe ? ` | 元素=${JSON.stringify(probe)}` : ` | （找不到文字「${label}」可見節點）`;
  }
  console.log(`[${i + 1}] 視窗=${which} URL=${pg.url()}\n   動作: ${line}${info}\n   截圖: ${png}`);
}

// 組重播 body：popup 綁定行原樣保留；動作行包 try/catch + 對該視窗截圖
const body = lines
  .map((l) => {
    if (/^const\s+\w+\s*=/.test(l)) {
      // popup 綁定行加 timeout + catch，避免觸發 popup 的點擊失敗時苦等 30s／拋未捕捉錯誤
      const safe = l.replace(
        /waitForEvent\(\s*(['"`]popup['"`])\s*\)/,
        'waitForEvent($1, { timeout: 8000 }).catch(() => null)',
      );
      return `  ${safe}`;
    }
    const pgVar = (l.match(/^await\s+(\w+)\./) || [, 'page'])[1];
    const enc = JSON.stringify(l);
    return `  try { ${l} await ${pgVar}.waitForTimeout(1200); } catch (e) {\n    console.log('   ✗ 失敗:', String(e.message).split('\\n')[0]);\n    await __diag(__target(${enc}), ${pgVar});\n    if (${STOP_ON_FAIL}) { throw e; }\n  }\n  await __snap(${enc}, ${pgVar});`;
  })
  .join('\n');

const runner = new Function('page', '__snap', '__diag', '__target', `return (async () => {\n${body}\n})()`);

try {
  await runner(page, snap, diag, targetText);
  console.log('\n[walk] 重播完成。逐步截圖在 reports/walk_*.png（含 popup 視窗）。據此填 selector 規劃表後再寫 flow。');
} catch (e) {
  console.log('\n[walk] 在某步停止（STOP_ON_FAIL）。修正該步定位後重跑。');
} finally {
  await browser.close();
}
