# E4：實際檔案讀者代理

模型執行前固定8次Sol/high：四種控制包（齊備有合成核准、待核准、必要CSV缺失、說明空泛），及E2兩臂各一個CSV-only與一個handoff packet。不是八次真人訪談。

CSV-only只允許真正對外主表，不給內部報告或答案；handoff packet另測完成邊界與入口，不把它的表現當成CSV-only效果。讀取原始E2檔案，凍結hash前後核對，不改寫產物或換掉路径。

控制包固定五欄契約。Missing只不建立指定CSV，沒有刪除任何既有檔案。Opaque label與private truth留在manifest，actor只看entry/files/task。讀取隔離是prompt約束加trace審查，非存取控制；sandbox保持read-only。

裁決分為檔案可用性、語意真實/充分性、讀者代理回述。必要檔案缺失只使該檔語意not-assessable，不等於真實業務失敗；空泛文案不能靠檔案齊全或核准標記過關。實際E2成果為高值預覽，PM核准未發生；CSV單獨不足確認狀態時必須保留未知，不是替它補上正確答案。

先freeze再run，保留raw讀檔trace、實報usage、耗時、失敗與原資料hash。主線看輸出與trace後判斷，無自動總分或真人理解宣稱。
