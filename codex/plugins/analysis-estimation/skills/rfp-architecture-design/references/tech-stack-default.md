# 預設技術棧細節（覆寫時對照替換）

本檔記錄第二段架構設計的預設技術棧。使用者若覆寫，把對應名詞整套替換，但**保留同樣的分層思想與文件骨架**。

## 前端（預設）

| 面向 | 預設選用 | 覆寫時替換什麼 |
|---|---|---|
| 框架 | Vue 3（Composition API + `<script setup>`） | React / Angular / Svelte 等;views/components/composables 命名隨之改 |
| 建置 | Vite | Webpack / Next 等 |
| UI 庫 | Vuetify 3 | MUI / Ant Design / Element Plus 等;頁型樣板元件名改 |
| 樣式 | Sass(SCSS) | Tailwind / CSS Modules 等 |
| 狀態 | Pinia | Redux / Zustand / NgRx 等 |
| 路由 | Vue Router（角色化守衛） | React Router 等;權限守衛機制保留 |
| HTTP | Axios 封裝 apiClient（攔截器掛 JWT、解封套） | fetch wrapper 等;統一封套解析保留 |

## 後端（預設）

| 面向 | 預設選用 | 覆寫時替換什麼 |
|---|---|---|
| 框架 | Spring Boot | .NET / NestJS / Django 等 |
| 分層 | Action → Facade → Service(Domain) → JPA DAO | Controller→Service→Repository 等;但保留「表現→編排→領域→持久」四層 + 交易邊界在編排層 |
| 對外整合 | mware（API client / 檔案交換 / Mail） | Integration / Gateway 層,職責不變 |
| 共用元件 | util（無狀態工具） | helpers / common,無狀態原則保留 |
| 日誌 | log（AOP + Filter + Logback） | 對應框架的攔截器 + 結構化日誌;稽核軌跡與遮罩保留 |
| 安全 | Spring Security + JWT | 對應框架的 auth middleware;SSO + JWT + 角色授權保留 |
| 持久 | JPA / Hibernate | MyBatis / EF Core / TypeORM 等 |
| 批次 | Spring Batch / Quartz | 對應排程框架;監控/rerun/log 能力保留 |
| DB | 單一資料庫(SQL Server 優先 / Oracle) | 依非功能需求 |

## 不可因覆寫而丟失的原則

無論技術棧怎麼換，下列必須保留（這些是 RFP 硬規則的承載點）：
- 依賴方向單向向下;橫切（log/security/util）獨立於業務。
- 統一回應封套 `{success, data, error, meta}`。
- 個資遮罩集中、預設遮罩、解遮罩獨立授權並寫 access trail。
- 稽核軌跡保留年限、寫入型操作記前後值。
- 簽核流程與核決權限不可 Hard-coded，由設定驅動。
- 交易邊界明確、失敗 rollback、例外統一轉封套不洩敏感資料。
