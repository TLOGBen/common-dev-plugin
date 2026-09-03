# 審查迴圈（writer → reviewer → fixer）

> 這是編排器的心臟：單一 task 內的閉環。三個角色職責不重疊——writer 只產、reviewer 只審不改、fixer 只依清單修。獨立性是品質的來源，所以**reviewer 必須是與 writer 不同的 subagent**（無 subagent 環境見 portability.md）。

## 角色契約

### writer
- 輸入：該 producer 的 SKILL.md + template + 來源依據 + 全域約定（命名慣例/共用件/REQ 前綴/包別）。
- 產出：目標檔，嚴格依 template 骨架。
- 禁止：自評、自行擴張範圍、發明 template 沒有的結構。

### reviewer
- 輸入：writer 的產出 + 同一份來源 + 該 producer 的格式/覆蓋標準（見 producer-registry.md）。
- 產出：**判定（PASS / FAIL）+ 具體缺失清單**（每條缺失要可定位、可修：指出哪一段、缺什麼、應該長怎樣）。
- 禁止：自己動手改檔（它只審）。含糊評語（如「再加強些」）不算數，必須具體。

### fixer
- 輸入：原產出 + reviewer 的缺失清單。
- 產出：**只針對清單逐條修**後的新版本。
- 禁止：擴張改動範圍、改 reviewer 沒提的地方、推翻 template。

## reviewer 評分準則

對照五個面向逐項判，任一面向有 blocking 缺失即 FAIL：

| 面向 | 看什麼 | 常見 FAIL |
|---|---|---|
| **結構** | 章節/區塊組成是否符合 template 骨架 | 缺區塊、層級錯、自創結構 |
| **欄位** | 表格欄位是否與標準一致 | API 表欄位缺漏、Gherkin 三段不全 |
| **命名慣例** | REST 複數名詞、統一封套、REQ 三段式、狀態機用語 | 命名飄移、編號格式錯、子段字母自選 |
| **覆蓋粒度** | 功能數/REQ 數是否對得上來源、子聚合根是否各自成列 | 覆蓋偏粗（漏拆）、漏「補充參照」衍生功能 |
| **防臆造** | 內容是否都能對回來源，不確定處是否標註 | 自行補規則、預設套用來源沒要求的橫切（如個資遮罩）、編數字 |

## PASS 定義

reviewer 判 **PASS** 的條件：五個面向皆無 blocking 缺失，且——
- 結構/欄位/命名與 template 及全域約定一致；
- 覆蓋粒度對得上來源（功能數相符、該拆的拆了）；
- 無臆造（內容可追溯、不確定處已標）。

只有 PASS 才能把該 task 在 checklist 勾完成。

## 迴圈與輪數

```
round = 0
writer 產出
loop:
    reviewer 審 → 若 PASS：勾完成，結束
    round += 1
    若 round > 3：標「需人工」，附最後一版 + reviewer 缺失清單，結束（不卡死產線）
    fixer 依缺失清單修
（回到 loop 由 reviewer 再審）
```

- **max 3 輪**修正。逾次仍未過 → task 標 `需人工`，記錄最後產出與未解缺失，**繼續其他 task**。
- 每輪 reviewer 應確認上一輪缺失是否已解 + 是否引入新問題（避免修了 A 壞了 B）。
- 反覆在同一缺失打轉（fixer 改不動）→ 提前判需人工，多半是來源本身有矛盾或 template 不適用，留給人決定。

## 與 checklist 的關係

task 狀態流轉：`待產 → 審查中 → 需修(round n) → PASS✓` 或 `→ 需人工⚠`。每次狀態變化更新 TaskCreate/TodoWrite，讓使用者隨時看得到產線進度與卡點。
