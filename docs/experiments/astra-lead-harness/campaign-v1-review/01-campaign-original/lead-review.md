# Astra 主手 campaign-v1：原版未完回合覆核

結論：原版這一 episode 未達一般服務成果；但不能把它算成 Astra 自行放棄，或完整且接線正確的原版戰略失敗。

主線已檢查兩次 call 的所有行動／派工及 scribe 的失敗、恢復、validate、self-test、render 輸出；大型重複 doctrine／script 讀取用實際命令定位，不把未逐字重讀的重複輸出標成全面內容覆核。未有 scribe 完成回覆或 Astra 驗收回合。

## 效果與邊界

Astra 先把 standard-v3 選為主攻，premium 人的決定分開處理，並依原技能派 scribe 後 auditor。scribe 用了 600.017222918 秒到 carrier 逾時，留下狀態、基線與 HTML/SVG；產品、原始資料、歷史與接受端未改。主線獨立 oracle 的 standard 結果為未完成、whole goal 未完成；不能用 state validate PASS 抵銷服務仍 v2。

舊 carrier 在 child timeout 立即停止整個 episode，沒有把 partial receipt 交回 Astra，也沒執行排在後面的 auditor。Astra 首 call 83.311060252 秒；整段 683.375319043 秒。Astra 已知 170,748 tokens，scribe 無完整 turn.completed、用量未知，不可當 0，也不可直接與 Lab 完整成本比較。

## 已定位的摩擦

1. **角色指令未接上**：原 Codex root 只命名 sa-scribe，沒有精確 .codex-agents resolver。lead 的非 hidden 檔案查找沒有取得 sa-scribe.toml，brief 反要求 scribe 讀整套 root／references。真正角色規約明令 consolidation 不重讀 doctrine。這次是實際讀了原 root 的流程，並不是忠實載入完整 bundled role 的對照。
2. **資料狀態維護反客為主**：scribe 先讀大型 root、reference、例子與數千行 script 區段，接著 init 25 claims。六次 set-claim 因 criterion/risk/clarity 衍生欄位未同步被拒；改 state 同步後又修一次 clarity 才 validate PASS。這是能重現研究的工具摩擦，不只是覺得文字長。
3. **自測適用面不清**：對本 campaign 跑 self-test 因 takeover 範例假設失敗；改用官方 example-state 才 PASS，並成功 render。應區分技能工具自測與實際業務驗收。
4. **派工載體未交回失敗**：明確在新 carrier 分支測試 failure handoff，舊 raw、原版 skill 都不修改；不是在 Lab 塞一條重複「遇到失敗要診斷」。

當前四 victoryCriteria 仍 FAIL；candidates.unmetVictoryCriteria=0 是策略後預測，不能誤報為目前全完成。Premium 在 objective/constraint/deferred front 中，卻沒有獨立 victory criterion，是待 lead 審核的覆蓋風險；草稿未交回，不能當最終假綠燈。

## 後續反證

campaign-v2 使用 fresh 相同 fixture 與新 failure handoff：原版＋精確 role metadata、Lab、原版三組。只有 metadata 的原版對照才能幫忙定位接線代價；仍須核對是否真的讀／傳該角色，不以配方名稱當實際使用。
