# AI 自驅審測迴圈（兩個 skill 共用）

把「轉好/寫好的 `test.mjs` 跑到真的能重現流程」這件事，從「丟給使用者反覆雙擊」變成 **AI 自己在 app 主機 headless 跑、自己診斷、自己改、受停損保護、收斂後附變更摘要交付**。使用者全程只碰兩個觸點：**①錄製（或給需求）②最終 headed 確認**。

> 適用：`gen-e2e-record` 轉換後、`gen-e2e-test` 手寫 flow 後想自我驗收時。

> **這裡是「確認」，不是「發現」。** 若 gen-e2e-record 的 Stage 4 視覺勘查（先逐步看畫面、定好 selector）做足，本迴圈應該一兩次就綠。若你在這裡才一輪輪發現 selector 問題、面板要不要點、popup 漏掉——代表**該回頭補看畫面**，不是在這裡硬試錯。試錯只是勘查沒做足的補救，不是常態。

---

## 前提：自測可不可行？

自測 = 在「app 所在主機」headless 跑 `test.mjs`。先判斷：

- **app 前後端有開、AI 能到該主機** → 可自測，進迴圈。
- **受測站台沒開 / AI 不在 app 主機且無橋接** → **不要硬跑**。降級成「備好 flow + 請使用者雙擊跑一次回報」，並告知為何不能自測。

## 環境無關調用（邏輯一致，只差怎麼跑）

| AI 環境 vs app | 調用 |
|---|---|
| **同機**（原生 Windows PowerShell/cmd；或 macOS/Linux app 在本機） | 直接：PowerShell `$env:HEADLESS='1'; node test.mjs`；bash `HEADLESS=1 node test.mjs` |
| **WSL，app 在 Windows**（唯一特殊處理） | 橋接：`powershell.exe -NoProfile -Command "..."`，**必須**用絕對路徑帶 `PW_DEPS`（WSL 的 NODE_PATH 對 Windows node 無效） |

WSL 橋接範例：
```bash
timeout 240 powershell.exe -NoProfile -Command \
  "\$env:PW_DEPS='C:\path\to\tests\.e2e-deps\node_modules'; \$env:HEADLESS='1'; \
   Set-Location 'C:\path\to\tests\<name>'; node test.mjs" 2>&1 | tr -d '\r'
```

---

## 迴圈演算法

```
loop:
  1. headless 跑 test.mjs，收 stdout
  2. 判讀：流程結果 ✅/❌、哪個 step timeout/失敗、API 有沒有攔到
  3. 若 ✅ 且「每個 step 都實際執行到」：
       → 再跑 1 次（共 2 次）都綠 → ★收斂★，跳出
       → 第 2 次掛 → 視為 flaky，當失敗處理（加等待）
  4. 若某 step 失敗（timeout / 0 元素 / 點不到）：
       a. 先分類失敗原因：
          - 「無資料 / 無權限」（inspect 命中 0 且頁面文字含「無資料 / No data / 權限」）→ 不可自行修，停損回報
          - 「authed 白頁」（用了 auth.json 跳過登入、但頁面整片空白：nav 不出來、`document.body.innerText` 幾乎為空、console 有 `pageerror`）→ 多半是 **sessionStorage 沒還原**（SPA 把 Vuex/Pinia 存 sessionStorage，而 storageState 不含它）。確認 `auth.session.json` 有產出且引擎有印「已還原 sessionStorage」；缺檔就重跑 capture-auth。**不要把它當 selector 壞了一直改 selector**（畫面根本沒 render，改什麼都命中 0）。
          - 「selector 不對」→ 可修
       b. 可修：執行 `LABEL=<目標文字> GOTO=<目標頁 path> node $SKILLS_ROOT/gen-e2e-record/assets/inspect.mjs`
          （需前置點擊時改用 `LABEL=<目標文字> CLICK=<前置點擊> node ...`）
          列出候選 selector，從中挑穩定的（結構/icon，禁用 hover-tooltip 的 description），
          改 flow 的那一步，並把這次改動記進「變更摘要」
       c. 回到 1 重跑
  5. 停損（任一觸發即停，帶診斷回報，不空轉）：
       - 同一步「改完後」仍連續失敗 2 次
       - 整體已跑 ≥ 5 輪
       - 偵測到無資料 / 無權限
```

> 停損閾值（2 次 / 5 輪）是預設值，跑過幾個真實流程後可依回饋校。

> **等待類修法優先序**（修 timing 問題時依序嘗試，硬 sleep 是 Playwright 官方明列的 flaky 根因）：
> ① 等具體 locator：`locator.waitFor()` 等目標元素真的出現 → ② `waitForLoadState('domcontentloaded')` → ③ **最後手段**才 `waitForTimeout`，且必須加注釋說明為什麼只能硬等。

---

## 收斂後的交付（必附「變更摘要」）

收斂即產出報告，並給使用者：

1. **報告**（`reports/*.html`）：含 API 來源頁（主頁/popup）。
2. **自動修正摘要**：逐條列出 AI 為了讓它跑起來改了什麼、為什麼。範例：
   - `step5 明細：getByRole(description:'明細') → button:has(i.mdi-file-document-outline)（codegen 錄的是 hover tooltip aria，隱藏時命中 0）`
   - `step4 送出查詢後：加 listRow.first().waitFor()（等清單列真的渲染出來，依等待類修法優先序①，不用硬等）`
3. 一句話請使用者 **headed 雙擊 `run-test.bat` 確認一次**——重點看「自動修正摘要」裡的 selector 是不是點到對的東西（擋 AI 改成錯元素卻假綠）。

## 停損回報格式（卡住時）

不要硬湊綠。帶以下回報，把球交回使用者：
- 卡在哪個 step、症狀（timeout / 0 元素 / 點不到）
- 執行 `LABEL=<目標文字> GOTO=<目標頁 path> node $SKILLS_ROOT/gen-e2e-record/assets/inspect.mjs` 得到的候選命中數 + 表格列按鈕 icon
- 已試過哪些 selector / 等待（變更摘要）
- 研判：是 selector 問題還是「該帳號/此時段清單無資料、需有資料帳號或測試單據」

---

## MUST / MUST NOT

| | 規則 | 為什麼 |
|---|---|---|
| MUST | 收斂前自測**連跑 2 次**都綠 | 跑一次綠可能是 timing flaky |
| MUST | 交付**必附變更摘要** | 使用者 headed 確認要能聚焦審語意，擋 false-green |
| MUST | 無資料/無權限 → 停下問人 | AI 無法自行造資料 |
| MUST | 用 auth.json 跳過登入時，成功判定要看「畫面真的 render」（已知 nav/元素存在、body 有文字），不是只看「URL 不是 /login」 | 白頁的 URL 也不是 /login，URL-only 會給假綠 |
| MUST | authed 白頁 + pageerror → 先查 sessionStorage 還原（auth.session.json），別當 selector 問題 | storageState 不含 sessionStorage；SPA 的 Vuex/Pinia 常存那 |
| MUST NOT | 為了湊綠，無限改 selector / 放寬到 force click 點到別的元素 | 假綠比紅燈更糟 |
| MUST NOT | 把自測寫死成 WSL+powershell | 同機就直接 `node`，只有 WSL→Windows 才橋接 |
| MUST NOT | 用 hover-tooltip 的 `description` 當 selector | tooltip 隱藏時 aria 失效，命中 0（見 `$SKILLS_ROOT/gen-e2e-record/references/codegen-to-flow.md` §5b） |
