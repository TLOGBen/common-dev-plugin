# 暫不採用新增條款

四次實跑中，A=.5 與 B=候選.6 的兩次主手都把 non-Git 事實送入 worker brief，四個 worker 均沒有再跑 Git 命令。B 的 brief 額外帶 exit128／fatal 字樣，但未観察到因此才避免的摩擦。五組獨立 oracle 全通過，包括逆序重試與輸入不變性。這個 fresh variant 沒有重現 A 的缺口，因此不支持為 Astra 增加此條必讀規則。

候選只保留在 /tmp/common-lab-delegate-context-016a 與其 export receipt，不合入下一個發行版本；它不是已完成升級。這是未證明有需要，不是已證明該原則在任何場合無用。既有 Delegate 已要求 relevant context；下一步優先處理有實證的角色接線／失敗回主手問題，不為單次異常堆提醒。

| 次序 | 事實傳遞 | worker 重踩 Git | 獨立 MOE | episode 秒 |
|---|---|---|---|---:|
| A1 | 有 | 0 | PASS | 156.818 |
| B1 | 有 | 0 | PASS | 142.445 |
| B2 | 有 | 0 | PASS | 142.025 |
| A2 | 有 | 0 | PASS | 144.156 |

共 12 次實際 CLI calls、1,051,454 tokens；全部已由 exact session interval 與 raw CLI 核對。input 1,032,319 含 cached858,752；output19,135 含 reasoning5,352。費用未知，非完整隔夜任務用量；详 usage-v1.json。

主線已讀四份實際 dispatch brief、以結構化 raw 篩查 worker 的 Git 命令、四份 handoff，並真執行 oracle；全段 raw tool output／所有 lifecycle 副作用尚待完整覆核，因此此裁決只針對事實傳遞增益，不冒稱整段零越界或完整品質評鑑。
