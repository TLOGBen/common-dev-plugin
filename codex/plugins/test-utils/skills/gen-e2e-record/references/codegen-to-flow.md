# recording.js → gen-e2e-test flow() 轉換規則

> **目錄**（head -100 預讀也要看得到全貌）
> - §0 逐步視覺勘查 — 轉換前先用 walk.mjs 看真實畫面、定案規劃表（test-template 查詢起手）
> - §1 codegen --target javascript 長相
> - §2 轉換步驟 — 抽動作、揪脆弱定位、CONFIG、step()、expect 轉非斷言檢查、success 非恆真規則
> - §3 動作對應表 — 幾乎 1:1（expect 轉檢查、waitForTimeout 改條件等待）
> - §4 登入段 — 機制換穩定片段、帳號保留錄製帳號
> - §5 轉換範例骨架 — 含條件等待與非恆真 success 示範
> - §5b codegen 會漏掉什麼 — 捲動 / hover / 等待 / tooltip-description selector 雷、inspect.mjs
> - §6 轉完之後 — 複製 assets、驗證、交付（含最關鍵環境眉角）
> - §7 第二視窗 / popup — 最容易整段漏掉的轉換雷

把 Playwright codegen 錄出的 `recording.js` 轉成 `gen-e2e-test` 的 `flow(page, { step })`。動作行用的是同一個 `page` 物件，搬起來看似 1:1——**但「看似可直接搬」正是陷阱**。codegen 記得下「點了什麼」，記不到決定成敗的畫面現實（預設展開的面板、chip vs button、icon class、登入帳號有沒有對應資料）。

所以這份文件的真正主張是：**先做 §0 逐步視覺勘查、親眼看過每一步畫面、把 selector 定案，再依規劃表寫 flow**。不要把 recording.js 直接翻譯成 flow，然後靠跑失敗、看 timeout、回頭補的方式收斂。翻譯 + 試錯會把「看一眼就知道」的事拖成好幾輪失敗——而那些事讀檔本來就讀不到，只有看畫面才看得到。

> **站台事實另存**：本文件談的是通用做法。每個站台自己的登入片段、環境眉角、跑過的流程、難搞 selector，都沉澱在專案的 `.claude/test-template/` 記憶庫。動手前先用 `query.py` 查本站台有沒有現成 template（見 §0），有就照用，沒有就照通用原則做、做完把可重用的部分沉澱回去。

---

## 0. 逐步視覺勘查（轉換前先做，對抗「直接動手」的慣性）

模型的預設慣性，是把 recording.js 一行行翻成 flow，再開始跑、跑壞了才回頭修。這份文件要你反過來：**寫任何一行 flow 之前，先逐步看過每個錄製動作的真實畫面**，把每一步定案成規劃表。理由很簡單——畫面上的現實（這是 chip 不是文字、這個面板已經展開、這顆按鈕的 aria 只有 hover 才在）讀檔看不到，看畫面卻一眼就懂。先看懂再寫，等於把「翻譯 + N 輪試錯」換成「看懂 + 一次寫對」。

### Stage 0 起手：先查 test-template

先確認專案根有沒有 `.claude/test-template/`：

- **沒有** → 先跑該 skill 的 init 腳本把記憶庫鋪好，再繼續。
- **有** → 用 query.py 查本站台是否已有可用 template：

```bash
python .claude/test-template/query.py [關鍵字] --site <站台代號> --kind login
python .claude/test-template/query.py [關鍵字] --site <站台代號> --kind env
python .claude/test-template/query.py [關鍵字] --site <站台代號> --kind flow
python .claude/test-template/query.py [關鍵字] --site <站台代號> --kind selector
```

命中的 login / env / flow / selector template 直接 Read 載入照用——別人已經踩過的雷不必再踩一次。查不到就照下面的通用原則做，做完把這次學到的（穩定登入片段、難搞 selector、跑通的流程）沉澱成新 template 回 `.claude/test-template/`。

