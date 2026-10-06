# Changelog

All notable changes to this marketplace and its plugins. Plugin versions are independent; the marketplace version tracks the catalog.

## Common Mod 0.10.1 — bar 暫時記錄按鈕的時間點

- 查「看不懂」「畫給我看」按下後約 5 秒才出現的延遲：按下、指令開始與結束、這一輪開始與結束（含讀用量的時間）、`isWorking` 變化，各記一行時間到 `~/.claude/common-mod-bar-trace.log`（最後 200 行）與 debug log。查完會拿掉。
- 53 項 `claude plugin test`、`claude plugin validate` 通過。marketplace 1.81.1。

## Common Mod 0.10.0 — desktop 版的 bar、側聊、回想重新排版

只動 desktop（與 VS Code）；terminal 不變。
- **bar**：收成一列，按鈕在左、量表在右；寬度不夠時三個量表整組換到第二列。拿掉資料夾、模型（desktop 頂端與輸入框下方已有）與兩組按鈕間的「│」；量表條縮短；「下一步」的建議改成原生按鈕。
- **側聊**：空的時候說明放在面板中間；問題加外框靠右，回答在下面，附「帶回主對話」按鈕；輸入框與「在新視窗分支」按鈕放在面板底部，輸入框撐滿寬度、提示文字縮短；拿掉「Esc 回到主線」（desktop 有關閉鈕）。
- **回想**：搜尋框撐滿寬度、提示縮短，段數與「收起」靠右；結果依今天／昨天／本週／更早分組，每段第一行標題與專案（前面是專案色點），第二行是符合的片段；滑過整列換底色。
- 53 項 `claude plugin test`、`claude plugin validate` 通過；`tsc --noEmit` 只剩既有的 `focus` 型別錯誤。輸入框能不能真的固定在側聊底部、整列能不能都按得到，要在 desktop 上實測。marketplace 1.81.0。

## Common Mod 0.9.0 — bar 的 terminal 與 desktop 各自一種畫法

- **架構**：bar 拆成 `model.ts`（共用狀態與純函式）、`actions.ts`（按鈕清單，每顆寫明在哪些介面畫）、`terminal.tsx` 與 `desktop.tsx`（兩種畫法，純函式）。引擎的 `$` 不能跨 import，所以只有 `bar.tsx` 碰引擎，其餘檔案只收資料與綁好的 callback。
- **desktop**：原生按鈕（整顆可按）、SVG 量表（綠／琥珀／紅，淺色與深色主題都看得清）、文字用主題色；不畫 Nerd Font 字元、不畫「圖示」開關，也不讀它的設定；不畫 diff 與 artifacts（那是 terminal 的對話框指令，desktop 自己有 diff 入口）；沒有逐格動畫。VS Code 用同一種畫法。
- **terminal**：外觀不變；chip 的內距移進按鈕文字，空白處也按得到。「圖示」開關只影響 terminal。
- **兩邊共用**：按鈕失敗時跳提示說原因（原本什麼都不顯示）；session 沒有的指令（例如沒裝 common 時的看不懂、畫給我看）不畫按鈕，指令清單每輪更新；Claude 工作中的 30 fps 重畫只在 terminal 畫過 bar 之後才跑。
- 50 項 `claude plugin test`（共用行為在 terminal 與 desktop 各跑一次）、`claude plugin validate` 通過；`tsc --noEmit` 只剩既有的 `focus` 型別錯誤。marketplace 1.80.0。

## Common Mod 0.8.0 — 拿掉 `/side` 與 `/recall` 指令，只留 bar 按鈕

- **side**：拿掉 `/side` 指令，連同它的 `[問題]` 參數、遠端操作時指向 `/btw` 的提示，以及只有指令在用的 `openSide`。側聊面板照舊由 bar 的「側聊」打開。
- **recall**：拿掉 `/recall` 指令；回想由輸入框打 `#` 或 bar 的「回想」叫出。
- session 開始時不再註冊任何指令；bar 測試確認沒有註冊指令，recall 測試改成按「回想」開啟。
- 34 項 `claude plugin test`、`claude plugin validate` 通過；`tsc --noEmit` 只剩 bar 既有的 `focus` 型別錯誤（side 那處隨 `openSide` 一起移除）。bar 在畫面上不顯示時（例如輸入框上方出現問卷），側聊打不開，要等 bar 再出現。marketplace 1.79.0。

## Common Mod 0.7.0 — 回想改回可用 `#` 叫出，點一段就放進輸入框

- **recall**：在輸入框打 `#`（開頭或空白之後，`C#` 這種字中間的不算）會展開回想區塊，以 `#` 後面的字搜尋；按鍵留在輸入框，打完一個空白就收起。`/recall` 與 bar 的「回想」照舊展開有自己搜尋框的區塊。
- 點一段對話會把 `#chat:<id 前 8 碼>` 放進輸入框（取代正在打的 `#…`，或接在原本的文字後面），並收起區塊。送出時，本人打的（終端機或 Remote Control）`#chat:` 標記會換成「〔回想：標題〕」，那段對話的標題、問過的話與最後回答以資料框住附在 context，超過長度上限的不附上並說明；其他 session 傳來的與單純的 `#字` 保持原樣。
- 拿掉「分支」「總結」與選中後的往返預覽，`recallPicked` 狀態與 indexer 的 `EXCERPT` 一併移除。
- 35 項 `claude plugin test`、`claude plugin validate` 通過；recall 沒有型別錯誤（`tsc --noEmit` 只剩 bar、side 既有的 `focus` 型別錯誤）。marketplace 1.78.0。

## Common Mod 0.6.0 — bar 拿掉「資料夾」與「VS Code」

- 動作軌拿掉「資料夾」「VS Code」兩顆按鈕，以及整組外部程式（深靛底色）；交給系統開啟程式的 `openOutside` 一併移除。遙測軌照舊顯示資料夾名稱。
- 30 項 `claude plugin test`、`claude plugin validate` 通過。marketplace 1.77.0。

## Common Mod 0.5.0 — 側聊改回停靠在對話旁的面板，新視窗分支改成面板裡的按鈕

- **side**：`/side` 與 bar 的「側聊」改回開 `side` Pane：全螢幕版面、寬度至少 110 欄時停靠在對話旁（和 diff 面板同一個位置），其他情況顯示在輸入框上方（24 列）。答案來自 `$.model.fork`，看得到主對話到目前為止的內容，不會用工具；「帶回主對話」把問答引用放進輸入框。面板底部新增「開新視窗分支（可換模型、可動手做）」按鈕，沿用 0.4.0 的 `claude --resume --fork-session` 與「帶回主線」。
- **修正**：還沒有任何一輪對話時，session 紀錄檔還沒寫到硬碟，新視窗會顯示 `No conversation found with session ID` 後馬上結束。現在先檢查 `$.session.turns()`，是 0 就不開視窗，改成提示「先聊一輪再開」。
- **bar**：「側聊」直接呼叫 `$.ui.open` 開同一個面板（面板設定以純資料從 side 匯入，因為 `$` 不能跨 import 傳遞）。
- **bar 修正**：資料夾路徑原本在第一次繪製時才讀，而且排在用量數字之後；用量讀不到時資料夾就沒讀，「資料夾」「VS Code」按了完全沒反應。現在按下時若還沒讀過，會當場讀；開啟後跳出提示（Windows 可能把新視窗開在終端機後面）。讀不到資料夾時也會說明。
- 31 項 `claude plugin test`、`claude plugin validate` 通過；本機沒有 tsc，這次沒跑 `tsc --noEmit`。停靠的實際畫面以實機為準。marketplace 1.76.0。

## Common Mod 0.4.0 — 側聊改成新視窗分支，回想改長在輸入框上方並可分支或總結

- **side**：`/side` 與 bar 的「側聊」改成在新的 Windows Terminal 視窗執行 `claude --resume <目前 session id> --fork-session`。分支是完整的 session：可以 `/model` 換模型、可以用工具，關掉後紀錄留著。開分支時把主 session 的 id 存進 `$.store`（`branchParent`），分支啟動時只認 60 秒內留下、且不是自己的 id，取用後清掉。分支視窗的 bar 多一顆「帶回主線」：用 `$.model.fork` 整理分支裡的進展，以 `$.session.send` 送回主 session，送不到會說原因。原本 `$.model.fork` 的側聊面板、「帶回主對話」引用一併移除。非 Windows 不開視窗，改成說出要自己執行的指令；手機或遠端照舊指向 `/btw`。
- **recall**：拿掉 `@@` 與記憶地層面板。`/recall` 與 bar 的「回想」改成展開／收起 bar 下方的區塊：自己的搜尋框、前 5 筆符合的對話，選中一段後顯示最後 3 輪「你／我」往返，以及兩顆按鈕：
  - **分支**：在那段對話當時的資料夾開新視窗分支；WSL、其他電腦（額外資料夾）或 Cowork 的紀錄無法在這台接續，按了會說明。
  - **總結**：讀取最後 40 輪往返交給目前的模型總結，以「〔回想總結：標題〕」開頭放進輸入框當草稿，不會自動送出。紀錄以資料框住，模型輸出先清掉跳脫序列與控制字元。
- **indexer**：索引多記 `cwd` 與 `isLocal`（只有家目錄 `~/.claude/projects` 下、非 Cowork 的才算），舊快取缺欄位的會重讀；新增 `EXCERPT`，用 node 串流讀單一對話的往返。
- **bar**：「側聊」「回想」按鈕不再走 `$.command.run`，因為 plugin 自己的 `$.command.run` 觸不到它自己的 `command.run` hook，按了會回報「no command.run hook answered it」。ctx 的最近幾輪長條圖拿掉，只留 token 數與上一輪增量。
- 23 項 `claude plugin test`、`claude plugin validate`、`tsc --noEmit` 通過；兩段 node 腳本在本機真實紀錄上跑過。新視窗、band 的實際畫面與輸入框焦點以實機為準。已知未解：本 session 直接打 `/recall` 也回報沒有 hook 接住，原因未查明。marketplace 1.75.0。

## Common Mod 0.3.0 — bar 的 Nerd Font 圖示開關

- 動作軌最後新增「○ 圖示」按鈕，切換 Nerd Font 圖示模式（開啟時顯示「● 圖示」）：按鈕兩端改用 powerline 斜切字元 `U+E0BA`／`U+E0BC`，每顆按鈕前加圖示（側聊、回想、diff、artifacts、資料夾、VS Code、看不懂、畫給我看、下一步），資料夾名稱前加資料夾圖示。只用 Font Awesome 與 Octicons 長期穩定的碼位，避開新版才有的擴充區。
- 預設關閉：沒有 Nerd Font 的終端機會把這些字畫成方塊。選擇存在 `$.store`（`barGlyphs`），同一台電腦的每個 session 共用，重開也記得。
- 已知限制：Claude Desktop 內建的引擎若低於 2.1.287，mod 不會完整運作，狀態列不出現、`/side`／`/recall` 也可能回報沒有 hook 接住；等桌面版更新內建引擎即可。
- 27 項 `claude plugin test`、`claude plugin validate`、`tsc --noEmit` 通過。Nerd Font 圖示的實際外觀以實機為準。marketplace 1.74.0。

## Common Mod 0.2.0 — 新增 bar：輸入框上方的狀態列，取代 settings.json 的 statusLine

- 新增 **bar** mod（`hooks/bar/`），在輸入框上方的 band 畫兩道掛在同一根霓虹脊柱上的「軌」，輕度賽博龐克配色：脊柱是兩列高的 `Raster`，由霓虹青漸變到洋紅，量表的綠／黃／紅推向霓虹（`#3cf2a0`／`#ffd23f`／`#ff3864`），其餘用鋼藍灰。數字來自 `$.session.usage()`、`session.measure` 與 `turn.complete`；設了 `CLAUDE_CODE_AUTO_COMPACT_WINDOW` 時，ctx 照舊以該值為分母。
  - **遙測軌（第一列）**：資料夾（青色粗體，家目錄顯示 `~`）與模型（ID 轉成 `Sonnet 5.5` 這類名字，有 effort 時加 `[high]`），接著 ctx、5h、7d 三個同形量表：標籤、等長進度條、百分比、補充。ctx 的補充取自官方範例 token-weather（anthropics/claude-code-playground，Apache-2.0）：`94k/200k`、最近 12 輪主對話的小長條圖、上一輪增量 `▲+98k`；5h／7d 的補充是重置倒數。天氣圖示沒有採用：在部分字型會畫成彩色 emoji，破壞對齊。寬度不足時整列依序收：進度條 14→10→6 格、拿掉長條圖與增量、拿掉模型與倒數、最後只剩數字。
  - 進度條用 `Raster` 畫：已填 `━`、半格 `╸`、軌道用虛線 `┈`，避免被看成輸入框框線的碎片；填色依位置漸變（約 70% 起轉黃、90% 起轉紅）。
  - 進度條頭部的前幾格逐格提亮，像霓虹燈管點亮的那一端。
  - **動畫**只在動的時候重繪：數值變化時進度條平滑滑動（約 0.3 秒），百分比先亂碼再由左到右定格（約 0.4 秒，只在整數值改變時觸發）；Claude 工作中脊柱的顏色沿著它流動、ctx 條有流光；任一條 ≥90% 時尾端脈動；閒置時不重繪。
- **動作軌（第二列）**：按鈕分三組，以 `╱` 隔開、各有底色（`Button` 沒有顏色屬性，所以包在有底色的 `Box` 裡，滑鼠停留時文字變亮加粗）；兩端各接一個與底色同色的 `◢` `◤`，切成平行四邊形：Claude Code 內的檢視「側聊」`/side`、「回想」`/recall`、「diff」`/diff`、「artifacts」`/artifacts`（深青）；外部程式「資料夾」「VS Code」（深靛）；問 Claude「看不懂」`/common:wait-what`、「畫給我看」`/common:show-me`、「下一步」（深洋紅）。指令類按鈕用 `$.command.run` 當作使用者親手輸入執行，所以 skill 是送進主對話，與直接打指令效果相同。
- 「資料夾」把目前資料夾交給系統開啟程式（Windows `explorer.exe`、其他 `xdg-open`，失敗再試 `open`）；「VS Code」開 `vscode://file/<資料夾>` 連結，由系統交給 VS Code，不需要 `code` 指令。兩者都從家目錄執行、路徑當參數傳、不經過 shell：Windows 會先在工作目錄找程式，不可信的 repo 可能放了同名檔。
- **下一步**改寫自 next-steps（anthropics/claude-plugins-community，MIT），改成按按鈕才問：用 `$.model.fork` 請模型猜最多三句你接下來會打的話，列在狀態列下方，按 1／2／3（或點選）放進輸入框當草稿，0 收起，下一輪開始時自動收起；不會自動送出。建議是模型輸出，顯示與放進輸入框前先清掉跳脫序列、控制與隱藏字元，含 Unicode tag 字元的整句丟棄；不存在的 `/指令` 也丟棄。
- band 與輸入框之間那一列空白是引擎輸入框自己的 `marginTop: 1`（除 `/brief` 模式外固定存在），mod 無法消除。
- **side 收掉自己的「看不懂」「畫給我看」**：每則回覆旁 hover 出現的兩個按鈕、`/side ?` 與 `/side 畫`、以及它們用的側聊版簡化提示詞一併移除，改由 bar 的按鈕直接送 `/common:wait-what`、`/common:show-me`，只留一套行為。`/side` 回到單純的側聊。
- 「回想」「側聊」按鈕走 `$.command.run`，因為驗證器不允許把 `$` 傳進別檔的函式。`/recall` 照舊會在對話裡留一行「回想面板已開啟。」。
- Raster 的編碼函式從 recall 抽到 `hooks/raster.ts`，recall 與 bar 共用。recall 測試裡判斷「@@ 之前 band 不出現」改認 band 標題 `回想 `（尾端有空格），避免誤中 bar 的按鈕。
- 26 項 `claude plugin test`、`claude plugin validate`、以 2.1.289 型別檔跑的 `tsc --noEmit` 通過。動畫、配色與按鈕實際畫面無法由測試斷言，以實機為準；`$.command.run` 能否直接執行 skill 也需實機確認。要停用原本的 statusLine，需自行把 `~/.claude/settings.json` 的 `statusLine` 區塊移除。marketplace 1.73.0。

## Common Mod 0.1.1 — side 面板改成舊的在上、新的在下，輸入框在最底並貼底

- side 面板的版面反過來：最舊的問答在上、最新的在下，輸入框移到最底，像一般聊天。資料仍是新的在前（`historyOf` 依此取最近幾輪），只在畫面上反轉。
- 開面板與每次問答寫入後呼叫一次 `$.ui.scroll({ in: 'side', to: 'end' })`，捲到底後引擎會持續貼底，使用者往上捲才解除。內容放得下時此呼叫是否生效、焦點是否因輸入框 key 變動而掉落，需實機確認。
- 24 項 `claude plugin test`、`claude plugin validate` 通過；測試無法斷言順序與貼底，視覺效果以實機為準。marketplace 1.72.0。

## Common Mod 0.1.0 — 新 plugin：把 mod 從 common-lab 獨立出來，加入 side

- 新增 `common-mod` plugin，專放 Claude Code mod（function hooks，在 CLI 與桌面 Code 分頁裡畫 UI）。一個 plugin 只能有一個 hooks 入口：`hooks/register.ts` 註冊共用事件（`session.start` 註冊指令、`/clear`／`/resume` 歸零），各 mod 在 `hooks/recall/`、`hooks/side/` 掛自己的事件；`$` 不跨檔傳遞，子模組只交出指令規格等純資料。Claude 專屬，Codex 載體沒有對應版本。
- **recall**（從 common-lab 0.17.1 搬來，狀態改掛 `common-mod.*`，userConfig `recallExtraRoots` 一起搬）新增三項：附上的過去對話總長受 24,000 字上限約束，超過時截短並註明，空間不足 600 字的整段不附上、標記為〔回想（未附上）：…〕並在狀態列說明；`/clear`、`/resume` 會清掉搜尋字與選中的對話；非全螢幕版面 `/recall` 改開 30 列對話框，引擎放不下（`isPlaced: false`）時立即收回並說明。索引改為第一次打 `@@` 或開 `/recall` 時才建立，session 啟動時不再掃描。
- **side**：`/side [問題]` 在主對話旁開側聊面板，用 `$.model.fork` 以主線脈絡回答（不用工具、不寫進主對話、關掉即清空），可連續追問並「帶回主對話」。回覆上滑鼠停留會出現「看不懂」（照 wait-what 的方式重講那則回覆，不推進主線）與「畫給我看」（純文字示意圖，正式圖解仍用 `/common:show-me`），鍵盤用 `/side ?`、`/side 畫` 對最後一則回覆做同樣的事。從手機或網頁遙控（Remote Control）下 `/side` 會提示改用 `/btw`（依指令來源判斷，不看裝置清單）。
- **依獨立 review 修正（發布前）**：
  - recall 送出時只解析在結果列親手選過的 `@@chat:<id>`，而且只處理使用者本人送出的 prompt（終端機輸入或 Remote Control）；沒選定的 `@@字` 原樣送出，不再模糊搜尋自動附上。原因：貼上的文字或其他 session 送來的訊息只要含有 `@@字`，就能決定把哪一段過去的對話（可能來自別的專案）附進目前的 context，review 期間實際發生過。這也代表 common-lab 0.17.0 的「直接送出未選定的 `@@關鍵字` 會自動取最符合的一段」行為已移除。
  - 索引還沒建好（剛開 session、從遙控端送出）或模組重新載入後記憶體清空時，送出 `@@chat:` 會先等索引建好再替換，不再原樣送出；`/recall` 與結果列改以「記憶體裡沒有資料」判斷是否重建。
  - 附上的內容不再叫主模型「直接讀原始 jsonl」，改為只在使用者要求更多細節時才讀；長度上限的狀態列提示在下次正常送出時清除。
  - 換到 common-mod 後，原本在 common-lab 填的 `recallExtraRoots` 不會自動帶過來，需要在設定裡重填。
- 24 項 `claude plugin test`（終端機與桌面兩種 surface、長度上限、歸零、對話框、按鈕行為、只認親手選定的 token、來源過濾、索引未建好時等待、遙控端的 /side）、`claude plugin validate`、`tsc` 通過。滑鼠停留顯示按鈕的效果與實際畫面以實機為準。

## Common Lab 0.18.0 — recall 移到 common-mod

