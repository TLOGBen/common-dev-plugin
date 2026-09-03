---
name: quality-orchestrator
description: 通用「品質編排」產線——吃任一陌生專案 + 指定要產出哪些交付物（rfp-requirement-analysis / rfp-architecture-design
  / rfp-sa-bdd / cold-estimation 之一或多個），先產出可見的 task checklist，再對每個 task 跑 writer →
  reviewer →（未過則 fixer）→ reviewer 的迴圈直到 PASS 才勾完成，最後做跨 task 整合覆蓋檢查。Use whenever the
  user wants to 批次產出 / 編排產線 / 帶審查迴圈地產文件 across a 陌生專案，or says「幫我把這個案子的需求分析+架構+BDD
  都產出來，要有審查把關」「建 checklist 一個個產一個個審」「跑 reviewer 迴圈確保品質」「orchestrate 這幾個 producer」「批次盤點+估算+審查」.
  觸發詞：品質編排, checklist, 審查迴圈, reviewer, 批次產出, 陌生專案產線, orchestrate, writer reviewer
  fixer。繁體中文輸出。
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# 品質編排器（Quality Orchestrator）

這是一個**可複用的編排骨架**：給它任一陌生專案，加上「要產出哪些交付物」，它就建立一張可見的 task 清單，逐 task 跑「產出 → 審查 → 修正 → 再審」的閉環，**只有 reviewer 判 PASS 才把 task 勾掉**，全部完成後再做一次跨 task 的整合覆蓋對帳。

它本身**不寫內容**——內容交給註冊在案的 producer skill（見 `references/producer-registry.md`）。它的價值在於那層**審查迴圈與 checklist 治理**，讓批次產出的品質不靠運氣。

## 核心契約（務必照這個行為執行）

1. **吃輸入**：任一陌生專案來源（RFP / SOW / 需求文件 / 既有需求分析），加上使用者指定要產出哪些 producer——可選 `rfp-requirement-analysis`、`rfp-architecture-design`、`rfp-sa-bdd`、`cold-estimation` 之**一或多個**。若使用者沒指定，依 `references/producer-registry.md` 的鏈式關係建議順序並確認。

2. **先產出 task checklist（可見）**：依**功能 / 章節 / 模組**把工作拆成多個 task，用 **create a `task-map.md` record**（或環境的 track steps internally）建立一張使用者看得見的清單。拆法見下「如何拆 task」。每個 task 要標：所屬 producer、產出目標檔、來源依據。

3. **逐 task 跑審查迴圈**：對**每一個 task**——
   - **writer subagent** 依該 producer 的 SKILL.md + template 產出；
   - **reviewer subagent** 對照來源 + 該 producer 的格式/覆蓋標準審查（判準見 `references/review-loop.md`）；
   - 若未 PASS → **fixer subagent** 依 reviewer 的缺失清單修 → **再 reviewer**；
   - 迴圈**直到 reviewer 判 PASS 才把該 task 勾完成**。設 **max 3 輪**，逾次仍未過則把 task 標為「需人工」並繼續其他 task，不卡死整條產線。

4. **跨 task 整合覆蓋檢查（含修補回路）**：全 checklist 完成後，做一次跨 task 對帳——回到來源確認無缺漏（每個模組/章節都有對應產出、功能數對得上、共用件沒被各 task 重做、命名/編號跨 task 不衝突）。
   - **若整合檢查發現跨 task 衝突**（命名/編號衝突，或共用件被多個 task 各自重做）→ **把受衝突影響的那些 task 由 PASS 退回「需修」狀態**，重新進入該 task 的 **fixer → reviewer** 審查迴圈做定點修正，**同樣受 max 3 輪與「reviewer 判 PASS 才勾完成」閘約束**；全部受影響 task 重新 PASS 後**重跑整合檢查**確認衝突已消。這是回邊，不是只在報告中記載。
   - **收斂紀律（不得回歸效能）**：修補必須**重用既有 reviewer 的 PASS 判準作為唯一收斂閘**，不得另開未經審查的旁路修正；且**只重審受衝突影響的 task**，不重跑全 checklist、不重審無關 task。
   - 整合檢查最終（衝突已清或退回次數逾 max）產出一份整合報告，記載覆蓋對照、已修補項與任何仍需人工項。