### 用 walk.mjs 逐步重播

`assets/walk.mjs`（bundle 在錄製器資料夾裡）逐行重播 `recording.js`，每個動作後截圖 `reports/walk_<n>.png` + 印出當下 URL、動作、目標元素真實樣貌（tag / 是不是 chip / icon class / aria-expanded / 命中數）；某行失敗自動 dump 候選 selector。

```bash
# 同 test.mjs 執行環境（跨平台橋接的眉角見站台 env template）
PW_DEPS=<abs> node walk.mjs
```

逐一看 `walk_*.png` 與輸出，把每步定案進**規劃表**：

| # | 錄製動作 | 真實畫面觀察（walk 輸出 + 截圖） | 定案 selector | 注意事項 |
|---|---------|--------------------------------|--------------|---------|
| 2 | `getByText('<某分頁標籤>')` | 其實是 chip，標籤含筆數尾碼；上層面板已 `aria-expanded=true` | chip hasText '<標籤>' | 面板預設展開，別再點它（再點＝摺疊，chip 反而消失） |
| 3 | `button{description:'<動作>'}.nth(1)` | icon 按鈕，icon class 為 `mdi-...` | `tr button:has(i.mdi-...)` | description 來自 hover tooltip，沒 hover 時命中 0 |

（上表欄位是通用範式；填進去的值因站台而異，定案後值得沉澱成站台的 selector template。）

### 勘查時就要主動攤開的「畫面現實」

這些都不在 recording.js 裡，等跑失敗才發現就是在試錯。勘查時逐項確認：

- **登入帳號對不對**：流程要的待辦 / 權限 / 資料綁在哪個帳號？walk 重播的就是使用者錄製當下登入的那個帳號。若把它換成「萬用 / 管理員帳號」，那個帳號常常**沒有**這條流程要的那筆待辦或資料 → 整列空白、流程走不完，或更糟：開到的是別人的資料，畫面照樣綠，但測的根本不是使用者錄的東西。帳號是流程能否成立的**前提**，不是可隨手替換的細節（詳見 §4）。
- **預設展開的面板**（`aria-expanded=true`）→ 別再點它，再點等於摺疊。
- **chip / link / icon button vs 純文字**：`getByText` 命中的常是 chip 或連結，不是純文字節點，後續定位邏輯會差很多。
- **需要捲動 / hover / 等資料**才會出現或可點的步驟（見 §5b）。
- **會開新視窗（popup）的點擊**（見 §7）。

> 看完規劃表、整條流程都有把握了，才進 §2 轉換。若勘查中發現某步根本到不了（無資料 / 無權限）→ 立刻停下來問使用者要對的帳號 / 測試單據，不要硬寫一個跑得過但測錯東西的版本。

---

## 1. codegen --target javascript 長相

codegen 產出大致長這樣（站台不同、selector 不同，骨架一致）：

```js
const { test, expect } = require('@playwright/test');

test('test', async ({ page }) => {
  await page.goto('https://<host>/<login-path>');
  // ...錄製的登入動作...
  await page.goto('https://<host>/<目標頁>');
  await page.getByRole('button', { name: '查詢' }).click();
  await expect(page.getByRole('cell', { name: '...' }).first()).toBeVisible();
});
```

要的就是 `test(...)` 大括號裡那串動作行。

---

## 2. 轉換步驟

1. **抽出動作序列**：取 `test('...', async ({ page }) => {`（或錄製器 IIFE）與對應收尾之間的所有動作行。
   - ⚠️ **不是只取 `await page.*`**：popup 流程會有 `const page1Promise = page.waitForEvent('popup')`、`const page1 = await page1Promise`、`await page1.*`——這些**沒有 `await page.` 前綴，最容易被漏掉**，漏了＝產出的測試點完那顆鈕就停、popup 裡的操作與 API 全失（見 §7）。**全部保留**。
1b. **先揪 codegen 的脆弱定位**。轉換前先 grep：

