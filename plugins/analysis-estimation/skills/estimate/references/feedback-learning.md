# 公司 SOP 回饋與學習手冊

當使用者提出體驗、建議、缺少能力、操作摩擦或 Agent 判斷問題時讀取。

## 回饋先服務使用任務

第一個問題是：使用者原本要完成什麼？記錄任務、摩擦位置、實際影響、期望結果、根因假說、證據強度與可分享的最小重現。使用者不需要先提出技術解法。

執行：

```text
python scripts/feedback.py prepare <case-root> --task ... --friction ... --impact ... --expected ... --root-cause ...
```

輸出本地 Markdown／JSON 回饋卡。沒有 Git、未登入、不是 repo、缺少遠端／權限或禁止外送時，到此即算完成。

## 中央 Issue

環境允許時，Skill 可產生 `common-dev-plugin` Issue 草稿。中央內容只保留：抽象任務、可遷移根因、對 Skill 的影響、期望行為、合成最小重現與證據等級。

客戶名、專案名、repo、branch、路徑、類別／資料表、內網、帳密、原始碼、log、畫面與原始產物不進 Issue。若去識別後不能說清根因，留在本地繼續分析。

Issue 建立是外部寫入。Agent 先顯示標題、正文、目標 repo 與去敏結果；只有使用者明確確認後，才使用可用的 GitHub／GitLab 工具建立。

## 集中評議與分支

維護者依回饋量、重要事件或版本規劃主動開啟回顧。跨案重現、核心風險，或維護者具理由的判斷都可進入候選改善，並如實標示證據等級。

每個核准 Issue 使用獨立 branch／PR。改善先在原情境與不同情境驗證；決定性規則同步更新 tests。核心思考放正向原則、特定判斷放指南、脆弱工具流程放手冊、一致規則放 script／test、PM 認知問題回到決策包與交付內容的 fresh-reader 驗證。維護者核准後才合併 `common-dev-plugin/main`。