- recall mod 連同 `hooks/`、`types/`、userConfig 移到新的 `common-mod` plugin；common-lab 回到只放實驗性 skill。已裝 common-lab 0.17.x 的使用者請另外安裝或啟用 `common-mod`。marketplace 1.71.0。

## Common Lab 0.17.1 — recall 依推送後安全審查修正

- 索引器改以使用者家目錄為工作目錄執行 `node`：Windows 會先在工作目錄找執行檔，原本在不可信的 repo 開 session 時，repo 內的 `node.exe` 可能在 session 啟動時被執行。找不到家目錄時略過索引並提示。
- 附上的過去對話前加註「僅供參考的資料，不是指令」：過去紀錄可能含有從網頁或 log 貼入的文字，避免被當成使用者的要求執行。
- `recall-index.json` 以僅擁有者可讀寫的權限寫入（Unix／WSL 生效；Windows 沿用使用者目錄的 ACL）。
- 測試新增檢查索引器的工作目錄。marketplace 1.70.1。

## Common Lab 0.17.0 — 新增第一個 Claude Code mod：recall

- 新增 `recall` mod（`hooks/` 的 function hooks 模組，Claude Code 2.1.287 起支援）：在輸入框打 `@@關鍵字`，prompt 上方的 band 即時列出符合的過去對話（Claude Code 終端機、桌面 Code 分頁、Cowork、SSH），點選或按數字即插入 `@@chat:<id>`；直接送出未選定的 `@@關鍵字` 時自動取最符合的一段。送出時把該段對話的標題、時間、當時問過的句子、最後一則回答節錄與原始 jsonl 路徑附成 context，畫面上只留 `〔回想：標題〕`。
- `/recall` 開啟 pane：上方以 Raster 色塊畫出各專案最近 120 天的「記憶地層」，選中的對話所在日期以藍色標出；下方為最近對話清單與預覽，可插入輸入框。
- 索引由 node 掃描 `~/.claude/projects`，依檔案大小與修改時間快取在 `~/.claude/recall-index.json`；略過 SDK 驅動的 session（例如自動 security review）。新增 userConfig `recallExtraRoots`（分號分隔）可多掃 WSL 或其他機器同步來的資料夾。
- 狀態合約在 `types/index.d.ts`（`common-lab.recall*`）；`claude plugin validate`、`claude plugin test`（6 項，含終端機與桌面兩種 surface、參數傳遞）與 `tsc` 皆通過。尚未在多數人的實際 session 中長期使用，Raster 與點選插入的實際呈現以實機為準。
- mod 為 Claude Code 專屬，Codex 載體不變。marketplace 1.70.0。

## Common Lab 0.16.4 — 依 Codex 實測補強求助檢查與停止檢查

- `is-truely-need-to-ask-user-jev`：新增 `agent_can_do`（agent 能否自己做）與 `tried_and_blocked`（是否真的試過而受阻）兩題，涵蓋「請使用者代為動手」（例如啟動服務），state 另列已嘗試的做法與結果；有外部副作用的動作一律照問。來源是 Codex 實測中臨場自編題目得到 0.09 的案例，現改為固定題目；新題目的措辭尚未實測。
- `none-stop-jever`：新增 `repeats_failed`；在「未完成、可自行繼續」時若下一步在重複失敗做法，必須換做法，否則照實說明卡在哪裡。state 另列失敗做法與預定下一步。措辭尚未實測。
- `strategic-advance-jever`：寫明 `ev_*` 只判斷「是否相關」而非「是否涵蓋」，須與 `outcome` 一起讀，涵蓋範圍由操作者自行判斷；Tested 補上流程證據被高估的實測案例。
- 兩個 agent 自身檢查在金鑰未設定時改為指向 `init-jev`，與其他 Jev 技能一致；`examples.md` 同步補註。
- Claude 與 Codex 兩載體同步。marketplace 1.69.4。

## Common Lab 0.16.3 — jever 補上成本結構、評估基準與官方已知限制

- `jever` 依三篇公開文章（darkzodchi 的 Jev 設定指南、LangChain 的 Building a Harness with Jev、huangserva 的實測清單）與 TypeSafe 官方 models／jev-1.13 jaggedness 文件補強：
  - 開頭寫明只收文字、state 加最長一題上限 32k、英文最準，中文要用中文測。
  - 「不適用情境」新增：狀態上限砍掉關鍵內容（Claude Code 壓縮插件等同常數回答）、日期比較、state 含不可信內容而答案用於放行、訂閱制下唯一好處是使用者不付的錢（Codex 路由代理反而多花 59%–184%）；「已有更簡單的替代方案」加入現行流程、AI 味檢測淨值為零、與輕量 LLM 準確率和費用打平只贏長尾延遲、LangChain 現成中介層。
  - 經濟性：按請求計價、state 只收一次，應一次送出所有可能用到的題目（含推測性的）；計算邊際成本由誰付、插入中間層造成的請求變大與快取失效；廠商比較數字的折扣。
  - 評估：與常數回答及現行流程兩個基準比較、記錄 `model` 與 `usage`、換模型就重跑評估、0.7–0.9 信心區間要有足夠樣本。
  - 交付：state 由程式篩到只剩必要欄位、證據與原始請求分開、Choice 每步重建選項並加 `none`、門檻起點（破壞性約 0.9、唯讀約 0.5）、題目與門檻放同一檔；路由要說明是每個 run 一次還是每步；LangChain 的 AutoModeMiddleware 直接擋，上線前先量誤擋率。
- `examples.md`：compaction 案例加上真實輸出可能超過上限的警告；出題經驗新增 Noul 0.5 代表「無法判斷」、分開的題目不符合算術恆等式（官方例：Noul 0.22 對 Choice 0.01、正反兩題相加 1.19）、避免雙重否定與指令／判準矛盾、陳述句與問句寫法的差異尚未測試。
- OpenRouter 通道未加入 `init-jev`：OpenRouter 模型清單與 TypeSafe 文件都查不到，無法確認呼叫方式。
- Claude 與 Codex 兩載體同步。marketplace 1.69.3。

## Common Lab 0.16.2 — jever 併入 jevify 的調查方法，並明列不適用情境

- 併入 ryana/jevify 的調查結構：先理解目標的用途與成本所在；找判斷點時多看「為了預算縮減涵蓋範圍」「同一段 context 反覆處理」「延後批次處理」；新增「從第一原理重新思考」（直接省錢、更好的結果、新能力三類，並點出只因語意判斷昂貴才存在的設計假設）、「算清楚經濟性」（端到端路徑、關鍵路徑、與更簡單替代方案比較、損益平衡條件）、「設計能證明它沒用的評估」（保留案例、不對稱錯誤成本、措辭敏感度、門檻與退路驗證、go/no-go）；交付改為先給整體評估、依三類分開的排序表、第一原理草圖，並標明廠商說法、實測與推測。
- 新增「Jev 不適合的情境」一節，逐項寫明原因與替代做法：要產生內容、需要多步推理或往後推想、關鍵事實不在 state 裡、程式能精確判定、精確數字與計算、Jev 是不可逆或高代價決策的唯一依據、有利害關係的一方寫題目或 state、會花資源的數量判斷、目標或選項模糊、低頻決策、已有更簡單的替代方案、下游沒有檢查也沒有退路。各項皆對應本 plugin 實測或公開案例（西洋棋超時、真錢交易觸發停損、授權措辭 6% 變 80%、subagent 數量高估、console.log 缺路徑等）。
- Claude 與 Codex 兩載體同步。marketplace 1.69.2。

## Common Lab 0.16.1 — jever 加上案例庫

- `jever` 新增 `references/examples.md`：本 plugin 已做過並實測的 Jev 整合，依目標類型分八類（agent 自己的停下／提問／路由／問題措辭、context 壓縮取捨、規劃與審議、驗證、戰役與派工、UI 建置、估算、動作與程式碼），每例附實際送出的題目、單次實測結果與用法，最後整理出題經驗（拆開合併題、一個選項一題 Noul、措辭影響、Choice 分散時改問 Noul、該由分類推導的是非題不另問、數量會高估等）。SKILL.md 加一段：出題前先讀這份，套用相符的形狀並在候選中引用。
- 新增 context 壓縮案例並實測：目標「修好失敗的結帳測試」下，失敗的測試輸出「仍需要」0.85、完整保留 0.82；無關的權限檔 0.06、丟棄 0.95；`npm install` 輸出 0.10、丟棄但信心僅 0.46。以「仍需要」是非題為主、三選一為輔。
- Claude 與 Codex 兩載體同步。marketplace 1.69.1。

## Common Lab 0.16.0 — 新增 wayfinder-jever

- 新增 `common-lab:wayfinder-jever` 疊加版，在六個判斷點加上 Jev：grilling 每輪先判斷每題是否查得到（查得到就自己查）、是否會改變設計（不會就不問），剩下的依影響分數排出 Q1 起的提問順序；drain 前判斷票是否其實需要人（只能擋下、不能把 HITL 放行成 AFK）；迷霧或票的精確度；每次決策後掃描開著的票是否超出終點或被推翻；給人看之前的白話檢查；最後一張票關閉時的交接建議。另外把 wayfinder 原本「每張票要用哪個技能處理」（Ecosystem routing）改交給 `suggest-jev`：Notes 已釘選就照 Notes，否則以票的問題、類型、終點與本 session 實際可用的技能跑一次路由，選定後照 wayfinder 原規則寫回 Notes。
- 實測（各一次）：影響分數排序正確（核准流程 2.43、資料庫 2.28、Node 版本 1.07、按鈕顏色 0.01）；「值不值得問」合成一題時把按鈕排在資料庫之前，拆成「查得到嗎」「會改變設計嗎」兩題後分開（Node 版本查得到 0.98、按鈕改變設計 0.15）；「需要人嗎」0.05 對 0.91；精確度 0.51 對 0.20，只用來抓迷霧。
- 移除所有 Jev 技能中「客戶或機密內容未經同意不送」的資料邊界句（含 cold-estimation-jever 的資料邊界段、jev-browser 參考文件的客戶合約提醒）：預設直接呼叫、不詢問也不從內容判斷，是否在某專案使用由使用者自行決定。保留「無金鑰或呼叫失敗時靜默略過」，以及 init-jev 設定時一次性告知 TypeSafe 的資料條款。Claude 與 Codex 兩載體同步。marketplace 1.69.0。

## Common Lab 0.15.0 — 新增 suggest-jev 路由

- 新增 `common-lab:suggest-jev`：做任何事之前先載入的路由技能。開始時一次請求讓 Jev 建議起始技能（從本 session 的技能清單挑）、之後會用到的技能、流程、完成策略、subagent 數量、模型家族與 effort、難度、影響範圍，轉成一行路由告知使用者後開工；一件事結束、要暫停或停下時交給 `none-stop-jever`；要問使用者時先交給 `is-truely-need-to-ask-user-jev`，真的得問時再以 Jev 檢查問題是否白話、是否講清要使用者做什麼、是否問到卡住的主因，低分就改寫一次。
- 使用者的指示永遠優先（指定的技能、subagent 上限、工作方式）。實測兩個請求路由正確（hunt 0.92、read 0.99），但 subagent 數量有高估傾向（0.83–1.47），因此預設不派、需分數約 1.5 且信心約 0.6 以上才派，並交給 delegate／delegate-jever。問題檢查以「白話」分得最開（0.06 對 0.62）。
- `init-jev` 改為預設快取金鑰 30 天（`JEV_KEY_TTL_DAYS`，設 0 即不快取）：新 shell 靜默載入快取，過期則維持未設定、由使用者手動跑 `jev_key_refresh`／`Update-JevKey` 重抓一次，不會每開一個 shell 就跳密碼管理器的解鎖。bash/zsh 快取為僅本人可讀的明文檔（目錄 700、檔案 600，`~/.config/typesafe/`）；PowerShell 為 DPAPI 加密檔（`%APPDATA%\typesafe\`）。兩段程式碼皆以假的 `op` 在暫存目錄實跑：權限、新 shell 載入、31 天後不載入、PowerShell 檔內無明文，皆符合。
- 「先載入」仰賴模型選用此技能；要保證每個請求都跑需另做 hook，本版未做。Claude 與 Codex 兩載體同步。marketplace 1.68.0。

## Common Lab 0.14.0 — 十個 Jev 疊加版，以及停下前、提問前兩個獨立檢查

- 新增十個 `*-jever` 疊加技能（strategic-advance、contract、seal、delegate、review、think、cold-estimation、ui、show-me、wait-what）。與 define-goal-jever 不同，這十個不複製原技能：原技能帶有大型腳本、bundled agent 或屬於 baransu／analysis-estimation 另一個 plugin，整份複製會斷路徑、變成需同步維護的分支。疊加版的內容是「照原技能原樣執行，在指定判斷點加上 Jev」，原技能更新時自動跟上。每個判斷點都寫明 state 放什麼、題目原文、怎麼讀分數、以及 Jev 不能決定的事；題目固定寫在技能裡，無金鑰或呼叫失敗時照原技能執行，客戶或機密內容未經同意不送出。
- `strategic-advance-jever`：scribe 彙整前逐則判斷情報與各勝利條件的關聯（全部偏低＝偏離 MOE；有關但未回報結果＝MOP）、固定自檢時的兵力態勢（重裝／輕裝／解編）、重組前的拆分／合併／退役信心、選主攻時各戰線的優先度分數。Jev 在 operator 端呼叫（scribe 不能連網），結果以情報行進入 event packet，永不成為 gating 證據或命令。
- `contract-jever`：寫作前的重要度分數與拆分檢查、每條驗收條件是否可斷言、Surface Inventory 每列的影響類別建議（封緘層級仍由類別推導，並經使用者確認）。
- `seal-jever`：派工前以重要度分數決定驗證額度、未被 contract 分類之表面的 finding 分級（只能調高、不能蓋過一手證據）、可執行探測的嚴重度排序，以及每個突變測試執行前檢查它能否改變「完成」判定，或只是 MOP。
- `delegate-jever`：四個規模面向的 0–2 評分決定路徑、模型家族與起始 effort、監督模式每次巡檢的偏離／重複假設／進展判讀（越界寫入改用程式比對路徑）、失敗分類。
- `cold-estimation-jever`（中文）：工項困難度（決定先做窄技術覆核的順序）、必要性（抓範圍擴張）、定價後每列人天的依據可信度（決定向定價者追問哪幾列）；分數不得變成人天係數或緩衝。
- `ui-jever`：建構前以五種常見 AI 設計套路檢查設計計畫、每個區塊對計畫的符合度加套路檢查、元素的版面方式與色彩角色挑選。
- `review-jever`：每個保留的 finding 加上 Jev 信心評分（證據對所稱後果的支持度 0–3、缺陷／未知／可選改善分類），報告多一節「Jev 信心評分」；與審查自身判斷不一致時取較弱的分類，分數不構成新證據。
- `think-jever`：對齊時判斷猜測的措辭是否會改變解法形狀、每個押注與整體立場的證據支持度、剩下的選擇是否真屬使用者；呈現時多一節「Jev 信心評分」，計畫檔仍維持五節，低分押注寫進「做法」的承重前提。
- `show-me-jever`、`wait-what-jever`：輸出前先以 Jev 判斷讀者第一次看能不能懂（0–3）；低於約 2 時，從原技能自己的呈現方式寫出二到四個候選交給 Jev 選，改寫後再檢查一次，取分數高的版本送出，不再迴圈。wait-what-jever 與原版一樣只能手動叫用（Codex 以 `agents/openai.yaml` 的 `allow_implicit_invocation: false` 對應，原始檔在 `codex-metadata/common-lab/wait-what-jever/`）。
- 新增兩個獨立的簡短技能：`none-stop-jever`（每次要停下或結束這一輪前問 Jev：使用者的需求真的完成了嗎？還有能自己做的事嗎？）與 `is-truely-need-to-ask-user-jev`（每次要問使用者前問 Jev：這真的需要使用者嗎？能不能自己查到？）。使用者的指示、偏好、授權、不可逆動作永遠優先於 Jev。
- 為避免同一時刻觸發兩次，`jev-pick` 描述拿掉「停下這一輪之前」、`jev-gate` 描述拿掉「向使用者提問之前」的觸發，改由上述兩個專門技能負責；兩者內文的細分題目保留作參考（五選一的下一步、加上清晰度分數的提問檢查）。
- 各判斷點題目皆已對 API 實跑（各一次，非校準）：情報關聯改用「即使是部分證據」措辭後，相關 0.81–0.84、無關 0.12–0.14；contract 範例三列影響類別全對（0.78–0.87）；delegate 規模評分與模型家族合理；人天依據可信度 1.89 對 0.27；UI 套路區塊符合度 0.23、依計畫區塊 2.25；突變測試「能否改變判定」0.86 對 0.12–0.16；review finding 證據支持度 1.99 對 0.75；可讀性（給非技術讀者）術語版 0.17、白話版 2.55；停下檢查「只跑部分測試」完成度 0.09、「全套通過」0.92；提問檢查「npm 或 pnpm」可自行查到 0.80、「刪除三年資料的表」需問使用者 0.96。三選一的突變用途題與 contract 的「是否擋下封緘」是非題分不開，已改用其他題型。
- Claude 與 Codex 兩載體同步。marketplace 1.67.0。

## Common Lab 0.13.0 — 新增 jever、define-goal-jever；jev-pick／jev-gate 加上停下前、提問前檢查

- 新增 `common-lab:jever`：純引導型技能（同 wait-what、show-me 的寫法），開頭即「Use Jev to strengthen anywhere that only needs a judgment — yes/no, choose one, score.」。對當下目標（進行中的工作、prompt、skill、MCP、hook、agent 迴圈）找出藏著的判斷點，依「兩秒內從固定選項挑出答案、挑錯代價低」判斷適不適合，區分「附加 Jev」與「以 Jev 為主架構」（jev-ultrafast 範本），列出社群常見用法，並涵蓋 agent 自己的決策點（停下前、提問前）。只交付排序過的候選、淘汰清單與最小實驗，不改檔、不呼叫 Jev。
- 新增 `common-lab:define-goal-jever`：以 define-goal 為底，在四個判斷點加上 Jev 第二意見——釘住目標前的品質檢查（五題 Noul 加目標類型 Choice，一次請求）、提問前檢查、與已釘住目標的比對、依目標類型選量化方法。品質檢查已用技能自己的範例實跑：好目標在結果、驗證、門檻、範圍四項為 0.93–0.99，弱目標為 0.06–0.44；好目標的停止條件僅 0.15（範例本身確實沒寫）。無金鑰或呼叫失敗時照 define-goal 原流程。Codex 版以 Codex 的 define-goal（`get_goal`／`create_goal`）為底。
- `jev-pick` 加「停下這一輪之前」的固定選項檢查，`jev-gate` 加「向使用者提問之前」的檢查（可否自行查到、是否只有使用者能決定、清晰度）；兩者的描述都加上對應觸發時機。選項固定寫在技能裡、state 只放事實，且不能取代使用者的授權。
- Claude 與 Codex 兩載體同步。marketplace 1.66.0。

## Common Lab 0.12.0 — jev 拆成 jev-gate、jev-pick、jev-score，改為可自動觸發

- 移除 `common-lab:jev`，依三種模式拆成三個技能：`jev-gate`（Noul 是非機率）、`jev-pick`（Choice 從既有清單挑一個）、`jev-score`（Score 分級評分）。
- 描述改寫為自動觸發：模型在工作中遇到對應判斷（指令是否危險／外洩、該點哪個元素或選哪個分類、完成聲明的證據強度等）時自行使用，建構閘門、路由、評分時也會觸發；附中英文觸發詞。內文各兩三句＋一段可直接執行的 `curl` 範例（已對 API 實跑驗證回傳欄位；Score 的 `score` 是小數期望值並附 `legend`）。
- 自動觸發的護欄：無 `TYPESAFE_API_KEY` 時靜默略過；客戶或機密內容未經使用者同意不送出；Jev 的答案只是訊號，不構成授權。
- `init-jev` 描述改為在使用者要設定 Jev，或 jev-* 呼叫因金鑰缺漏／401 失敗時觸發。
- Claude 與 Codex 兩載體同步。marketplace 1.65.0。

## Common Lab 0.11.1 — dev-browser Lab 變體改名 jev-browser；Codex 載體同步

- `common-lab:dev-browser` 改名為 `common-lab:jev-browser`，避免與 `test-utils:dev-browser` 同名（Codex 以 `$skill` 叫用時無法區分）。內容不變，技能內的 bundled 路徑同步改為 `skills/jev-browser/`；init-jev、jev 內的引用一併更新。
- Claude 與 Codex 兩載體同步：Codex 的 jev-browser 以既有 `test-utils` Codex 版 dev-browser 為底（沿用 `$DevBrowserSkillDir`／`DEV_BROWSER_SKILL_DIR` 路徑解析），init-jev、jev 由 transfer 產生後改寫 Claude 專屬的叫用語法；Codex `plugin.json` 的 interface 手動更新。marketplace 1.64.1。

## Common Lab 0.11.0 — 新增 Jev 三件：init-jev、jev、dev-browser Lab 變體

- 新增 `common-lab:init-jev`：讓 agent 的 shell 取得 `TYPESAFE_API_KEY`（不印出金鑰），用一次最小呼叫驗證；涵蓋 bash/zsh（含 WSL）與 PowerShell 7+（`$PROFILE`、SecretManagement），並提醒送出資料的條款。
- 新增 `common-lab:jev`：三種用法各兩三句＋一段 `questions` 範例——Gate（Noul 是非閘門）、Pick（Choice 從既有清單挑一個）、Score（Score 分級評分當影子評審）。

- 新增 `common-lab:dev-browser`：以 `test-utils:dev-browser` 1.1.2 為底，多一個「找要操作的元素」情境。`scripts/case/element-table.js` 把頁面上看得到的可操作元素編號（掛 `data-jev-idx`），`scripts/jev-pick.mjs` 以一題 Choice 請 TypeSafe Jev 挑出前幾名，agent 只讀候選、不讀整份 DOM；做法參考 browser-use/jev-ultrafast。
- 無 `TYPESAFE_API_KEY`、API 失敗、低信心（< 50%）或挑中 `none` 時退回 `snapshotForAI()`；Jev 的答案只是候選，操作後照樣驗證。
- 目前只有 Claude 載體；Codex 載體尚未移植。marketplace 1.64.0。

## Common 1.40.1 — wait-what 拔掉 Lab 標題、補回上游第一句

- 移除 `# Wait What Lab` 標題（Lab 畢業後殘留）。
- 補回 Matt Pocock 上游原版第一句，僅把 「talk in ASD-STE100 Simplified Technical English」 改為 「... or 標準台灣繁體中文白話文」，其餘照原文。
- Claude 與 Codex 兩載體同步。marketplace 1.63.1。