```bash
grep -nE "getByRole\([^)]*description:|getByText\(" recording.js
```

凡 `getByRole(..., { description: ... })`（這 description 來自 hover tooltip 的 aria）一律視為**不穩、跑起來常命中 0**，改成結構 / icon 定位（見 §5b）。不確定該頁實際長怎樣 → 用 `inspect.mjs` 列候選（見 §5b 末）。

2. **CONFIG**：
   - `BASE_URL` ＝ 第一個 `page.goto` 的 origin。
   - `START_PATH` ＝ 第一個 goto 的 path。
   - `BACKEND` ＝ 使用者提供（攔 API 報告用；預設值見站台 env template）。
   - 後續的 `page.goto(絕對網址)` → 改成 `page.goto(CONFIG.BASE_URL + '<path>')`，讓網址集中管理。
3. **插 step() 階段**：依語意分段，每段前加 `step(n, '說明')`（n 從 2 開始，1 已被引擎的「啟動瀏覽器」用掉）。分段點通常是 `goto`、送出類 `click`（按鈕含「查詢 / 送出 / 儲存 / 登入」）。
4. **清雜訊**（codegen 常見）：
   - 移除 `const { test, expect } = require(...)` 與 `test(...)` 外殼。
   - 錄到的 `await expect(...)` **不刪除**：轉成等價的非斷言檢查（如 `await loc.waitFor({ state: 'visible' })`、`await page.waitForResponse(...)`），並把檢查結果納入 `success` 判定（見第 6 點）。codegen 錄下的 expect 是使用者親眼確認過的驗證意圖，丟掉等於放棄擋假綠的依據。
   - 連續對同一元素的 `click()` 後緊接 `fill()`，`click()` 可保留（codegen 慣例，無害）。
   - 合併重複 `waitForTimeout`；不要保留 codegen 偶發的 `page.waitForLoadState`（引擎已有 settle）。
5. **回傳**：`return { success, summary }`。
6. **summary / success 啟發式**：
   - ⛔ **每條 flow 的 `success` 至少含一個非恆真條件**：`rowCount >= 0`、「URL 不含 login」這類恆真 / 弱條件**單獨使用就是假綠**。success 必須綁流程的關鍵結果（查詢筆數 > 0、目標元素可見、popup 已開等——來源通常就是 expect 轉成的檢查）。
   - 「URL 已離開登入頁」只能當**輔助**條件疊加，不可單獨成立；summary 放關鍵資訊（落地頁面、輸入的關鍵值、登入帳號）。
   - 有資料表的查詢流程：在結尾 `page.evaluate` 抓筆數放進 summary，並以 `rowCount > 0` 之類的條件參與 success（見下方範例）。

---

## 3. 動作對應表（幾乎 1:1）

| codegen | flow 裡 | 備註 |
|---------|---------|------|
| `await page.goto('https://host/p')` | `await page.goto(CONFIG.BASE_URL + '/p', { waitUntil: 'domcontentloaded' })` | 絕對網址改用 BASE_URL 串接 |
| `await page.getByRole('button', { name: 'X' }).click()` | 原樣保留 | 送出類前加 `step()` |
| `await page.getByRole('textbox', { name: 'X' }).fill('v')` | 原樣保留 | 帳密類值改用 `CONFIG.USER_ID/PASSWORD` |
| `await page.locator('sel').click()/fill()` | 原樣保留 | — |
| `await page.getByLabel('X').selectOption('v')` | 原樣保留 | — |
| `await expect(...)` | **轉成等價非斷言檢查**（`await loc.waitFor({ state: 'visible' })` 等），結果納入 `success` | 不刪驗證意圖；flow 不放會丟例外的斷言 |
| `await page.waitForTimeout(n)` | 盡量改條件等待（`loc.waitFor()` / `waitForResponse` / `waitForLoadState`） | 真的無具體目標可等才保留，並加注釋說明原因 |

---

