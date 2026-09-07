# Skills Lab：下一週實戰入口

> **目前試用版：Common Lab 0.2.2；Baransu Lab 與 Estimate Lab 0.2.0。** 請先看 [0.2.0 基線的 15 個技能改動與驗證](lab-v0.2.0/README.md)。Common Lab 0.2.2 另納入新版 Wait What 與 MIT 授權的 Show Me Lab。Git 只保留各包最新版套件；歷史測量與原始紀錄不代表新版本的用量、測試或結論。

這次強化的是技能本身：讓 agent 有判斷空間，也讓成果、限制與下一個人的決定能清楚交接。正式插件、既有案件、隔壁 Baransu 與全域安裝均未變更。

[本輪結論與費用](RESULTS-20260907.md)先給重點；[15 個技能逐項判斷](SKILL-VERDICTS.md)交代改動與證據深度。已到指定的 **2026-09-07 03:00（Asia/Taipei）** 並完成收斂；實驗包供下一週試用，真人實戰尚未進行。

| 實驗包 | 現在可試什麼 | 已驗證／尚不能推論 |
|---|---|---|
| [Common Lab 0.2.2](lab-v0.2.0/README.md) | 11 個 `lab-*` 技能；加入新版 Wait What 與 Show Me Lab，長程戰役仍保留獨立校準 | 0.2.0 基線已有短情境證據；0.2.2 的新增呈現技能仍待實戰驗證 |
| [Baransu Lab 0.2.0](lab-v0.2.0/README.md) | think、contract、review、seal；合約先落檔，驗證按風險設有限額度 | 套件驗證與短情境紀錄可查；不是原版完整封緘或 hook 替代品 |
| [Estimate Lab 0.2.0](lab-v0.2.0/README.md) | `$lab-estimate`；保留唯一計價與 PM 核准，長程跨包按需獨立核對 | 導出、暫存安裝及回歸紀錄可查；情境回應不等於實際案件或真人 PM 驗收 |

## 安裝所選實驗包

以下命令在此 repository 根目錄執行；這輪實際驗證的是 Ubuntu WSL 的 Codex CLI，未修改 Windows App 的全域安裝。

```sh
codex plugin marketplace add ./experiments/common-lab
codex plugin add common-lab@common-lab

codex plugin marketplace add ./experiments/baransu-lab-v0.2.0
codex plugin add baransu-lab@baransu-lab

codex plugin marketplace add ./experiments/estimate-lab-v0.2.0
codex plugin add estimate-lab@estimate-lab
```

Lab 的版本是獨立套件版號，不與正式 Common 的 1.x 比大小，也不覆蓋正式版。三包可分別選用，不必一次全裝。安裝後用 `codex plugin list --json` 核對實際版本；重新開啟對話後，也要確認載入的技能名稱與版本。暫存 CLI 安裝成功不代表另一個 App／Host 已載入新版。

不要把正在使用的正式 Estimate 案件直接交給 Lab runtime。新案例預設放 `.estimate-lab/<case>`；跨版遷移另以明確範圍的副本試驗。回到原流程時選原技能與原案件，保留實驗證據，不需要刪除原始資料。

先看 [15 個技能的成果選用指南](FIELD-GUIDE.md)：依你缺的是理解、決定、推進、實作或驗收來選，不必背完整流程。

## 實戰怎麼看成效

每次比較固定一個版本。若原版與 Lab 都可被選用，先明確指定這次使用哪一版，並核對實際讀取的技能；同一任務若混用兩版，就記為混合條件，不當成純 A/B。這輪的凍結 CLI 對照隔離了所選技能，不能假定一般 App 對話也天然隔離。

挑一件真的要做的工作，記下使用的版本／模型與你原本要拿到的結果。結束時只回答：拿到了什麼、哪裡還不能用、哪個停頓幫到了決策、哪個停頓只是重問、接手成果時還必須向 agent 追問什麼。

完成與品質不是同一個分數：先核對任務是否真的完成，再記漏抓問題、誤判阻擋、證據是否支持內容。一次多快或多省不能代替這些觀察。Astra／Sol／Luna 有部分實測；Fable 與 Opus 未完成實測，不推論通用模型排名。

新增分支：[Astra 當主手時，哪些 harness 真正有效？](astra-lead-harness/REQUEST-AND-MOE.md) 已有真主手初篩、完整戰役與窄入口對照；[逐機制暫定取捨](astra-lead-harness/MECHANISM-VERDICTS.md)保留原目的、因果證據強度及未知，不以整包勝率替代判斷。[四組決策後接續](astra-lead-harness/resume-v1-review/lead-disposition.md)及[無額外技能完整戰役](astra-lead-harness/campaign-noextra-v1-review/lead-disposition.md)已完成：可辨識保留機制、冗餘流程與測試載體摩擦，不宣稱所有 harness 均不需要。

## 查證據，不必讀完整實驗目錄

- [目前發現與不能宣稱的事](common-lab/RESULTS.md)
- [285 次已結束 Codex CLI 呼叫索引](measurement-index-285calls-20260907/index.json)：277 次已知 42,623,631 tokens、8 次未知，原始去重／用量／價格可重算檢查通過。涵蓋 manifest 指定批次至最終封存題目，排除主線及原生代理；API 短 Standard 等值 US$96.06783308，不是實際帳單。
- [截止主線快照](native-usage-20260906/snapshot-c.json)：2026-09-07 03:00:58 Taipei 取樣，去除 fork 繼承後 314,516,128 tokens；短 Standard API 等值 US$459.1258084。不含明確基準以前、未歸屬 session 或取樣後交接；與 CLI 分開計量，非帳單。
- [Common 0.1.8／Baransu 0.1.1／Estimate 0.1.3 最終暫存安裝收據](install-final-20260907/result.json)：20／7／24 檔逐位元一致，Estimate 安裝後 64 項 Python 與 5 項事件測試通過。
- [Astra 追加成果 A/B：四組皆成功，新 helper 的窄幅採用](astra-lead-harness/extension-v1-review/lead-disposition.md)
- [Baransu 0.1.0／Common 0.1.2 先前安裝收據](install-verification-20260906-a/result.json)
- [show-me／wait-what 一手來源研究](human-handoff-web-research-20260906.md)

每次導出使用新目錄；發布清單只保留各包最新版，舊包與候選包僅保留本機副本並忽略。需要重跑歷史測試時，請從 Git 歷史中的 `49a7e4c7094efdaa5215886f5ef03849fcb835a3` 在獨立 checkout 取回當時版本；不要把歷史腳本的固定路徑直接換成新版後沿用舊結論。原始報告與收據維持當時內容。生成物和模型回應不會自行變成授權、真人理解或實際產品完成證據。