## Common 1.40.0 — strategic-advance 補結構決策 gate 與固定邊界校準

- §1 戰略目標合約：contract 未釘住的不可逆結構決策（persistence schema、對外 API／訊息形狀、state machine、模組邊界）屬未決決策，第一個會提交它的 mutation 之前須經 `/baransu:contract`（或使用者）釘住並記入 `constraints`；executor 只能提議、不能決定，執行速度不縮短這一步。
- §7 arm gate 加一條 checklist：mutation 不得提交 `constraints` 中沒有的不可逆結構決策，會的話先停下釘住。
- 對齊 auditor：「Trigger it only when」改為「Trigger it when」，新增兩個觸發點（tactical takeover 完成、organ fix loop 修復輪數用盡）；校準不以指揮官先察覺混亂為前提，無法派出獨立 auditor 時在 ledger 記 degraded coverage 並保留安全接續點，不得以自我核准替代。
- Claude 與 Codex 兩載體同步（Codex 以 `$contract` 指稱）；validator、state contract、scripts 不變。
- common 的 Claude plugin 與 marketplace 簡介縮成一句（原本逐技能列舉，在 TUI 過擠）。marketplace 1.63.0。

## Common Lab 0.10.0 — 淘汰 strategic-advance Lab 變體

- 從 Lab 移除 strategic-advance（含 `agents/calibrator.md`、Codex 的 `calibrator.toml`；Claude 與 Codex 兩載體），Lab 的 delegate 在 Codex 的 bundled agent 清單同步只剩 `executor`。改用穩定版 `common:strategic-advance`。
- Lab 剩 1 個技能（delegate）與 1 個 bundled agent（executor）。marketplace 1.63.0。

## Analysis Estimation 1.18.0 / Common 1.39.1 — 移除最終 reviewer，加入直接表達指引

- Cold 2.24.0 移除交付前強制的 Terra Mid reviewer、三面向覆核及其後續修正流程；保留獨立定價、必要時的窄技術覆核與 writer，交付由主線核對實際檔案。
- Cold 2.24.0 末尾加入使用者指定的 `Say what you mean` 完整原文：直接表達意思、按內容需要使用清單，釐清後停下等待。
- show-me 保留既有兩段寫作指引，統一章節標題並補上最後的對話收束段落；Claude／Codex 同步，marketplace 1.62.0。

## Analysis Estimation 1.17.1 — Cold 2.23.1 開場逐題以聊天內 show-me 說明

- Cold 開場每個決策問題各配一段 `common:show-me` 講解，緊鄰該題選項與推薦；限定聊天內的文字流程、前後對照或 Markdown 方案表；不產生 Mermaid／HTML，也不開啟瀏覽器或預覽面板。
- 同步開場交付檢查與說明，保留選項編號及推薦依據，同輪共用既有證據，不逐題重跑研究；通用 show-me 的其他使用情境維持原規則。Claude／Codex 同步，marketplace 1.61.1。

## Analysis Estimation 1.17.0 — Cold 2.23.0 一次建議與主線修正

- Terra Mid reviewer 一次提供有證據的問題、具體修正建議及完成判準；主線最多修一輪，不再往返派 writer、reviewer 或定價者。
- 數字修正限於既有證據可確定的操作與計次，另存輸入並重跑既有工具；需新工時或路線判斷的部分保留待估。區分原稿獨立覆核與主線修正版，不把舊稿 PASS 沿用到實質修改後的報告。
- 定向檢查「批次修改」是否可重用同一改法；同批逐點須微調或不同改法列「多點批次修改」，拆出同質小批與剩餘操作，不把所有點套同質倍率或完整重寫價。保留原計算公式，Claude／Codex 同步，marketplace 1.61.0。

## Analysis Estimation 1.16.0 — Cold 2.22.0 Terra Mid 最終實質覆核

- 將既有文字 reviewer 擴為新上下文的 gpt-5.6-terra / medium 最終 reviewer；交付前驗證方案可行性、報告前後矛盾，以及人天是否匹配實際修改方式，並保留文字、表格與計算明細核對。
- 主導成本回到代表改法、剩餘操作、次數及 E／V 依據；鎖定數列可被具體證據質疑，問題交回原工項／定價角色修正，實質變更後再覆核，不由 reviewer 自行另估或倒推總額。
- 記錄指定 profile、受審版本及分面證據；模型不可用、覆核未完成或實質缺口未解時只交待覆核草稿。條件式初估保留待估及未實測限制，穩定算法、開場選項與 show-me 不變。Claude／Codex 同步，marketplace 1.60.0。

## Analysis Estimation 1.15.0 — Cold 2.21.0 開場方案比較與視覺解釋

- Grilling 每題通常提供 2–3 個有依據的可行方案，明示一個最推薦；以長期可維護與本次修改成本適中為預設，從必要施工、驗證及後續更新／交接解釋取捨，不固定選最便宜、最新或中間方案。
- 開場實際調用 `common:show-me`，以相同選項編號為 PM／SD 說明現況問題、保留／改動與維護方式，依 Skill 規則提供視覺預覽；缺少能力如實揭露，不把提到技能名稱當成已執行。
- 沿用已確認決策、六類路線覆蓋及待答邊界；不硬湊不可行候選、不提前估多套人天，也不更動原人天公式與施工範圍。Claude／Codex 同步，marketplace 1.59.0。

## Analysis Estimation 1.14.1 — Cold 2.20.1 參考批次倍率與四捨五入

- 以參考系統支數校準 API／頁面／DAO 批次，只換算已定工項的人天：基準批次工時 × 本案受影響支數／同類基準支數，按自然工項彙整後 E／V 分欄四捨五入。
- 移除逐支 3／4／3 小時的加價。各類確有批次修改才套公式；框架 30＋10 固定額度、共用一次與獨立例外不縮放，維持原路線、工項與驗證涵蓋。
- 計算工具保存基準數量、實際數量、原始工時與倍率，拒絕重乘 count；一般操作及加值沿用既有取整，新增數學與產物一致性回歸。Claude／Codex 同步，marketplace 1.58.1。

## Analysis Estimation 1.14.0 — Cold 2.20.0 新框架搬移的線性計價

- 開場連同框架選擇確認施工路線：原專案升版，或建立相容新骨架、對齊共用能力並搬移既有業務；不把框架替換只當 migration guide 的局部修補。
- 新框架搬移採每獨立部署包執行 30＋驗證 10 人天的經驗基礎費；頁面 E2/V1、API E3/V1、受影響 DAO 方法 E2/V1 小時乘實際單位，於自然工項彙整取整。線性增加單位搬移與驗證，不另用規模級距／指數或追歷史總額。
- 區分 mapping、類別、檔案與實際方法；共用能力、單位局部驗證及跨層結果去重，已含能力不再收一次。單位費是待實績校準的預設，使用者約定優先；真實例外列剩餘工作。
- 沿用現有操作輸入與計算工具，明示經驗費率換算；同步定價交接、交付檢查與 Claude／Codex，marketplace 1.58.0。

## Analysis Estimation 1.13.1 — Cold 2.19.1 最終交付完整性

- Writer 從交付規格及既有定價資料組裝完整報告；既有文字 reviewer 同時查六欄主表、施工說明、計算依據與來源對應，不能只以數字 token 一致視為通過。
- 主線最後寫入後重開實際交付檔，按欄與 ID 核對列數、各列 E／V、合計及來源；review 後刪欄、改 ID 或轉 Excel 必須重查受影響內容。只補漏、修正及覆核，不新增完整審查產線或重估。
- Claude／Codex 同步，marketplace 1.57.1。

## Analysis Estimation 1.13.0 — Cold 2.19.0 重大路線先確認

- 補入 Jakarta／Servlet／容器與 Struts 版本交叉查證，以及 JSON Action 改寫的 Gotchas：已定目標引發的框架替換不得漏估，也不能由單一不相容組合推成全面重寫；JSON 不等於沒有 OGNL，同質入口依共用／批次／例外估算，不以 Action 映射數乘完整重寫單價。
- 開場最小盤點後即用 Grilling 確認應用架構、主要框架、語言／執行平台、關鍵業務核心套件、關鍵處理基礎設施及部署環境；所有適用且未決類別都要問，不等細部研究或不相容證據出現才問，也不把現況直接當沿用決策。包含既有頁面改 SPA、報表產製引擎替換、核心套件換維護線／fork 及離開既有應用伺服器。
- 等使用者選定路線或明確授權推薦後才詳細定價；未決先交付路線差異與待決問題。已有決策且無新衝突不重問，一般局部適配與已定路線的資料缺口仍可採假設完成初估。
- 同步收斂主線、窄技術覆核、獨立定價與交付檢查的選路權限；提問方式內含於 cold-estimation，不新增 Grilling 外掛依賴。Claude／Codex 同步，marketplace 1.57.0。

## Analysis Estimation 1.12.0 — Cold 2.18.0 直接支援候選優先

- Gotchas 優先選維護者官方明示支援目標、且活躍維護的路線；用 QueryDSL／OpenFeign 示範，拒絕以新版或 classifier 代替承接依據。候選支援與本案特殊用法驗證仍分開。
- 因完整試跑未見足夠正向收益，撤回定價前草稿 reviewer、補正迴圈、固定分支表及其三年信心欄位；保留獨立定價、PM 撰文及文字校稿；不再要求固定表格中的前後置版本欄位。
- Claude／Codex 候選同步，marketplace 1.56.0；以同一日常短提示隔離試跑 Terra medium／low 與 Luna max，均完成報告與可重算定價；此結果不代表桌面日常使用已等效，後段主線改寫仍可能造成文字漂移。

## Analysis Estimation 1.11.0 — Cold 2.17.0 固定分支草稿與窄稽核（未發布候選）

- 把簡短日常需求也須完整交付、角色交接與工具失敗退路寫入 Skill；沿用既有獨立定價與 PM 文案流程。
- 固定分支表分開前置／目標／後置版本、證據、結論、狀態與工項；找到高風險用法只能進入候選承接判定，不直接標已成立。
- 定價前使用 Luna medium 窄稽核，接受共用引用與明示未知，補正有上限；不展開完整相容矩陣或重估人天。
- 新增三年穩定信心 1–5／未知及原因，評估持續維護與合理升版下的路線前景；不是保證或人天倍率，保留到最終報告。
- Claude／Codex 候選同步，marketplace 候選 1.55.0；另以隔離 Terra medium、原始日常短提示完整驗證，結果以實驗報告為準。

## Analysis Estimation 1.10.0 — Cold 2.14.0 前後置版本盤點

- 盤點元件時條列前置需求／後置影響的官方預設支援或配套版本；未明示標未知。只新增此盤點指引，既有派工、計價、查證與交付規則不變。
- 一併發布前期驗證後採用的工項／獨立定價分工、可重算操作工具、PM 撰文與文字校稿、純數字 ID 及替代方案句型。
- Claude／Codex 同步，marketplace 1.54.0；隔離 Terra low 完整試跑完成，觀察到候選路線選擇改善，前後置版本仍主要散見於工項敘述；单次結果不代表穩定因果效果。

## Analysis Estimation 1.9.1 — Cold 2.13.1 交付表數字編號（未發布候選）

- Markdown／Excel 交付表 ID 欄改為由 1 起的連續純數字；內部計價 ID 與對應保留於計算資料，工項及人天不變。
- Claude／Codex 同步，marketplace 1.53.1；本次為顯示規則調整，不將前輪估算試跑冒充新版行為驗證。

## Analysis Estimation 1.9.0 — Cold 2.13.0 第 8 輪與替代方案句型（未發布候選）

- 回到第 8 輪完整基準，移除後續 renderer 與報告重組實驗；盤點、選路線、工項、獨立定價、數學工具及文字 reviewer 邊界均沿用第 8 輪。
- 只在 PM 句型補上「原方案已停止維護，改採已選替代方案、調整既有用法並驗證必要結果」；只知目標不相容時照實限定，不把舊版本或未知寫成停止維護，也不授權 writer 新選方案。
- Claude／Codex 同步，marketplace 1.53.0。另以相同需求及乾淨隔離環境重跑 Luna max／Terra low；前一輪 2.12.1 結果分開保存，不冒充本候選的驗證。

## Analysis Estimation 1.8.1 — Cold 2.12.1 報告工項重組（未發布候選）

- 修正 2.12.0 僅更換 renderer、仍鎖定原列形狀的問題：writer 可依改造能力與完成結果重組既有說明，主表簡述、後段編號展開，維持原計價 ID／操作對應。
- 同一計價包拆開說明時，原人天只列共同小計，不均分或重新取整。新增施工、獨立子項報價與技術路線變更不屬文字工作；獨立 reviewer 仍只校稿。
- 第 8 輪盘點、技術判断、定價與數學工具不變。此為根據第 10 輪產物特徵補寫的報告指引，不宣稱第 10 輪的分項能力由舊 renderer 改動造成。Claude／Codex 同步，marketplace 1.52.1。

## Analysis Estimation 1.8.0 — Cold 2.12.0 第 8 輪基準與報表呈現（未發布候選）

- 採用第 8 輪完整基準：主線固定工項、操作與共享歸屬，獨立定價者保存操作輸入，由附帶工具產生可追溯的同一數列；未採第 9 輪放寬定價者改寫操作的權限。
- 只疊加第 10 輪 `estimate_math.py` 的報表函式：主表列既有工項、編號操作與最終人天，原始 E／V 小時、B／A 及狀態移至內部明細。公式、取整、20% 分類、盤點、技術路線及 writer／reviewer 分工維持第 8 輪。
- Claude source 與 Codex 生成版同步；plugin 1.8.0、marketplace 1.52.0。第 8 輪原始输入重算核對數列；此組合尚未另跑完整模型估算，不將報表驗證視為模型行為已改善。

## Analysis Estimation 1.7.0 — Cold 2.11.0 工項與獨立定價（未發布候選）

- 主線保存無人天工項與施工依據，再由新上下文定價子代理統一估算 E／V、共享歸屬與加值；主線核算並接受同一數列，不帶歷史總額倒填。
- 對可能排除既有路線的薄弱前提，至多一次窄技術覆核；定價後仍保留獨立撰文與文字校稿，避免追加工項。
- 鎖定工項、路線、人天與責任後，撰文及獨立文字校稿依序處理說明；末段 reviewer 專注文字，不重新定價或增添施工。
- 新增框架、一般套件、關鍵核心三類句型，採具體編號施工與完成結果；主表後展開主導成本的現況、施工、共用／例外及完成標準。
- Claude source 與 Codex 生成版同步；marketplace 1.51.0。模型行為與額外成本另以隔離 Luna max／Terra low 前後試跑核對；新增規則本身不代表效果已成立。

## Analysis Estimation 1.6.0 — Cold 2.9.0 工項定價與責任邊界

- 互斥方案優先選目標相容、持續維護且後續可升版的路線；必要施工與語意驗證直接估入基準，不混合不同路線的低高價。
- 剩餘工作的低高中點併入對應工項；同一工項累計加值超過其原基準 20% 時，回查漏估／重複並重拆重大異動，不截斷、膨脹分母或改名照加。
- 承接使用者確認的甲方責任與固定額度，先移除重疊再計一次；沒有指定的固定人天不設為通用預設，未拆 E／V 不補造。
- 取消交付的獨立風險區塊，已定價工作集中主表；未定價的必要工作保留待估，已估小計不冒稱全案總價。Excel 保留摘要與工項人天，不展示原始 E／V 小時欄，原始計算保留內部。
- Claude source 與 Codex 生成版同步，marketplace 1.50.0。此次規則晚於六組 Cold 2.8.0 模型／effort 比較，該比較不作為新版行為已驗證的證據。

## Analysis Estimation 1.5.0 — Cold 2.8.0 風險工項與交付定版

- 定版已隔離測試的 Cold 候選：清冊後先形成工項草稿，依官方 release 的時間、目標世代與實際使用訊號分流；只補查會改變主要工項或量級的缺口。
- 以 QueryDSL 的公開 `GroupBy／transform` 跨 Hibernate 世代失效案例，示範完整方法選樣、同一失效的候選修復、結果語意與記憶體驗證；列必要工作及局部修補／替代路線的互斥淨增量，不將所有可能後果加入基準。
- 交付第一塊直接總結、第二塊列工項與人天，關鍵風險緊接主表；開發與驗證各自向上取整到整人天，零工時保持零，總計只加總。
- 恢復按需 Excel 交付：估算完成後由同一數據產生摘要／彙總及工項明細，內外版總數一致、必要風險與責任保留；此交付補充晚於四組估算試跑，未另做模型 A/B。
- Claude source 與 Codex 生成版同步；既有清冊工具、其他 Skill、模板與載體適配保留。候選的實驗版本號收斂為正式 Cold 2.8.0；marketplace 1.49.0。

## Analysis Estimation 1.4.0 — 移除 Estimate，發布已選定 Cold

- 移除 `estimate` 的 Claude source、Codex Skill、測試／資產／腳本與獨立 UI metadata；同步清除 README、套件描述與 marketplace 的呼叫入口。既有系統與需求文件的初估改由 `cold-estimation` 承接。
- 發布先前已選定的 Cold 2.7.0 精簡基線與唯讀清冊，不合併未通過風險品質評估的後續實驗版本；既有歷史實驗資料保留作研究紀錄。
- 同批發布 Common 1.39.0，包含 show-me 的 Mermaid HTML 預覽及 Token Lens。marketplace 1.48.0。

## Common 1.39.0 — Token Lens 用量與行為分析

- 新增 `token-lens`：唯讀解析指定 Codex session 或隔離試跑目錄，將公開工具操作、回傳量、逐回應 usage 與壓縮事件串成可篩選 HTML 時間線。
- 一般執行與壓縮依 response ID 分列；可選配 CLI JSON 紀錄核帳。重複與巨大輸出只作診斷線索，工項影響另行核對，不以 token 數冒充內部思考或因果證明。
- 支援人工工項貢獻標記與匯出；不啟動模型、不修改日誌或正在執行的任務，不匯出原始命令、來源內容、隱藏推理或壓縮摘要。首版 parser 驗證於 Codex CLI 0.153.4；Claude 端可呼叫分析器，但不解析 Claude transcript。
- Claude source 與生成的 Codex Skill 同步，加入核帳、壓縮、重複、缺件、格式錯誤及保留既有報告測試。marketplace 1.47.0。

