# Producer 登記表

> 編排器本身不寫內容，內容交給下列 producer skill。這張表登記每個 producer 的**輸入 / 輸出 / 格式標準 / 覆蓋檢查方式**，讓 writer subagent 知道照誰跑、reviewer subagent 知道照什麼審。

## 鏈式關係

```
rfp-requirement-analysis ──→ rfp-architecture-design
                         └──→ rfp-sa-bdd
cold-estimation （可獨立執行，或與需求分析並行——同吃 RFP/SOW）
```

需求分析是架構與 BDD 的唯一上游。若使用者要架構或 BDD 但還沒有需求分析，先跑 `rfp-requirement-analysis`。估算不依賴前三者，可單獨或並行跑。

---

## 1. rfp-requirement-analysis（需求分析，第一段）

- **輸入**：RFP / 需求規格書（PDF / docx / md），需讀完全文。
- **輸出**：`RFP分析_<系統名>.md`（單檔需求分析報告）+ `功能API分析/`（`00-索引與彙總.md` + 每模組一檔）。
- **格式標準**：每功能固定三段（目標 / API 表 `Method·Path·輸入·輸出·用途` / 頁面操作表 `操作·對應API·說明`）；模組檔開頭有「來源章節 + 補充參照 + 共通設計約定」blockquote、結尾有 `## 設計備註（跨功能）`；共用 API 只在索引設計一份。
- **覆蓋檢查方式**：逐章比對 RFP，每條業務功能都落到某模組某功能；機械統計功能數（數 `## 功能` 標題）；下「無缺漏 / 缺漏清單」結論。
- **task 拆法**：一模組一 task；索引與共用 API/命名慣例為奠基 task。

## 2. rfp-architecture-design（架構設計，第二段）

- **輸入**：第一段的需求分析報告 + 功能 API 索引。
- **輸出**：`archi/` 下五檔——`00-架構總覽` / `01-前端架構` / `02-後端架構` / `03-命名與開發規範` / `04-資料模型ER`。
- **格式標準**：**嚴格依各 template 骨架**，不額外發明 template 沒有的結構（如自創 crosscut/ 目錄）；技術棧預設 Vue3+Spring Boot 分層，可覆寫但骨架不變。
- **覆蓋檢查方式**：對照第一段共用 API，每個都在「橫切服務 ↔ 架構層」表有落點且未被業務模組重做；對照非功能需求每項有承載機制；確認五檔齊備。
- **task 拆法**：一檔一 task；`00-架構總覽`（技術棧 + 分層 + 共用服務落點）為奠基 task。

## 3. rfp-sa-bdd（BDD 驗收規格，第三段）

- **輸入**：第一段的逐功能 API 分析（索引 + 各模組檔）。
- **輸出**：`sa/` 下一模組一檔 + `00-索引與覆蓋檢查.md`。
- **格式標準**：每功能三段（Goal / Requirements 三段式 `<前綴>-NN-NN` REQ / 繁中 Gherkin Scenario 正常+異常）；REQ 前綴對齊索引對照表（不自選子段字母）；載荷/資源命名沿用第一段來源檔的實際 REST 名。
- **覆蓋檢查方式**：BDD 檔的 `## 功能` 數與來源功能 API 檔逐一相符；每功能 ≥1 正常 +1 異常；每 REQ 前綴實際出現；機械統計功能/REQ/Scenario 數。
- **task 拆法**：一模組一 task；REQ 前綴對照表 + 撰寫慣例為奠基 task。

## 4. cold-estimation（冷啟動估算）

- **輸入**：陌生專案 SOW / RFP / 需求規格。
- **輸出**：功能估算清單（`包 | 模組 | 功能介紹 | 功能類型 | 簡述 | 來源章節 | 需壓測 | 人天`）+ 總人天 + 三道驗證結論。
- **格式標準**：欄位固定；顆粒度依其 `references/granularity.md`；費率依 `references/rate-card.md`。
- **覆蓋檢查方式**：四道閘 CHK-1～CHK-4（薄章節 / 去重率 / 批判乾涸 / 型別分布+重複計算+來源完整性）。
- **task 拆法**：一 chunk 一盤點 task，或整份估算當單一複合 task（估算本身已內含多視角批判，編排器主要負責對其輸出做最終 reviewer 把關）。