5. **並行紀律**：**task 之間可並行**（不同模組的 writer 同時跑）；**單一 task 內 writer → reviewer → fixer 必須串行**（審查要看到完整產出，修正要看到審查結論）。派 task 前，把跨 task 的共同約定（命名慣例、共用 API、REQ 前綴、包別定義）先定稿並一字不差交給每個 writer，避免並行漂移。

## 如何拆 task

拆 task 的顆粒度決定並行度與審查精度。原則：**一個 task = 一個可獨立審查的交付單位**。

| Producer | 一個 task 通常是 | checklist 來源 |
|---|---|---|
| rfp-requirement-analysis | 一個模組的「功能 API 分析」檔 | RFP 模組清單 |
| rfp-architecture-design | 一個架構檔（00 總覽 / 01 前端 / 02 後端 / 03 規範 / 04 ER） | 五檔骨架 |
| rfp-sa-bdd | 一個模組的 BDD 檔 | 第一段功能清單的模組數 |
| cold-estimation | 一個 chunk 的盤點，或整份估算當單一複合 task | SOW 章節 / 功能域 |

先在主流程完成**全域約定的奠基 task**（如需求分析的命名慣例與共用 API、架構的技術棧與總覽、BDD 的 REQ 前綴對照、估算的包別與費率），再 fan-out 其餘 task。奠基 task 也走審查迴圈，但它必須**最先且單獨**完成，因為其他 task 都依賴它。

## 為什麼要這層編排

直接叫一個 producer skill 跑完整個專案，會遇到三個問題：模組多時注意力稀釋、沒有獨立第三方檢查（自己產自己過）、批次跑完才發現某幾個模組格式飄掉但已難回溯。

這個 skill 把產出與審查**拆成獨立 subagent 角色**（writer 不評自己、reviewer 只審不寫、fixer 只依清單修），並用**可見 checklist** 讓每個 task 的狀態（待產 / 審查中 / 需修 / PASS / 需人工）一目了然。這是用工程化的閉環換取批次品質的穩定，而不是靠單次運氣。

## 工作流程

1. **盤點與確認**：確認來源檔、要跑哪些 producer、輸出位置。讀 `references/producer-registry.md` 取得各 producer 的輸入/輸出/格式標準。多 producer 時依鏈式關係排序（需求分析 → 架構 / BDD；估算可獨立或並行）。
2. **奠基**：跑奠基 task（全域約定），審查 PASS 後鎖定約定。
3. **建 checklist**：依模組/章節用 create a `task-map.md` record 建可見清單，標註每 task 的 producer / 目標檔 / 來源。
4. **fan-out + 審查迴圈**：並行派 task；每 task 內走 writer → reviewer →（fixer → reviewer）≤3 輪，PASS 才勾完成，逾次標需人工。迴圈細節見 `references/review-loop.md`。
5. **整合覆蓋檢查（含修補回路）**：全部回來後做跨 task 對帳。**若發現跨 task 衝突（命名/編號衝突 或 共用件被各 task 重做）→ 把受影響的 task 由 PASS 退回「需修」，重新進入該 task 的 fixer → reviewer 審查迴圈做定點修正（同受 max 3 輪與 PASS 閘約束、以既有 reviewer PASS 判準為唯一收斂閘、只重審受影響 task），修正後重跑整合檢查**，而非僅在報告中記載。衝突清乾淨（或退回逾次）後產整合報告（覆蓋對照表、共用件去重確認、命名/編號衝突修補紀錄、需人工清單）。
6. **交付**：回報 checklist 最終狀態 + 整合報告 + 任何需人工項。

## 可攜性

非 Claude Code 用戶（無 subagent）如何用，以及退化為單模型分段自我審查的做法，見 `references/portability.md`。核心：把 writer / reviewer / fixer 當**三段獨立 prompt 串接**，無 subagent 環境則由單一模型換角色分段執行、靠分段紀律維持獨立性。

## 參考檔

- `references/producer-registry.md` — 四個 producer skill 的輸入/輸出/格式標準/覆蓋檢查方式。
- `references/review-loop.md` — reviewer 評分準則、PASS 定義、fixer 契約、max 輪數與逾次處置。
- `references/portability.md` — 非 Claude Code / 無 subagent 環境的退化執行法。
