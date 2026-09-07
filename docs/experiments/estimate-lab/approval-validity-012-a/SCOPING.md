---
hunt_id: HUNT-2026-001
status: scoping
created: 2026-09-06
---
# Estimate Lab 0.1.2 核准有效性診斷
此 ID 僅屬本次實驗目錄。依明確任務，不寫唯讀 .codex，也不更改產品或真正案件。
## Locate
- 事件：rev9 已核准後，透過 merge／append 再更新案件。
- 基線：fixed-validation/synthetic-e3 的原始 rev9 合成案件；逐 byte 保留新副本。
- 差異：責任範圍或已選方案改變，沒有新的 confirm-estimate。
- 環境：frozen 0.1.2 scripts；全新 /tmp/estimate-approval-validity-012-a。
- 症狀：尚待實測是否 validate 通過，產物仍聲稱「人天已核准，待交付」。
## 凍結探針
1. 反證控制：merge workItems 提高費率，應拒絕且保留 rev9。
2. 假說一：merge responsibilityBoundary 改變責任後，旧核准仍生效。先關閉此探針。
3. 假說二：append 新 scenario 與合成選案紀錄，merge 選案後，沒有新的人天核准仍顯示已核准。
獨立交叉確認：真實 CLI 持久化狀態、validator、generated HTML 與靜態呼叫鏈。
允許證據：command、exit_code、stdout/stderr（合成資料）、revision、status、選案、責任範圍、currentDecision、approval IDs／未變比較、gate state、HTML 宣稱、檔案 hash、時間。
父任務明確要求保存完整合成 rev9 基線；這不是任何真實客戶 payload。所有新暫存產物保留，不清理。
## 範圍
只診斷核准沿用。主線另處理 Gate5 呈現，不合併歸因。Graphify 無現成圖，不擴張建圖。
沒有修改正式 source/test，也沒有模型 generation calls。完成後追加獨立結論，不把診斷完成稱為修復完成。