## 4. 登入段：穩定「機制」，但**保留錄製的帳號**

這裡要把兩件事分開想，因為它們的最佳策略剛好相反：

- **登入機制**（怎麼點到登入完成）——可以、也應該換成穩定寫法。codegen 對動態 class 框架（元件庫自動生成、每次 render 可能變的 class）錄出的登入 selector 很脆，照搬常一跑就壞。所以機制改用站台 login template 裡那段驗證過的穩定片段。
- **登入帳號**（登的是誰）——**不能**隨手換成萬用 / 管理員帳號。帳號是這條流程的**資料依賴**：流程要的待辦、權限、那筆單據，都綁在錄製當下登入的那個人身上。換帳號＝換了一整組前提，測出來的常是「畫面綠、但走的是另一條流程」的假成功。

模型的慣性是「反正 admin 權限最廣，登它最保險」——這正好是要對抗的直覺。權限廣不代表有那筆資料；很多時候 admin 反而沒有那條被指派的待辦，於是流程漂移到別的頁、或開到別人的單據，而表面上完全看不出錯。

實務原則：

- **帳號**：忠實重現 recording.js 登入段點 / 填的那個帳號。`walk.mjs` 重播的也是它，§0 勘查時就能看到「資料綁在這個帳號」。只有當流程**與帳號無關**（任何登入者都看得到、走得完，例如查公開資料）時，才可退回站台 login template 提供的通用帳號。
- **機制**：去 `.claude/test-template/` 查本站台的 login template（`--kind login`），照它的穩定片段組登入段，但 **`CONFIG.USER_ID` 填錄製帳號**，不是 template 預設帳號。查不到 login template，就照 §5 的通用骨架（找到登入欄、填帳密、按登入鈕、等登入完成的條件成立）做一段，做完沉澱成新的 login template。
- **保留**登入之後錄到的業務動作，接在登入段後面。

不同站台的登入細節（帳號欄是什麼元件、登入鈕文字、登入完成怎麼判定）全部屬於站台事實，住在 login template，不寫進這份通用文件。

---

## 5. 轉換範例骨架

下面是通用骨架——登入段用穩定片段、帳號帶錄製帳號、業務動作照搬、結尾抽值進 summary。實際 selector 依站台 template 與 §0 勘查結果填入：

```js
async function flow(page, { step }) {
  const summary = [];

  // 登入：改用站台 login template 的穩定片段（捨棄 codegen 錄的脆弱登入機制），帳號用錄製帳號
  step(2, '開啟登入頁');
  await page.goto(CONFIG.BASE_URL + CONFIG.START_PATH, { waitUntil: 'domcontentloaded' });
  // 等登入欄出現（selector 依站台 login template），不要用 waitForTimeout 硬等
  await page.locator('<登入帳號欄 selector>').waitFor({ state: 'visible' });
  step(3, `登入（${CONFIG.USER_ID}）`);
  // ↓ 這幾行是「機制」，依站台 login template 替換成穩定寫法
  //   USER_ID 仍填錄製帳號，不要換成萬用/admin
  // ... 找登入欄 → 填 CONFIG.USER_ID / CONFIG.PASSWORD → 按登入鈕 ...
  // ... 等「登入完成」條件成立（離開登入頁 / 取得登入憑證），條件見站台 login template ...

  // ↓↓↓ 以下是 codegen 錄到的「登入後」業務動作（保留、依 §0 勘查定案 selector） ↓↓↓
  step(4, '進入目標查詢頁');
  await page.goto(CONFIG.BASE_URL + '<目標頁 path>', { waitUntil: 'domcontentloaded' });

  step(5, '按下查詢');
  await page.getByRole('button', { name: '查詢' }).click();
  // 等查詢結果回來：等結果列出現（0 筆時由下方 rowCount 條件擋下），或改 await page.waitForResponse(/api\/<查詢API>/)
  await page.locator('table tbody tr, [role="row"]').first()
    .waitFor({ state: 'visible', timeout: 15000 }).catch(() => {});

  // 結尾把查詢結果筆數抓進 summary（承接 codegen 的 expect 驗證意圖，轉成非斷言檢查）
  const rowCount = await page.evaluate(() =>
    document.querySelectorAll('table tbody tr, [role="row"]').length);
  summary.push({ label: '登入帳號', value: CONFIG.USER_ID });
  summary.push({ label: '查詢結果列數', value: rowCount });
  summary.push({ label: '落地頁面', value: page.url() });

  // success 必須含非恆真條件（rowCount > 0）；rowCount >= 0 或只看 URL 都是恆真/弱條件 = 假綠
  return { success: rowCount > 0 && !page.url().includes('login'), summary };
}
```

