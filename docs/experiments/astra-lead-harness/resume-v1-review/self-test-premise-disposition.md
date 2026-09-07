# 自測失敗不是當前任務狀態無效

resume-v1 原版 unknown 的 scribe 在 002-implementation item_39 先 validate 當前 state 成功，再對同一任務 state 執行 self-test，出現 unreliable-ambiguous-target 預期字串沒被拒絕。原 raw 保存；沒有把它當成功或刪失敗。

現行／凍結原版函式 run_self_test(state) 的首個負控制只把 targetIdentity 改成 AMBIGUOUS，卻假設輸入 automationActuatorStatus 已是 UNRELIABLE。validator 的 EXACT_ONE 限制正是受 UNRELIABLE 分支條件控制（script 489–493），不是所有未知/不可執行狀態都必須精確唯一。

[零模型唯讀探測](self-test-premise-probe.json)確認：bundled example 的 UNRELIABLE＋EXACT_ONE 本身 valid，改成 AMBIGUOUS 被拒；真實接續任務 UNKNOWN＋UNKNOWN 本身 valid，改成 AMBIGUOUS 仍 valid。這符合該条件分支，不證明 validator 漏掉預期規則。三檔 hash 不變，只呼叫 validate_state 與記憶體副本，沒有跑完整自測或改原狀態。

根因是自測輸入前提與介面暗示不一致：SKILL.md 第 397 行示範 self-test <state.json>，state-contract 第 433 行則限定 example-state.json。自測內有固定 claim ID 與範例設定，不能當任意活動任務的健康檢查。額外無關自測會製造假警報及排查成本；這一次 scribe 正確沒有為了綠燈捏造狀態，繼續 render。

處置：不改正式版。Lab 的帳本驗證及 fixture 自測入口已分開，保留這個介面設計理由；也不因此取消與當前改動相關的真測試。此 probe 是失敗訊息的根因補查，不代表所有 self-test cases 或完整原版驗證器已審完。
