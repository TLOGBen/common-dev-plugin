# 開發指南

回到 [文件索引](README.md)。Codex 移植規則與驗證流程以 [`AGENTS.md`](../AGENTS.md) 為正式來源；本頁是導覽，兩者不一致時以 `AGENTS.md` 為準。

## 專案結構

```text
common-dev-plugin/
├── .claude-plugin/
│   └── marketplace.json          # Claude marketplace 目錄（source of truth）
├── .agents/plugins/
│   └── marketplace.json          # Codex marketplace（Layout A，git URL 安裝入口）
├── plugins/                      # Claude source
│   ├── common/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── agents/               # luna-max-sidekick, sa-scribe
│   │   └── skills/               # better-prompts, delegate, define-goal, strategic-advance, wait-what, wayfinder, show-me, token-lens（+ grilling/domain-modeling/research/prototype）
│   ├── common-lab/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/               # 16 個 TypeSafe Jev 實驗技能
│   ├── common-mod/
│   │   ├── .claude-plugin/plugin.json
│   │   └── hooks/                # bar / recall / side 等 function hooks（Claude 專屬，無 Codex 版）
│   ├── test-utils/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/               # gen-e2e-test, gen-e2e-record, dev-browser
│   ├── analysis-estimation/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/               # rfp-*, cold-estimation, quality-orchestrator
│   └── linkstart/
│       ├── .claude-plugin/plugin.json
│       └── skills/link-start/    # 單一 public skill；Claude/Codex adapter references 與 exact Runtime assets
├── codex/                        # 手工維護的 Codex 移植
│   ├── .agents/plugins/
│   │   └── marketplace.json      # Codex marketplace（Layout B，自包含佈局）
│   └── plugins/                  # common / common-lab / test-utils / analysis-estimation / linkstart
│       └── common/.codex-agents/ # luna-max-sidekick.toml 等 package-local agent 定義
├── codex-metadata/               # Codex 專屬的 skill UI metadata（openai.yaml）
├── docs/                         # 文件、圖片與 experiments/ 歷史紀錄
├── scripts/                      # 驗證與實驗用腳本（含 validate_linkstart_release.py）
├── tests/                        # 契約測試
├── AGENTS.md                     # Codex 對應結構、移植規則與驗證流程
└── CHANGELOG.md
```

## Claude source 與 Codex 移植

Claude Code 是 source of truth：

- Claude marketplace：`.claude-plugin/marketplace.json`
- plugin：`plugins/<name>/.claude-plugin/plugin.json`
- skills：`plugins/<name>/skills/<skill>/SKILL.md`（自動探索，`plugin.json` 不列 skills／agents 陣列）
- plugin 層 agents：`plugins/<name>/agents/<agent>.md`

Codex 版是 Claude source 的**手工移植**：每個散佈變更都在同一個變更裡手動移植到 `codex/plugins/<name>/`，**不要**用 `codex-skill-transfer` 腳本重新產生 `codex/`。（舊版 README 曾寫「`codex/` 由 `codex-skill-transfer` 從 `plugins/` 生成、勿手改，轉換會丟掉 `templates/` 等非標準子目錄需手動補回」；這個流程已由 `AGENTS.md` 的手工移植規則取代。）

兩版可以不同的地方只有 Codex 需要的部分：frontmatter 欄位、`/plugin:skill` 改成 `$skill`、路徑變數改成執行時解析的目錄、Claude 專屬元件（mod、monitors、`userConfig`、plugin `dependencies`、LSP）不移植。完整清單見 [`AGENTS.md`](../AGENTS.md) 與 [Claude 與 Codex plugin 平台對照](experiments/claude-codex-plugin-parity-20261008.md)。出貨前用 `diff --strip-trailing-cr` 比對兩份副本。

兩份 Codex marketplace catalog（Layout A、Layout B）也是手工維護，見 [安裝與管理](install.md#marketplace-佈局)。

## 驗證

Claude marketplace 結構：

```bash
claude plugin validate .
```

Codex marketplace 改動，至少跑 `AGENTS.md` 列出的檢查：

```bash
python3 -c "import json, pathlib; [json.load(open(f, encoding='utf-8')) for f in pathlib.Path('.').rglob('*.json')]"
python3 -c "import json, pathlib; root=pathlib.Path('.'); assert (root/'.agents/plugins/marketplace.json').is_file(); assert (root/'codex/.agents/plugins/marketplace.json').is_file(); assert (root/'codex/plugins/test-utils/.codex-plugin/plugin.json').is_file(); assert (root/'codex/plugins/analysis-estimation/.codex-plugin/plugin.json').is_file(); assert (root/'codex/plugins/linkstart/.codex-plugin/plugin.json').is_file()"
python3 scripts/validate_linkstart_release.py
```

再用暫存 Codex home 試裝，指令見 [安裝與管理](install.md#用暫存-codex-home-試裝)。

## 貢獻

- **保持 skill 通用**：不寫死專案品牌、路由、port 或帳號；skill 引用自帶檔案用 `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/...`，plugin 層 agent 用 `${CLAUDE_PLUGIN_ROOT}/agents/<agent>.md`。只有 skill 在使用者專案裡建立的路徑（`tests/<name>/`、`.claude/test-template/`）維持專案相對路徑。
- **語言**：`common` 的 Skill 指令用英文；給人看的輸出與產物預設繁體中文。
- **每次散佈變更都要 bump plugin `version`**（Claude Code 與 Codex 都有快取）。
- 改完 Claude source 後，在同一個變更裡手動移植對應的 `codex/` 副本（見上節）。
- 安裝路徑、marketplace 佈局或散佈內容改變時，同步更新 `README.md`、`docs/` 與 `CHANGELOG.md`。
- Commit 遵循 conventional commits（`feat`、`fix`、`refactor`、`docs`、`chore`）。

## 授權

目前仍在內部測試，repo 本身暫不附授權。部分 `common` skill 目錄帶有上游的 `LICENSE`（第三方來源授權，須保留），例如 [show-me 的來源說明](plugins/common.md#show-me-的來源)。