---

## 5b. codegen 會漏掉什麼（復測時最常補的）

codegen 只記「明確動作」，**不記**下列東西——因為它假設 Playwright 的 auto-wait / auto-scroll 會處理。但實務上常失效，導致轉出來的測試 timeout：

| codegen 漏掉 | 何時會出事 | 補強 pattern |
|--------------|-----------|--------------|
| **捲動** | 目標在虛擬化清單 / 可捲動容器 / 被 sticky header 遮住 → 自動捲入失效 | 點擊前 `await loc.scrollIntoViewIfNeeded().catch(()=>{})`；元素根本還沒渲染（虛擬清單）→ 先 `await page.mouse.wheel(0, 1200)` 捲到它出現 |
| **hover 才出現的元素** | 滑過才顯示的按鈕 / 選單 | 點擊前 `await trigger.hover()` |
| **動畫 / 懶載入的等待** | 點完馬上下一步，但元素還在動畫或資料還沒回 | `await loc.waitFor({ state: 'visible' })`，或對關鍵資料 `await page.waitForResponse(/api\/xxx/)` |
| **多個同名元素** | 一列一個「明細」→ locator 命中多個 | 加 `.first()` 或用更精確條件鎖定那一列 |
| **hover-tooltip 的 aria 文字**（⚠️ 高頻雷） | codegen 對「圖示按鈕」常錄成 `getByRole('button', { description: '...' })`——這 description 來自 hover 才顯示的 tooltip。tooltip 沒 hover 時 `display:none`，aria 關聯失效 → 跑起來**命中 0**，且 `getByText('...')` 還會誤中那個隱藏 tooltip 文字（overlay 容器）而非真按鈕 | 別用 tooltip 文字。改用**結構 / 圖示**定位真按鈕，例如鎖到該列再 `button:has(i.<icon-class>)`（先 dump 該列按鈕的 icon class 找對的圖示） |

**標準強化寫法（點擊前）**：

```js
const btn = page.getByRole('button', { name: '明細', exact: true }).first();
await btn.scrollIntoViewIfNeeded().catch(() => {});
await btn.waitFor({ state: 'visible', timeout: 15000 }).catch(() => {});
await btn.click();
```

> 這些**無法用讀 recording.js 猜準**——但可以**用 §0 逐步看畫面提前抓出來**（walk.mjs 會印 icon class、aria-expanded、命中數）。看畫面把它們寫進規劃表，flow 一次就對；復測階段只是「確認連 2 次綠」，不是靠 timeout 回報才回頭補。若復測還在大量發現這類問題 → §0 沒看夠，回去補勘查。難搞的 selector 定案後值得沉澱成站台 selector template。

### 用 inspect.mjs 找正確 selector（省得每次手寫診斷）

selector 對不上時，跑 bundle 的 `inspect.mjs`：登入 → 走到目標頁 → 列出該 LABEL 各種 locator 的命中數 + 表格列每顆按鈕的 icon class。

```bash
# 同 test.mjs 執行環境（跨平台橋接眉角見站台 env template）
LABEL=<目標文字> CLICK=<前置點擊> node inspect.mjs
# 或直接導航：LABEL=<目標文字> GOTO=<目標頁 path> node inspect.mjs
```

