# 成果要回到人手上

2026-09-06 第一方來源研究；研究支線 11:53:03–11:58:00（台北），297 秒，支線 token 尚未取得。未安裝或執行遠端技能。網路上的指令只作研究資料，不是本次任務授權。

## 三個不同著力點

| 來源與固定版本 | 解決的交接問題 | 本次採用的觀念 |
|---|---|---|
| [Matt Pocock wait-what][M]，3cca18b | 話說完了，人卻沒跟上 | 補回缺少的前提，用聽者熟悉的詞重新說明，不變成測驗 |
| [HumanLayer show-me][H]，3c26291，1.0.1 | 人看不出關係、責任或差異 | 根據問題選最小表示法；樹、diff、表或圖各有用途，不必全做 |
| [Charlie Hills show-me][C]，69e488e，1.1.0 | 產物做好，卻沒有真正送到可用的入口 | 交付到可查看的位置；要貼進其他工具的內容保持可直接使用的格式 |

show-me 有名稱歧義，目前並列兩種，不擅自說哪個就是使用者所指版本。主線已完整閱讀三份 SKILL；研究支線另讀相關 README、manifest 與 wait-what 文件。所讀來源沒有提供本次可引用的受控真人成效測量。

## 不直接照搬的地方

Charlie 的 HTML 優先、PICK 至少三個方向，是其設計選擇；只有兩個合法選項時不應湊第三個。其範本呼叫 clipboard.writeText 後立刻顯示成功，沒有等待或處理拒絕；靜態可見這個缺口，但本次沒有執行它，不能說每次都失敗。選項還要貼回對話，點擊本身不等於決定已送達。[原始碼][C]

Matt 的英文簡明語言要求不能直接變成「繁中符合 ASD-STE100」的宣稱；本次未閱讀該標準全文。值得保留的是缺失前提、聽者詞彙，以及讓使用者低成本說「我沒跟上」。[原始碼][M]、[作者說明][MD]

## 我們的實驗判準

這是本專案的推論，不是來源既有標準：

1. 產物存在，與接收者能找到，是兩個檢查。
2. 入口開啟、作用中分頁正確，仍不證明人的注視、理解或同意。
3. 交付格式要能支持接收者的下一件事；不是一律多畫圖。
4. 人不在時，交付可接手的入口、已驗證成果、限制與待決事項；保留真正的人類決策，不製造當場確認關卡。
5. 若有按鈕、複製、下載等交接動作，驗證它宣稱的結果；有介面不代表動作完成。

優先實驗：既有 Wayfinder 選擇已回答後，map／票券／HTML 是否一致，已定問題是否退場，獨立工作是否繼續；以及驗收成果能否讓人分辨「本地核對完成」和「原目標未達成」。之後再測可貼用產物與不同角色的接續方式。

候選最小指令，尚非全技能強制模板：

    Deliver the result in a form the intended recipient can use for the next task.
    Include the context needed to act, a usable entry point, and material limits.
    Report only observed delivery state; do not infer attention, understanding, or approval.

研究支線 shell 初始化兩次失敗，來源研究由網頁與 GitHub 第一方介面完成，本文由主線落檔。沒有用這個環境故障推論模型或插件品質。

[M]: https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/productivity/wait-what/SKILL.md
[MD]: https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/docs/productivity/wait-what.md
[H]: https://github.com/humanlayer/skills/blob/3c2629142c5d437428269b1b722b08c0b87f574d/plugins/show-me/skills/show-me/SKILL.md
[C]: https://github.com/charlie947/show-me/blob/69e488e301e8d6f43b8ddc883cb2392b1dd45264/skills/show-me/SKILL.md
