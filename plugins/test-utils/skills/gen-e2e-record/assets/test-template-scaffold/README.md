# test-template — 測試流程的內建記憶庫

`gen-e2e-record` / `gen-e2e-test` 是**通用** skill（任何站台都能用），只講原則與手法，不綁特定系統。
**站台專屬的知識**（登入怎麼登、環境眉角、跑過的流程、難搞的 selector）放這裡，成為 skill 的「內建記憶」。

> Skill 在動手前會**先查這裡**：有現成 template 就照用、不要重新摸索；沒有就照通用原則做，做完把可重用的部分**沉澱成新 template** 回填這裡。

---

## 為什麼這樣切

通用 skill 教「怎麼想」（先看畫面、別把錄製當成畫面現實、帳號是資料依賴…）。
這裡存「這個站台的事實」（登入片段、路由、環境限制、跑過的流程）。
兩者分開：skill 帶得走、到處能用；記憶留在專案、越用越厚。

---

## 目錄

| 子目錄 | 放什麼 |
|--------|--------|
| `login/` | 站台登入片段（穩定機制 + 帳號注意事項） |
| `env/` | 環境眉角（後端綁哪、瀏覽器要不要同機、檔案編碼眉角…） |
| `flow/` | **跑過並驗證過的完整流程**，整理成可重用骨架 |
| `selector/` | 難搞元件的穩定定位法（動態 class、icon、popup tab…） |

> 不必預先建滿。**做過一次、驗證過、覺得會再用到** → 才沉澱成 template。重複比壞抽象便宜，但驗證過的流程值得留。

---

## Frontmatter schema（每個 template 檔頭必填）

```yaml
---
id: app-login                     # 唯一代號（kebab-case）
kind: login                       # login | env | flow | selector | gotcha
site: app                         # 站台代號（各專案自取，例 app / shop / admin）
tags: [login, vuetify, jwt]       # 速查標籤，越具體越好
when: 產此站台測試、需登入時        # 一句話：什麼情況該載入這個
summary: 穩定登入片段 + 帳號忠實度  # 一句話內容摘要
---
```

- `kind`：決定它是哪一類記憶；`flow` 是跑過的完整流程骨架。
- `tags`：速查工具靠它命中。放元件名、機制、頁面類型等。
- `when`：讓人（與 skill）一眼判斷要不要載入。

檔頭以下就是內容本體（片段、提醒、骨架）。

---

## 速查工具

```bash
# 列全部
python .claude/test-template/query.py

# 依站台 / 標籤 / 類別 / 關鍵字
python .claude/test-template/query.py --site app
python .claude/test-template/query.py --tag login
python .claude/test-template/query.py --kind flow
python .claude/test-template/query.py popup        # 關鍵字（掃 tags/when/summary/id）
```

輸出每個命中 template 的 `id / kind / site / when / 路徑`，再 Read 路徑載入內容。

---

## 新增 template

1. 放到對應子目錄，檔名 = `id`.md。
2. 填好 frontmatter（schema 見上）。
3. 內容只放「這個站台的事實」；通用手法留在 skill，不要複製進來。
