# 依賴可持續性、整合足跡與語意相容

升版／混合案件必讀。純 CR 觸及 framework、runtime、產碼、界接、部署或私有元件時也讀取。

## 要達到的結果

依賴分析的成果不是一張套件清單，而是一個可反證的答案：目前候選方案使用的每項承重元件，在目標組合上有可持續的來源、可理解的整合足跡、可承諾的執行語意與明確責任。

SBOM／dependency snapshot 提供「實際會被建置與部署的系統由什麼組成」的基準。來源優先採 resolved dependency tree、lockfile、實際 WAR／JAR／node bundle、systemPath、私有 repository、產碼 plugin 與 runtime image；manifest 是入口之一。`dependencyCoverage` 記錄取得方式、元件總數、盤點邊界及會改變方案的 dependency ID。

## 找出值得深入的元件

Agent 從實際依賴全集主動尋找下列訊號。它們是探索線索，不是固定技術清單：

- 跨 JDK、framework、ORM、namespace、browser 或 container 的 major 邊界。
- annotation processor、code generation、compiler plugin、enhancer、classifier 或 generated source。
- framework integration adapter、dialect、registry、contributor、serializer、service loader 或客製 SPI。
- 私有修改版、systemPath、民間 fork、無原始碼元件、local cache 才能重建或上游維護責任不明。
- runtime type、transaction、identity、cache、dirty checking、序列化、function resolution、分頁、例外或 wire contract 可能改變。
- 上游停止支援、目標組合未列入支援矩陣、issue 被拒絕／wontfix，或替代 fork 的治理風險。

每個命中訊號的元件都先回答一個反證問題：

> 哪項可觀察事實會使目前目標不可採用、必須換路線，或讓長期維護責任轉到我方？

接著選擇最能回答它的證據：官方 migration／compatibility 文件、release notes、上游 issue、fork 說明、實際 classpath、反編譯、完整 package imports、設定與 service registration、clean build、隔離啟動或代表性 runtime probe。維護狀態與支援矩陣可能變動，形成正式方案時以當前上游一手來源查證。

## 六層判斷

1. **實際身分**：artifact、版本、hash、來源、官方／fork、license 與 resolved/deployed 位置。
2. **可持續性**：上游維護者、維護狀態、最後支援組合、替代線與供應鏈責任。
3. **build-time 機制**：APT、codegen、compiler plugin、classifier、generated-source 路徑及乾淨重建能力。
4. **整合足跡**：先找完整 package／artifact／設定使用全集，再分類 factory、template、高風險 API、客製 SPI 與代表案例。單一類別計數只能作為子分類。
5. **執行語意**：以目標組合核對型別、查詢、交易、identity、cache、序列化、函式、分頁與例外契約；compile／namespace 證據與 runtime／upstream-support 證據分開記錄。
6. **採用策略**：以 `keep`、`fork`、`replace`、`self-maintain`、`stay` 或 `vendor` 表達實際路線，分開記錄 upstream maintainer、internal owner、成立條件與 PM 決策。

## 收斂與 PM 停等

技術事實由 Agent 查明。`blocksReadiness` 表示一項未知仍會阻擋正式估算；`requiresHuman` 表示它需要 PM 承諾。兩者互相獨立：技術 blocker 可以由 Agent 繼續查證而不打斷 PM；當可行策略涉及成果、費用、責任、生命週期或風險接受時，再把可比較的策略送到 PM。

每項 decision-bearing dependency 至少保存：

- upstream source／maintainer、internal owner 與 maintenance status；
- 完整 footprint 的取得方法、範圍與高風險 API 分類；
- 一項以上 compatibility claim，含 target、supported／conditional／unsupported／unknown、證據與理由；
- 採用的 selected target、策略、責任與結論；
- semantic breaks、probe、fallback strategies、evidence references 與是否仍會推翻方案。

只有 selected target 的 compatibility claim 為 `supported` 或 `conditional`、resolution 已收斂且 `blocksScenario: false`，才可進入正式人天確認。其餘結果保留在 mapping 狀態，並把下一個高價值查證或 PM 策略選擇放到 Frontier。

## QueryDSL 代表案例

QueryDSL 是一個回歸案例，不是特別寫死的判斷規則。相同方法也適用於報表引擎、序列化元件、認證 adapter、模板產碼器與私有 ORM patch。

以 QueryDSL 為例，Agent 會先從所有 `com.querydsl` imports、APT／plugin、generated Q-Class、classifier 與設定建立全集，再分類 `JPAQueryFactory`、`JPQLQueryFactory`、`fetchResults()`、`fetchCount()`、template／function expression 與客製 Hibernate SPI。上游 release／issue 用來判斷目標 Hibernate 組合是否受支援；clean build 只回答產碼與編譯，代表性 query／transaction probe 回答 Date function、FunctionRegistry／Contributor、重複 Entity ID 與結果語意。

證據形成互斥工作：

```text
QueryDSL／Hibernate 共用產碼與 function registry 底座 × 1
+ Q-Class 全量乾淨重產與編譯驗證 × 1 批
+ function signature／客製 contributor／特殊 identity 語意 × 實際類型與數量
+ 代表性 DB transaction／query runtime probe × PM 選定保障口徑
```

## Compatibility probe

靜態 footprint 決定 probe 的代表樣態。Probe 使用隔離、唯讀或可回復資料，固定現行與目標環境、輸入及觀察點，保存實際 SQL、回傳、例外與 entity state 差異。結果回寫 compatibility claim 與 resolution，讓方案和人天能回到同一證據鏈。
