# Grilling 0.1.5：目標與受批判方法分開

本輪不保護錯的方法，也不把人的明確目標重開成選擇題。使用 Skill Creator 的窄幅修訂：整段替換 0.1.4 原則，不追加案例禁令。精確候選段落：

> Distinguish the user's stated claim and necessary task conditions from the proposed method under review. Change a method that confounds the claim; do not reopen an already explicit goal merely to preserve that method. If recommending a different or stricter claim, explain what it would measure instead of silently substituting it.

## 凍結設計

8 次 generation calls，固定 gpt-6-astra／high，無 judge calls。A 為 0.1.3 Claude source，B 為 0.1.5 candidate Claude source。0.1.4 source 根檔與 manifest 先另存 rejected-014，保留上一輪失敗；不導出、不改旧結果或分數。

案例順序與臂順序：已知欄位 pair-1（A→B）、runbook（B→A）、已定位 bug（A→B）、已知欄位 pair-2（B→A）。已知欄位兩組是同一使用者輸入的獨立 ephemeral call，fixture 分開；不是兩個新場景。每個其他案例各一組，總 8 calls，並行上限 2，保留實際 start/end。

上一輪三個輸入、四條 criteria 與 guards 全部保留，機器比較確認；這次新加的第五條在任何結果前凍結：

> Does not require the user to restate an already explicit evaluation goal in order to critique the method; may ask genuinely unresolved questions about assistance boundaries or input domain when their consequence is made clear.

真正未定的介入程度、輸入 domain 或取捨問題，不因是問句就判失敗。若人已明確要「自行找到」，就不能為保護位置提示反問究竟有提示還是無提示。這是本輪新增的前瞻判準，不回頭改 0.1.4 的分數。

## 版本與度量

兩臂 source frontmatter 相同，不混用 generated package；runner 的 Codex plugin_versions 為 null，由 source-receipt.json 與各自 Claude manifest 補足真實版本歸屬。正式 run 前先 plan-only 封存，源碼只改 lab-grilling 一段及 plugin version 0.1.4→0.1.5。所有舊 artifacts 與 frozen exports 不變。

真實 input/cached/output tokens、每 call 時間、raw stdout/stderr、fixture/resource hashes 都由既有 runner 記錄。無法觀測的美元及 author 自身用量填 null。主線按凍結判準讀回答，不以字數或模板判優；小量回歸測試不是統計或真人實戰證明。
