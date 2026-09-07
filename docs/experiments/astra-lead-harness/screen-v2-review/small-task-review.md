# 小任務四臂初篩：沒有證據支持強制增加流程

四個真實 Astra/high 主手 → Luna/high worker → 同一 Astra 主手返回的 episode，全部通過獨立 0/1/2/11 export oracle。原測試意義保留，只修改兩個允許檔案。這是本地小任務的接受結論，不是整包技能或模型排名。

| 臂 | Episode 秒 | 真實 tokens | 主手 / worker tokens | 技能啟動 |
|---|---:|---:|---:|---|
| None | 107.473 | 227,470 | 109,099 / 118,371 | 無額外技能 |
| Original | 105.128 | 218,566 | 146,055 / 72,511 | Delegate |
| Guard | 97.276 | 213,029 | 126,769 / 86,260 | 無額外技能；此題沒有接受端操作，ensure 約束未作用 |
| Lab | 198.493 | 237,230 | 141,215 / 96,015 | Lab Delegate + runtime + executor |

用量由原始 turn.completed 與各主手原生 task interval 核對；原始 carrier 的 resume unknown 保留，派生結果在 usage-checkpoint-a.json。輸入含 cached、輸出含 reasoning，不重加。時間不含主線獨立 oracle 與本文審查；不是訂閱扣款。

## 機制與摩擦

所有主手都親自讀實際產物、執行真實 export 行為檢查。沒有一臂把 worker DONE 直接當總體完成。沒有要求人在場重確認，也沒有啟動 Define Goal、Wayfinder 或 Strategic。只能說此題的入場判斷沒有引入不必要的戰略流程，不能說戰略已被證明無效。

主線已完整讀完 12 個 CLI trace；原版已讀過的 Delegate 本文在二次檢閱中省略重複展示，操作事件仍逐筆核對。

- 四臂都曾遇到非 Git fixture 的 Git 取證摩擦。None 和 Lab worker 的 git diff -- fileA fileB 是 no-index 比較，不是工作樹差異。
- Original 和 Guard 主手把「不是 Git repo」交代給 worker，避免再次查 Git。Lab 主手已看到此事，但 brief 未傳遞，worker 又把 no-index 結果誤猜成 rename 偵測並重查。這是已確認資訊遺失的具體候選根因，不等於已證明加一句技能就能修好。
- Lab worker 用 nested zsh -lic 產生數次 oh-my-zsh cache/compdump 寫入拒絕和 zle 警告。這些沒有成功改寫全域，但也不能記成零嘗試。其他臂沒有相同殼層路徑；耗時受環境與 worker 軌跡影響。
- Lab worker為確認測試數切換 reporter，最後正確回報「1 test file passed」。Original worker 寫「3 tests passed」，與可見 runner 的 1 檔案級 pass 不同；主手最終未沿用這個不受該摘要支持的數字。
- 四個主手最終交接均忠於已完成的函式與測試，沒有錯誤擴成業務完成。Lab 最清楚標示檔案級測試數，但單次不構成可讀性優勢或真人理解結果。

## 目前處置

**不增加小任務固定關卡、不因這次秒數就丟掉 Lab、不把短 prompt 當成本保證。** 已觀察的候選是「派工時保留會改變下一步的已知環境事實」，先單機制重測再决定是否改入技能。測試數應以實報層次說明；不因一次 worker 誤報就替所有任務增加測試儀式。

原版原則仍保有價值：實作與接受責任分離。此題只能證明四臂皆出現這個行為，尚不能證明是哪條文字造成。大型 campaign 的注意力陷阱與 human-AFK 分支另外測，不以這個函式代替。

## 證據入口

- 01-count-label-none/lead-review.md：首輪與用量 reset 依據。
- small-task-oracles.json：其餘三臂獨立驗證，全部前後 hash 不變。
- usage-checkpoint-a.json：5 個已完成 episode 的派生用量快照；小任務僅前四個。
- 原始 run：/tmp/astra-lead-screen-20260906-b/runs/，各 calls 的 prompt、stdout、stderr、result、fixture-after.zip 全部保留。
