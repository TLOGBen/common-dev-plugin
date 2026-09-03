# 陌生系統探索決策指南

當案件剛開始、現況證據不足，或不知道下一步該查哪個面向時讀取。

## 先找能改變決定的證據

探索不是把固定清單全部填滿。先問：目前哪個未知最可能改變可行方案、範圍、責任或人天？再選擇能以合理成本分辨它的證據。

常見高價值來源依案件選用：

- build manifest、lockfile、實際 classpath、容器描述與部署設定：確認真實技術線與執行環境。
- 路由、Controller／Action、API schema、頁面呼叫與 runtime trace：確認入口、契約與實際使用量。
- DAO／ORM mapping／native SQL、migration 與 datasource：確認資料層耦合與變更切片。
- scheduler、batch class、外部排程清單與 job log：確認批次數量及啟動責任。
- client stub、Receiver、SOAP／REST／RPC 設定與 endpoint：確認 inbound／outbound 界接及合約所有者。
- Filter、AOP、security、session、logging、upload／download、encoding 與 config loader：確認橫切行為是否被框架承載。
- build、test、啟動、部署與環境診斷：確認靜態可行性是否能轉成運行證據。
- 私有 JAR、產生碼、重複目錄、停用設定、無原始碼元件：確認哪些能力不能只靠 Java 原始碼推斷。

## 模式差異

### 升版評估

實際依賴基線是形成可信方案的必要前提。先建立 SBOM／dependency snapshot，再找版本邊界、已移除 API、namespace／runtime 斷點、私有元件相容性與部署容器責任。全域可機械替換與需要逐項理解的語意改動分開。套件盤點需繼續追到產碼機制、整合擴充點與執行語意，詳見 [dependency-behavior.md](dependency-behavior.md)。

### CR 承接

優先找使用者可見行為、入口、domain rule、資料與界接影響。至少保存輕量 dependency snapshot；CR 觸及 framework、runtime、產碼、界接、部署或私有元件時，提升為完整 SBOM 與整合語意盤點。只估 CR 成功鏈真正需要改動的部分；系統其他面向可作風險證據但不計價。

### 混合型

先建立實際依賴基線，再分清楚哪些工作由升版硬條件產生、哪些由新增／改變業務成果產生，最後處理兩者共用底座，避免同一工作算兩次。

## Gate 2 後的平行盤點

成果大方向確認後，可把互斥的證據面切成 3–5 個唯讀工作包並行蒐集。Codex 優先以乾淨上下文的 Luna Max 執行；Claude Code 使用 Host 可用的 Haiku／Sonnet research subagent。工作包回傳事實、數量、代表案例、來源定位、交叉 stable key、否定結論的查找邊界與仍待釐清的迷霧。

主 Agent 保留成果理解、證據採信、跨包去重、方案形成、PM 推薦與人天估算。sidekick 不寫案件主檔，也不把局部觀察提升為方案結論。切包、briefing、權限與驗收格式見 [inventory-sidekick-brief.md](inventory-sidekick-brief.md)。

## 證據記錄

每項可用結論至少保存：命題、來源定位、取得方式、commit／版本／環境、強度、信心、仍未知部分，以及它會改變哪個決定。不同統計視角使用穩定 dedupe key；頁面、route、Action 與 endpoint 若描述同一能力，不因數字不同就重複計價。

## 工作集合只盤一次

Discovery 在 `detailCatalogs` 建立全案唯一的 canonical 工作集合，並一次分類施工性質：

- `direct-touch`：每項可能需要獨立理解、修改或驗證，完整保存 stable ID、名稱／repository-relative path、用途、處置、修改重點與驗證。
- `generated`：由 Entity、schema、規格或其他來源可重現產生；保存輸出數、產製來源、方法與核對，不展開成 N 筆人工修改。
- `evidence-only`：只證明覆蓋範圍，不作人工乘數；說明完整性邊界與計價角色。

盤點後不在 Wayfinder、估算或 generator 重掃。Wayfinder 只有在 treatment 分類會改變候選方案、計價方式或責任時才開決策票；否則直接引用同一 stable workset ID。

## 足夠條件

當剩餘未知已不會改變方案，或能以明確條件、上限與責任表達時，停止廣泛探索並建立成功鏈。若下一項查證只增加知識量、不能改善決策品質，把它留在技術附錄而不是繼續消耗案件時間。
