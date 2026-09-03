# 可攜性（非 Claude Code 用戶如何用）

> 這個編排器的設計刻意不綁 Claude Code 的 subagent 機制。核心抽象是「writer / reviewer / fixer 三個獨立角色 + 可見 checklist + 審查迴圈」，這在任何 LLM 環境都能表達，只是執行載體不同。

## 三種執行載體

### 一、有 subagent（Claude Code / Cowork）— 完整版

照 SKILL.md 主流程：task 之間並行派 subagent，單 task 內 writer/reviewer/fixer 為三個獨立 subagent 串接，checklist 用 TaskCreate。獨立性最強（reviewer 真的沒看過 writer 的思路）。

### 二、無 subagent，但能多次呼叫（Claude.ai / 一般 chat / API 腳本）— 三段獨立 prompt 串接

把 writer / reviewer / fixer 拆成**三個獨立 prompt、分三次呼叫**，每次只餵該角色需要的輸入：

1. **Writer prompt**：餵 producer SKILL.md + template + 來源 + 全域約定 → 收產出。
2. **Reviewer prompt**：**新開一段對話/呼叫**，只餵「產出 + 來源 + 該 producer 格式/覆蓋標準」，不餵 writer 的推理過程 → 收 PASS/FAIL + 缺失清單。新開對話是維持獨立性的關鍵。
3. **Fixer prompt**：餵「產出 + 缺失清單」→ 收修正版 → 回到第 2 步再審。

checklist 用一份外部清單（Markdown 表 / 試算表 / issue tracker）人工或腳本維護狀態。迴圈與 max 3 輪規則照舊。

非 Claude Code 的程式化串接（如自寫腳本 + LLM API）非常適合這個模式：三個角色就是三個固定 system prompt，迴圈就是程式的 while loop，PASS 判定解析 reviewer 回傳的結構化結果。

### 三、無 subagent、單一連續對話 — 退化為分段自我審查

最受限的環境（只能一個模型、一條對話）。退化做法：**同一模型換角色、分段執行**，靠分段紀律與重讀來源維持半獨立：

1. 「我現在是 writer」→ 產出。
2. **明確切換**：「我現在是 reviewer，忘掉剛才怎麼寫的，只對照來源與標準挑毛病」→ 重新讀來源 + 產出，列具體缺失。切換時重讀來源是補回獨立性的手段。
3. 「我現在是 fixer，只修上面列出的缺失」→ 修正。
4. 再切回 reviewer 審。≤3 輪。

退化版的弱點是同一模型既產又審，容易自我合理化；用「強制重讀來源 + 明確角色切換宣告 + 只准依清單修」三個紀律來壓低這個風險。

## 不變量（三種載體都要守）

- writer 不評自己的產出；reviewer 的判定與缺失清單必須具體可定位；fixer 只依清單修。
- checklist 可見、狀態即時更新（不管載體是 TaskCreate 還是一張 Markdown 表）。
- PASS 才勾完成；逾 3 輪標需人工，不卡死其他 task。
- 全域約定（命名/共用件/編號/包別）先定稿再 fan-out，避免並行或分段間漂移。