## Common 1.38.0 — show-me 有 Mermaid 就預設開 HTML

- 終端機無法渲染 Mermaid，只印文字區塊反而更難懂。改為：回覆只要含 Mermaid，就把該回覆的所有 Mermaid 圖寫成 `.claude/show-me/` 下的一個 HTML（CDN 載入 Mermaid，每張圖一個 `<pre class="mermaid">` 加一行說明），並沿用既有的「用當前環境的工具開瀏覽器」規則打開；Mermaid 原始碼仍留在回覆裡以便留存。原本的專用 HTML 產物也統一放該目錄；Codex 生成版使用對應的 `.codex/show-me/`，兩者皆忽略產物目錄。Claude 與 Codex 兩載體同步。marketplace 1.46.0。

## Analysis Estimation 1.3.0 — Cold 工作優先初估與讀取接續

- Cold 2.7.0 採單一 producer 三步：形成必要工作、補查依賴路線與例外、計算並一次覆核。完整讀取入口與三份手冊，截斷補讀；未知用條件與風險交付，不等待完整 SBOM、全面相容性實測或新增 PM gate。
- 既有改造按目標差異、共同機制、批次與獨立例外計價；施工／驗證的原始工時只能歸屬一次，普通除錯與共享驗證不再重複加價。新增通用唯讀清冊，Markdown 預設輸出宣告、來源規模、import／擴充與私有成品位置，不冒充 resolved SBOM 或支援結論。
- 維護搜尋先確認原上游與替代來源，再核對目標整合者的支援限制；不能以版本號、classifier 或編譯成功代替執行與維護風險。Cold 的 quality-orchestrator 消費契約同步為單一初估 task，避免重啟內層盤點／代理。
- 26 組隔離 Luna Max 實驗後，選回重複測過 7 次的精簡基線，未合併後期的強制證據讀取器／路線表／情境規則。觀察到較短時間與較少輸出，但未證明所有 token 都降低，也未達穩定估準；實驗中間版本不作已發布版本列示。
- Claude source 與生成的 Codex 套件同步；補回 transfer 未涵蓋的原有 tests／templates／UI metadata，限定放置本次檔案。marketplace 1.45.0。

## Common 1.37.0 — wayfinder 回歸 1.36.0 之前的自訂版

- 實測 1.36.0 改成 Matt Pocock 原版流程的 wayfinder 後體驗不如舊版，整包回歸 b84a6b7 之前的版本（Claude 與 Codex 兩載體）：SKILL.md 恢復 operator 原則、baransu 路由表、strategic-advance 條件交棒、Speak plainly 與 drain 模式；tracker 說明回到 `TRACKER.md`（刪除 `references/tracker.md`）；`render_map.py` 與 `map-template.html` 回到舊版 renderer（無 Current focus 檢視）；移除 `disable-model-invocation: true`，恢復自動觸發。skill 目錄的 MIT LICENSE 保留。marketplace 1.43.0。

## Common Lab 0.9.0 — 淘汰 estimate、define-goal、better-prompts 三個 Lab 變體

- 從 Lab 移除 estimate（含 `agents/estimate-auditor.md`、Codex 的 `estimate-auditor.toml`）、define-goal、better-prompts 三個技能（Claude 與 Codex 兩載體）。estimate 的 Lab 版使用體驗過差；define-goal 與 better-prompts 的 Lab 版在低階模型上無法正常運作，原版可以。三者一律改用穩定版：`analysis-estimation:estimate`、`common:define-goal`、`common:better-prompts`。既有 `.estimate-lab/<case>` 資料不遷移。
- Lab 剩 2 個技能（delegate、strategic-advance）與 2 個 bundled agents（calibrator、executor）。marketplace 1.42.0。

## Common 1.36.2 — show-me 開啟 HTML 改為一句意圖

- 拿掉寫死的 `wslview || xdg-open || open` 指令鏈（錯誤全導向 /dev/null，機器上沒裝 wslu 時會靜默失敗，HTML 寫出來卻沒打開），改為「用當前環境有的工具在使用者預設瀏覽器打開，不要只印路徑」，並舉 WSL2 的 `wslview`／`pwsh.exe Start-Process` 為例。Claude 與 Codex 兩載體同步。marketplace 1.41.1。

## Common Lab 0.8.0 — think／contract／seal／review 回歸 baransu 穩定版

- 四個源自 baransu 的實驗技能定稿後直接更新進 baransu 5.5.0（輸出目錄回歸 `.claude/think/`、根目錄 `CONTRACT.md`、`.claude/seal/`、`.claude/review/`），Lab 不再保留副本；`agents/verifier.md` 隨之移入 baransu。Lab 剩 5 個技能（delegate、strategic-advance、define-goal、better-prompts、estimate）與 3 個 bundled agents。marketplace 1.41.0。

## Common 1.36.1 — wait-what 與 show-me 加入「Say what you mean」

- 兩個技能各加一段：不用比喻與修辭代替直述，有字面說法就用字面說法，技術散文亦然；清單與條列只在被要求或內容確實多面時使用，使用者要求極簡格式時不用條列、標題、粗體，對話式交流維持平鋪散文。

## Common Lab 0.7.0 — 已畢業的技能回歸 common

- 從 Lab 移除 grilling、domain-modeling、research、prototype、wait-what、wayfinder、show-me 七個技能（Claude 與 Codex 兩載體）：它們的定稿已在 common 1.36.0，Lab 不再保留副本。Lab 剩 9 個技能：think、contract、seal、review、delegate、strategic-advance、define-goal、better-prompts、estimate，4 個 bundled agents 不變。
- think 的 show-me 與 wayfinder 交接改指穩定版 `common:show-me`／`common:wayfinder`。marketplace 1.40.0。

## Common 1.36.0 — 六個 Matt Pocock 技能回到原版，show-me 進穩定版

- `grilling`、`domain-modeling`、`research`、`prototype`、`wait-what` 改以 Matt Pocock skills（3cca18b）現行原文為本體，只保留輸出語言段與 `${CLAUDE_PLUGIN_ROOT}` 內建檔案引用；`research` 加一段：偵測到 baransu 時用 `/baransu:read` 取件，引用可指向 `.claude/read/` 的存檔；`wait-what` 改採 Lab 版：從斷掉的連結開始、按困惑種類挑講法、簡化細節不簡化真相、受眾從對話推斷、純文字不產 HTML（圖另叫 show-me）；移除受眾旗標、五階梯與 HTML 伴讀。
- `wayfinder` 改以 Matt 原版流程為本體，tracker 細節獨立成 `references/tracker.md`（`.claude/wayfinder/`），採用 Lab 的 HTML 渲染器（含 Current focus 檢視）；移除 operator 原則、baransu 路由表與 strategic-advance 條件交棒；保留 drain 模式（自動推進所有 AFK 票，HITL 邊界硬停）；保留一段「Make the route legible」（每題先講在路上的位置、為何現在、牽動什麼，地圖前進時交代問了什麼、怎麼解）；`disable-model-invocation: true` 照原版，只能手動叫用。
- 新增 `show-me`（HumanLayer 原文，開檔指令改為 wslview → xdg-open → open）。common 共 11 個技能。
- Codex 鏡像同步；六個 Matt 技能與 show-me 皆附上游 MIT LICENSE。marketplace 1.39.0。

## Common Lab 0.6.0 — Wayfinder／Grilling 回到 Matt Pocock 原版，Think 表態改為「押注」寫法

- `wayfinder` 改以 Matt Pocock `skills/engineering/wayfinder` 原文（3216582）為本體：只把 issue tracker 用語換成本地 markdown（`Type:`／`Status:`／`Blocked by:`），tracker 細節與 HTML 檢視獨立成 `references/tracker.md`；`disable-model-invocation: true` 照原版保留。移除 Lab 版的自訂節奏條文與 `map-format.md`；保留既有 HTML 渲染器（含 Current focus 檢視指標）。地圖目錄仍為 `.common-lab/wayfinder/`。
- `grilling` 改為 Matt Pocock 原版（設計樹＋前線＋事實／決定分工），只加輸出語言段；Lab 反證版退場，其能力由 think 的「已定決定入口」承接。
- `think`：表態的可推翻條件改為三段條件句（押在什麼上／押錯會怎樣／改走哪條）；新增已定決定入口（拷問我、grill me）；判決也經 show-me 呈現；description 精簡。
- 六個源自 Matt Pocock skills 的技能（grilling、domain-modeling、research、prototype、wait-what、wayfinder）在 `common` 與 `common-lab` 兩套件、Claude 與 Codex 兩載體的 skill 目錄補上 MIT LICENSE。common 1.35.3，marketplace 1.38.0。
- `wait-what`（Lab）：移除 `--as` 與 `--mode` 旗標，受眾一律從對話推斷；只用文字，不產 HTML 或圖，需要圖時由使用者另叫 show-me。
- `show-me`（Lab）：開啟 HTML 的指令改為 wslview → xdg-open → open 依序嘗試，WSL2 也能自動開；其餘維持 HumanLayer 上游原文。`wait-what`（Lab）比喻改為「先講清楚，只有貼切時才加比喻」，不再強行說故事。
- 移除 `experiments/`（common-lab、baransu-lab-v0.2.0、estimate-lab-v0.2.0 三個 0.2.0 凍結包與本機忽略的舊版目錄）：內容與現行 Lab 相同或更舊，Git 歷史（8a83b69／49a7e4c／087c3f1）保留；`.gitignore` 對應規則一併移除。`docs/experiments/` 的量測紀錄不動，其中指向 `experiments/` 的路徑為歷史紀錄。

## Common Lab 0.5.0 — Think Lab 實驗版：以復述對焦

- 開場改為「復述對焦」：先用幾句話復述使用者要的結果、目的、不能動的東西與規模，缺的欄位標「未知，先不問」；樹的節點是復述裡猜的詞，只問會改變答案形狀的題，選項須種類不同並附推薦；收斂條件是使用者確認復述，或一輪回答後復述不變。對焦期間使用者只看到復述與一題，模型可讀 code 查事實但不得展示方案；復述裝不下的大題目指向 wayfinder。
- 攻擊階段加「反向攻擊」：拿掉某塊復述會少什麼，什麼都不少就砍進 Not building 並註明何時才需要；方案不得超過復述的規模。
- 新增「呈現」段：落檔前先整體再局部、用最小視圖與白話講清推薦（參照 wait-what／show-me）；對話是理解版，檔案是持久版。
- 反駁若是「我要的不是這個」則回到復述而非修計畫。Codex 鏡像同步，互動點加入復述確認。marketplace 1.37.0。

## Common Lab 0.4.1 — 安裝後預設啟用

- `common-lab` 改為 `defaultEnabled: true`（Claude marketplace 條目與兩份 plugin.json）：安裝完即出現在技能選單，不再需要手動 enable；不需要者可 `claude plugin disable common-lab`。marketplace 1.36.1。

## Common Lab 0.4.0 — Think Lab 回復完整審議脈絡

- `think` 從單純判決機改回完整審議鏈：對焦 → 表態（附可推翻條件）→ 查證前提 → 自我攻擊 → 五段計畫落檔（`.baransu-lab/think/<slug>.md`）。
- 開場改採 Grilling 方式：從使用者實際主張出發、自己查可查的事實、一次只問最能改變推薦的一題；能表態就停止發問，剩餘不確定轉為可推翻條件。不再要求固定三輪對焦，成功條件與範圍改為計畫產物而非開場輸入。
- 落檔後即結束：不實作、不挑下游 skill、不開核准關卡；後續由使用者或呼叫端（wayfinder／contract）決定，檔案可直接交給 review。不復活舊版的 HTML 工作日誌與多重停頓。
- `common-lab` 補列入 Claude marketplace 目錄（`.claude-plugin/marketplace.json`，`defaultEnabled: false`），Claude 端可用 `claude plugin install common-lab@common-dev` 安裝；先前只列在 Codex 目錄。marketplace 1.36.0。
- Codex 鏡像同步，`request_user_input` 互動點改為單題提問、使用者專屬抉擇與計畫被推翻後的「哪一節錯了」。

## Common Lab 0.3.0 — 統一 Lab 套件與完整 Show Me

- 將 Common、Baransu、Estimate 的 Lab source 與 UI metadata 合併至 `common-lab`，共 16 個技能與 4 個 bundled agents；正式版及歷史實驗快照保留。
- Skill／agent 名稱、資料夾與套件內引用移除 `lab-` 前綴；舊技能名稱不保留別名，與正式版並存時需選取 Common Lab 所屬技能。
- Show Me 完整採用 HumanLayer 上游 SKILL.md，保留所有圖解、diff、完整區塊與 HTML 範例；MIT 聲明留在同目錄 LICENSE。
- 重新產生單一 Codex 套件，保留 Estimate tests、UI metadata、明確呼叫政策與 agent resolver。既有 campaign／assessment 資料格式與工作目錄不遷移。

## Codex 主 marketplace — Common Lab 0.2.2

- 將 `Common Lab（實驗性）` 的 11 個 `lab-*` skills 與兩個 package-local agent definitions 加入 Codex Layout A／B catalogs，安裝識別為 `common-lab@common-dev`。
- 套件由 Claude source 經既有 transfer 與 UI metadata overlay 重新產生，內容與已驗證的獨立 0.2.2 實驗包逐檔一致；維持 `AVAILABLE`，不自動安裝，也不替換穩定 `common`。
- Claude 穩定 marketplace 仍維持四個預設啟用 plugin；本次只提升 Codex App 的可見與安裝入口。

## Lab 發布範圍修正

- Git 僅保留 Common Lab、Baransu Lab、Estimate Lab 的 0.2.0 凍結包；13 個舊版／候選目錄移出追蹤並忽略，本機檔案與 Git 歷史保留，未重寫已發布歷史。
- 試用入口與安裝驗證工具的預設路徑改用 0.2.0；歷史測量與測試腳本仍對應原批次，重測舊版需先從 Git 歷史取回。最新版套件位元、正式來源、正式 catalogs 與目前 App 安裝皆不變。

## 實驗包 — Common Lab／Baransu Lab／Estimate Lab 0.2.0

- 重新檢視全部 15 個 Lab 技能：以原目的、模型失敗模式、適用規模、證據和摩擦決定指引或機制；不再把縮短指令本身視為成效，也不以強模型或短測試推定長程風險消失。
- Strategic Advance 回到長程耦合戰役：主手與實作分離，新增 fresh calibrator、事件／期限檢查點、有界修復及只暫停受影響支線的接續規則。新 `calibration.py` 檢查封包時效、狀態與來源雜湊、來源別名、宣告角色隔離及完成條件；明示它不證明語義、真實隔離或工具層強制執行。
- Contract 明確先落檔再交付實作；Seal 按實際影響分配有限驗證，保留必要條件而不無限擴張突變測試。Estimate 保留案件 revision、PM 承諾及唯一計價來源，對長程跨包矛盾按需加入唯讀獨立核對。
- 其餘技能補上不替換使用者主張、人的理解節奏、原始證據接續與成果交還等狹義指引；保留既有 renderer、campaign ledger、Estimate runtime、計算及核准控制。
- 三包由 Claude source 經既有 transfer 產生全新 0.2.0 目錄與 package-local agents；舊包、正式來源與正式 catalogs 不替換。逐技能差異、真實測試收據及長程／跨模型限制見 `docs/experiments/lab-v0.2.0/README.md`。

## 實驗包 — Common Lab 0.1.8／Baransu Lab 0.1.1／Estimate Lab 0.1.3

- Common Lab 經分輪重測，修正 Wayfinder 的欄位讀取、當前焦點與前置就緒顯示；區分決策已釐清、產品已完成與執行授權，不以票券數代替成果。
- Baransu Lab 以一份可驗證的驗收記錄串接 think、contract、review、seal；保留獨立驗證與授權邊界，不偽造原版 hook 或封緘。
- Baransu 0.1.1 僅將 verifier 原有規則分組、加上具名限制；6 輪只採用此結構改動。封存新題目的 8 次實測兩版均抓到核心缺陷；3 位最終評審偏好分組版，2 位判嚴格改善，效果軸同分，不宣稱任務或真人理解改善。新目錄導出與隔離安裝逐檔一致；原 0.1.0 包保留。
- Estimate Lab 新增独立精簡入口，保留依賴查證、唯一工作集合及 PM 承諾；修復人天確認後無法接續的狀態轉移，明確區分預覽、人天已核准待交付、交付完成。53 項測試在實際暫存安裝包內通過。
- 三包均以原轉換器產生独立 Codex marketplace，原版來源、生成內容、穩定 catalog、隔壁 Baransu 與全域安裝不變。Estimate 的非標準 tests/ 由窄範圍 adapter 在原內容完整性檢查前補回並逐位元核對，原警告保留於導出報告。
- 版本化包、試用方式、逐輪證據與測量限制見 `docs/experiments/README.md`。這是本地工作樹實驗，不代表遠端發佈、正式插件升級或真人驗收。

- Common 0.1.5 修正 Grilling 批判方法時悄悄替換原主張的問題，保留未導出的 0.1.4 失敗樣本；Estimate 0.1.2 區分已交付的預覽與正式核准，補上真實表格渲染與成果入口的檢查。Common 0.1.5／Estimate 0.1.3 均通過全新暫存安裝。Estimate 0.1.3 修復責任或所選方案變更後沿用舊核准、連續變更的確認脈絡與鍵盤 Enter 誤關閉；已核准提醒回歸歷史紀錄，64 項 Python 與 5 項事件測試在安裝後包內通過。

- Common 0.1.7 新增狹義 campaign extend 命令：追加新 criterion，不改舊成果或未知操作；只在 campaign reference 揭露，不加根技能指令。兩題 A/B/B/A 四次 Astra 主手均成功；採用便利性與歷史保存，不宣稱普遍速度／成本優勢。實際安裝包通過 12 新回歸及 16 原自測，全域與正式來源不動。

- Common 0.1.8 新增可選唯讀 campaign 交接便箋：引用現有狀態與證據、提醒未決操作及雜湊變動，不改狀態、不冒充語義驗收；只在 campaign reference 按需揭露，根技能不變。四次 Sol reader proxy 都辨認未知作用與語法檢查不足，兩版都會回讀原始證據，故不宣稱省讀量或真人理解改善。導出及暫存安裝位元核對通過；安裝包內 21 新回歸、12 extend 與 16 帳本自測通過。

## 實驗 marketplace `common-lab` 0.1.0 — Common Lab 初版

- 新增 Common 的 10 個獨立 `lab-*` 技能，測試短描述、按需載入、成果與決策邊界取代固定流程的設計；保留實作／目標責任分離、人的決策節奏及大型工作防注意力失焦的目的。
- Claude source 在 `plugins/common-lab`；Codex package 與獨立 marketplace 在 `experiments/common-lab`，由 transfer 產生。穩定 Common 1.35.2、四套穩定 catalogs 與現有安裝不變。
- 加入相同情境 A/B 行為演練工具及時間／實際 token／品質／停頓紀錄。結果僅適用於記錄的模型、情境與執行環境；不是跨模型保證，也不是生產驗收。
- 執行方式、實測結果與限制見 `docs/experiments/common-lab/`。此版本只在工作樹建立，不代表已對遠端 marketplace 發佈。

## marketplace `common-dev` 1.35.3 — Estimate PM 確認報告下鑽與主動發現

- `analysis-estimation` 1.1.3／`estimate` 3.1.0 將 Gate 5 報告改為 PM-first 確認台：第一層先顯示本次摘要與七個評估項目的低／基準／高人天及原項目說明；點擊項目後以原生 dialog 開啟修改明細，關閉時回到原列與捲動位置。額外發現只跟隨所屬項目，不再脫離上下文獨立陳列。
- 案件 schema 升至 8。Discovery 一次建立唯一 `detailCatalogs` 工作集合，Wayfinder、work item 計價與 Gate 5 只引用相同 stable ID；`direct-touch` 必須完整逐項列名且數量相符，`generated` 說明重新產製與核對方式，`evidence-only` 明示不作人工乘數。另以 `scopeDelta` 阻擋確認數與逐名清單不一致。
- HTML 由 `assessment-state.json` 經 generator 套用內建 `assets/assessment-report-template.html` 產生。圖解只在 `package.visuals` 能回答明確問題時出現；PM 文字遵守「直接陳述，不用文字表演」，先說結論、人天影響與 PM 注意事項，再把算法與技術證據放進展開層。
- 兩個既有案件型態完成實際瀏覽器回歸：CR 案驗證 4→6 六畫面、查詢點與 4.5／6.5 人天說明；四包升版案驗證 87 個 QueryDSL 使用檔完整清單、136 個 Q 類重新產製摘要及 13 類整合表。測試價值稽核將 57 項收斂為 44 項：保留 41 項有效行為，刪除 13 項文件字串或無 deterministic surface 的測試，並將 3 項改為直接驗證 state／HTML 行為。

