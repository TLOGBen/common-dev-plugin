# 追加條件 A 基線：不靠新指令也能安全完成

Astra/high 單 call，121.880929805 秒、113,029 實報 tokens。主線已覆核全部實際命令／修改程式／簡短輸出與最終交接；重複已知的 skill/reference/state 全文未再逐字重讀。獨立 oracle 14/14 PASS，僅 local task pass，整體戰役仍 blocked。

Astra 讀取整份 campaign.py，透過現有 Python module 的 inspect_state 與 save(previous_bytes) 安全追加 C3、scope 及 extend-criteria event，再用既有 focus/record/block/validate 完成操作。没有嘗試不存在的 extend CLI。

實際來源聚合為 east 1/4、north 2/14、south 1/0；驗收綁定來源／報告 SHA-256，精確欄位、排序、篩選與整數型別；C1 六筆盤點及其原證據、C2 unmet、publish-041 unknown、原始 history/data 保留，舊 state bytes 封存。

最終交接用三列結果表、實際報告／驗收連結，清楚分開本地 C3 完成與遠端 C2 未完成；沒有額外要求缺席使用者批准本來已授權的本地工作，也沒有遠端操作。

這個正例直接推翻「Astra 沒有新 helper 就做不到」的主張。候選版價值只能再從是否少讀內部程式、少造一次性修改、品質與保留邊界是否不退步來衡量；不能把基線沒有 extend API 本身當失敗。
