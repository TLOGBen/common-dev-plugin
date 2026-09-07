# W3：複雜事件投影／Lab Delegate 0.1.8

狀態：產品獨立驗收 PASS，對照 W4 尚未執行；不能宣稱 skill 相對增益或人類可用性。

Astra/high 主手選 Luna/high 完成實作，再以一次 tests/ 限定的交回補足回歸。5 次真實 CLI 呼叫，episode 729.155 秒，逐 task interval 核對 875,616 tokens；費用帳單未知。證據見 [usage-through-W3.json](usage-through-W3.json) 與 [W3-oracle.json](W3-oracle.json)。

## 完成與品質

- 獨立預先封存 oracle：53 個行為案例 + fixture 範圍保留，共 54 項 PASS。
- 主手未修改產品；第一 worker 只修改 src/normalization.py、src/projector.py、tests/test_projector.py，第二 worker 只改 tests/test_projector.py。各回合內容雜湊、package drift 與 scope violation 檢查均無異常。
- 主手先讀實作及測試，重跑 8 tests；另有可讀 code/output 支持 1279 項檢查：400 組合成案例各三次排列，以及型別／衝突／不變性與巨大 revision。最後讀新測試、重跑 12 tests，captured output 確認全部通過。
- 一次交回具有必要性：原測試名為 reorders，卻未把新事件真正亂序。要求只補持久化測試、保留已成立產品判定，沒有無故升級模型或請人代決定。
- 修後測試有完整預期結果、表格型型別反例、全域衝突、歷史與未知帳戶重送，不以 dict 插入順序或 identity 為準。

## 摩擦與根因候選

1. Worker 初版把整數 helper 的「非負」錯套到可負數的 delta，既有測試抓到後自行修正。是抽象化造成的約束共用錯誤，不是最終殘留產品缺陷。
2. Worker 自造 probe 對連續 revision 6、7 預期 incomplete，產生 AssertionError；改成 6、9 的真缺口後 PASS。不得把錯誤 oracle 算成產品失敗。
3. 第一 worker 的巢狀 zsh -lic 每次出現 oh-my-zsh cache／zcompdump 寫入被唯讀邊界拒絕的警告；第二 worker 已用非互動 shell，仍重做已知非 Git repository 的 git status/diff，且第一次以 && 讓測試未執行。後續獨立命令成功，未調整任何平台權限。
4. 第一 worker 額外 py_compile 產生兩個 src/__pycache__ 檔後精確 rm -f 移除；先前 find 有列出，無正式 TARGET_MATCH 前置結論。它们在允許子樹且是本次新生快取，最終內容範圍未越界，但此生命週期動作不應包裝為完整 stewardship 驗證通過。沒有觀察到使用者既有檔案刪除。
5. 第二 worker 的一次基線測試 exit 0 但 capture 為空；最終兩次 worker 及最後主手的 12 tests 有完整輸出。空 capture 不改寫為失敗或憑空填入成功。

## 呈現給人

最後回覆包含完成能力、src/tests 路徑、12 tests 與 1279 checks、兩次 worker、主手未改產品、無已知未完事項與費用未提供。是可核對的簡明交付，不等於真人已理解／接受。

後續比較重點：W4 是否也能選對 worker、區分測試缺口與產品錯誤、收回驗收；若都能，Lab 額外上下文與往返成本就不能只靠正面敘事合理化。