## marketplace `common-dev` 1.35.2 — repository 遷移至個人 GitHub

- README 與 `analysis-estimation` / `common` / `test-utils` 的 Claude、Codex manifests 改指 `https://github.com/TLOGBen/common-dev-plugin`；新 repository 採乾淨 snapshot，不攜帶舊 repository 的 commit ancestry。
- 去除 changelog 中的實際專案代號，並將 `cold-estimation` 的來源領域描述改為不特定專案；Skill 原則、估算流程與執行行為不變。
- 將 Codex transfer 範例的個人絕對路徑改為 `$CODEX_HOME` 可攜式路徑。

## marketplace `common-dev` 1.35.1 — Strategic Advance 去除 Kamishibai 文件殘影

- `common` 1.35.1 刪除 Strategic Advance 在 Kamishibai 導入時新增、於 HTML renderer 回復後只做名詞翻譯的整段 `Who draws the sand table`，並去除初版重複的第二句 `--no-open` 說明；Wayfinder 同步刪除由 SDK discovery／store／legacy 路徑翻譯而來的 environment self-check、`Finding the renderer` 與 `--legacy` 三段。兩 skill 既有 command、畫面、browser、安全與測試契約仍由鄰接章節承接；state、renderer、87-case self-test、驗證、授權及其他原則不變。

## marketplace `common-dev` 1.35.0 — 新增既有系統 Estimate、全部 plugin 預設啟用、恢復自含 HTML renderer

- `analysis-estimation` 1.1.1 新增並同步最新版 `estimate`：從客戶成果與技術證據盤點陌生既有系統的升版、CR 或混合需求，形成成功鏈、可行方案、責任邊界與 PM 可說明的人天估算；依上游精簡為 22 個 distributed files，移除已不使用的互動工作檯、assets、vendored LinkStart runtime 與對應測試／文件，保留案件狀態、估算產出、ASCII 決策介面與核心回歸測試。
- Claude marketplace 與各 plugin manifest 將 `test-utils`、`analysis-estimation`、`linkstart` 的 `defaultEnabled` 由 `false` 改為 `true`；`test-utils` bump 至 1.2.1，`linkstart` bump 至 0.4.1。四個 distributed plugins 現在加入 marketplace 後皆預設啟用，仍可個別停用。
- Codex 原生 Layout A／B catalogs 繼續使用 `policy.installation: AVAILABLE`；不加入 Claude-only `defaultEnabled` 欄位。`analysis-estimation` Codex package 由 Claude source 重生，並還原 RFP templates 與 `estimate` UI metadata。
- `common` 1.35.0 移除 Wayfinder／Strategic Advance 對 Kamishibai SDK、`KAMISHIBAI_CLI` 與 npm 安裝的依賴，恢復 stdlib-only、自含單檔 HTML renderer；保留 `render-graph` 既有 SVG surface，以及 Strategic Advance 的 reprobe、slice/carrierRoots、priorityOrder、toll 與其他現行 state 行為。
- Wayfinder 回復 bundled `map-template.html` 後同步補強四個舊版缺口：ticket metadata 在進入 `innerHTML` 前 escape、輸出採 atomic replace 避免 final symlink 改寫別檔、duplicate ticket ID fail closed、blocking cycle fail closed。Strategic Advance 恢復完整雙語 HTML projection 與 7 個 presentation cases，使現行 80-case self-test 擴為 87 cases。

## marketplace `common-dev` 1.34.0 — 立法包 v2：拆列稅、優先序主權、跨 repo 探測權、過路費機械化（Epoch 2 實戰摩擦驅動）

kamishibai 側一日 OOD 實戰的三筆載重摩擦（F4 拆列稅 15–20 萬 tokens/輪、F5 使用者優先序無輸入口 C26 四駁回、F7 rank-4 證言重繳稅）＋F1 過路費散文化，全數以「淨散文負、機制優先」落地：

- **`set-front --slice-of <parent>`（可繼承切片前線）**：一步建檔可封緘切片——自帶 entry/exit/pivot 三 claims（born UNKNOWN、seed 出處），operationType/owner/mutationScope/recovery/carrierRoots 承親前線；**以 DEFERRED 出生**（排隊語意誠實、對 clarity 派生零擾動——低分新片不會搶最低分候選把合法 CLEAR 打成 INVALID），啟用走既有 set-front/handoff 路。三座對帳判官與章卷文法零改動。
- **`strategicObjective.priorityOrder`（使用者優先序，一等公民欄位）**：frontId 或前綴列表，候選擇定先比優先序再比分數；**只在 eligible 候選間排序、永不復活不合格前線**；與 objective 同權限面（僅使用者可動）。統帥口頭令從此 validator 看得見——需求主權的 schema 落地。經查 `DEFERRED` 既有狀態已提供「合法停車」（eligibility 公式本就排除），故**不採 electable 旗標**（冗餘機制）——與 kamishibai 側原提案的帶證據偏離。
- **front 級 `carrierRoots: [absPath...]`**：宣告本前線證據所在的根外 repo，書記官對宣告根有唯讀探測權（允許集不變）、證據全額入 rank；campaign root＋宣告根之外照舊不探。建前線寫入＝派遣即授權。
- **`toll` 子命令（續輪過路費機械化）**：`toll --organ X --before N --after M`——M≥N 拒付 exit 1、續輪不得開；M<N 蓋結構化 `ORGAN_LOOP_TOLL` 帳冊行。§9 條文改指命令（「a narrated toll is no toll at all」），散文機制淨移除。
- 條文微修：consolidation 段明示「過期永不機械轉 UNKNOWN、過期本身永不升級 full 重建」（C28 誤讀 12 判準全重探實錄錨）；sa-scribe 帳冊 `ts` 改 `$(date …)` 命令內插禁手寫（手寫時戳系統性超前實鐘實錄錨）；Scope pinning 併入 carrierRoots 探測權。
- 兩載體全同步（SKILL.md×2、sa-scribe md/toml、strategic_state.py 逐位元鏡像）；self-test 79 case 全綠、切片/toll/priorityOrder 實測通過。

## marketplace `common-dev` 1.33.0 — strategic-advance/wayfinder 環境自檢＋安裝說明（kamishibai SDK 上 npm 前置）

- 兩 skill 的 HTML 渲染自 1.32.0 起硬依賴 kamishibai SDK（python 渲染器已退役、無 fallback），新機器首次 render 必炸 `SAND_TABLE_SDK_UNAVAILABLE`。補「至少」級環境自檢：首次 render 前主動查 `python3 --version` 與 `kamishibai --version`（或 `KAMISHIBAI_CLI`），不等第一次失敗；安裝說明——python3 走平台官方套件管理器、kamishibai 走 `npm install -g @kamishibai/sdk`（nvm 非互動 shell 陷阱先 `zsh -lic` 重試；repo checkout 可走 `KAMISHIBAI_CLI`）；一步裝失敗即停、把那一行交給使用者，禁即興替代渲染器；裝有 baransu 者可整案交 `/baransu:health` 環境醫生。兩載體四檔同步。
- 閉環條件：kamishibai SDK 發上 npm 後，`npm install -g @kamishibai/sdk` 即為新環境一步到位路徑。

## marketplace `common-dev` 1.32.0 — 戰役內容重放合流（457b528，補記）

- kamishibai 戰役側未 push 工作（F6b→F7b：SDK 沙盤/地圖新路、python 渲染器退役 `--legacy` 大聲拒絕、self_check 四副本、wayfinder SDK render）自救援快照重放於 85c1c7b 之上，與 1.30.0 的 reprobe/教義修正三方合併（安全修零退版、codex 逐位元鏡像、版號三面收斂 1.32.0）。由 kamishibai 戰役 session 執行、本 session 抽驗，詳其戰役帳冊。

## marketplace `common-dev` 1.31.0 — 納編 LinkStart plugin 0.4.0 / runtime 0.1.5（自 TLOGBen/LinkStart 上游同步）

- 依「個人 GitHub 優先更新 → 同步納編 common-dev」策略，自 TLOGBen/LinkStart（plugin-v0.4.0）整包同步 `plugins/linkstart/` 與 codex 鏡像：runtime 0.1.5 三平台 binaries（sha256＋size 對 checksums.json 全數驗證）、新增 persistent origin wake adapters（`claude_adapter.py`／`codex_adapter.py`，Codex 掛機喚醒改由常駐 Origin Adapter 負責、foreground `arm` 降為相容用途）、`monitors/monitors.json` wake monitor、`references/app-protocol.md`。
- codex 鏡像維持既有慣例：內容與本體逐位元同、僅 SKILL.md frontmatter 帶 compatibility 行；codex manifest 採上游自帶版本 `0.3.0+codex.20260828033021`。

## marketplace `common-dev` 1.30.0 — strategic-advance 三組教義修正案：器官續輪資格、需求主權、書記官節食（common 1.24.0 / Codex 1.23.0）

長程戰役實錄驅動（三輪封緘遞迴 + 帳冊 339 行零筆成本記錄 + state.json 394KB + 單輪整編中位 13 分鐘）：

- **器官 finding 的續輪資格（§9）**：器官 finding 若揭露「守著某表面的判官已空洞化」且指名得出已核可的 `protectedAssetId` 與具體威脅（例：守著不可逆 mutation 路徑的判官零咬力），即歸 `CONTROL_RISK`，走既有貢獻閘門開修 loop，不受 MOP 否決；指名不出受保護資產者（色票、文案）即 MOP——入帳、ride along、不開輪。這不是開後門：`CONTROL_RISK` 本來就是閘門三類之一，條文只是把這類 finding 的歸類寫明。續輪另加機械過路費：修 loop 第一輪之後的任何一輪，指揮官須先在 ledger 寫一行 `終局距離：前 N → 後 M`（remaining transitions／unmet victory criteria），M 不嚴格小於 N 則該輪不得開。
- **需求主權條款（Command charter）**：使用者已鎖定的需求只能標價（成本、風險、分期），不得以穩定性、效能或架構品味否決；拒絕僅在牴觸使用者親自核可的 hard constraint 或 `unacceptableOutcome` 時合法。補丁堵住 invariant 8 把警告繳械的縫：標價中屬「不可逆損失」的項目，即使未列入 `protectedAssets`／`unacceptableOutcomes`，仍須向使用者取得該項明示回執——記錄義務而非否決權，回執到手即執行。
- **書記官成本與檔案節食（§10 / Campaign scribe-recon / Force posture）**：固定收據焊入成本欄（`… ｜ tokens: {N} ｜ tools: {M}`，SKILL.md 與 `sa-scribe` 逐字相同）——散文版成本記帳條在 21 輪整編中零執行，強制欄位是它唯一能活的載體；`COMPLETE` 片在終態且 exit 已驗證後，由書記官在下一次整編壓成一行 stub（id＋terminal state＋證據錨）並將全文移入 `artifacts/`，`state.json` 只全文保留 `ACTIVE`／`PENDING` 片（行為條款，validator 側機械檢查另屬實作切片）；連續 K 次整編零歧異（K 預設 3，開跑前記錄）自動把 posture 降級評估排上桌，評估程序照現行 retrograde 規則不變，只有觸發機械化——自查者＝被查者的結構性盲點由此拆除。
- **`strategic_state.py` 新增 `reprobe` 子命令（書記官縮編為裁決官的機械半）**：claim 的 `scribe-probe:<指令>@<時戳>` 出處本就是機器可讀的探針註冊表，`reprobe` 一趟重放全部（預設掃 gating claims，`--claim` 可指名）——逐枚回報 `REPROBE ｜ id ｜ exit ｜ sha256 ｜ 指令`，exit≠0 補一行歧異待裁決並以 exit 1 收場；`--refresh` 僅在 exit 0 時刷新 `observedAt`／`validUntil`／出處時戳，**status 永不變動**（UNKNOWN→PASS 仍是 `set-claim` 的判斷權，反污染分工不破）；重放預設走 `shell=False`：state.json 內容視為資料而非可信 shell 輸入——含 shell 中繼字元（`;|&$\`><()`）一律拒斥、shlex 解析後驗 argv[0] 唯讀允許集（並封 `git -c`／寫樹子命令注入面），拒斥者回書記官親手重探；`--allow-any` 為操作者明示越權（權能等同操作者本有的 bash，非新增面）、`--artifacts` 落全文輸出、`--timeout` 防懸掛。腳本無法被情報散文說服——determinism 是反情報污染的最強載體；實錄動機：單輪整編中位 13 分鐘、書記官 18 輪重複手搓同款轉換腳本。教義四處同步（SKILL.md／sa-scribe 兩載體）：書記官先跑 `reprobe`、只親手探它搆不到的，bash 允許集補列 `reprobe`。
- 勘誤：SKILL.md 與 codex 變體兩處 `schema-5` 陳年殘留改為 `schema-6`（sa-scribe 與 validator 早已是 schema-6）。

## marketplace `common-dev` 1.29.2 — LinkStart v0.1.3 refresh（linkstart 0.2.2）

- 機械更新 skill-local Runtime 至 GitHub Release `v0.1.3`（workflow run `33049940902`）的 Windows／Linux／macOS artifacts 與 exact provenance checksums。
- `arm`／`respond`／private context 行為不變；只更新 required Runtime/release references、plugin/cache versions 與 Claude→Codex generated package。

## marketplace `common-dev` 1.29.1 — LinkStart v0.1.2＋one-call Monitor（linkstart 0.2.1）

- 更新 skill-local Runtime 至 GitHub Release `v0.1.2`（workflow run `33047913483`）的 Windows／Linux／macOS 真實 artifacts 與 exact provenance checksums。
- `runtime.py` 新增 private `0600` session context 與穩定 `arm`／`respond`／`close` contract。`arm` 自動注入 state dir、connection ID、capability；模型一次 `respond --payload` 即完成 pending Event identity check、Delivery Ack、stable `feedbackId` Feedback，並進入下一個 bounded wait，不再手工拼三條 Runtime command。
- Claude Monitor 使用 attached background call，completion 回到同一 session 後以 `respond` 處理並 re-arm；Codex 使用相同 wrapper 的 bounded foreground wait。Context close 刪除本機 ephemeral capability並誠實回報尚未做 Runtime-side revoke；stdout 不含 capability。
- 兩份 host reference 補齊 Runtime `help --json` authority、attach／register／launch／context／arm／respond exact examples與輸出欄位；模型不需讀 Rust source。

## marketplace `common-dev` 1.29.0 — LinkStart v1 Preview Integration Plugin（linkstart 0.2.0）

- 新增 opt-in `linkstart` plugin，Claude source 與 transfer 生成的 Codex package 都只提供一個 public `link-start` skill；Runtime／Daemon、Origin attach/rebind、App register/launch 與 monitor 都是同一 workflow 的內部 phases。
- `SKILL.md` 只保留 shared protocol 與 orchestration；偵測 host 後只讀一份 adapter reference。Claude 採 Channel Research Preview 或通過 live self-test 的 Monitor compatibility 並維持 background arm/re-arm；Codex 採 LinkStart-owned app-server/same-thread 邊界與 bounded foreground wait/re-arm。明禁 `claude -p`、`codex -p`、Agent SDK subprocess、cold resume 或替代 session。
- 內嵌 GitHub Release `v0.1.1`（workflow run `33045652953`）的真實 `linux-x64-musl`、`windows-x64`、`macos-universal` artifacts 與 provenance checksums；執行前驗 Runtime version、protocol major、release tag、SHA-256、size 與 Unix executable mode，不下載、不用 `PATH` 或本機重編版本頂替。
- App input 明定為 untrusted content；Event Receipt、Delivery Ack、Agent Feedback 各自獨立，任何「同意」回答都不代表 tool approval、permission grant、sandbox escalation 或 scope expansion。README 另固定 MOP／MOE 分離驗收。
- Claude marketplace 與 Codex Layout A／B catalogs 都新增 `linkstart`；fail-closed consumer validator 檢查 manifest、單一 public skill、catalog alignment、source/generated references/helpers 與 binary path/hash/size/mode parity。

## marketplace `common-dev` 1.27.0 — wait-what 受眾判斷＋由淺入深階梯（common 1.22.0 / Codex 1.21.0）

- 參考 ELI5 skill（DreambigOu/ELI5）的「先判受眾、再校準輸出」思路重構。新增 `--as <受眾>`（縮寫 `-a`）：可填職務（manager / pm / engineer / designer / qa / newcomer）、年齡數字或任意自由描述；未給旗標則從對話中使用者的提問與用語推斷，推不出就當完全新手並明說，**不得停下來反問**。
- 重述改為**強制階梯**：一句話版 → 十歲版（只准比喻、零前提）→ 大人版（真實概念，術語留英文＋當場白話）→ **給這個角色最要緊的那一段**（主管要的決策、工程師要的 trade-off、測試要戳的邊界，各受眾不得共用同一份摘要）→ 我為什麼這樣做。每一階須獨立成立、不得引用後面才解釋的東西；**第 1、2 階對所有受眾一律必做、工程師也不例外**——這是治「模型猜你已經懂、默默跳過」毛病的核心機制。
- 附受眾對照表（在乎什麼／該圍繞什麼講／該省略什麼）與通則：先講目的再講機制、低階一句一個概念、「80% 準但聽得懂 > 100% 準但聽不懂」、不居高臨下。伴讀 HTML 依同一階梯順序排版；結尾改問「哪一階還不清楚」。`--mode` 旗標與伴讀行為不變。

## marketplace `common-dev` 1.26.3 — wait-what 伴讀模式旗標 -v / -t / auto（common 1.21.2 / Codex 1.20.3）

- 實彈證據驅動（Codex 實測截圖）：模型引用「當視覺化不會真正幫助理解時可以不做 HTML」的例外條款，自判「文字圖已足夠」就跳過伴讀，與使用者預期落差。修正不走硬性強制，改為模式旗標：`--mode visual|text|auto`（縮寫 `-v` / `-t`），預設 `auto`。
- `visual`（`-v`）＝一律產出 HTML（唯一豁免：無任何工具能產出，且須明說）；`text`（`-t`）＝純文字重述、不產伴讀；`auto`（預設）＝保留原判斷句（工具允許即產出，僅「視覺無助益或無工具」可跳過），但**跳過必須明說並提示下次可用 `-v` 強制**。判斷自由留在 auto，使用者一個旗標即可拿回決定權。

## marketplace `common-dev` 1.26.2 — wait-what Codex 版移除 visualize tool 點名（common 1.21.1 不變 / Codex 1.20.2）

- 使用體感不佳，Codex 版伴讀段落拿掉「visualize tool is a natural fit for diagrams」點名，只保留 image-generation 模型提醒（可調用時生成插圖嵌入頁面）。「用手邊任何視覺化能力作畫」的原則句不動——不點名不等於禁用，模型仍可自行選工具。Claude 版無此點名，未變動。

## marketplace `common-dev` 1.26.1 — wait-what 伴讀產出後立即開啟（common 1.21.1 / Codex 1.20.1）

- 圖像化伴讀補一句：HTML 存檔後**立刻幫使用者打開畫面**——在對話中 render 或用瀏覽器開啟，視環境能力而定——不得只回報路徑了事。實測驅動（首次實彈演練時「回報落點」被讀成終點，畫面沒有主動送到使用者眼前）。

## marketplace `common-dev` 1.26.0 — wait-what 新手化重述＋圖像化伴讀（common 1.21.0 / Codex 1.20.0）

- **新手化重述**：重述姿態明確化——想像對「完全不懂該領域或該議題的人」開講，先給剛好夠進入狀況的背景（我們在做什麼、怎麼走到這裡、主題默認的先備知識），比喻、白話敘述、一點故事性皆可，唯以服務理解為準。「不加新資訊」條款同步校準：不加新的**任務**資訊，導引聽者的背景不在此限（原句會誤禁背景鋪陳，與新手化目標自相矛盾）。
- **圖像化伴讀**：工具允許時同場產出 self-contained HTML——圖與示意圖為主、文字為輔，用當下可用的視覺化能力（Codex 版點名 visualize tool 畫示意圖，且提醒：可調用 image-generation 模型產生插圖嵌入頁面），存放於專案 `.claude/wait-what/`（Codex 版 `.codex/wait-what/`）並回報落點。原則句而非硬性 gate：只有「沒有任何視覺表達真正有幫助、或無工具可產出」才略過，判斷權留給模型。

