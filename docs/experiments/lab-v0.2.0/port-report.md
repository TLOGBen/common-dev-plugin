# Lab 0.2.0 Codex port report

三包均經既有轉換器產生；source 未在轉換中改動，package-local agents 完整可達。原始報告及 receipt 保留於各 export 目錄。以下呈現原報告本文；最末彙整每項 dropped／manual-review 處置。

## common-lab

# common-lab transfer receipt

{
  "manifest_mapped": [
    "加入 `skills: \"./skills/\"` 指標 (Codex manifest-driven)",
    "加入 `interface` 預設 (display_name + short_description)"
  ],
  "manifest_dropped": [],
  "manifest_manual": [],
  "agent_definitions": 2,
  "rules_copied": 0,
  "skill_count": 10,
  "plugin_name": "common-lab",
  "source_components": [
    ".claude-plugin",
    "agents",
    "skills"
  ],
  "unhandled_components": [],
  "content_closure_verified": true,
  "aux_dirs_copied": [],
  "aux_manual": [],
  "marketplace_written": true
}

## Codex Transfer Report — lab-better-prompts

- 來源: `/home/vakarve/projects/common-dev-plugin/plugins/common-lab/skills/lab-better-prompts`
- 輸出: `/tmp/common-lab-v020-export-0800/plugins/common-lab/skills/lab-better-prompts`

### 完整保留 (lossless)
- `name`
- `description`

### 翻譯處理 (mapped)
- 加入預設 `compatibility`
- 加入預設 `metadata.version: 0.1.0-codex`


## baransu-lab

# baransu-lab transfer receipt

{
  "manifest_mapped": [
    "加入 `skills: \"./skills/\"` 指標 (Codex manifest-driven)",
    "加入 `interface` 預設 (display_name + short_description)"
  ],
  "manifest_dropped": [],
  "manifest_manual": [],
  "agent_definitions": 1,
  "rules_copied": 0,
  "skill_count": 4,
  "plugin_name": "baransu-lab",
  "source_components": [
    ".claude-plugin",
    "agents",
    "skills"
  ],
  "unhandled_components": [],
  "content_closure_verified": true,
  "aux_dirs_copied": [],
  "aux_manual": [],
  "marketplace_written": true
}

## Codex Transfer Report — lab-contract

- 來源: `/home/vakarve/projects/common-dev-plugin/plugins/baransu-lab/skills/lab-contract`
- 輸出: `/tmp/baransu-lab-v020-export-0800/plugins/baransu-lab/skills/lab-contract`

### 完整保留 (lossless)
- `name`
- `description`

### 翻譯處理 (mapped)
- 加入預設 `compatibility`
- 加入預設 `metadata.version: 0.1.0-codex`

### ⚠️ 需人工檢視 (manual review)
- `SKILL.md` 含 Claude-only token（CLAUDE_PLUGIN_ROOT）；skill 本體不自動改寫，請依實際 Codex package 路徑人工確認


## estimate-lab

# estimate-lab transfer receipt

{
  "manifest_mapped": [
    "加入 `skills: \"./skills/\"` 指標 (Codex manifest-driven)",
    "加入 `interface` 預設 (display_name + short_description)"
  ],
  "manifest_dropped": [],
  "manifest_manual": [],
  "agent_definitions": 1,
  "rules_copied": 0,
  "skill_count": 1,
  "plugin_name": "estimate-lab",
  "source_components": [
    ".claude-plugin",
    "agents",
    "skills"
  ],
  "unhandled_components": [],
  "content_closure_verified": true,
  "aux_dirs_copied": [],
  "aux_manual": [],
  "marketplace_written": true
}

## Codex Transfer Report — lab-estimate

- 來源: `/home/vakarve/projects/common-dev-plugin/plugins/estimate-lab/skills/lab-estimate`
- 輸出: `/tmp/estimate-lab-v020-export-0800/plugins/estimate-lab/skills/lab-estimate`

### 完整保留 (lossless)
- `name`
- `description`
- `metadata`

### 翻譯處理 (mapped)
- 加入預設 `compatibility`
- 複製 skill-root 零散檔案：requirements.lock

### 動態注入改寫 (rewrites)
- 注入 bundled agent resolver（定義缺失即 `AGENT_DEFINITION_MISSING`，禁止臨場杜撰）

### 已捨棄 (dropped)
- skill-root 子目錄 `tests/` 未複製（非 scripts/references/assets/evals/agents 標準目錄）

