# 採用窄幅 extend helper，不加根技能規則

## 結果

四個 actual Astra/high lead tasks，順序 A/B/B/A，兩種新成果：區域容量報告、共用標籤報告。無 forced worker，這是主手的本地成果／既有帳本維護，不是完整派工測試。

| 題型／臂 | CLI call 秒 | 實報 tokens | 獨立 oracle | 實際追加方式 |
|---|---:|---:|---|---|
| regions A (.5) | 121.881 | 113029 | 14/14 PASS | 自寫 criteria/revision/event，呼叫原 save |
| regions B (.7) | 114.482 | 92267 | 14/14 PASS | extend CLI |
| shared-tags B (.7) | 111.495 | 114345 | 14/14 PASS | parser/execute 的 extend 命令 |
| shared-tags A (.5) | 153.550 | 172871 | 14/14 PASS | 自寫 criteria/revision/event，呼叫原 save |

總計 492512 tokens，exact native task interval 校準 4/4；不是整晚總量或帳單。兩題單次配對、模型有隨機性，wall 不證明普遍加速，tokens 不等於 cache-adjusted cost。

## 主手覆核

四組實際命令、修改邏輯、產物／驗收及最後對人交接已覆核；重複已知 root/reference/source dumps 未逐字重讀。CLI aggregate 空白不當作模型不可見證據；沒有聲稱已逐一復原所有 native 輸出。

兩 A 都安全保留原 criteria/evidence/events/operation 和 state 原稿；兩 B 都用新 extend 命令，不直接重造 criteria/revision/event 更新。B 並未避免閱讀程式：regions B 明確 cat 完整 campaign.py，shared-tags B 同樣發出 cat 命令（aggregate 空白）。因此拒絕「新 helper 消除了閱讀內部實作」的說法。

四組的本地結果精確符合題目；C1 原六筆盤點保留，C2 unmet、publish-041 unknown、整體 blocked 全保留，沒有遠端操作。四個 final 都給實際報告連結及已完成／仍未完成；A regions 表格、B regions 列表、tag 題短文都能承載這種小結果，不強制 HTML。

## 判斷與根因

採用候選 Common Lab 0.1.7：原本我們自己的長任務中增加 Estimate／Astra 目標，卻沒有安全、受測的追加入口。這是工具表面缺口，不是 Astra 缺能力；A 的成功就是反例。二十行左右 additive command 把易漂移的 state bookkeeping 集中在現有原子保存／歷史機制，兩個候選真任務均使用並保留邊界，12 新單元控制及原 16 自測通過。

不新增根 SKILL.md 文字，不要求更多確認、不重開已鎖定範圍、不建通用契約引擎。僅在已使用 campaign reference、使用者增加必要成果時揭露入口。新 criterion 從 unmet 開始；不得清空 unknown operation 或替換舊 criterion。可選 objective/scope 只用來描述使用者新增事項，不賦予權限。

這是便利性／狀態保留改善的窄幅採用，沒有證明任何架構層神經根因或 MoE 內部效應，也沒有推出 Fable／Opus 的結果。候選 source/export hashes 及離線控制在 common-lab/strategic-extend-017a-*。正式 Common 與全域 cache 不變；尚須依 repo 的生成與暫存安裝檢查流程發布實驗包。