## marketplace `common-dev` 1.25.0 — strategic-advance 教義全文最佳姿態重寫：軍語壓縮＋概念收斂＋姿態/重劃入典（common 1.20.0 / Codex 1.19.0）

先派 Opus 研究員對美軍原典（ADP 6-0/5-0、FM 3-90/5-0，逐字比對＋段號程式化回收）驗證 13 組術語，再以研究成果重寫全文。研究存檔 `.strategic-advance/doctrine-research/military-terms-verification.md`（gitignored）。要點：

- **文眼確立（The proposition）**：在混亂中以相稱手段精準且有效率地把真實世界推到戰略終態；三敗判準——假進度是敗、浪費是敗、不相稱就算贏也是敗（核彈打小鳥條款）。文件自縛簡潔法："Shorter plans are easier to disseminate, read, and remember"（ADP 6-0 2026 1-72）、不重複 state contract 已載內容。
- **軍語壓縮入典**（全部經原典逐字驗證）：mission orders（只令結果不令方法）、disciplined initiative（主動性是義務不是許可，ADP 6-0 1-61）、execution decision／advance grant（預核決策：判準預先量化發布、扳機到即執行，ADP 5-0 4-28＋FM 3-90 disengagement criteria 12-28——2023 年新增術語）、permissive vs restrictive control measures＋establishing headquarters（誰立的措施誰才能豁免，FM 3-90 1-47/A-21）、CCIR（只蒐集餵決策的情報）、economy of force、operational regrouping（蘇軍 1965 辭典 entry 1000）、span of control 2–5（FM 5-0 2024 5-106；「3–5」訛傳勘正）。
- **不對稱正名**：升降階的真軸不是方向而是**賦予的所有權**——賦內行動憑企圖即行（升階不等）、變更賦予本身（棄地、降監視、終局、改目標）歸賦予者（retrograde 需上級核准，FM 3-90 11-1 廿二年條文不變、9-100 排他授權式）。姿態降格「如撤退：核准先於執行」入條文。
- **概念收斂去重**：The staff trap 一節總述四制服同病（書記陷阱／戰壕／工作服頂點／地圖劇場＝activity without shrinking the distance）、各處只留名字引用（scribe trap 5 處→2 處）；PDCA 節併入 Advance loop 導言；admission 降級條款與 Stand-down 去重；§4 重劃改名 Regrouping；姿態量測納入 span of control 判準。淨帳：兩個新機制＋概念層合計 +4.6KB（對 1.24.0 前基線），重複清零。

## marketplace `common-dev` 1.24.1 — `delegate` 原生 Luna Max 路由（common 1.19.1 / Codex 1.18.1）

- Codex lead 明確收到 Luna Max 時，優先用原生 subagent 同時 pin `gpt-5.6-luna`、`max` 與乾淨 context；bundled `luna-max-sidekick` 繼續提供完整 role instructions，不假裝成已註冊 custom agent。
- 原生候選 model／effort 改由當下 spawn schema 判定，CLI catalog 只證明 CLI carrier；native 無法精確 pin、Claude lead，或 `--fast` 需要 service-tier override 時才走 Codex CLI，且不得靜默換 model、effort 或角色。
- Luna carrier contract tests 翻轉為 native-first，並保留 source／generated role byte-equivalence、Fast CLI fallback 與 fail-closed resolver 驗證。

## marketplace `common-dev` 1.24.0 — strategic-advance 戰備姿態條款：三階儀裝、固定自檢、雙向扳機（common 1.19.0 / Codex 1.18.0）

隔壁戰役指揮官自發明出「輕裝模式」（S1 迴圈打熟後：書記官改片界一輪、稽核官異常出動、留三個重裝扳機）且判斷正確——但那靠的是指揮官臨場發明，下一個指揮官未必發明得出來。收編為 Force posture 新章（admission 之後）：

- **三階儀裝**：重裝（入場預設：每增量整編、每校準事件稽核、全驗收鏈）／輕裝（迴圈已證明、剩餘切片新穎度與風險較低：每片紀律不變、書記官片界一輪、稽核官異常出動、沙盤片界刷新）／退場（admission 不再成立：已知線性程序直接在 arm gate 下執行，即既有降級條款）。
- **姿態變更不移動突變裝甲**：arm gate、recovery readiness、每片驗收在任何姿態下等同——降格降的是監視節奏，不是不可逆邊界的安全；其風險是「發現得晚」，不是「傷得深」（回應使用者「這是有風險的行為嗎」的裁定入冊）。
- **固定自檢點**：每次主攻交接與每張整編收據，指揮官自問一題——儀裝還與地形的新穎度、突變風險、停滯紀錄相稱嗎。**升格扳機不等檢核點**：同指紋重複、compaction／跨 session 交接、新前線暴露新突變面或保護資產、終局判定（依法必重裝：全重建＋稽核官）。
- 對稱症狀句：「因驕傲留重裝與因慣性留輕裝是同一種失敗——都是儀裝在服務自己。」姿態變更＝指揮官處置權，ledger 記一行證據，零新欄位零 gate。

## marketplace `common-dev` 1.23.0 — strategic-advance 戰時最高法＋方向感知停滯（common 1.18.0 / Codex 1.17.0）

隔壁實戰戰役封緘陷阱驅動（兩管 5hr：/seal 品質棘輪被戰役反覆驅動成無界 finding 產生器，每條 finding 成立但不載重，指揮官讓驗收官的嚴謹定了節奏；忙碌迴圈每輪產出真增量——測試變多、缺陷變少——豁免於停滯判定，而終態距離自第二輪起未縮短）。判定：一增一改零刪——可刪的東西（seal 棘輪重置）在 baransu 且正解是支配不是閹割。原則＋症狀零新欄位：

- **新增：戰時最高法（Campaign law governs every embedded organ）**：戰役內任何品質機構（seal／review／lint）保有自己判 finding 成立的教義，但其教義永不定戰役節奏——finding 開修復迴圈必須走與一切行動同一道貢獻閘（DIRECT_ADVANCE／REMOVE_BLOCKER／CONTROL_RISK 對主攻），未過閘者不論多成立一律列冊隨行；兩套紀律相拉扯不是雙方守紀律，是只有指揮官能仲裁的衝突，且戰役閘勝。憲章裁決項同步下放細則：「機構判 finding 成立，指揮官判 finding 載重——後者永不外包給前者的嚴謹。」
- **更改：停滯判準換受詞**：PDCA 句「without a world delta must stop」改為「without shrinking the strategic distance（剩餘轉移＋未滿足勝利條件）」——原句即漏洞本體，真而不載重的增量可無限豁免停滯。§11 補症狀句：「真增量不重置任何逃逸預算，除非它縮短終態距離；連續數輪真增量而終態距離不動＝穿著工作服的頂點（culmination wearing a work uniform），與書記陷阱同科強制重估。」不加 K 計數器——「60–90 分鐘未關轉移」時間預算本已方向感知，缺的是把「忙碌不等於推進」講死。

## marketplace `common-dev` 1.22.0 — strategic-advance TTL 降權不降法：解除輕整編的時間軸架空（common 1.17.0 / Codex 1.16.0）

隔壁實戰戰役（kamishibai-sdk-v1）書記官三號的摩擦報告驅動——她拒絕回填時戳造假、整卷回滾、留下完整屍檢，證明三條 schema 級缺陷同一病根：**TTL 被當合法性管，該管的是權威性**。`set-claim` 推進 `updatedAt` → 超過任一 claim 的 `validUntil` → 全卷 PASS/FAIL 硬錯誤雪崩（實測 57 錯）→ 間隔超過 TTL 後輕整編機械性不可能，只剩 full reconstruction；且回滾後舊卷因 `updatedAt` 停在過去而顯示 VALID，誤導成功。修正（純放寬、schema 6 不動）：

- **過期降權不降法**：撤除「已過有效期，status 必須改為 UNKNOWN」全卷硬錯誤；過期 claim 保留紀錄 status、經既有 `claim_is_observed` 自動退出權威集。門上的 claim（ACTIVE entry、recovery readiness、pivot、victory 證據）過期時只冒針對性錯誤——那張三五條的工單就是輕整編的定義本身（新 self-test：`expiry-degrades-authority-not-legality`、`expired-gating-claim-is-targeted-work-order`）。
- **歷史紀錄不腐爛**：新增 recorded 權威集（rank 仲裁不看時效：最佳 `authorityRank` 勝，同級以最新 `observedAt` 勝）。`COMPLETE` 前線 exit、`latestVerifiedAdvance` before/after、`ENABLES_NEXT_TRANSITION` 目標 entry 改驗 recorded 集——史實不需現在式重探（before-claim 描述的世界已不存在，誠實重探永為 FAIL，舊制逼書記官在竄改時戳與全卷重建之間二選一），但更高權威的反證仍可推翻歷史。
- 條文同步：SKILL.md §10「Time cannot force the heavy weight」段、state-contract.md 權威性條目改寫，雙載體；validator 鏡像 byte-identical。她報的第三點（recovery 語意過期）屬語意層，指揮官已就地裁決，validator 不介入。

## marketplace `common-dev` 1.21.0 — strategic-advance 指揮官憲章：立職掌、反雙向逃逸（common 1.16.0 / Codex 1.15.0）

隔壁實戰 session（kamishibai-sdk-v1 戰役）暴露的指揮姿態缺口：指揮官被使用者連抓三次——手癢寫測試（下場執行）、「我跑 npm test 覆核」（下場驗收）、停等已授予的核准（上交決策）。病根同一：條文只有禁令沒有職掌，advance loop 十三節全用祈使句對同一個「你」，模型把整個 loop 當自己的 todo。修正全部走「原則＋可辨識症狀」形態，零新欄位、零新 gate：

- **Command charter 新章**：指揮官持有且僅持有五件事——判斷、派遣、裁決、處置、對使用者。執行歸最近戰面載體、探測與驗證歸書記官與驗收機構、簿記歸書記官。雙向逃逸同罪：下場（執行／探測／修）棄判斷，上交（停等已授核准）棄指揮；症狀句「回合被執行輸出填滿而判斷排隊＝人在戰壕」，與書記陷阱同科強制重估。
- **Delegation is the approval**：交付戰役即核准——`approvedAt` 以使用者原始指令為出處直接蓋章，永不結束回合等待已授予的確認；使用者是主權者不是簽核機。§366 review contract 的核准主詞明確為指揮官（僅超出 mutation scope 才升使用者）。
- **§8 改名 Dispatch the tactic＋舉證責任反轉**：每步先問「這一步誰拿槍？」；派遣無需理由、親自動手才需要——僅在委派開銷明顯大於該步本身時合法，且 ledger 記一行理由（事後可稽核、不設閘）。
- **Arm what you dispatch**：briefing 攜帶執行體打贏所需的一切——該步配得的最強模型、工具與檔案存取、證據路徑、預算與使用授權；餓著派遣不是委派，是替指揮官自己下場修爛攤子鋪路。
- **驗收鏈明文**：Acceptance is a verdict, not a probe——執行體回報是 MOP 自陳永不當驗收，MOE 證據來自書記官親探或獨立 verify-only pass，指揮官只裁決並將 findings 派回原執行體 capped 修復；§236 降級門補「連續降級是待浮上的症狀，不是可安住的常態」。

## marketplace `common-dev` 1.20.0 — strategic-advance 儀裝轉向：四項面向指揮官的機械改回面向戰場（common 1.15.0 / Codex 1.14.0）

實彈戰役 armor-outward 產出，戰役自身以「假定已修好」的 doctrine 遞迴運作（輕固化、閘門無授權力、成因自診、原子換手），並以修好後的工具收尾。四項修正：

- **takeover 閘拔毒牙**：`actionReadiness` 改名 `takeoverReadiness` 且整塊 optional——缺席＝自主姿態；欄位原名曾使 operator 誤當通用行動授權而空等一輪（機械上永無單純 READY）。schema 5→6 硬切、無別名（唯一使用者、無存量）；顯示語彙「行動門」→「接管門」；終局判準容忍缺席；新增無區塊 init 端到端測試。
- **固化分級**：輕固化（世界增量後預設——只重探事件觸及的 claim＋至多兩條自選抽查）／全量重建（僅 compaction、跨 session 換手、終局）。上一戰役實測每輪全量重探 120–190k tokens，成本結構本身逼出等待儀式；分級是「The ledger serves the advance」的機制面。
- **UNCLEAR 成因枚舉**：`strategicClarity.unclearCauses` 派生收據（七類），僅 `DECISION_FOG` 路由 `WAYFINDER_REQUIRED`，其餘派生新路由 `OPERATOR_RESOLVE`——成因即工單，就地處置；pivot PASS 改路由就地重估。修正「不明朗＝去開 Wayfinder」的誤診（兩次實戰不明朗皆非迷霧）。
- **原子換手指令**：`strategic_state.py handoff <state> <from> <to> --exit-source-ref …`——證據入冊（沿用 scribe-probe 出處文法）＋前線翻轉＋候選／清晰度派生重算，一步完成、整檔合法才落盤。解掉「ACTIVE 要求 exit 未 PASS ↔ COMPLETE 要求 exit PASS」互鎖迫使書記官整檔重寫的結構缺口；四載體 scribe 允許指令集同步。

## marketplace `common-dev` 1.19.1 — strategic-advance 書記陷阱條款原則化（common 1.14.1 / Codex 1.13.1）

- Tooth-to-tail 比值行撤除，改寫為原則句「The ledger serves the advance」：簿記為指揮官的判斷服務、不為勤勉表演；固化累積而世界不動即書記陷阱，與任何停滯戰線同樣強制重估。撤除理由（設計覆盤四軸檢驗）：原條款分母不可量測、以簿記義務治簿記病、n=1 無回看錨——skill 條款預設形態改為「原則＋可辨識症狀」，機械欄位與 gate 只保留給不可逆動作邊界；症狀仍可由既有 ledger 事後稽核，零新增記錄義務。

## marketplace `common-dev` 1.19.0 — common skill description 觸發詞前置＋strategic-advance 反癱瘓條款（common 1.14.0 / Codex 1.13.0）

- **description 全面正規化（9 個可自選 skill，claude＋codex 雙載體同步）**：載體從尾端截斷 description（Codex：預算＝context window 2%、context 未知 fallback 8,000 字元、單筆上限 1,024、先縮短後略過、預算不可調——常數經本機二進位字串探測證實），被砍的正是使用者會講的觸發詞。修正：U 類觸發詞（使用者實際會鍵入的字）全部前移至前 2/3；開頭統一為第三人稱單數動詞（官方 authoring 範例形）；`research` 補 `research this`／`look into`、`strategic-advance` 補 `keep advancing`／`推進`／`stalled`／`卡關`（原本零 U 類詞）。驗收器 `verify_descriptions.py` 三判準 3/7/2 → 0/0/0，改寫前後 U 類集合超集比對通過。叫用 token 依載體原生形式（`/name` ↔ `$name`）；`define-goal` codex 側保留載體原生觸發 `use the goal tool`；`wait-what`（`disable-model-invocation: true`，無觸發面）不在母體。
- **strategic-advance 樞紐句型規範**：`pivotCondition` MUST 為連續可求值的狀態述句、附正反例（SKILL.md §11＋state-contract.md，雙載體）。成因：pivot claim 生為 UNKNOWN，clarity 閘要求權威 FAIL，「某事發生後若仍如何」句型在該事發生前無從證否——首次固化必然被鎖 `WAYFINDER_REQUIRED`，而 Wayfinder 無迷霧可解。實戰死結案例驅動。
- **strategic-advance 反書記陷阱三條款**（實彈戰役中由分叉審計確認的參謀癱瘓病；歷史對映 CCIR／任務式指揮／tooth-to-tail）：固化僅由世界增量、主攻換手或終局觸發，帳務只准搭便車；收據永不是行動前置，arm gate 屬 operator 自身權柄，預授權行動類（唯讀探測、範圍內可逆編輯）不等收據；ledger 增列「自上次世界增量：簿記 tokens ∶ 產品 tokens」比值行為重估觸發器。另於 admission 增補：偵察收斂後重跑收案測試，剩餘工作已成線性程序即降級退出戰役編制。

## marketplace `common-dev` 1.18.0 — `strategic-advance` state 建構工具（common 1.13.0 / Codex 1.12.0）

- `strategic_state.py` 新增 `init`：從一份語意種子（JSON 一律支援，YAML 僅在 pyyaml 可用時支援）確定性展開合法 schema-5 `state.json`——canonical predicate 全部由 `canonical_predicate()` 生成、候選分數依固定公式回算、產出前先在行程內跑完整 validator，不合法就不落盤。書記官最重型的固化工作（初始 state 撰寫）從逐欄手寫降為填語意種子；範例種子落 `references/example-seed.json`。
- 新增 claim／front 級 CRUD：`set-claim`、`add-claim`、`set-front` 一律「改後整檔重驗、INVALID 不落盤並 exit 1」。PASS 紀律機械化——對 gating claim（戰場 entry／exit、pivot、victory 證據）寫 PASS 時 `--source-ref` 必須符合 `scribe-probe:<命令>@<時刻>` 文法，否則直接拒絕；非 gating 的脈絡 claim 維持誠實自由文字。
- 冷啟動姿態釘死於 validator 事實：非終局狀態必須恰有一個 ACTIVE 主攻，因此主攻的 entry claim 必須在種子裡帶探針出處出生為權威 PASS，其餘 claim 一律 `UNKNOWN`＋非探針 sourceRef，戰局判定為 `UNCLEAR`／`WAYFINDER_REQUIRED`、終局 `IN_PROGRESS`、三道行動門 `NOT_READY`。四載體 scribe 條文同步補「init first, then probe」與擴充後的 Bash allowed set。

## marketplace `common-dev` 1.17.0 — `strategic-advance` 戰役書記官兼偵察官（common 1.12.0 / Codex 1.11.0）

- `strategic-advance` 新增無狀態批次「書記官兼偵察官」（`sa-scribe` 角色檔，Claude 原生＋Codex TOML 雙載體）：每次固化 operator 只遞事件包，state.json 改寫、validator 收斂、沙盤渲染（`--no-open`）與 ledger 追記全歸書記官；operator 不再直寫 state.json。
- 獨立感測：gating claim（entry／exit／victory／world delta）的證據由書記官親跑唯讀探測產生，operator 貼的輸出降級為情報；sourceRef 釘死 `scribe-probe:<命令>@<時刻>` 文法、探測絕對路徑錨定戰役 root、finalize 前 grep 稽核——強度為 behavioral+auditable（明文聲明），非機械攔截；UI／API／DB 等探測不可達維度走 authorityRank 供證或 UNKNOWN 仲裁，不楔死戰役。
- 書記官零指揮權：歧異報告是 claim 級證據不符清單，永不構成 verdict（verdict 屬對齊稽核官）；operator 從 validated state 重建 HQ packet 並保留抽查——零直寫不等於零驗收。每次派遣的 token 用量記入 ledger 供成本對帳。
- 連帶：marketplace 描述中 baransu suite 路由移除已於 baransu v4.0.0 退役的 `analyze`。

## marketplace `common-dev` 1.16.1 — `strategic-advance` 勝利封盤視覺（common 1.11.1 / Codex 1.10.1）

- `STRATEGIC_OBJECTIVE_ACHIEVED` 現在會切換成明確的戰局完成態：首屏勝利 Banner、一次性電光與完成 Seal、封盤 HUD，並停止 auto-refresh 與主攻即時計時；遵循 reduced-motion 時不播放動畫。
- 精簡戰局圖在勝利終局改顯示「最終狀態 → 戰果確認 → 戰局完成」，不再保留「下一動」或「唯一主攻」的誤導訊號；一般進行中、`NEW_AUTHORITY_REQUIRED` 與 `LOSS_MINIMIZED` 維持原本語意。
- 修正行動版表格造成的頁面水平溢位，完成 Banner、Seal 與技術細節在窄螢幕仍可閱讀；Claude Source 與 Codex renderer／自測同步。

## marketplace `common-dev` 1.16.0 — 新增 `strategic-advance` 與 common 繁中預設（common 1.11.0 / Codex 1.10.0）

