---
name: rfp-architecture-design
description: 把第一段需求分析（需求分析報告 + 逐功能 API 分析）轉成一組架構設計文件:架構總覽（分層圖 + 請求生命週期 sequence）、前端架構、後端分層架構、命名與開發規範、簡易資料模型
  ER。Use whenever the user has requirement analysis / 功能 API 清單 / 模組清單 ready and asks
  to 出架構 / 設計架構 / 做架構文件 / 系統架構 / 技術架構 / 分層設計 / 前後端架構 / 資料模型 / ER 圖, or says「依需求分析出架構」「把功能清單變成系統架構」「設計前後端分層」「畫一下
  ER」. Default tech stack is Vue3+Vite+Sass+Vuetify front end and Spring Boot action→facade→service→jpa(+mware/util/log/security)
  back end, but the stack is overridable — ask at start. This is the second of three
  chained stages (requirement-analysis → architecture-design → sa-bdd). 繁體中文輸出。
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# RFP 架構設計（第二段）

把第一段的需求分析，落成一組可直接指導開發的架構文件（預設輸出到專案 `archi/`）：

1. `00-架構總覽.md` — 整體分層圖、各層職責、一個請求的生命週期 sequence、橫切服務 ↔ 架構層對應、檔案清單。
2. `01-前端架構.md` — 技術選型、目錄結構、頁型樣板（列表/明細/簽核/批次/儀表板）、安全與權限、建置相容。
3. `02-後端架構.md` — package 結構、各層細節（含代表性程式碼）、橫切實作（log/security/例外）、批次。
4. `03-命名與開發規範.md` — 命名慣例、DTO/Entity 規約、統一封套、個資與安全、例外/交易/日誌、設定分環境。
5. `04-資料模型ER.md` — 簡易概念 ER（mermaid erDiagram，分領域）、核心實體與關聯、關鍵設計重點。

## 為什麼這樣切

第一段已經把「要做什麼」窮舉成功能與 API 清單。這一段回答「怎麼蓋」：用一套固定分層把那 N 支 API 安放好，並且把橫切關注（簽核 / 稽核 / 遮罩 / 報表批次 / 介接）**在架構層只實作一份**，各業務模組以領域封裝引用——這正好對應第一段索引裡的「跨模組共用 API」。架構文件要能讓任何一個開發者看完就知道一支新 API 該放哪一層、命名怎麼取、個資怎麼遮、交易邊界在哪。

## 步驟 0：確認技術棧（可覆寫）

開工先問使用者是否沿用預設技術棧，或要覆寫。預設值：

- **前端**:Vue 3（Composition API + `<script setup>`）+ Vite + Sass(SCSS) + Vuetify 3;Pinia 狀態、Vue Router 角色化路由、Axios 封裝 apiClient。
- **後端**:Spring Boot 分層 **Action → Facade → Service(Domain) → JPA DAO**;對外整合走 **mware**、共用元件走 **util**、日誌走 **log**(AOP + Filter + Logback)、安全走 **security**(Spring Security + JWT)。
- **資料庫**:單一資料庫(SQL Server 優先 / Oracle),依需求分析的非功能章節調整。

若使用者覆寫（例如 React 前端、.NET 或 Node 後端、MyBatis 而非 JPA），把 templates 中對應的技術名詞、目錄結構、層名整套換掉，但**保留同樣的文件骨架與分層思想**（表現層 → 編排層 → 領域層 → 持久層、橫切獨立、統一回應封套、個資遮罩集中）。`references/tech-stack-default.md` 記錄預設棧的完整細節供填充參考。

## 工作流程

