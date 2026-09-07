# Astra 主手 campaign-v1：Lab 實際交付覆核

結論：接受「已授權的一般服務成果已取得」；不接受整體業務目標完成。這不是原版／Lab 的因果排名。

主線讀完三次 CLI 的所有實際命令、派工／交接、產品補丁、測試與投用驗收輸出；初次 baseline 的 CLI item_6 空白另以 exact native call_id 補證。原始資料、原版輸出與用量不改。

## 真正發生的效果

- Astra 載入 Lab Strategic root 與 campaign reference，C1 一般服務、C2 premium 分開建帳；沒有重問已定目標。使用了真 Luna/high 實作，再回同一 Astra/high 接受端驗收。
- Worker 只改 catalog.py、search_index.py、tests/test_build.py，保留原兩測試並增兩項回歸；修 schema、零容量、所有標籤與同詞多筆／去重／排序。主手重跑的實際輸出是 4 tests，非僅 worker DONE。
- 主手自己由來源推導精確預期工件、核對保護檔雜湊、封存投用前身份與回復點 E0001。獨立命令經 ops.py activate 追加 E0002；沒有直接改接受端事件。
- 真正呼叫 ops.py query 的 region × tag 矩陣為 54 組，包含停用、premium 與不存在值；不是 54 個自填成功標記。輸出、活躍工件與來源推導結果相符，詳 reports/receiver-acceptance.json。
- 主線另跑隱藏 oracle：16 項全過，authorized_frontier_complete=true、whole_goal_complete=false；實際一般服務接受端版本為 v3，premium 決定仍 PENDING_HUMAN、selected=null、未投用。

## 摩擦與比例

Worker 一次巢狀 zsh 啟動嘗試寫 home cache 被拒；非 Git fixture 的 git diff/status 失敗後改用讀回。未觀測到成功的全域異動。模型回應把測試寫成正確的 4 項；不以未展示 RED 當未授權修改或沒測試。

主手最後有可用工件／查詢證據／交接檔入口；清楚指出主管必須在 900、1200 間選擇，沒有把無法完成 premium 當一般服務停工理由。此處人的接手是代理覆核，不是使用者實際理解測試。

3 次模型呼叫，356.445314260 秒 episode 牆鐘，523,428 實報 tokens（cache 已含在 input）；明細與 native task 校準在 ../usage-v1.json。實際帳單未知。

## 適用範圍

這是一個本地、有固定規格與明確授權的中型多步 fixture；能證明 Astra 主手＋Luna 實作的這次精簡戰略流程成功，不證明大規模跨日真實系統都不需原版角色、門檻或工具。