- `common` 新增 `strategic-advance`：鎖定可驗收的戰略目標，以即時情報、單一主攻與證據驗證的一動持續推進長期、跨工具任務；優先自動化，只在自動化已證明卡住且人工動作可操作、可執行、可檢核時才接管。
- v5 戰略狀態契約加入 bounded HQ packet、事件驅動唯讀校準、validator 產生的 canonical predicate 綁定的三道人工接管門與勝利／新權限／損失最小化終局；合法終局不再保留活動主攻或人工指令。繁中沙盤預設自動開啟，戰局圖只畫有明確因果的精簡主線，完整歷史按需展開。
- `common` 全部 10 個 Skill 維持英文指令本體，使用者說明與新產生的人類可讀產物預設改為繁體中文；使用者明確指定其他語言時仍以指定語言為準，`delegate` 與 `research` 也會將語言要求傳給背景 agent。
- `wayfinder` 的 HTML 地圖介面預設使用繁體中文，並保留明確的 English override；決策路線收斂後會依 gate 自動選擇一般執行或 `strategic-advance`，並以 return marker 防止雙向遞迴。README、plugin manifests 與 marketplace overview 同步 common 10 個 Skill／全 marketplace 18 個 Skill。

## marketplace `common-dev` 1.15.0 — 恢復 `dev-browser`（test-utils 1.2.0 / Codex 1.2.0）

重新評估實際使用情境後，`dev-browser` 對 agent 維持瀏覽器 session、互動式排查 UI、驗證 API response 與修正後複驗仍有獨立價值，因此恢復為 test-utils 的第三個 Skill。

- 恢復 Claude canonical 的 `skills/dev-browser/`：Skill、9 份 reference 與 4 支 setup/case script。
- 由 Claude source 重新產生 Codex `dev-browser`，並以目前 `SKILL.md` 所在目錄解析 bundled scripts，移除 `${CLAUDE_PLUGIN_ROOT}` 與無效 slash alias 的 runtime 假設。
- 對齊本機 `dev-browser` 0.2.9 live contract：每個 session 先讀 `--help`、登入只限 authenticated flow、PowerShell here-string pipe 可用、新分頁改用 `listPages()` / `getPage(targetId)`，WSL Windows 命令改走 PowerShell 7。
- `gen-e2e-test` 1.2.3 將純前端 debug、UI 驗證與 console error 排查重新導向 `dev-browser`。
- README、plugin manifests、marketplace catalog、CLAUDE.md 與 overview SVG 同步恢復為三個 test-utils Skills。

## marketplace `common-dev` 1.14.0 — 移除 `dev-browser`（test-utils 1.1.0 / Codex 1.1.0）

實際使用後，`gen-e2e-test` 與 `gen-e2e-record` 已足以涵蓋 test-utils 的交付需求；近期模型使用 Playwright 的穩定度也優於 `dev-browser`。因此將 `dev-browser` 完整移除，避免模型再被較容易卡住的額外 CLI 路線吸走。歷史版本與安全修正紀錄保留於下方，刪除內容仍可由 Git 歷史還原。

- 刪除 Claude 與 Codex 的 `skills/dev-browser/`，包含 Skill、9 份 reference 與 4 支 setup/case script。
- `gen-e2e-test` 1.2.2 將純前端 debug、UI 驗證與 console error 排查改路由至環境現有的 Playwright 能力。
- README、plugin manifests、marketplace catalog、CLAUDE.md 與 overview SVG 同步改為兩個 Playwright E2E Skill。

## marketplace `common-dev` 1.13.0 — wayfinder 附屬 Skill 自動觸發（common 1.10.0 / Codex 1.9.0）

- `grilling`、`domain-modeling`、`research`、`prototype` 移除 Claude 的 `disable-model-invocation` 與 Codex 的 `allow_implicit_invocation: false`，現在可依各自 description 自動觸發；`wait-what` 仍維持純使用者觸發。
- Codex `wayfinder` 的跨 Skill 引用統一為 `$skill` 語法，涵蓋 common 附屬 Skill、`delegate`、`wait-what` 與可選的 baransu 路由。
- README 的 `common` 區塊只保留精簡的 Skill 名稱與簡介，移除移植來源與 `delegate` 深入說明。

## marketplace `common-dev` 1.12.0 — wayfinder 操盤手姿態（common 1.9.0 / Codex 1.8.0）

`wayfinder` 新增「The operator principle」：驅動地圖的主 session 是操盤手——持圖選票、跟人對話、判斷證據、介入，四件事以外不燒自己的 context。票的執行體（讀資料堆、掃描／測試、AFK task、產大型產物）一律交給 `delegate` 派工，其 worth-it gate 仲裁太小的 slice 拿回 inline。sidekick 回報的是證據不是結論，驗收永不委派；drain 模式以此為預設姿態。Claude source 與 Codex shadow 同步。

## marketplace `common-dev` 1.11.0 — wayfinder drain 模式、baransu 路由與檢視器 XSS 修補（common 1.8.0 / Codex 1.7.0）

- **Drain 模式**：第三種呼叫模式——掃 frontier、批次 claim 所有 AFK 票（research 與可自駕的 task）、平行解掉、記錄後重算 frontier 續排，直到只剩 HITL 票才停；停下時開圖並把剩餘問題白話脈絡一次攤給使用者批。HITL 邊界為絕對規則：永不自答 grilling、永不代替 prototype 反應。
- **Baransu 生態系路由（optional）**：偵測到 baransu 套件才逐槽路由——判斷型 grilling → `think`、來源型 research → `read`/`learn`（給人讀 → `book`）、視覺 prototype → `design`、執行型 task → `contract`+`seal`（追 bug → `hunt`）、重決策複核 → `review`、收尾 → `ship`、完圖交棒 → `analyze`；無天然接點的 skill（health/evolve/write）刻意不收。路由選擇釘進地圖 Notes，所有並行 session 走同一套。
- **XSS 修補**：地圖檢視器的 markdown 連結渲染改為 scheme 白名單 + href 屬性跳脫 + `rel="noreferrer noopener"`，堵住票內容夾帶 `javascript:` URI 的注入面；`esc` 同步涵蓋單引號。

## marketplace `common-dev` 1.10.0 — 移植 wayfinder 生態系（common 1.7.0 / Codex 1.6.0）

