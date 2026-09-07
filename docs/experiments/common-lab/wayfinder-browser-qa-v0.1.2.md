# Wayfinder 0.1.2：主線瀏覽器驗收

記錄日期：2026-09-06（Asia/Taipei）。檢查對象是 `wayfinder-regression-v0.1.2-c/`，不是原版或 a/b 產物。此筆整理的是主線先前已做的 IAB 操作；沒有另行估算檢查起迄或 token。

## 實际觀察

- valid-focus 首屏顯示明確選定的 23，不因 02 編號较小就把它當成人要回答的問題。
- 對原生 details 的 `#map-overview-summary` 送出 Enter，實際展開全圖；三類已定／未知／範圍外內容均可回取。
- 已解前置顯示「前置已解」，不再用停止符號與可處理狀態互相矛盾。
- 390 × 844 viewport：innerWidth 390、documentWidth 375、focusWidth 319，沒有水平溢出；檢查後已還原 viewport。
- resolved-focus 不再要求回答已解問題；警告且全圖維持展開。

## 邊界與摩擦

WSL Playwright wrapper 有 CRLF 問題，CLI 能執行但 Chrome 未安裝；改用現有 IAB，没有安裝新瀏覽器。IAB 的 screenshot 呼叫無法擷取，因此本筆只證明 DOM／可存取樹、鍵盤互動與幾何，不宣稱像素、配色或整體視覺舒適度通過。summary 的文字／role 定位未匹配，觀察到的 ID 定位可用。

resolved-focus fixture 只改票券狀態，map 的未知段落仍保留舊問題。Renderer 忠實显示資料，不應猜測替人改決策。後續真正的 agent 跨回合更新測試會查這種敘述漂移。

## 可重查產物

- regression receipt SHA256：`e22b0daea117bfdb5fbad7e49f3f5b4c0d93c4ce90183a079ce840d4167ccc25`，54 checks PASS。
- valid-focus/map.html：`9154c854363225fc57620578ba4d0168aabac79839aab51690625ae7bcaa9dc4`。
- resolved-focus/map.html：`806b25799a3d2bc81e62bc5a451a70d92af3d75e56072ce61f8fe03d7cf8025d`。

此驗收接受 0.1.2 這組有證據的呈現修正，並非承諾所有未知狀態與真實專案均已覆蓋。