看哪個 locator 命中 1（或合理數量）就用哪個；icon 按鈕看 icon class 用 `button:has(i.<icon-class>)`。

## 6. 轉完之後

1. 從 `../gen-e2e-test/assets/` 複製 `test-template.mjs → test.mjs`、執行用的批次 / shell script、`package.json`（已存在就保留 recorder 那份的 scripts，合併 dependencies）。
2. 把 `test.mjs` 的 `flow()` 換成轉好的，`CONFIG` 填好。
3. 驗證：`node --check test.mjs`、`PREVIEW=1 node test.mjs`。
4. 交付：使用者雙擊執行檔跑真實測試 + 出報告。`recording.js` 與錄製啟動檔留著，之後流程變了可重錄重產。

> 最關鍵的兩條環境眉角直接記在這裡：(1) 執行用 `.bat` 內容**必須全 ASCII 英文**，任何非 ASCII 字元都可能因 codepage 讓批次檔壞掉；(2) **瀏覽器必須與受測後端同機**執行，跨機時 localhost 會指錯地方。完整環境眉角見 `$SKILLS_ROOT/gen-e2e-test/references/gotchas.md`（也列於 gen-e2e-record SKILL.md 參考檔表）與站台 env template。

---

## 7. 第二視窗 / popup（最容易在轉換時整段漏掉）⚠️

很多「明細 / 檢視 / 流程圖 / 列印」類動作是**開新視窗（popup）**。點某顆鈕 → context 的頁面數從 1 變 2 → 出現一個獨立 popup 視窗，裡面還有自己的分頁與動作。這整段最容易在轉換時消失。

### 三個事實（都實測過，別再憑印象）

1. **codegen 會錄子 popup**：從錄製視窗點出來的 popup，codegen 會錄成
   `const page1 = await page.waitForEvent('popup')` + 一串 `await page1.*`。
   （只有你**自己另開的獨立視窗**它看不到——那是 codegen 真正的盲區，少見。）
2. **轉換最常見的 bug＝把 popup 行漏掉**：因為它們不是 `await page.*`（是 `const page1 = …` 與 `await page1.*`）。§2.1 的抽取若只 grep `await page.`，popup 整段消失，測試點完那顆鈕就停。
3. **popup 的 API 不用你管**：引擎已在 context 層自動攔 popup（`context.on('page', ...)`），popup 一開、它的 request / response 就自動進報告並標記來源 `popup`。你只要把 popup 的 **UI 動作**搬對。

### flow 怎麼寫 popup（把 codegen 的 page1 模式照搬即可）

關鍵是**先掛 `waitForEvent('popup')`、再點**，拿到 popup 物件後**對 popup 操作**（不是對原 page）：

```js
step(6, '點明細，開啟明細視窗');
const popupPromise = page.waitForEvent('popup');   // 先掛，再點
await detailBtn.click();
const popup = await popupPromise;
await popup.waitForLoadState('domcontentloaded');

step(7, 'popup 內切換分頁');
await popup.getByRole('tab', { name: '<分頁名>' }).click();   // ← 對 popup 操作，不是 page
```

> popup 內的 selector 一樣要走 §0 視覺勘查＋§5b（tab 用 `getByRole('tab', { name })` 通常穩；圖示鈕用 icon class）。`walk.mjs` 會重播 popup 行並對 popup 視窗截圖，勘查時就能看到 popup 裡長怎樣。
> 若 `walk.mjs` 顯示 popup「視窗不存在」→ 多半是**觸發 popup 的那顆點擊本身壞了**（例如 `description:'...'` 命中 0）：先把那顆 selector 修對（icon 定位），popup 自然就開。

### 錄製端的預防

提醒使用者：整段流程都在 **codegen 開的那個視窗**裡操作；讓點擊自然開出子 popup 沒問題（codegen 跟得到），但**別自己另開獨立視窗**去點——那 codegen 錄不到，會變成覆蓋黑洞。
