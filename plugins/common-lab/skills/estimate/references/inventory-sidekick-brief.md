# 盤點 Sidekick 派工手冊

當成果方向已確認，而且派工能縮短某個可獨立驗收的唯讀查證時讀取。主 Agent 保留理解、取捨、去重、方案與估算責任。

## 何時並行

依案件選擇互斥證據面、清楚範圍與可驗收成果；數量不固定。只有 Host 授權與可用能力支持，而且主 Agent 同時有獨立工作可推進時才派工。模型與上下文依難度、能力、成本及可用性選擇，不固定廠牌、型號或推理等級。

提供自足目標、證據範圍、權限與驗收；不附預期技術結論或既有人天，避免錨定。無子代理能力時由主 Agent 完成同一查證，不能為此卡住評估。

## 建議的工作包

依案件裁切，不必固定全部使用：

1. **建置與依賴基線**：runtime、build、SBOM、實際 classpath、私有 JAR、repository、systemPath、產碼工具與版本衝突。
2. **使用者入口與契約**：頁面、route、Action／Controller、REST、SOAP、輸入輸出、Session 與前端呼叫足跡。
3. **資料與查詢語意**：Entity、DAO、ORM mapping、native SQL、QueryDSL、資料庫設定、自訂 function／dialect／contributor 與語意斷點。
4. **批次與外部整合**：batch、scheduler、Receiver、RPC／SOAP／REST client、檔案傳輸、外部設定及合約所有者。
5. **執行與橫切能力**：部署容器、config loader、security、Filter、AOP、logging、encoding、upload／download、測試與可觀測性。

工作包以「證據面」互斥，不以資料夾名稱硬切。相同能力跨越多層時，由主 Agent 指定唯一主包，其他 sidekick 只回報交叉引用，避免重複統計。

## 每個 briefing 必須具備

### 1. 目標與驗收

描述要查明的事實與完成格式，不預先指定期望結論。例如：

> 建立資料層整合足跡，列出實際 ORM／Query 工具、客製擴充、使用位置、數量、代表案例、未解矛盾與 file:line 證據。完成時需讓主 Agent 能判斷哪些是共用斷點、批次樣態與逐項例外；本任務不選方案、不估人天。

### 2. 權限與寫入邊界

- 唯讀存取指定 repo、案件資料與已授權環境。
- 可用搜尋、解析、反編譯、dependency tree、靜態統計及不改變客戶狀態的診斷。
- 不修改產品、Git、DB、外部系統、`assessment-state.json` 或交付成果。
- build、啟動、網路或資料庫操作依案件既有授權；若會產生副作用，回報所需權限與替代唯讀證據。

Subagent 繼承目前 Host 的 sandbox 與權限；模型名稱與角色不會擴張授權。

### 3. 策略自主

給出適合此切片的檢查點與有限查證嘗試額度；長切片還要指定最晚交回部分證據的時間。不必讓簡單查找跑滿額度，也不能只寫「做到完成」。

將下列文字原樣放入 briefing：

```text
You may change tools, commands, and technical approaches at will,
within the granted permissions and write set.
A single tool or approach being unavailable means only that this
strategy failed — choose another permitted, evidence-producing approach.
Honor the supplied checkpoint and attempt allowance. Repeated failed
hypotheses, widening evidence scope, or an exhausted allowance return
the partial evidence and a bounded next proposal to the lead; do not
continue indefinitely or bypass a runtime permission failure.
```

### 4. 結果格式

每個 sidekick 回傳：

- 已查明事實表：命題、數量、代表案例、`file:line`／設定／命令證據、信心。
- 交叉引用：可能和其他工作包描述同一能力的 stable key。
- 重要否定結論：查找範圍、使用方法及「未找到」的邊界。
- 矛盾與迷霧：目前證據為何不足、哪項查證最能消除不確定。
- 範圍外觀察：只列可能改變方案的事項，不延伸成建議。

Sidekick 的完成責任是回傳事實；方向、方案與人天由主 Agent 和 PM 在完整證據上收斂。

## 主 Agent 的驗收與整合

主 Agent 收件後：

1. 抽查所有會排除方案、改變責任或形成大量人天的承重證據。
2. 對每個「未找到／沒有使用」的否定結論重做範圍檢查。
3. 用 stable key 合併跨包重複，保留不同視角但只建立一個計價來源。
4. 把證據矛盾保留成 fog，先要求 sidekick 說明原因與證據，再決定採信、補查或退回。
5. 由主 Agent 更新 `assessment-state.json`，建立成功鏈、候選方案、工作樣態及人天。

並行化的成果是更快取得可核對的事實。對客戶成果的理解、選項設計、推薦、方案選擇與費率合理性始終由主 Agent 與 PM 共同收斂。
