# 先修正載體歸責，不把更多規則塞回 skill

campaign-v1 原版：Astra 用83.311秒安排scribe/auditor，scribe於600.017秒上限被截斷。已產生基準／有效state／sand table，但產品及接受端仍原狀。原載體遇worker失敗便停止整个episode，未執行auditor，也沒有把partial receipt送回Astra。這是預先凍結的傳輸限制，不是Astra自主宣告放棄；用量缺失仍unknown，不算0。

现有 Lab Delegate 已要求辨別實作與環境失敗，診斷後選擇縮小範圍、重試、適配模型或真正人工界線。再加同義規則會增加負擔；先讓載體能把實際失敗送回保有目標的主手，才可測這套原則。

新 astra_lead_failure_handoff.py 只另存一份 episode 控制迴圈，重用原 command/process/scope/evidence functions；原 astra_lead_episode.py 和已凍結試驗不變。失敗／逾時worker的raw status保留；將其partial message、改動、exact raw receipt交回原Astra，後續同batch角色暫停且記錄，不自動重啟任何工作。產品是否已變、是否重試或需要更窄下一步由主手判斷，controller不驗收、不授新權限。

有scope違反、package／receipt漂移或無法觀察fixture仍停止；lead自身失敗不自動續跑；共用模型／wall budgets仍生效。此候選尚未進行真模型推進測試，不聲稱已證明改善。

離線8項新控制通過，18項原控制也實際替換成新loop再跑通過（0.072秒）。首次26項中1失敗是測試期待字串 not automatically restarted 與實際 No failed request was automatically restarted 不同，非行為反例；原收據保留。18項base＋8項new合跑0.104秒PASS，無模型呼叫；fake traces不是人或模型成果。

另需分開控制的根因：原生成 strategic entry 只稱 bundled role sa-scribe，沒有讀取 .codex-agents/sa-scribe.toml 的明確resolver。此次Astra用沒有--hidden的rg列包內容，未讀該角色；brief叫scribe讀整個SKILL/refs，而真正role說不應在consolidation重讀整套doctrine。不能把未接上的角色限制稱為已忠實測完；下一輪應明標角色接線補充的 treatment，不能回寫原試驗。所有下屬固定Luna/high也限制了推論，結果不是Astra＋任意適配worker的普遍結論。
