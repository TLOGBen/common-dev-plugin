# 小型工作：兩組都完成，未觀察到 Delegate 節省

兩組 Astra 都選 Luna/high；都是 Astra → Luna → 原 Astra，沒有第二個 worker 或返工。獨立 oracle 的 0、1、2、11 真實 export 輸出全部正確，驗收器未改輸入。原有 0／2 測試保留並增加 1 的測試。主手未改產品，worker 僅改授權的 2 檔。

| 臂 | 完整 CLI tokens | 實際 episode 秒數 | 主手獨立驗收 |
|---|---:|---:|---|
| W1 無額外 skill | 181177 | 87.190 | 回讀2檔，指定測試exit0，另5組export斷言有captured PASS |
| W2 Lab Delegate0.1.8 | 190460 | 99.551 | 回讀2檔，指定測試命令同composite執行，另6組export斷言有captured PASS |

用量來自 usage-small-pair.json：6/6 已以 exact native turn interval 或 fresh ephemeral turn.completed 校準；原始 resume usage null保留，不重寫raw或summary。實際帳单仍未知，這裡不是API費率換算。Lab多9283tokens、12.361秒僅是此對實測差，不能以單一順序樣本推論因果。

## 命令與人類交接

全部6calls的命令範圍、file_change、產品及完整final已主線讀取。W1主手一次git status返回not a git repository，未阻擋正確完成；W2原始composite含同命令但外部trace只保留測試摘要，不能補造其錯誤。沒有網路、額外模型或越界寫入。

W1 worker稱1suite／3tests，而捕捉到的Node摘要為1file-test、0suite；數字沒有當次摘要支持。其主手不沿用數字，只說exit0並提供独立5組行為。W2 worker按test-file回報；主手提供6組獨立行為。W1主手重跑測試的captured output為空；W2主手composite亦只捕捉末尾輸出。既有trace control限定我們不能據空白推定未執行或模型捏造；產品完成由另行實際oracle支持。

兩份人類交接都先講實際功能、驗證及限制，不捏造金額；均含真正換行，不是字面反斜線n。無真人閱讀／滿意度量測。

## 技能作用與邊界

W2確實完整讀Lab Delegate root、runtime reference與bundled executor TOML；主手將完整操作契約納入brief，worker再次讀同TOML。W1沒有該context，也做了有界brief與主手驗收。這支持「在已明確授權、很小的任務裡，Astra自行協作已足夠」的窄結論；不支持刪除跨任務目標所有權或要求所有主手都免skill。

下一組多約束工作仍待完成，未拿本對數字挑選有利模型。原始、scope、oracle、usage均保留於相鄰目錄。
