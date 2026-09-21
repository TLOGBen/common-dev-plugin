# Jev 元素挑選（Lab）

> 🔗 Template：`scripts/case/element-table.js`（產生編號表）＋ `scripts/jev-pick.mjs`（請 Jev 挑元素）
>
> 取代「`snapshotForAI()` 整包印出再截斷」的找元素方式：頁面上看得到的可操作元素先編成一張表，
> 由 TypeSafe Jev 用一題 Choice 挑出最符合目標的前幾名，agent 只讀候選，不讀整份 DOM。
> 做法參考 [browser-use/jev-ultrafast](https://github.com/browser-use/jev-ultrafast) 的 indexed action space。

---

## 什麼時候用

| 情境 | 用 Jev 挑選？ |
|------|--------------|
| 要點／填某個元素，但 DOM 很大、selector 不確定 | ✅ |
| 同一頁要連續找好幾個元素 | ✅ 編號表跑一次，jev-pick 可跑多次 |
| 排查 console error、畫面空白、API 回應 | ❌ 用原本的 template（這不是「找元素」問題） |
| 沒有 `TYPESAFE_API_KEY` | ❌ 直接用 `snapshotForAI()` |

---

## 跑法

```bash
# 1. 產生編號表（連線方式同其他 template；PowerShell 改用 127.0.0.1:9222）
dev-browser --connect http://${HOST_IP}:9333 run ${CLAUDE_PLUGIN_ROOT}/skills/dev-browser/scripts/case/element-table.js

# 2. 請 Jev 挑元素（需要 TYPESAFE_API_KEY）
node ${CLAUDE_PLUGIN_ROOT}/skills/dev-browser/scripts/jev-pick.mjs "查詢按鈕"
node ${CLAUDE_PLUGIN_ROOT}/skills/dev-browser/scripts/jev-pick.mjs "填寫出發日期的欄位" --top 5
```

輸出範例：

```
目標：查詢按鈕
92.3%  [12] button 查詢  → page.locator('[data-jev-idx="12"]')
 4.1%  [13] button 清除  → page.locator('[data-jev-idx="13"]')
confidence 92.3%｜來回 640ms
```

```javascript
// 3. 用候選操作，並驗證結果
const page = await browser.getPage("app");
await page.locator('[data-jev-idx="12"]').click();
await page.waitForTimeout(500);
console.log(page.url(), (await page.snapshotForAI()).full.substring(0, 1500));
```

---

## 規則

| 規則 | 原因 |
|------|------|
| Jev 的答案是候選，不是證據 | 操作後一定要看畫面／DOM 確認結果；`DONE` 由驗證決定，不由 Jev 決定 |
| 低信心（< 50%）或挑中 `none` → 改用 `snapshotForAI()` | jev-pick 會印出 ⚠️ 提示；不要照最高分硬點 |
| `exit 2` = 沒有結果 → 改用 `snapshotForAI()` | 無金鑰、API 失敗、編號表不存在都走這條；不擋 agent 做事 |
| 換頁或畫面重新 render 後重跑 `element-table.js` | `data-jev-idx` 掛在 DOM 節點上，節點被換掉就失效 |
| 上限 254 個元素 | Jev 一題 Choice 最多 255 個選項，留一個給 `none` |

---

## 送出去的資料

會送到 TypeSafe（美國）的內容：頁面標題、網址、每個可操作元素的角色、名稱（label／aria-label／文字，截 80 字）、
欄位值（截 40 字；password 只送 `***`／`empty`）、是否 disabled。不送 DOM 結構、API 回應、localStorage／token。

TypeSafe 條款：不拿送出的內容訓練模型；一般帳號會保留資料，零保留只限企業方案（https://docs.typesafe.ai/legal.md）。
客戶專案使用前，先確認客戶合約或公司政策允許這個服務。
