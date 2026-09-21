// window.open 新分頁操作
// 完整說明：references/case-new-tab.md
//
// 用法（WSL2，先跑 setup-wsl2-chrome-debug.sh；來源頁受保護時才先跑 login.js）：
//   HOST_IP=$(ip route show default | awk '/default/ {print $3; exit}')
//   dev-browser --connect http://${HOST_IP}:9333 run ${CLAUDE_PLUGIN_ROOT}/skills/dev-browser/scripts/case/new-tab.js
//
// ▶ 兩種模式（改 USE_REAL_TAB 切換）：
//   USE_REAL_TAB = false  → Method A：攔截 window.open，用 getPage(name) 建持久分頁（Chrome 不開真實 tab）
//   USE_REAL_TAB = true   → Method B：讓 Chrome 真的開新分頁，用 listPages() + getPage(targetId) 接手
//
// API 以當前 `dev-browser --help` 為準。

// === 編輯此區 ===
const SOURCE_URL     = 'http://localhost:3000/app/detail/123';  // 範例路由，請改成你自己站台的來源頁
const TAB_TO_CLICK   = '流程圖';                 // 進入 SOURCE_URL 後要先點的分頁 tab（空字串=不切換）
const CLICK_KEYWORD  = 'ID-';                    // 點擊目標元素包含的文字
const NEW_TAB_NAME   = 'new-tab';                // Method A 用：新分頁命名
const USE_REAL_TAB   = true;                     // true = Method B（真實開分頁）；false = Method A（攔截）
// ================

const page = await browser.getPage("app");

// 導航到來源頁
await page.goto(SOURCE_URL, { waitUntil: "domcontentloaded" });
await page.waitForTimeout(2000);

// 若有要切換的 tab，先切換
if (TAB_TO_CLICK) {
  await page.evaluate((tabName) => {
    for (const t of document.querySelectorAll('[role="tab"]')) {
      if (t.textContent.includes(tabName)) { t.click(); return; }
    }
  }, TAB_TO_CLICK);
  await page.waitForTimeout(1000);
}

// 確認目標元素存在
const targetExists = await page.evaluate((keyword) => {
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
  let node;
  while ((node = walker.nextNode())) {
    if (getComputedStyle(node).cursor === 'pointer' && node.textContent.includes(keyword)) {
      return node.textContent.trim().substring(0, 80);
    }
  }
  return null;
}, CLICK_KEYWORD);

if (!targetExists) throw new Error(`找不到包含 "${CLICK_KEYWORD}" 且 cursor:pointer 的元素`);
console.log('目標元素:', targetExists);

let resultUrl, newTab;

if (USE_REAL_TAB) {
  // ─── Method B：真實開分頁，透過 targetId 接手 ──────────────────────────
  const beforeIds = new Set((await browser.listPages()).map((p) => p.id));

  await page.evaluate((keyword) => {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
    let node;
    while ((node = walker.nextNode())) {
      if (getComputedStyle(node).cursor === 'pointer' && node.textContent.includes(keyword)) {
        node.click();
        return;
      }
    }
  }, CLICK_KEYWORD);

  let opened = null;
  for (let i = 0; i < 20 && !opened; i++) {
    await page.waitForTimeout(250);
    opened = (await browser.listPages()).find((p) => !beforeIds.has(p.id)) ?? null;
  }
  if (!opened) throw new Error('未偵測到 window.open 新分頁');

  newTab = await browser.getPage(opened.id);
  await newTab.waitForLoadState('domcontentloaded');
  await newTab.waitForTimeout(2000);
  resultUrl = newTab.url();

} else {
  // ─── Method A：攔截 window.open ─────────────────────────────────────────
  await page.evaluate(() => {
    window._newTabUrl = null;
    window.open = (url) => { window._newTabUrl = url; };
  });

  await page.evaluate((keyword) => {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
    let node;
    while ((node = walker.nextNode())) {
      if (getComputedStyle(node).cursor === 'pointer' && node.textContent.includes(keyword)) {
        node.click();
        return;
      }
    }
  }, CLICK_KEYWORD);

  await page.waitForTimeout(300);
  const interceptedUrl = await page.evaluate(() => window._newTabUrl);
  if (!interceptedUrl) throw new Error('未攔截到 window.open，請確認目標元素觸發了 window.open');

  const fullUrl = interceptedUrl.startsWith('http')
    ? interceptedUrl
    : 'http://localhost:3000' + interceptedUrl;

  newTab = await browser.getPage(NEW_TAB_NAME);
  await newTab.goto(fullUrl, { waitUntil: "domcontentloaded" });
  await newTab.waitForTimeout(2000);
  resultUrl = newTab.url();
}

// ─── 驗證與輸出 ─────────────────────────────────────────────────────────────
const hasJWT  = await newTab.evaluate(() => !!localStorage.getItem('jwtToken'));  // jwtToken 僅為範例 key，請改成你站台實際的 token key
const hasVuex = await newTab.evaluate(() => !!sessionStorage.getItem('vuex'));
const snap    = await newTab.snapshotForAI();

console.log(JSON.stringify({
  mode:     USE_REAL_TAB ? 'Method B (real tab by targetId)' : 'Method A (intercept)',
  newTabUrl: resultUrl,
  hasJWT,
  hasVuex,   // 真實 window.open tab 通常會複製 opener 的 sessionStorage
  snapshot:  snap.full.substring(0, 600),
}, null, 2));
