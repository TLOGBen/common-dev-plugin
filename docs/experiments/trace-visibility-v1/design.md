# CLI 紀錄可見性控制

四個新上下文、Astra／Sol 各一個順序讀取與可平行讀取臂。每臂六個獨立 cat、只讀一次；六個新 nonce 不出现在 prompt 或命令參數，只存在合成檔案。若 nonce 出現在 final，卻不在任何工具輸出事件，即有工具事件不足以重建該次模型可用內容的證據。若全可見，僅本批未重現，不能證明歷史紀錄無缺口。這不是 skill 品質訓練／held-out，也不改變 evolve 的凍結判準。

CLI 使用 normal ephemeral read-only、保留 execpolicy；不切換權限或重試。最多兩個呼叫並行；實際帳單未知。