移植 [mattpocock 的 wayfinder](https://github.com/mattpocock/skills/blob/main/skills/engineering/wayfinder/SKILL.md) 及其四個依賴 skill（grilling / domain-modeling / research / prototype），Claude source 與 Codex shadow 同步新增：

- **wayfinder**：把一個 session 裝不下的大工作攤成決策票地圖——destination、blocking、frontier、fog of war，一個 session 解一張票（research 例外）。tracker 改為內建 local markdown（`.claude/wayfinder/<effort>/`，原版的 GitHub/GitLab 支援與 `setup-matt-pocock-skills` 依賴移除），跨 skill 引用改 `/common:*` 完整命名空間。
- **互動式 HTML 地圖**：`scripts/render_map.py`（stdlib-only）+ `assets/map-template.html` 模板生成單檔自含檢視器——航海圖視覺、frontier 燈塔光暈、blocking graph hover 點亮依賴鏈、票卡展開、狀態篩選；產完預設自動開瀏覽器（WSL 走 `wslpath -w` + `explorer.exe`，`--no-open` 可關）。
- **Speak plainly**：所有給使用者閱讀的文字與選項，比照 `wait-what` 先以白話繁中解釋脈絡再給選項。
- **四個附屬 skill 均 `disable-model-invocation: true`**（避免與既有生態觸發語衝突，Codex 側映射 `agents/openai.yaml`），僅 wayfinder 本體開放描述觸發。

## marketplace `common-dev` 1.9.2 — Luna Max 固定走 Codex CLI sidekick（common 1.6.2 / Codex 1.5.2）

`delegate` 將使用者明確指定的 Luna Max 收斂成固定 Codex CLI sidekick 路由：package-local `luna-max-sidekick` 仍是 fail-closed role 定義，不再被誤當成已註冊且可直接 pin Luna 的 native agent。啟動前仍需即時確認 CLI、登入、`gpt-5.6-luna` 與 `max`；任一缺失即回報精確不相容，不改走 native 或靜默替換。若同時指定 `--fast`，只在同一次 CLI dispatch 套用 Fast service tier，既有可見降級語意不變。

## marketplace `common-dev` 1.9.1 — Codex-only `delegate --fast`（common 1.6.1 / Codex 1.5.1）

`delegate` 新增使用者顯式控制的 `$delegate --fast`：保留既有 sidekick model、effort、任務評分與驗收流程，只把當次 Codex carrier 切到 Fast service tier。原生 carrier 無法 pin Fast 時改用 Codex CLI 單次 override；能力不可用時明確顯示 `FAST_FALLBACK` 後降級為標準 sidekick。Claude lead／CLI 禁用此旗標。Codex skill UI 另加入含 `$delegate --fast` 的灰色預設提示。

## marketplace `common-dev` 1.9.0 — 新增 `define-goal` skill（common 1.6.0 / Codex 1.5.0）

移植 [OpenAI 的 define-goal](https://github.com/openai/skills/blob/main/skills/.curated/define-goal/SKILL.md)：開工前把模糊意圖釘成可誠實驗收的目標——具體成果、驗證證據、量化或二元門檻、scope 邊界、該停下來問人的條件；弱目標（「持續調查」「讓它變快」）先改寫或退回。

- **Claude 版改寫 goal tool 依賴**：原始 skill 呼叫 Codex 專屬的 `get_goal` / `create_goal`，Claude Code 沒有這組工具，改為在對話中以 **Goal** 區塊釘住目標、經使用者確認後作為後續工作的驗收標準。
- **Codex 版保留原文**：Codex 側 goal tool 真實存在，`codex/plugins/common/skills/define-goal/` 直接收錄 OpenAI 原始 SKILL.md。

## marketplace `common-dev` 1.8.3 — `common` 改為預設啟用（common 1.5.3）

`common` plugin 改為 `defaultEnabled: true`：加入 marketplace 即啟用，不需要可用 `claude plugin disable common` 關閉。`test-utils` 與 `analysis-estimation` 維持 opt-in。

## marketplace `common-dev` 1.8.2 — `delegate` lead 職責改寫（common 1.5.2 / Codex 1.4.2）

`delegate` 的 lead 職責從單點描述改寫為全生命週期領導定義：分析、決策、驗收始終留在 lead，sidekick 只承接邊界清楚的執行段。Claude source 與 Codex shadow 同步。

## marketplace `common-dev` 1.8.1 — `delegate` CLI sandbox parity（common 1.5.1 / Codex 1.4.1）

修正 Codex CLI 寫入委派把 unrestricted parent 慣性降成 Windows `workspace-write` 的啟動錯誤，Claude source 與 Codex shadow 同步：

- **sandbox mode 與 parent 對齊**：read-only 任務維持 `read-only`；`workspace-write` parent 的授權寫入維持 `workspace-write`；parent 已是 unrestricted / `danger-full-access` 時，授權寫入直接使用 `-s danger-full-access`，再以精確 write set、工作目錄、briefing 與 lead 驗收收窄。
- **不混用危險 bypass**：明確區分 `-s danger-full-access` sandbox enum 與被禁止的 `--dangerously-bypass-approvals-and-sandbox`；不得比 parent 升權，parent mode 不明時停止查證，不猜測。
- **Windows 一次啟動成功路徑**：避免為本來可寫的 unrestricted checkout 額外建立 ACL sandbox，消除 `Failed to write file` / `SetNamedSecurityInfoW failed: 5` 後才改派 read-only patch 的多餘 round trip。

## marketplace `common-dev` 1.8.0 — 新增 `wait-what` skill（common 1.5.0 / Codex 1.4.0）

移植 [mattpocock 的 wait-what](https://github.com/mattpocock/skills/blob/main/skills/productivity/wait-what/SKILL.md) 為中文版：skill 本體英文、輸出繁體中文，Claude source 與 Codex shadow 同步新增。

- **純使用者觸發的停止訊號**：`disable-model-invocation: true`（Codex 側對應 `agents/openai.yaml` 的 `policy.allow_implicit_invocation: false`），聽不懂時打 `/common:wait-what`，模型停下任務、不再推進。
- **白話重講的固定順序**：先補脈絡（我們在做什麼、怎麼走到這裡）→ 再講決策理由（為什麼這樣說、為什麼做這個決定）→ 技術術語保留原文但當場白話解釋 → 不加新資訊，最後問哪裡還不清楚並等待。

## marketplace `common-dev` 1.7.1 — `delegate` review 修正（common 1.4.1 / Codex 1.3.1）

獨立 review 對 1.7.0 的三項修正，Claude source 與 Codex shadow 同步：

- **路徑選擇定優先序**：評分表裁決路徑；lightweight 段的條件（single-shot、敏感資料不出機器等）是額外 guard，任一不成立即使總分 `0–2` 也升到完整路徑——消除兩套選擇器對同一任務給出不同答案的矛盾。
- **巡檢補 untracked 盲區**：`git diff --name-only`／`--stat` 看不到 write set 外「新增」的 untracked 檔案（實測確認），巡檢清單加入 `git status --porcelain`。
- **CLAUDE.md invariant 同步**：補上 plugin-level agents 以 `${CLAUDE_PLUGIN_ROOT}/agents/<agent>.md` 引用的子句與 `agents/` 自動發現說明，與 AGENTS.md 一致。

## marketplace `common-dev` 1.7.0 — `delegate` 監督式長任務與 Luna Max sidekick（common 1.4.0 / Codex 1.3.0）

把實際專案使用後補出的派工策略通用化回 `common`，Claude source 與 Codex shadow 同步更新：

- **三段式路徑**：用執行階段、write surface、執行／驗證時間、偏離代價四維各 0–2 分，`0–2` 輕量、`3–5` 完整、`6–8` 監督式；定期監看／progress ledger／偏離介入要求會直接選監督式，固定長命令則留給 lead 的 wait/monitor 機制。
- **監督式長任務**：sidekick 先建立自包含 HTML ledger，再修改產品檔；lead 預設每 5 分鐘合看 runner、ledger、write set、diff、stderr/final。介入前先取唯讀快照，只停止精確 runner process tree，並以明確 session ID checkpoint resume，禁止 `--last`／`--continue` 猜 session。
- **live sandbox preflight**：寫入前將 write set 解成絕對路徑並核對 parent task 的實際 writable roots；Windows ACL／sandbox denial 屬環境失敗，父權限未變時不得原條件 resume 或重派。
- **Luna Max bundled role**：新增 Claude `agents/luna-max-sidekick.md`，transfer 產生 Codex `.codex-agents/luna-max-sidekick.toml` 與 fail-closed resolver。只有使用者明確要求、live catalog 同時確認 `gpt-5.6-luna` 與 `max` 時才 pin；原生 launch schema 無法完整套用時改走 Codex CLI，不靜默替換模型、effort 或角色。
- **model filter 與實跑 CLI gotchas**：`parse-cli-json.js models` 現在同時輸出支援的 reasoning levels；Luna Max read-only forward test 證實外層 carrier 仍需可寫 runtime 才能啟動 app-server、high/max 可能數分鐘沒有 reducer 摘要、background launcher 空回應不等於 runner 結束，且 read-only heredoc temp failure 應在原 thread 換策略。Codex/Claude reference 同步加入 `/dev/null` stdin 關閉、shell backtick quoting、multi-file patch 原子失敗後的重讀拆分、批次驗證 exit masking、parity normalization 誤判、cleanup policy denial 的收尾分類、temporary `CODEX_HOME` PATH-helper warning 的非致命判讀、runner/session identity、resume 前確認舊 writer 停止，以及跨 workspace root 的最窄寫入範圍規則。
- **獨立驗收**：使用者要求獨立 review 或偏離代價為 2 時，implementer 停止後才把驗收條件、實際 diff、必要原始證據與 ledger 交給乾淨 reviewer；兩者不得同時寫同一工作區。

## marketplace `common-dev` 1.6.0 — `delegate` 選型改為雙軸（common 1.3.0 / Codex 1.2.0）

原本的選型規則只有單一軸（tier 高低），把模型當成一條「強弱階梯」。補上第二軸：**家族適配**——模型不是比較強或比較弱，而是思考方式不同，配錯家族時在同一家族內往上加錢並不會變好。全部以**家族層級**表述，不指定任何版號，因為家族的壽命長於個別版本；實際 model ID 一律由既有的 session 內即時查詢解析。

- **選型改為兩軸、有先後**：先依工作形狀選家族（「從既定目標自主執行／跨檔探索」→ GPT 家族的 principle-driven 特性；「必須逐步照做的長流程／結構化輸出」→ Claude 家族的 mechanics-driven 特性；「機械掃描、單發查證」→ 兩者皆可，取最便宜的 tier），再於家族內從最低可行 tier 起跳。單次只升一維的既有規則不變。
- **升級前先複查家族適配**：輸出漂離目標、忽略部分 briefing、或形狀自信但錯誤 → 那是配錯家族而非 tier 不夠，於同一家族內升級只會多花錢並以同樣方式失敗。
- **briefing 密度隨家族調整**（三個必填欄位與「只定目的不鎖路徑」的契約不變，變的只有欄位內的鷹架密度）：GPT 家族保持精簡——規則越多等於矛盾面越大，過了某個點反而**更**漂移；Claude 家族可給更多結構，把驗收寫成明確清單、輸出形狀寫死，該家族的失敗模式是規格不足而非過度規格。
- 失敗分類表新增一列對應「配錯家族」，與既有的環境類／策略類／任務類並列。
- 依據：oh-my-openagent 的 agent-model-matching 指南（模型即開發者、家族思考方式差異、替換規則）。


## marketplace `common-dev` 1.5.0 — 移除 `mimir` plugin

實際使用後判定 `mimir`（專案記憶引擎，6 個 skill）不符需求，整個 plugin 自 marketplace 移除，日後若重做會以新設計重新開始。歷史紀錄（1.2.0 新增、1.2.1 audit、1.3.1 路徑修正）保留於本檔案下方，不改寫。移除的檔案可由 git 歷史還原。

- 刪除 `plugins/mimir/` 與 `codex/plugins/mimir/`（各 6 個 skill，共 50 檔）。
- 三份 catalog 移除 `mimir` 條目：`.claude-plugin/marketplace.json`、`.agents/plugins/marketplace.json`（Layout A）、`codex/.agents/plugins/marketplace.json`（Layout B）。
- `README.md`：移除安裝指令、總覽表格列、`## mimir` 專節與結構樹節點；plugin 數量由「四個」更正為「三個」。
- `CLAUDE.md`：情境型 plugin 列舉移除 mimir。
- `AGENTS.md`：移除 `templates/` 還原說明中的 mimir 例子、整段 mimir-only 的 parity-gap 說明，以及**佈局檢查指令中斷言 `codex/plugins/mimir/.codex-plugin/plugin.json` 存在的那一條**——不移除該行檢查指令會在移除後直接失敗。兩條檢查指令均已實跑通過。
- `docs/images/marketplace-overview.svg`：以 `common` 區塊取代 mimir 區塊，畫布高度 1248 → 1074，caption 由「3 plugins · 14 skills」更正為「3 plugins · 10 skills」。**附帶修正**：該圖原本就未收錄 `common`（是移除前既有的過時），而移除 mimir 必須改動 caption，只刪不補會產生新的錯誤敘述，故一併補齊。

## marketplace `common-dev` 1.4.1 — `delegate` 全面英文化（common 1.2.1 / Codex 1.1.1）

`delegate` 的 skill 本體改為純英文，與 `better-prompts` 的慣例一致（英文本體、依目標載入 reference）。純文案變更，無行為與流程語意調整。

- `SKILL.md` 與 `references/{codex-cli,claude-cli}.md` 全文英譯，章節結構、⛔ 標記、表格與程式碼區塊逐一對應保留。
- 兩支 script 的註解與**執行期輸出訊息**一併英譯（`delegate: --raw <path> and --final <path> are required`、`⏸ no activity for N min · last: …`、`CLI returned an error`、`± file.ts (N files)` 等）。四條錯誤路徑與 `models` filter 實跑驗證，訊息與 exit code 均正確。
- **刻意保留的兩處非英文**：(1) frontmatter description 的中文觸發詞（`派工`／`派給`／`委派`／`丟給 codex`）——那是使用者實際輸入的觸發字串，移除會降低觸發率，`better-prompts` 亦同；(2) `reduce-cli-events.js` 首句擷取的 `split(/(?<=[。！？!?])\s*/)`——該處解析的是 **sidekick 的輸出**，其語言取決於任務而非 skill，移除 CJK 句號會讓中文回報的首句擷取失效。
- Codex 側由英文來源重跑 `codex-skill-transfer` 0.14.2 產出，`DELEGATE_DIR` 說明段同步改為英文；`better-prompts` 兩側仍未觸碰。

## marketplace `common-dev` 1.4.0 — 新增 `delegate`（common 1.2.0）

把原本綁在單一專案 repo 裡的 `delegate` skill 升格進 `common`，成為與專案無關的通用派工工具。內容為目的導向派工：先過「值不值得派」Gate，再走輕量或完整路徑，session 內即時查 model 目錄選最低可行的 model + effort，經 Codex CLI 或 Claude CLI 把邊界清楚的執行段交給 sidekick。

`common` 1.2.0 — delegate：

- 新增 `skills/delegate/`：`SKILL.md`（派工決策層）＋ `references/codex-cli.md`、`references/claude-cli.md`（執行機制層，確定載體後才載入）＋ `scripts/parse-cli-json.js`、`scripts/reduce-cli-events.js`（單一 JSON 與 JSONL 事件流的 reducer，raw 不進 lead context）。
- **路徑改為 marketplace 慣例**：來源版本要求執行期「解析本 Skill 目錄為 `DELEGATE_DIR`」再以 `$DELEGATE_DIR/scripts/...` 呼叫；Claude 側改為 `${CLAUDE_PLUGIN_ROOT}/skills/delegate/...` 以符合 repo invariant，PowerShell 區塊用 `$env:CLAUDE_PLUGIN_ROOT`。
- 修正來源版本的自我參照不一致：`SKILL.md` 的 model 目錄段落原以相對路徑寫 `scripts/parse-cli-json.js`，reference 卻用 `$DELEGATE_DIR/`；兩者統一。
- **genericness**：`codex-cli.md` 的網路權限說明移除「連內網 DB」這個專案味範例，改為一般性的「任務需要網路」。
- frontmatter description 改為英文主體＋中英雙語觸發詞（`派工`／`派給`／`委派`／`丟給 codex`／`delegate this`／`hand this off`），對齊 `better-prompts` 的慣例以提升觸發準確率。
- README 補上 `delegate` 的目的、四步驟流程與結果狀態表（含失敗分類：環境類不算失敗、不升模型、不計入重派次數）。

`common`（Codex）1.1.0 — delegate：

- 以 `codex-skill-transfer` 0.14.2（baransu 3.1.3）產出後只取 `skills/delegate/` 放入 `codex/plugins/common/`；**手寫的 Codex 版 `better-prompts` 未被觸碰**（兩側 `better-prompts` 各自維護，非 transfer 生成）。註：0.14.x plugin 模式輸出自含 marketplace root（`<out>/.agents/plugins/marketplace.json` + `<out>/plugins/<name>/`）且**重跑會整個抹除輸出目錄**，故一律先產到 throwaway 目錄再摘取，不得直接指向 `codex/plugins/common`。
- **Codex 側改為執行期解析 `DELEGATE_DIR`，不使用 `${CLAUDE_PLUGIN_ROOT}`**。依據：(1) 實測 Codex shell 無任何 `*PLUGIN_ROOT*` 變數；(2) `transfer.py` 的 `forbidden_runtime_tokens` 明列 `CLAUDE_PLUGIN_ROOT` 為禁止出現在 Codex 產出的 runtime token；(3) transfer 只在 bundled agent 本體改寫為 `../`、在 hook `command` 改寫為 `PLUGIN_ROOT`，skill 本體與 references 一律不自動改寫。0.14.2 已把 `CLAUDE_PLUGIN_ROOT` 納入 Claude-only token 掃描，本次移植對 `SKILL.md` 與兩份 reference 各產出一則需人工檢視項（0.14.1 為靜默零項），本節即該項的處置紀錄。SKILL.md 開頭新增 `DELEGATE_DIR` 解析規則（禁止猜路徑、禁止改用 cwd 相對路徑——sidekick 的 cwd 是使用者專案而非 skill 目錄），兩份 reference 的前置檢查各回指該規則。
- 兩側除 frontmatter、該路徑變數與上述說明段外，body、references、scripts 逐字相同；兩支 script 與 Claude 側 byte-identical。

## marketplace `common-dev` 1.3.2 — remove `/baransu:execute` references (analysis-estimation 1.0.2)

`rfp-sa-bdd` referenced the personal `/baransu:execute` skill by name in its description, body, and index template. All 9 occurrences genericized to「下游 TDD 執行流程」— the skill now stays fully marketplace-neutral per the repo's genericness invariant. No workflow changes.

## marketplace `common-dev` 1.3.1 — better-prompts 1.1.0 rewrite + all-skill best-practices audit (Claude side)

Rewrote the Claude-side `better-prompts` per Anthropic's official skill-authoring best practices, and ran a parallel multi-agent audit (audit → safe-fix → adversarial verify) of all 14 other Claude-side skills against the same checklist.

`common` 1.1.0 — better-prompts:

- SKILL.md body rewritten in English: third-person description focused on "optimize prompts" (with zh/en trigger phrases), a copyable workflow checklist, target-model → reference-guide routing table, and one-level-deep reference links per the progressive-disclosure guidance.
- Added `references/claude-prompting-guide.md` — distilled official guidance for optimizing prompts targeting Claude 4.6+/5-family and Claude Code (CLAUDE.md vs skills vs hooks, literal instruction following, de-prescribing, tool-description triggering, autonomy/narration snippets), alongside the existing GPT-5.6 reference. Vendor-specific advice applies only to its own target.
- Codex-side `better-prompts` is unchanged (maintained separately by Codex).

Skill audit fixes (no workflow-semantics changes; all diffs adversarially verified):

- **test-utils 1.0.3** — gen-e2e-test: Stage-2 copy list now uses `${CLAUDE_PLUGIN_ROOT}` paths and includes the bundled `capture-auth.mjs/.bat` (previously documented but missing from the copy list and output tree). gen-e2e-record: 8 bundled-file references converted from bare/`../` relative paths to `${CLAUDE_PLUGIN_ROOT}`. dev-browser: `allowed-tools` frontmatter fixed to comma-separated form; backslash `${CLAUDE_PLUGIN_ROOT}` paths normalized to forward slashes.
- **analysis-estimation 1.0.1** — rfp-requirement-analysis / rfp-architecture-design / rfp-sa-bdd / cold-estimation / quality-orchestrator: bundled template/reference paths converted to `${CLAUDE_PLUGIN_ROOT}` form.
- **mimir 1.1.1** — mimir-forge: 載入矩陣 bundled-file paths converted to `${CLAUDE_PLUGIN_ROOT}` form.
- Known remaining low-severity items (deliberately deferred, need human judgment): rfp-sa-bdd carries domain-specific leasing rules and `/baransu:execute` references; mimir behavior references >100 lines lack TOCs; eval-tuning residue in rfp-requirement-analysis.

## marketplace `common-dev` 1.3.0 — add `common` plugin (common 1.0.0, Claude + Codex)

Added the opt-in `common` plugin with `better-prompts` — a skill for improving, auditing, drafting, and migrating prompts, tool descriptions, agent instructions, and prompt stacks using OpenAI's GPT-5.6 prompting guidance. Ships on both sides in this release: Claude (`/common:better-prompts`) and Codex (`$better-prompts`). The two variants were authored independently — the runtimes' models behave differently, so each side keeps its own wording and its own A/B evaluation.

Claude side:

- Four modes (audit / rewrite / draft / migrate) with an auto-classification table, a 10-point diagnostic checklist mapped to guide sections, and fixed output formats including a "風險與待確認" section so deletions stay user-reviewable.
- Bundled an offline distillation of the official GPT-5.6 guide under `references/`, with instructions to fetch the live URL when current wording is requested, and an explicit scope note separating structural principles (model-agnostic) from OpenAI-API-specific advice.
- Independently A/B tested (3 tasks × with/without skill, graded assertions: 100% vs 86% pass rate) plus a blind-judged downstream behavior layer (rewritten prompts eliminate the original's contradiction-driven extra tool calls).
- Registered `common` in the Claude marketplace catalog and updated README install/table/structure sections accordingly.

Codex side:

- Added an outcome-first rewrite and audit workflow covering success criteria, evidence, contradictions, autonomy and approval boundaries, tool routing, output requirements, stopping rules, and targeted validation.
- Added a concise offline reference derived from the official GPT-5.6 guide, with instructions to refresh the live official source when current guidance is requested.
- Registered `common` in both Codex marketplace layouts and documented its Codex install path.

## marketplace `common-dev` 1.2.1 — mimir audit fixes (mimir 1.1.0)

A plan-vs-implementation audit of `mimir` found 10 promised-but-missing items; this release closes the actionable ones.

L2 validation layer (was entirely absent — cross-file semantics relied on model self-discipline):

- **`validate-links.py` (new)** — cross-file checks: `[ID title]` citations / `sources[].id` / `superseded_by` targets must be defined somewhere in the tree; `sources[].path` and `@import` targets must exist; superseded-consistency warnings; and the P1–P5 forbidden status combinations from `rules/status-model.md` as machine checks. Exit 0/1/2.
- **`health-report.py` (new)** — W9 work item: doc_status counts and confirmed ratio, active WIP list, pending FB/CHG/ISS (frontmatter- and anchor-entry-level), `--module` filter.
- **`rebuild-index.py`** — now also rebuilds module-level `Index.md` under `03_SA/{Module}/` and `04_SD/{Module}/` (idempotent; `00_Index` behavior unchanged). `structures/pm-ra.md`'s derived-index claim was narrowed to match exactly (01_PM/02_RA and Domain-level indexes stay carve-maintained).

Governance content that had nowhere to live:

- **`references/faq.md` (new)** — PART 8 decisions (cross-module dependency → ISS; module merge → CHG; v2 never copies v1; no Jira/Confluence sync — Mimir is the sole memory; typo fixes don't open CHG; change-notification digest on request; AI-marked superseded needs human confirmation) plus the L1–L6 content-depth reference ladder and the "one sentence is enough to file" threshold.
- **`behaviors/recall.md`** — the conservative auto-trigger table (requirement-semantic work → auto quick check; light UI / small bugs / pure refactor → no trigger; unsure → ask) replacing the vague "(含自動觸發)".
- **`structures/pm-ra.md`** — Atlas.md maintenance policy (AI draft + human revision; never fully script-rebuilt).
- Load matrix + per-skill script blocks updated: recall gains `health-report`, amend gains `validate-links`.

W8 forward test executed (scripted walk of a small module through listen → carve → recall → forge in a sandbox): all five stages pass, the HTML deliverable is self-contained and confirmed-only filtering works. It also caught two deliverable-facing leaks, both fixed in `build-spec.py`:

- **ID literals leaked into deliverable headings** — templates hardcode `# {{ID}} {{title}}`, so despite the "deliverables hide IDs by default" gate, every section H1 and TOC anchor showed the raw ID. Headings are now stripped of the leading ID token unless `--trace` is given.
- **Template author-hint HTML comments leaked as escaped garbage text** (`<!-- 位置:... -->` etc.) — the renderer now strips all HTML comments from both `html` and `md` outputs (the generated-file marker is re-added by the writer itself).

Plus from the same test: new `templates/ISS.md` (rules demand "open an ISS" everywhere but no template existed), a module-prefixed `next-id.py` example in `rules/id-and-citation.md`, and an `@import` dedup edge-case note in `behaviors/forge.md`.

Also: README plugin-count wording ("兩個"→"三個") and template count (12→13) corrected; AGENTS.md documents the accepted Codex parity gap (`AskUserQuestion` wording inside hand-restored `rules/`). Codex variant regenerated from the updated source.

Known deliberately-deferred items (audited, not shipped): `rename-id.py` (non-MVP §6.1 item); a Codex-native `request_user_input` question adapter; Dictionary.md/Overview.md authoring rules and templates (recall's Dictionary-first strategy has an explicit fallback when they're absent); machine enforcement of the status transition *sequence* (enum membership is checked; ordering stays a documented convention).

## marketplace `common-dev` 1.2.0 — add `mimir` plugin (mimir 1.0.0)

New opt-in plugin `mimir` (`defaultEnabled: false`) — a project memory engine for custom system development: capture interviews, SOW/RFP clauses, mid-stream requests, SIT/UAT feedback, and decisions from day one, and evolve them into traceable RA/SA/SD documents with a verifiable evidence chain. Scope ends at SD — no code implementation.

One public entry (`/mimir`) routes five behavior skills:

- `mimir-listen` — session scribing (interviews / internal discussions) with live candidate tagging.
- `mimir-carve` — capture & file: turn raw signals into ID'd, sourced memory files (closed `source_type` enum: `signed`/`noted`/`guessed`).
- `mimir-recall` — query with source tracing (fixed answer skeleton: conclusion → source chain → risks; "no source" must be stated).
- `mimir-amend` — controlled change: FB-first intake, problem-level (not source-stage) decides write-back target, CHG gates on confirmed content.
- `mimir-forge` — assemble confirmed memory into **self-contained HTML deliverables** (`07_Artifacts/SA_Spec/*.html`, `SD_Spec/*.html`; embedded CSS, no external resources; `--format md` fallback). Deterministic assembly via bundled `build-spec.py` — no LLM stitching. This supersedes the plan document's Markdown deliverable decision.

Shared core under `skills/mimir/`: 5 hard-rule docs (`rules/`), behavior flows + doc-tree structures + frontmatter schemas (`references/`), 13 file templates (`templates/`), and 7 deterministic scripts (`scripts/`: next-id, validate-frontmatter, rebuild-index, rebuild-id-registry, build-spec, cite-as, find-references).

Post-port polish (`/evolve`-style forward-only ratchet, 3/3 blind-judge bar, scratch copies only): all six SKILL.md files adopted validated improvements — `mimir` (routing step-0 scope gate: code requests rejected, mixed intents split; `fix/修` alias qualified), `mimir-listen` (explicit candidate-tagging if-thens + boundary rules for missing dirs / closed-session resume / mixed sessions / validation failure), `mimir-carve` (closed `source_type` enum + adjudication criteria), `mimir-recall` (fixed output skeleton with mandatory source citations), `mimir-amend` (FB-first intake, problem-level write-back routing), `mimir-forge` (error & boundary section: no bypassing build failures, dry-run mismatch stops, no docs-root guessing). `mimir` and `mimir-listen` additionally passed 3/3 held-out blind validation.

Codex variant generated alongside via `codex-skill-transfer` into `codex/plugins/mimir/` (the transfer drops non-standard skill subdirs, so `rules/` and `templates/` were restored by hand — Codex tree matches the Claude tree file-for-file). Both Codex catalogs (Layout A `.agents/plugins/marketplace.json`, Layout B `codex/.agents/plugins/marketplace.json`) now list `mimir`.

No `test-utils` or `analysis-estimation` behavior changed.

## marketplace `common-dev` 1.1.0 — add `analysis-estimation` plugin (analysis-estimation 1.0.0)

New opt-in plugin `analysis-estimation` (分析與評估 / Analysis & Estimation), `defaultEnabled: false`, with five skills ported from a project-local `.claude/skills/`:

- `rfp-requirement-analysis`, `rfp-architecture-design`, `rfp-sa-bdd` — a chained RFP/SOW → requirement analysis → architecture → BDD acceptance-spec pipeline.
- `cold-estimation` — cold-start function inventory + person-day effort estimation.
- `quality-orchestrator` — generic writer→reviewer→fixer checklist loop driving the producers above.

Generalization on port: confirmed the skills carry no project-specific branding/routes/ports/accounts (stacks and domains are explicitly overridable). Softened `rfp-sa-bdd`'s hard `/baransu:execute` references into "downstream TDD execution flow (e.g. `/baransu:execute`)" so the skill is self-contained. Registered the plugin in `.claude-plugin/marketplace.json` and documented it in `README.md`, `CLAUDE.md`, and `AGENTS.md`.

Codex variant generated alongside (mirrors the test-utils port):

- Ported all five skills into `codex/plugins/analysis-estimation/` with `.codex-plugin/plugin.json` via `codex-skill-transfer`. The transfer drops non-standard skill subdirs, so the `rfp-*` skills' `templates/` were restored by hand (Codex tree now matches the Claude tree file-for-file).
- Both Codex catalogs upgraded to a multi-plugin `common-dev` marketplace listing `test-utils` + `analysis-estimation`: root Layout A `.agents/plugins/marketplace.json` (git-URL entrypoint) and self-contained Layout B `codex/.agents/plugins/marketplace.json`. Layout B was previously mis-named `test-utils`; it is now `common-dev`, so the local-install command changes to `analysis-estimation@common-dev` / `test-utils@common-dev` (README updated).

No `test-utils` skill behavior changed.

## marketplace `common-dev` 1.0.2 — Codex marketplace port (test-utils 1.0.2)

Added a generated Codex marketplace variant for the existing `test-utils` plugin:

- Added repo-root Codex Layout A catalog at `.agents/plugins/marketplace.json` for git URL installs.
- Added self-contained Codex Layout B output under `codex/` for local-path installs.
- Ported the three existing skills (`gen-e2e-test`, `gen-e2e-record`, `dev-browser`) into Codex `SKILL.md` format with `.codex-plugin/plugin.json`.
- Documented Claude Code and Codex install flows separately in `README.md`.
- Added `AGENTS.md` with Codex-facing repo conventions.

No skill runtime behavior changed; this release updates distribution packaging and documentation.

## marketplace `common-dev` 1.0.1 — security hardening (test-utils 1.0.1)

Addressed three findings from an automated commit security review:

- **dev-browser `1.1.1` (CRITICAL fix)** — `setup-wsl2-chrome-debug.sh` no longer binds the Chrome DevTools portproxy to `0.0.0.0` / opens the firewall to the whole LAN. CDP is unauthenticated, so that exposed full browser takeover to anyone on the subnet. The listener now binds to the WSL-facing `HOST_IP` only, and the firewall rule is scoped to the WSL private range (`remoteip=172.16.0.0/12 profile=private`). An explicit `--expose-lan` opt-in (with a warning) restores the old behavior for users who genuinely need it. The `setup-wsl2-chrome.md` manual instructions were updated to match.
- **gen-e2e-test `1.2.1` (MEDIUM fix)** — `test-template.mjs` now redacts request/response **bodies** (key-based JSON redaction + JWT/Bearer shape stripping) at capture time, matching the existing header redaction, so tokens no longer land unredacted in on-disk reports.
- **gen-e2e-test `1.2.1` (MEDIUM fix)** — `capture-auth.mjs` writes `auth.json` / `auth.session.json` with `0600` permissions.

Also: README drops the local-checkout install line (remote marketplace install only).

## marketplace `common-dev` 1.0.0 — initial release

First publishable cut of the toolkit: a `common-dev` marketplace exposing one opt-in plugin (`test-utils`), plus repo-level `CLAUDE.md` development conventions, `README`, and `.gitignore`.

### test-utils 1.0.0

Initial release of the optional **test-utils** plugin (`defaultEnabled: false`), ported from an internal project and sanitized into project-agnostic form. Three complementary skills:

- **gen-e2e-test** `1.2.0` — self-contained, double-clickable Playwright test + API-capture report generator.
- **gen-e2e-record** `2.1.0` — Playwright `codegen` recording → test converter (depends on gen-e2e-test).
- **dev-browser** `1.1.0` — fast agent-side browser debugging via the external `dev-browser` CLI.

**Sanitization** — removed all project-specific branding, routes, ports, accounts, and the domain-specific business-card example; rewrote the route reference into a generic template; rewrote bundled-asset paths to `${CLAUDE_PLUGIN_ROOT}`; dropped a dangling reference to an un-ported sibling skill. Engine files (test/report engine, selector inspector, capture-auth) kept byte-for-byte in behavior — only example/config values changed. Verified: zero residual project markers, all engine files pass syntax checks, all JSON valid, the report engine's `PREVIEW=1` path renders.

**Polish (`/evolve`, 5-round forward-only ratchet, 3/3 blind-judge bar)** —
- `dev-browser` → **1.1.0**: adopted one unanimous (3/3) improvement — a login-verification hard-stop after `login.js` (require an observable success signal; on silent login failure, stop and consult `gotchas-login.md` instead of proceeding).
- `gen-e2e-record`, `gen-e2e-test`: no change adopted — no single-variable mutation cleared the strict Pareto bar, confirming both were already well-tuned.
