# Delegate 單條資訊傳遞候選

來源是 screen-v2 小修中的一次真摩擦：主手已知 non-Git，brief 卻沒有傳遞，worker 再嘗試 Git。它只支持一個可測假說，不能證明需要新規則。候選在 .5 基礎多一條「帶上已確認、會影響下一步的限制或失敗方法及證據範圍」，版本暫記 .6；未合入 plugins/common-lab 或正式實驗發行。

新 public task 為 queued ticket 的 owner 彙總，含 estimate=0、排序、排除 done、精確欄位與輸入不變；不是原 countLabel 修正。A/B/B/A 四個 fresh fixture，A=.5、B=候選.6。Astra/high 真主手與 Luna/high worker，由同一 Astra session 回來驗收。每個主手先取得 host 在該 fresh fixture 實際跑 git rev-parse 的 exit128／stderr；這份 observation 不在 worker public TASK，須由主手實際 brief 傳遞。任務不要求 Git、不刻意誘導已知失敗，worker 即使沒取得該資訊也可能自然完成。

預先量測：事實是否準確傳遞、worker 是否重做已知無效 Git 操作、五組獨立正確性／逆序輸入／輸入不變性 MOE、主手驗收、真實耗時與可得用量。無效果是有效結果，不按快幾秒作勝負；四次非盲固定序列不構成廣泛因果證明。版本號也是分發所需差异。凍結 manifest 在 delegate-context-v1-plan/manifest.json。

Oracle 負控制 v1 曾失敗：把 group 初值 0 改 false 後，JavaScript +=0 會轉回正確的 0，因此那不是有效壞產物；不是模型或 oracle 放過錯誤。v2 改成確實回傳 boolean 的變異，四個控制通過。兩份收據與全新暫存副本保留；model_calls=0。
