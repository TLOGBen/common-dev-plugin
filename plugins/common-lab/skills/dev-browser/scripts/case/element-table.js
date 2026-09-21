// 可操作元素編號表 — 給 jev-pick.mjs 用（Lab）
// 完整說明：references/case-jev-pick.md
//
// 用法（連線與 dev-browser 其他 template 相同）：
//   PowerShell：dev-browser --connect http://127.0.0.1:9222 run ${CLAUDE_PLUGIN_ROOT}\skills\dev-browser\scripts\case\element-table.js
//   WSL2：      dev-browser --connect http://${HOST_IP}:9333 run ${CLAUDE_PLUGIN_ROOT}/skills/dev-browser/scripts/case/element-table.js
//
// 產出：~/.dev-browser/tmp/elements.json，並在每個元素掛上 data-jev-idx，
// 之後可用 page.locator('[data-jev-idx="7"]') 直接操作同一個節點。
// 頁面換頁或重新 render 後編號會失效，要重跑本腳本。

const MAX_ELEMENTS = 254;  // Jev 一題 Choice 最多 255 個選項，留 1 個給「none」
const VALUE_MAX = 40;      // 欄位值截斷長度；password 一律遮蔽

const page = await browser.getPage("app");

const elements = await page.evaluate(({ MAX_ELEMENTS, VALUE_MAX }) => {
  const SELECTOR = [
    'a[href]', 'button', 'input:not([type="hidden"])', 'select', 'textarea', 'summary',
    '[role="button"]', '[role="link"]', '[role="combobox"]', '[role="textbox"]', '[role="checkbox"]',
    '[role="radio"]', '[role="switch"]', '[role="tab"]', '[role="menuitem"]', '[role="option"]',
    '[contenteditable="true"]',
  ].join(',');
  const clean = (s, n) => (s || '').replace(/\s+/g, ' ').trim().slice(0, n);

  document.querySelectorAll('[data-jev-idx]').forEach((el) => el.removeAttribute('data-jev-idx'));

  const visible = (el) => {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) return false;
    const cs = getComputedStyle(el);
    return cs.visibility !== 'hidden' && cs.display !== 'none' && cs.opacity !== '0';
  };

  const nameOf = (el) => {
    const labelled = el.getAttribute('aria-labelledby');
    const byId = labelled && labelled.split(/\s+/).map((id) => document.getElementById(id)?.innerText).join(' ');
    const label = el.labels && el.labels.length ? el.labels[0].innerText : '';
    return clean(
      el.getAttribute('aria-label') || byId || label || el.getAttribute('placeholder') ||
      el.innerText || el.getAttribute('title') || el.getAttribute('alt') || el.getAttribute('name'),
      80,
    );
  };

  const valueOf = (el) => {
    if (el.type === 'password') return el.value ? '***' : 'empty';
    if (el.type === 'checkbox' || el.type === 'radio') return el.checked ? 'checked' : 'unchecked';
    if (el.tagName === 'SELECT') return clean(el.selectedOptions[0]?.text, VALUE_MAX) || 'empty';
    if ('value' in el && el.tagName !== 'BUTTON') return clean(el.value, VALUE_MAX) || 'empty';
    return '';
  };

  const out = [];
  for (const el of document.querySelectorAll(SELECTOR)) {
    if (out.length >= MAX_ELEMENTS) break;
    if (!visible(el)) continue;
    const idx = out.length + 1;
    el.setAttribute('data-jev-idx', String(idx));
    out.push({
      idx,
      role: el.getAttribute('role') || (el.tagName === 'INPUT' ? `input:${el.type}` : el.tagName.toLowerCase()),
      name: nameOf(el),
      value: valueOf(el),
      disabled: !!(el.disabled || el.getAttribute('aria-disabled') === 'true'),
    });
  }
  return out;
}, { MAX_ELEMENTS, VALUE_MAX });

const payload = { url: page.url(), title: await page.title(), capturedAt: new Date().toISOString(), elements };
await writeFile("elements.json", JSON.stringify(payload, null, 2));

console.log(`elements.json：${elements.length} 個可操作元素（上限 ${MAX_ELEMENTS}）→ ~/.dev-browser/tmp/elements.json`);
for (const e of elements.slice(0, 15)) {
  console.log(`[${e.idx}] ${e.role} ${e.name}${e.value ? ' · ' + e.value : ''}${e.disabled ? ' (disabled)' : ''}`);
}
if (elements.length > 15) console.log(`...（其餘 ${elements.length - 15} 個見 elements.json）`);
