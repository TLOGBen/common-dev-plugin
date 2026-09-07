# 未執行的首次凍結

本次八個 spec 與 manifest 保留原樣；模型呼叫數為 0，不執行這組輸入。

凍結後、inference 前的獨立 code review 發現 oracle 以 Python 容器相等判斷 JSON，會把 quantity=false 與 quantity=0 視為相等，但公開規格要求保留原值及 canonical JSON 身份。這是量測器缺陷，不是 Astra、Luna 或某個 skill 的失敗。

修正方向：評估者獨立建立 canonical JSON bytes 比較，新增 false/0 的負控制；不得 import actor 的 delivery_tool 當 oracle。public fixture 不需變動，修正後以新目錄重新凍結，舊收據與本目錄不覆寫。