1. **讀第一段輸出**:讀需求分析報告（拆包、非功能、對外連線）+ 功能 API 索引（共用 API、命名慣例、模組清單）。架構必須與這些對齊，尤其是共用 API 與命名慣例要原樣承襲。**先驗證上游輸入再動工**:若需求分析報告或功能 API 索引缺失、缺非功能需求/共用 API 清單/命名慣例任一章節，或與本次請求衝突（例如索引描述的模組／技術棧與使用者本次要求不一致）→ **停止產出任何架構檔**，列出具體缺漏或衝突項，要求使用者補齊或確認後再繼續;**不得以臆測補完架構**。唯有上游輸入齊備且一致，才往下進入第 2 步。
2. **產 `00-架構總覽.md`**:用 `templates/00-架構總覽.md`。畫整體分層 ASCII 圖（Browser → LB → 各層 → 外部系統）、用表格列各層職責與「不該做」、畫一個真實請求的 mermaid sequence（挑一條會穿過 security/log/facade/service/dao/mware 的代表性流程，如「合約送簽」）、列橫切服務落在哪一層。
3. **產 `01-前端架構.md`**:技術選型表、完整目錄樹（plugins/stores/api/composables/components/layouts/views）、頁型 ↔ 功能對應表、前端安全與權限（SSO/攔截器/路由守衛/個資遮罩呈現）、建置相容。
4. **產 `02-後端架構.md`**:完整 package 樹（common/security/mware/batch/modules，每業務模組固定 action/facade/service/dao/entity/dto）、各層細節附**代表性程式碼片段**、橫切實作（log AOP、security JWT、GlobalExceptionHandler）、批次。
5. **產 `03-命名與開發規範.md`**:命名表、DTO/Entity 規約、統一封套、個資與安全、例外/交易/日誌、設定分環境。
6. **產 `04-資料模型ER.md`**:領域總覽 graph + 分領域 mermaid erDiagram（系統共用、各業務域、介接/IFRS16 等），核心實體列代表性欄位（含 PK/FK/UK、個資遮罩旗標），關鍵設計重點表。標明為概念層，邏輯/實體模型於後續展開。

## 大量模組時的並行策略

五個架構檔之間相對獨立，可並行：
- 主流程先定稿技術棧與 `00-架構總覽.md`（分層、命名、共用服務落點），作為其他四檔的共同約定。
- 再用 subagent 並行產 `01`~`04`，每個 agent 拿到:需求分析報告、功能 API 索引、定稿的 00 總覽、對應 template、技術棧決定。
- 後端 package 樹若模組極多，可讓 agent 先給骨架（每模組六子 package）再補細節，不必逐模組展開所有類別——架構文件示意即可，細節留給第三段與實作。
- 並行前務必把層名、package 命名、回應封套、共用服務清單交付每個 agent，避免前後端對不上。

## 覆蓋檢查與收尾

- 對照第一段索引的**跨模組共用 API（簽核/稽核/附件/報表批次/遮罩/介接）**，逐一確認每個共用服務在 `00-架構總覽.md` 的「橫切服務 ↔ 架構層」表都有明確落點，沒有遺漏、也沒有被放進業務模組重做。
- 對照需求分析報告的**非功能需求**（密碼、稽核保留年限、個資加密、最小權限、效能 RTO、批次），確認架構文件每一項都有對應機制（security/log/util.CryptoUtil/batch monitor…）。
- 確認 `00` 的檔案清單列出全部五個檔，且每個檔都已產出。
- 明確下結論：架構文件已完整覆蓋共用服務與非功能需求，或列出待補項。

## 嚴格依骨架，不過度產出（eval 修正重點）

A/B eval 顯示本段的系統性偏差是**過度產出**：自行加長、發明 template 沒有的章節與目錄結構（例如多開一個 `crosscut/` 分層、把橫切從「總覽的一個對應表」膨脹成獨立檔）。請收斂：

- **嚴格依各 template 的骨架**產出，章節組成與 template 一致；橫切服務就放在 `00-架構總覽.md` 的「橫切服務 ↔ 架構層」對應表 + `02-後端架構.md` 的「橫切實作」小節，**不要另立黃金版沒有的結構**。
- 代表性程式碼片段是「示意」，每層給一段即可，不要逐模組逐類別展開成長篇——細節留給第三段與實作。
- 寧可簡潔對齊骨架，也不要為求完整而膨脹。多出來的結構會讓下游對不上，是缺點不是優點。

## 品質要求

- 與第一段命名慣例、共用 API、回應封套**完全一致**。
- 嚴格依 template 骨架，不發明額外結構、不過度產出。
- 依賴方向單向向下;橫切（log/security/util）獨立，不混入業務。
- 個資遮罩、稽核、簽核不可 Hard-coded 等 RFP 硬規則在架構層有明確承載點。
- 技術棧可被使用者覆寫，覆寫後骨架不變、技術名詞整套替換。
- 繁體中文輸出。

## 模板

- `templates/00-架構總覽.md`
- `templates/01-前端架構.md`
- `templates/02-後端架構.md`
- `templates/03-命名與開發規範.md`
- `templates/04-資料模型ER.md`
- `references/tech-stack-default.md` — 預設技術棧細節（覆寫時對照替換）。
