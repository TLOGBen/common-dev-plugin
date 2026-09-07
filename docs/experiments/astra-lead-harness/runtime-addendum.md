# Astra 主手實驗：實際 runtime 校準

這是凍結前的設計校準，不是模型結果。先前稽核使用 Claude 原始技能定位目的；Astra 執行需用真正的 Codex 生成版，不能把 Claude API 或翻譯差異當成 harness 效果。

## 已確認的差異

- 正式 Claude Define Goal 第 6 步要求 Goal block 後取得確認；正式 Codex 對應步驟改為通過 quality bar 後建立 goal tool，沒有相同的固定重確認。兩者都排除一般實作任務的強制建目標。原稽核的確認假說不能直接套到 Codex。
- 正式 Codex Strategic 保留 full/light/stand-down、第三方降規、scribe 與獨立效果驗收；它也保留輕量 consolidation、普通小任務排除及未知異動先讀回。不能只測最重一段、忽略豁免後宣稱整包過度搭架。
- 正式 Codex Wayfinder 仍保留 Chart／Work 每 session 一票、Chart 後停下、Drain 不代答 HITL。這些是真實可測的流程機制，但只有任務真的進入該路徑才算 treatment 已啟用。

## 本批採用的 fixture

採 fixture 作者的 countLabel singular/plural 小修，以及 bundle generator 修復＋已接受但回覆晚到的本地交付。前份稽核的 0/null、雙預約與保留天數案仍是提案，不會冒充本批已執行案例。

兩案都要求真實便宜 worker 實作與 Astra 主手驗收。測試載具只是 dispatch／resume 傳輸，不能替主手決定工作順序、替它驗收或自動塞入所有技能。

## 四臂共有的控制

- 使用相同任務、資料、平台安全、source／test write set、本地接收端 CLI 與 economical worker profile。副作用只能經授權 CLI；禁止修改接收端歷史／oracle。
- 原版讀 Codex 正式 Common；精簡版讀 Common Lab 0.1.5 的已導出 Codex 包；沒有額外 skill 的臂不暗加新流程。技能可按 description 選用，不強迫小修啟用 Strategic。
- 替代守門臂與其他臂取得相同 ensure 能力；差別是將何時必用守門放入控制規則。守門不得使用隱藏答案。若需專屬能力，另標整體系統 treatment，不稱提示詞單變因。
- 全部原始 stderr、無效控制輸出、啟動失敗、額度截斷、scope violation 都保留。真值由 episode 結束後的獨立 oracle 與主線對照，不能被 lead 自評覆蓋。

若兩案的自然路由都不啟用 Strategic，首輪只能回答路由與普通派工，不能回答完整戰略流程的效果；後續才明標 workflow-requested trial，讓相同任務在指定流程內比較。這不是把自然路由的結果改判。

載具、案例、模型設定、順序、資源上限與機制預測仍須另以實際執行 manifest 凍結；本文件不代表已鎖定或已呼叫模型。

## 用量定義的一手核對

官方 [exec event 定義](https://github.com/openai/codex/blob/main/codex-rs/exec/src/exec_events.rs)把 Usage 定義為單一 turn 的用量；[非互動模式文件](https://developers.openai.com/codex/noninteractive/)提供 JSONL 與 resume 介面。這支持逐 turn 記錄，但上游 main 的註解不是本機 0.153.0 的實測保證。首個真 resume 仍核對 raw；native 累計 total 不與 CLI turn usage 重加，cached 是 input 子集，reasoning 是 output 子集。
