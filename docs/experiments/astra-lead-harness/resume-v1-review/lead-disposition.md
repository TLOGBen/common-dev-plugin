# 決策後接續：先保留正确停頓，再精簡代價

兩版都能承接人的已核准900：ready兩組各恰好一次premium900，standard/歷史保留；unknown兩組都不重送、不把歷史published與最新approved拼成成功，不要求人再選費率。故本批不支持「原版不會接續」或「Astra多餘確認必然停住」。

| 情境／版本 | 真call數 | episode秒 | 已知tokens | 無法取得用量 | 實際成果 |
|---|---:|---:|---:|---|---|
| ready／原版 | 3 | 1054.843448139 | 965,361 | 1次scribe timeout | 本地投用及驗收完成；hash摘要轉錄錯誤由主手另檔更正 |
| ready／Lab.7 | 1 | 171.562545243 | 309,634 | 無 | 一次投用；54組query實測；清楚限制外部效果 |
| unknown／Lab.7 | 1 | 154.478854178 | 163,814 | 無 | 唯讀釐清/交接完成，premium成果仍未證實 |
| unknown／原版 | 3 | 841.283819621 | 729,570 | 1次scribe timeout | 同上；主手更正pivot記錄後IN_PROGRESS |

本批8calls、6known合計2,168,379tokens，2unknown不填0。source input2,141,303含cached1,935,872、output27,076含reason2,889；校準在usage-complete-v1.json，原carrier跨resume null保留不改。時間包含真逾時，不能把兩次scribe成本排除才比較。也不能把兩版差距歸因到某一條指令：原歷史ledger來自不同前輪，角色、schema、讀量、重試選擇共同變動。

可定位摩擦：兩次scribe花時間完成多欄位draft及readback，均600秒未回；主手實際接到部分結果後能有限修復/交接，不是模型放棄。ready舊同權級claims衝突引發validator連鎖拒收；unknown字段pivot与證據語義不一致卻曾validate通過，主手仍需讀內容更正。語義判斷不是schema可以包辦。

值得保留：目標所有權、先確認真核准/可用權限、歷史與當前分離、未知作用釐清再重試、按當前證據交給人。值得縮減：每一步強制scribe和大量冗餘衍生欄位。Lab小帳本是替代手段，不是刪掉跨回合記憶；extend便於保存新增要求，但Astra基線同樣能手動維護。

人接手：四final均區分可證實結果、限制及下一步；Lab unknown相對反引號路徑較不便點入，其他直接文檔入口。只有主線/模型reader proxy，不宣稱真人一週已驗收。所有oracle正向/守界PASS均非全目標完成率；未知案如實未完成正是合格結果。

後續「無額外技能 vs Lab」完整可執行戰役已結案，見 [分開記錄的判讀](../campaign-noextra-v1-review/lead-disposition.md)。無額外 skill 組真正完成局部成果；Lab 組被額外 Python 快取寫入的載體邊界中止，不能混為純 skill 能力差異。