### ⚠️ 需人工檢視 (manual review)
- `SKILL.md` 含 Claude-only token（CLAUDE_PLUGIN_ROOT）；skill 本體不自動改寫，請依實際 Codex package 路徑人工確認
- `references/case-state.md` 含 Claude-only token（CLAUDE_PLUGIN_ROOT）；引用文件不自動改寫，請人工確認語境後處理
- `references/discovery-guide.md` 含 Claude-only token（CLAUDE_PLUGIN_ROOT）；引用文件不自動改寫，請人工確認語境後處理
- `references/estimation-guide.md` 含 Claude-only token（CLAUDE_PLUGIN_ROOT）；引用文件不自動改寫，請人工確認語境後處理


### Next-port follow-ups

- common-lab / lab-delegate: `SKILL.md` 含 Claude-only token（CLAUDE_PLUGIN_ROOT）；skill 本體不自動改寫，請依實際 Codex package 路徑人工確認 — `refresh-mapping`; verified LAB_SKILL_DIR adapter
- common-lab / lab-strategic-advance: `SKILL.md` 含 Claude-only token（CLAUDE_PLUGIN_ROOT）；skill 本體不自動改寫，請依實際 Codex package 路徑人工確認 — `refresh-mapping`; verified LAB_SKILL_DIR adapter
- common-lab / lab-strategic-advance: `references/campaign.md` 含 Claude-only token（CLAUDE_PLUGIN_ROOT）；引用文件不自動改寫，請人工確認語境後處理 — `refresh-mapping`; verified LAB_SKILL_DIR adapter
- common-lab / lab-strategic-advance: `references/long-run-control.md` 含 Claude-only token（CLAUDE_PLUGIN_ROOT）；引用文件不自動改寫，請人工確認語境後處理 — `refresh-mapping`; verified LAB_SKILL_DIR adapter
- common-lab / lab-wayfinder: `SKILL.md` 含 Claude-only token（CLAUDE_PLUGIN_ROOT）；skill 本體不自動改寫，請依實際 Codex package 路徑人工確認 — `refresh-mapping`; verified LAB_SKILL_DIR adapter
- common-lab / lab-wayfinder: `references/map-format.md` 含 Claude-only token（CLAUDE_PLUGIN_ROOT）；引用文件不自動改寫，請人工確認語境後處理 — `refresh-mapping`; verified LAB_SKILL_DIR adapter
- baransu-lab / lab-contract: `SKILL.md` 含 Claude-only token（CLAUDE_PLUGIN_ROOT）；skill 本體不自動改寫，請依實際 Codex package 路徑人工確認 — `refresh-mapping`; verified LAB_SKILL_DIR adapter
- baransu-lab / lab-review: `SKILL.md` 含 Claude-only token（CLAUDE_PLUGIN_ROOT）；skill 本體不自動改寫，請依實際 Codex package 路徑人工確認 — `refresh-mapping`; verified LAB_SKILL_DIR adapter
- baransu-lab / lab-seal: `SKILL.md` 含 Claude-only token（CLAUDE_PLUGIN_ROOT）；skill 本體不自動改寫，請依實際 Codex package 路徑人工確認 — `refresh-mapping`; verified LAB_SKILL_DIR adapter
- baransu-lab / lab-think: `SKILL.md` 含 Claude-only token（CLAUDE_PLUGIN_ROOT）；skill 本體不自動改寫，請依實際 Codex package 路徑人工確認 — `refresh-mapping`; verified LAB_SKILL_DIR adapter
- estimate-lab / lab-estimate: skill-root 子目錄 `tests/` 未複製（非 scripts/references/assets/evals/agents 標準目錄） — `refresh-mapping`; tests copied before unchanged content-closure guard; bytes verified
- estimate-lab / lab-estimate: `SKILL.md` 含 Claude-only token（CLAUDE_PLUGIN_ROOT）；skill 本體不自動改寫，請依實際 Codex package 路徑人工確認 — `refresh-mapping`; verified LAB_SKILL_DIR adapter
- estimate-lab / lab-estimate: `references/case-state.md` 含 Claude-only token（CLAUDE_PLUGIN_ROOT）；引用文件不自動改寫，請人工確認語境後處理 — `refresh-mapping`; verified LAB_SKILL_DIR adapter
- estimate-lab / lab-estimate: `references/discovery-guide.md` 含 Claude-only token（CLAUDE_PLUGIN_ROOT）；引用文件不自動改寫，請人工確認語境後處理 — `refresh-mapping`; verified LAB_SKILL_DIR adapter
- estimate-lab / lab-estimate: `references/estimation-guide.md` 含 Claude-only token（CLAUDE_PLUGIN_ROOT）；引用文件不自動改寫，請人工確認語境後處理 — `refresh-mapping`; verified LAB_SKILL_DIR adapter
