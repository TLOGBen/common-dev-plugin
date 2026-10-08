# Claude Code ↔ Codex 擴充機制對照（2026-10-08）

用途：手動維護同一組 plugin 的 Claude 版（`plugins/*`）與 Codex 版（`codex/plugins/*`），以及更新 baransu `codex-skill-transfer` 的對照表與檢查清單。

## 基準與標記

- 比對基準：Claude Code `2.1.293`、Codex CLI `codex-cli 0.161.0`（`claude --version`、`codex --version`，2026-10-08 本機）；Codex 原始碼取 tag `rust-v0.161.0`（2026-10-07 發布）；baransu `origin/main` = `10e7bfe`（2026-10-07），`codex-skill-transfer` frontmatter `metadata.version: "0.18.0"`。
- 標記：
  - 【官方】官方文件、官方 changelog、`openai/codex` GitHub 原始碼／release notes。
  - 【本機】本機 CLI 輸出、本機設定或快取、本 repo 與 baransu repo 的檔案。
  - 【推論】由上述證據推得，官方沒有明寫。
  - 官方沒寫的地方標「官方未公布」。
- 取材方式：載入 `/baransu:read` skill，照它的 save mode 流程（local-first 抓取 → markitdown 轉換 → `raw/` 保存原檔 → `material/<slug>/index.md` 寫 frontmatter → 更新 `.claude/read/index.md`），用 scratchpad 裡的輔助腳本批次執行。有兩點偏離：(1) 抓的是官方提供的 Markdown 版（`.md`），不是 HTML；(2) 沒有下載頁面圖片。沒有使用 WebFetch。Codex 原始碼以 sparse clone 到 session scratchpad 閱讀，沒有存進 `.claude/read/`，引用時寫 GitHub 路徑。
- 文件網域變動【官方】：`developers.openai.com/codex/*` 現在轉址到 `learn.chatgpt.com/docs/*`（`https://developers.openai.com/codex/changelog` → `https://learn.chatgpt.com/docs/changelog`；`developers.openai.com/codex/llms.txt` 列出的頁面都在 learn.chatgpt.com）。plugin 打包文件留在 `developers.openai.com/plugins/*`。下文「Codex 文件」指這兩個網域。

---

## 摘要：最重要的 10 個移植差異

1. **Codex skill 內文沒有任何路徑變數。** Claude 會在 skill、command、agent 內文中直接替換 `${CLAUDE_PLUGIN_ROOT}`、`${CLAUDE_SKILL_DIR}`、`${CLAUDE_PLUGIN_DATA}` 等變數【官方】(C1, C2)。Codex 的 `PLUGIN_ROOT`／`PLUGIN_DATA`，以及相容用的 `CLAUDE_PLUGIN_ROOT`／`CLAUDE_PLUGIN_DATA`，只會設給 plugin hook command 的環境【官方】(O6, O13；原始碼 `codex-rs/hooks/src/engine/discovery.rs`)。Codex 的 skill 系統提示要求「`SKILL.md` 裡的相對路徑以該 `SKILL.md` 所在目錄解析」【官方】(G-catalog)。所以 Codex 版要改寫成相對路徑。本 repo 的 `codex/plugins/test-utils`、`codex/plugins/linkstart` 內文仍有 `${CLAUDE_PLUGIN_ROOT}`【本機】。
2. **Codex 的 `SKILL.md` frontmatter 只讀 `name`、`description`、`metadata.short-description`**，其他欄位一律靜默忽略【官方】(G-parser)。`disable-model-invocation`、`when_to_use`、`context: fork`、`model`、`effort`、`allowed-tools`、`arguments` 在 Codex 都沒有作用。唯一有對應的是在 `agents/openai.yaml` 寫 `policy.allow_implicit_invocation: false`【官方】(O1)。
3. **呼叫與命名空間不同。** Claude 的 plugin skill 叫 `/plugin:skill`【官方】(C1)。Codex 用 `/skills` 或 `$` 提及【官方】(O1)，plugin skill 的名稱是 `<plugin>:<skill>`，提及字元允許 `:`【官方】(G-mentions)，所以寫成 `$plugin:skill`。Codex 沒有 `$ARGUMENTS` 這類引數替換，也沒有 `` !`cmd` `` 動態注入【推論，parser 與 catalog 都沒有這類處理】。
4. **Plugin 內附的 agent。** Claude 會自動註冊 `agents/*.md`（命名為 `plugin:agent`），但 plugin agent 的 `hooks`、`mcpServers`、`permissionMode` 會被忽略【官方】(C10)。Codex 0.161 的 plugin manifest 沒有 agents 欄位；custom agent 只從設定層的 `agents/` 目錄（`~/.codex/agents/`、`.codex/agents/`）與 `[agents.<name>] config_file` 載入【官方】(O5, O7；G-roles)。plugin 裡的 TOML 目前**仍不會自動註冊**。OpenAI 官方的 Claude 移植指引是「把 agent 程序併入 skill」【官方】(O15)。
5. **Manifest 的位置與優先序。** Codex 依序找：根目錄 `plugin.json`（`$schema` 為 `https://agent-plugins.org/schemas/...`）→ `.codex-plugin/plugin.json` → `.claude-plugin/plugin.json` → `.cursor-plugin/plugin.json`【官方】(O13；G-manifest)。官方建議新套件用可攜式根 `plugin.json`，OpenAI 專屬設定放在 `extensions."com.openai"`；這個物件會**整個取代** `.codex-plugin` overlay，兩者不合併【官方】(O13)。本 repo 的 Codex 版用 `.codex-plugin/plugin.json`，這仍受支援，屬相容路徑【本機】【官方】。
6. **Marketplace。** Codex 依序讀 `.agents/plugins/marketplace.json` → `.agents/plugins/api_marketplace.json` → `.claude-plugin/marketplace.json` → `.cursor-plugin/marketplace.json`，取第一個存在的檔案【官方】(G-marketplace)。來源類型只有 `local`／`url`／`git-subdir`／`npm`，沒有 Claude 的 `github`、`archive`、`command`【官方】(O13, C3)。每個 entry 必須帶 `policy.installation`、`policy.authentication`、`category`【官方】(O13)。Codex 沒有 `defaultEnabled`；最接近的是 `policy.installation: "INSTALLED_BY_DEFAULT"`，啟用狀態寫在 `config.toml` 的 `[plugins."name@market"] enabled`【官方】(O13, O7)。
7. **版本與快取。** Claude 版本的優先序是 manifest `version` → marketplace entry `version` → 來源 commit SHA；只要 manifest 釘了版本，不改字串就不會更新【官方】(C7)。Codex 的快取目錄是 `~/.codex/plugins/cache/<market>/<plugin>/<version>/`，`<version>` 取自 manifest，缺了就用預設值（文件說 local plugin 是 `local`）【官方】(O13；G-store)。本機實測，git marketplace 安裝的目錄名就是 manifest 版本（例如 `common-dev/analysis-estimation/1.19.0`）【本機】。兩邊都要靠 bump version 才能可靠更新【推論】。
8. **Hooks 能力差距大。** Codex 有 12 個事件：`SessionStart`、`SessionEnd`、`SubagentStart`、`SubagentStop`、`PreToolUse`、`PermissionRequest`、`PostToolUse`、`PreCompact`、`PostCompact`、`UserPromptSubmit`、`Stop`、`Interrupt`【官方】(O6)。Claude 有 30 多個【官方】(C11)。Codex 只執行 `command` 與 `mcp_tool` 兩種 handler，`prompt`／`agent` 會解析但略過【官方】(O6)。非 managed 的 hook（包括 plugin hook）要先在 `/hooks` 審核並信任才會跑，信任綁定的是定義的雜湊值【官方】(O6)。
9. **Mods 只有 Claude 有。** Claude 的 mod 是 in-process 的 JS／TS hook 模組，可畫 pane、band、狀態列、toast，可改寫 tool call，存檔就熱重載【官方】(C14, C15)，v2.1.287（2026-10-01）正式推出【官方】(C17)。Codex 沒有對等的 in-process UI 擴充：`tui.status_line` 只能從固定 ID 清單挑選【官方】(O7, O9)；OpenAI 的 Plugin Extensions 是 MCP App UI，掛在 ChatGPT 的側欄、面板、composer【官方】(O18)。另一個坑：mod 的 `hooks/hooks.json` 是 `{"modules": [...]}`，而 Codex 預設也會讀 `hooks/hooks.json`。所以 mod plugin 不能原樣放進 Codex 版【推論】。
10. **工具對照。** `AskUserQuestion` → `request_user_input`（每次 1–3 題，依 mode 開放）【官方】(G-rui)。`Agent` → `spawn_agent`（`agent_type`、`fork_context`／`fork_turns`、`model`、`reasoning_effort`）【官方】(G-spawn)。`TaskCreate`／`TodoWrite` → `update_plan`【官方】(G-tools)。`Monitor`、`userConfig`、`monitors`、`lspServers`、plugin `dependencies` 在 Codex 都沒有對應【官方】(O15)。

---

## 1. Skills

| 項目 | Claude Code | Codex | 移植做法 |
|---|---|---|---|
| 檔案結構 | `<skill>/SKILL.md` 加任意支援檔；文件舉例 `references/`、`scripts/`、`templates/` 等，沒有固定白名單【官方】(C1 §Add supporting files) | `SKILL.md` 加選用的 `scripts/`、`references/`、`assets/`、`agents/openai.yaml`【官方】(O1) | 兩邊都能放任意子目錄；Codex 文件只「列舉」四個，沒說其他目錄會被拒【推論】。`templates/` 這類目錄在 Codex 版照樣保留，SKILL.md 用相對路徑指過去即可 |
| 必填欄位 | 全部選填，建議填 `description`；沒寫 `name` 就用目錄名【官方】(C1) | parser：`name` 沒寫就用預設名稱、`description` 必填且不可空、`name` ≤64 字元【官方】(G-parser)；文件寫「`SKILL.md` must include `name` and `description`」【官方】(O1) | 兩邊都寫 `name` 和 `description`，`name` 跟目錄名一致 |
| frontmatter 欄位 | `name`、`description`、`when_to_use`、`argument-hint`、`arguments`、`disable-model-invocation`、`user-invocable`、`allowed-tools`、`disallowed-tools`、`model`、`effort`、`context`、`agent`、`background`、`hooks`、`paths`、`shell`、`metadata`、`license`、`compatibility`【官方】(C1 Frontmatter reference)。不認得的欄位直接忽略，不報錯【官方】(C1) | 只讀 `name`、`description`、`metadata.short-description`；YAML 解析失敗時會先嘗試修復單行值【官方】(G-parser) | Codex 版只留 `name`、`description`，需要時加 `metadata`。把 `when_to_use` 併進 `description`。其他欄位刪掉，或改寫成內文指示 |
| 長度限制 | `description` 加 `when_to_use` 在清單中截在 1,536 字元【官方】(C1)；agent／skill 的 `name` 最多 256 字元（v2.1.292）【官方】(C17)；`compatibility` ≤500 字元【官方】(C1) | `name` ≤64；`description` 在 parser 沒有上限【官方】(G-parser)。初始 skill 清單預算為 context 的 2%，未知時為 8,000 字元，超出會先縮短 description【官方】(O1)；`skills.max_context_tokens` 上限 10,000 token【官方】(O7)。`agents/openai.yaml` 的 `short_description`、`default_prompt` 上限 1024【官方】(G-interface) | 共用描述時以 Codex 的 `name` ≤64 為準。description 把觸發詞放最前面，因為兩邊都會截斷 |
| 觸發方式 | 模型依 description 自動呼叫，或使用者打 `/name`。`disable-model-invocation: true` 只能手動；`user-invocable: false` 只能由模型呼叫【官方】(C1) | 顯式：`/skills` 或 `$name`；隱式：依 `description` 比對【官方】(O1)。`allow_implicit_invocation: false` 時只能顯式【官方】(O1) | `disable-model-invocation` 改寫成 `agents/openai.yaml` 的 policy。`user-invocable: false` 在 Codex 沒有對應，在內文註明即可 |
| 命名空間 | plugin skill 是 `/plugin-name:skill-name`；名稱沒被占用時也可用裸名呼叫【官方】(C1) | plugin skill 名稱為 `<plugin_namespace>:<name>`【官方】(G-namespace)；提及字元允許 `:`【官方】(G-mentions) | 內文的 `/plugin:skill` 改成 `$plugin:skill`；同 plugin 內的裸 `/skill` 也要改成 `$plugin:skill` |
| 引數 | `$ARGUMENTS`、`$ARGUMENTS[N]`、`$N`、`$name`【官方】(C1) | 官方未公布任何引數替換機制 | 改寫成自然語言，例如「使用者提供的第一個值」 |
| 動態注入 | `` !`cmd` ``、` ```! ` 區塊在送給模型前先執行【官方】(C1) | 官方未公布對應機制 | 改成「先執行下列指令並讀輸出」 |
| skill 可用的路徑變數 | `${CLAUDE_SKILL_DIR}`、`${CLAUDE_PLUGIN_ROOT}`、`${CLAUDE_PLUGIN_DATA}`、`${CLAUDE_PROJECT_DIR}`、`${CLAUDE_SESSION_ID}`、`${CLAUDE_EFFORT}` 在內文直接替換；Bash 環境裡**沒有**這些變數【官方】(C1, C2 §Where each variable resolves) | 內文沒有任何變數；相對路徑以 `SKILL.md` 所在目錄解析【官方】(G-catalog) | 改成相對路徑（`scripts/x.py`、`../other-skill/...`）。執行腳本需要絕對路徑時，先叫模型解析 `SKILL.md` 的絕對位置，例如本 repo 的 `DELEGATE_DIR` 做法 |
| 每個 skill 的額外 metadata | 無獨立檔，全在 frontmatter | `agents/openai.yaml`：`interface.{display_name, short_description, icon_small, icon_large, brand_color, default_prompt}`、`policy.allow_implicit_invocation`、`dependencies.tools[]`（MCP）【官方】(O1, G-interface)；原始碼另有 `policy.products`，但目前只解析、不強制【官方】(G-model) | 只在 Codex 版放 `agents/openai.yaml`。Claude 版不要建 `agents/` 子目錄，以免和 plugin 的 `agents/` 混淆；本 repo 用 `codex-metadata/` 存放 |
| 內附 hook | `hooks` 欄位：skill 被呼叫後整個 session 有效【官方】(C1, C11) | 無 | 改到 plugin 層的 `hooks/hooks.json`，或刪除 |
| fork 子代理 | `context: fork` 加 `agent`、`background`【官方】(C1) | skill 沒有 fork 欄位；只能在內文叫模型 `spawn_agent`【官方】(O5) | 內文明寫「spawn 幾個、帶什麼輸入、是否等待、回傳什麼」 |
| 熱更新 | 監看 skill 目錄，`SKILL.md` 改了當場生效【官方】(C1) | 自動偵測 skill 變更，沒出現就重啟【官方】(O1) | — |
| 停用單一 skill | `skillOverrides` 設定【官方】(C1) | `[[skills.config]] path=… enabled=false`【官方】(O1, O7) | — |
| 舊式 commands | `commands/*.md` 仍支援，但建議改用 skills【官方】(C2) | custom prompts 已棄用，請用 skills【官方】(O10)；legacy manifest 的 `commands` 會被自動轉成 skill，但含 `$ARGUMENTS` 或 `{{…}}` 的會略過【官方】(G-cmdmig) | Codex 版一律改寫成 skill |

## 2. Plugins

| 項目 | Claude Code | Codex | 移植做法 |
|---|---|---|---|
| manifest 位置 | `.claude-plugin/plugin.json`（選填）【官方】(C2) | 根 `plugin.json`（Agent Plugins schema）優先，其次 `.codex-plugin/plugin.json`、`.claude-plugin/plugin.json`、`.cursor-plugin/plugin.json`【官方】(O13；G-manifest) | 新寫用根 `plugin.json` 加 `extensions."com.openai"`。沿用 `.codex-plugin/` 也能用，但兩者不要並存同一份設定 |
| 欄位 | `$schema`、`name`（唯一必填）、`displayName`、`version`、`description`、`author`、`homepage`、`repository`、`license`、`keywords`、`metadata`、`icon`、`documentationUrl`、`supportUrl`、`privacyPolicyUrl`、`termsOfServiceUrl`、`defaultEnabled`、`dependencies`、`settings`、`userConfig`、`types`、`channels`、`skills`、`commands`、`agents`、`hooks`、`mcpServers`、`lspServers`、`outputStyles`、`workflows`、`experimental.{themes,monitors,evals}`【官方】(C2 §Fields) | 可攜式：`$schema`、`name`、`version`、`description`、`author`、`homepage`、`repository`、`license`、`keywords`，加 `extensions."com.openai".{apps, hooks, interface{…}, onboardingSkill}`【官方】(O13)。legacy 的 raw manifest 讀 `name`、`version`、`description`、`keywords`、`skills`、`mcpServers`、`apps`、`hooks`、`interface`、`extensions`、`commands`【官方】(G-manifest)。`interface` 欄位：`displayName`、`shortDescription`、`longDescription`、`developerName`、`category`、`capabilities`、`websiteURL`、`privacyPolicyURL`、`termsOfServiceURL`、`defaultPrompt`（≤3 則，每則 ≤128 字元）、`brandColor`、`composerIcon`、`logo`、`logoDark`、`screenshots`【官方】(G-manifest) | 兩份 manifest 各自手寫。`displayName` 在 Codex 放在 `interface.displayName` |
| 元件自動探索 | `skills/`、`commands/`、`agents/`、`hooks/hooks.json`、`.mcp.json`、`.lsp.json`、`output-styles/`、`workflows/`、`themes/`、`monitors/monitors.json`、`bin/`、`settings.json`【官方】(C2 §Standard layout) | 可攜式：根目錄的 `skills/`、`mcp.json`（每個 server 要宣告 `type`）；hook 預設讀 `hooks/hooks.json`，manifest 有 `hooks` 時改用 manifest 的設定【官方】(O13, O6) | MCP：Codex 可攜式用 `mcp.json`，不是 `.mcp.json`，而且要加 transport `type`【官方】(O13)。LSP、output styles、themes、monitors、workflows、`bin/` 在 Codex 都沒有對應【官方】(O15) |
| 內附 agent | `agents/*.md` 自動載入，名稱為 `plugin:agent`；`hooks`、`mcpServers`、`permissionMode` 會被忽略【官方】(C2, C10)。frontmatter 欄位：`name`、`description`、`tools`、`disallowedTools`、`model`、`permissionMode`、`maxTurns`、`skills`、`mcpServers`、`hooks`、`memory`、`background`、`omitClaudeMd`、`effort`、`isolation`、`color`、`initialPrompt`、`experimental`【官方】(C10) | **plugin 不會註冊 agent**（manifest 沒有 agents 欄位，role loader 只掃設定層）【官方】(G-manifest, G-roles)。custom agent TOML 必填 `name`、`description`、`developer_instructions`，其他可放任何 `config.toml` 鍵【官方】(O5)。另外可以在 `config.toml` 用 `[agents.<name>] description` 加 `config_file` 指向任意 TOML【官方】(O7, G-roles) | 選項 A（OpenAI 建議）：把 agent 程序併進 skill【官方】(O15)。選項 B（本 repo 現況）：package 內放 TOML，consuming skill 在執行時讀檔並內嵌到 `spawn_agent` 的 message。選項 C：請使用者在自己的 `config.toml` 加 `[agents.x] config_file=<快取路徑>`。缺點是快取路徑跟著版本變動【推論】 |
| `defaultEnabled` | 預設 `true`；marketplace entry 的值優先【官方】(C2, C3) | 無此欄位；用 marketplace 的 `policy.installation: INSTALLED_BY_DEFAULT`【官方】(O13, G-marketplace) | Codex 版若要預設安裝就改 policy；否則用 `AVAILABLE` |
| `userConfig` | 啟用時提示使用者填值，以 `${user_config.KEY}` 引用，也會變成環境變數 `CLAUDE_PLUGIN_OPTION_<KEY>`【官方】(C2) | 不支援，也不展開 `${user_config.*}`【官方】(O15) | 依 O15 的對照表：每個任務都可能不同的值改成 skill 輸入；本機設定改用環境變數或設定檔，缺值時給出可操作的錯誤訊息 |
| plugin 相依 | `dependencies`，支援 semver 範圍（例如 `^1.2`），用 git tag `{name}--v{version}` 解析【官方】(C6) | 無；O15 要求移除 `dependencies`【官方】 | Codex 版在 README 或 skill 內文寫明需要哪些 plugin |
| 版本與快取 | 有釘版本就停在該版；沒釘則用 commit SHA。快取在 `~/.claude/plugins/cache/<mkt>/<plugin>/<version>/`；舊版在 14 天後清除；從本機路徑加入的 marketplace 會就地載入，不需 bump【官方】(C7) | 快取在 `~/.codex/plugins/cache/<mkt>/<plugin>/<version>/`，local plugin 的 `<version>` 是 `local`；安裝新版時刪舊版目錄【官方】(O13, G-store)。外部升級或回滾後，既有 session 會刷新 skill 與 hook（0.154.0）【官方】(R-0.154) | 每次發布兩邊的 `version` 都要 bump。Codex 的 `version` 是快取目錄名稱的一段，版本字串用單純的 semver 比較保險。`+` 字元是否合法：官方未公布 |
| 資料目錄 | `${CLAUDE_PLUGIN_DATA}`（`~/.claude/plugins/data/<id>/`）【官方】(C2) | hook 才拿得到 `PLUGIN_DATA`【官方】(O13) | skill 需要持久資料時，在 Codex 版自訂路徑，例如 `~/.codex/...` 或專案內 |
| plugin 名稱 | kebab-case；`name` 也是命名空間【官方】(C2) | kebab-case；`name` 也是元件命名空間【官方】(O13) | 兩邊用同一個 `name` |

## 3. Marketplace

| 項目 | Claude Code | Codex | 移植做法 |
|---|---|---|---|
| 位置 | `<root>/.claude-plugin/marketplace.json`【官方】(C3) | `.agents/plugins/marketplace.json` > `.agents/plugins/api_marketplace.json` > `.claude-plugin/marketplace.json` > `.cursor-plugin/marketplace.json`，取第一個存在的【官方】(G-marketplace)；個人 marketplace 在 `~/.agents/plugins/marketplace.json`【官方】(O13) | **Layout A（repo 根的 `.agents/plugins/marketplace.json`）一定要有**。少了它，Codex 會改讀 `.claude-plugin/marketplace.json`，裝到 Claude 形狀的 plugin（包括 mod）【推論】 |
| 頂層欄位 | `name`、`owner`（必填）、`plugins`、`$schema`、`description`、`version`、`metadata.{description,version,pluginRoot}`、`forceRemoveDeletedPlugins`、`allowCrossMarketplaceDependenciesOn`、`renames`【官方】(C3) | `name`、`interface.displayName`、`plugins`【官方】(O13, G-marketplace) | — |
| entry 欄位 | `name`、`source`、`description`、`version`、`category`、`tags`、`strict`、`relevance`、`dependencies`、`defaultEnabled`、`displayName`、`metadata`、`headers`、`headersHelper`【官方】(C3) | `name`、`source`、`policy.{installation, authentication, products}`、`category`；其他欄位會被當成「後備 manifest 欄位」保留，例如 `displayName`、`interface`【官方】(O13, G-marketplace) | Codex 的 entry 必填三項：`policy.installation`、`policy.authentication`、`category`【官方】(O13) |
| 來源類型 | 相對路徑、`github`、`url`、`git-subdir`、`npm`、`archive`、`command`【官方】(C3) | 字串路徑、`local`、`url`（可加 `path`／`ref`／`sha`）、`git-subdir`、`npm`；無法解析的 entry 會略過【官方】(O13, G-marketplace) | `github` 改寫成 `url`。`archive` 與 `command` 沒有對應 |
| 政策 | managed settings：`strictKnownMarketplaces`、`blockedMarketplaces`、`enabledPlugins`【官方】(C7, C17) | `installation`：`AVAILABLE`／`INSTALLED_BY_DEFAULT`／`NOT_AVAILABLE`；`authentication`：`ON_INSTALL`／`ON_USE`【官方】(G-marketplace) | — |
| 指令 | `claude plugin install|uninstall|enable|disable|update|list|details|configure|validate|eval|tag|test|prune|init`；`claude plugin marketplace add|list|remove|update`【本機】(`claude plugin --help`) | `codex plugin add|list|remove`；`codex plugin marketplace add|list|upgrade|remove`【本機】(`codex plugin --help`)。**CLI 沒有 enable／disable**，要改 `config.toml` 的 `[plugins."p@m"] enabled`【官方】(O13) | 安裝文件分開寫兩套 |
| 更新判定 | 依 §2 算出的版本；相同就不換快取；auto-update 預設只對官方 marketplace 開啟【官方】(C7) | `marketplace upgrade` 刷新 git snapshot；plugin 快取依 manifest 版本分目錄【官方】(O13, G-store)。「版本相同但內容不同時會不會重新複製」：官方未公布 | 一律 bump version |

## 4. Tools

| 能力 | Claude Code | Codex | 移植做法 |
|---|---|---|---|
| 檔案讀寫 | `Read`、`Edit`、`Write`、`Glob`、`Grep`、`NotebookEdit`、`LSP`【官方】(C12) | `apply_patch`（hook 比對時可寫 `Edit`／`Write` 別名）；讀檔與搜尋都走 shell【官方】(O6, G-tools) | 內文寫「讀取或修改檔案」，不要寫工具名稱 |
| Shell | `Bash`、`PowerShell`；`run_in_background`；背景指令預設 30 分、最長 2 小時【官方】(C12) | `exec_command`、`write_stdin`（unified exec，hook 比對時算 `Bash`）【官方】(O6) | 同義改寫 |
| 網路 | `WebFetch`、`WebSearch`【官方】(C12) | hosted `web_search`，預設 cached，`--search` 才是 live【官方】(O9)；沒有 fetch 工具，抓頁面要走 shell【推論】 | 改成「搜尋網路／用 shell 抓 URL」 |
| 問使用者 | `AskUserQuestion`（選擇題加 Other；題數上限官方未公布）【官方】(C12) | `request_user_input`：每次 1–3 題，選項需 `label`、`description`，只在允許的 mode 下可用【官方】(G-rui)。Default mode 需要 feature `default_mode_request_user_input`，目前「under development」【本機】(`codex features list`) | 一律加無工具時的退路：列編號選項後停止並等待回覆 |
| 計畫 | `EnterPlanMode`、`ExitPlanMode`【官方】(C12) | `update_plan`（顯示計畫）【官方】(G-tools)；Plan mode 由客戶端切換【推論】 | 改成「先產出計畫並停下等確認」 |
| Todo／任務 | `TaskCreate`／`TaskGet`／`TaskList`／`TaskUpdate`（預設）；`TodoWrite` 預設停用【官方】(C12) | `update_plan`【官方】(G-tools) | 重要狀態寫進檔案，不要依賴工具 |
| 子代理 | `Agent`：選 agent 型別、可覆寫 model、`effort` 參數（v2.1.292）、可背景執行、可 `isolation: worktree`【官方】(C17, C10)【本機】(本 session 的 Agent schema)；另有 `SendMessage`、`ListAgents`、`Workflow`、fork mode【官方】(C12) | `spawn_agent`。v1 參數：`message`／`items`、`agent_type`、`fork_context`、`model`、`reasoning_effort`。v2 參數：`task_name`（必填）、`message`（必填）、`agent_type`、`fork_turns`（`none`／`all`／N，預設 `all`）、`model`、`reasoning_effort`【官方】(G-spawn)。其他工具：`send_input`、`send_message`、`followup_task`、`resume_agent`、`wait_agent`、`list_agents`、`close_agent`、`interrupt_agent`【官方】(G-spawn)。只有在使用者或 AGENTS.md／skill 指示時才會 spawn；子代理繼承 sandbox 與 approval；沒設 model 就繼承上層【官方】(O5)。本機 `multi_agent` stable=true、`multi_agent_v2` stable=false【本機】 | 內文明寫「spawn N 個 `worker`／`explorer`／custom agent、每個的輸入、等全部完成、彙整格式」。要乾淨的 context 就要求 `fork_turns="none"`（v2）或 `fork_context=false`（v1） |
| 背景工作與監看 | `Monitor`（watch 最長 30 分）、`CronCreate`、`ScheduleWakeup`、`PushNotification`【官方】(C12, C17) | `sleep` 工具（feature `sleep_tool`）【本機】；hook `async: true`（最多 8 個並行）【官方】(O6)；沒有 Monitor | Codex 版改成輪詢或分段執行 |
| 交付檔案 | `SendUserFile`、`Artifact`【官方】(C12) | 無；Claude 的 live artifact 不支援【官方】(O15) | 寫檔後列出絕對路徑 |
| 叫用其他 skill | `Skill` 工具【官方】(C12) | 用 `$name` 提及【官方】(O1) | `/x` 改成 `$plugin:x` |

## 5. Runtime hooks

| 項目 | Claude Code | Codex | 移植做法 |
|---|---|---|---|
| 設定位置 | `~/.claude/settings.json`、`.claude/settings(.local).json`、managed、plugin `hooks/hooks.json`、skill／agent frontmatter【官方】(C11) | `~/.codex/hooks.json`、`~/.codex/config.toml` `[hooks]`、`<repo>/.codex/hooks.json`、`.codex/config.toml`、plugin（預設 `hooks/hooks.json`，manifest 的 `hooks` 會取代預設）、`requirements.toml`（managed）【官方】(O6, O13) | plugin 層都用 `hooks/hooks.json`，格式相同（三層：事件、matcher、handlers） |
| 事件 | `SessionStart`、`Setup`、`InstructionsLoaded`、`UserPromptSubmit`、`UserPromptExpansion`、`MessageDisplay`、`PreToolUse`、`PermissionRequest`、`PostToolUse`、`PostToolUseFailure`、`PostToolBatch`、`PermissionDenied`、`Notification`、`SubagentStart`、`SubagentStop`、`TaskCreated`、`TaskCompleted`、`Stop`、`StopFailure`、`TeammateIdle`、`ConfigChange`、`CwdChanged`、`DirectoryAdded`、`FileChanged`、`WorktreeCreate`、`WorktreeRemove`、`PreCompact`、`PostCompact`、`PreModelSwitch`、`PostModelSwitch`、`SessionEnd`、`Elicitation`、`ElicitationResult`【官方】(C11) | `SessionStart`、`SessionEnd`、`SubagentStart`、`SubagentStop`、`PreToolUse`、`PermissionRequest`、`PostToolUse`、`PreCompact`、`PostCompact`、`UserPromptSubmit`、`Stop`、`Interrupt`【官方】(O6) | Claude 有、Codex 沒有的事件：刪除並記錄，不要硬換成相近事件。`Interrupt` 只有 Codex 有 |
| handler 類型 | `command`、`http`、`mcp_tool`、`prompt`、`agent`【官方】(C11) | 執行 `command` 與 `mcp_tool`；`prompt`／`agent` 解析後略過；`SessionEnd` 不支援 `mcp_tool`【官方】(O6) | `http`、`prompt`、`agent` 都要改寫成 command |
| 欄位差異 | `if`（權限規則語法）、`once`（僅 skill）、`shell`、`args`（exec form）、`statusMessage`、`async`【官方】(C11, C2) | `statusMessage`、`timeout`、`async`、`additionalContextLimit`、`commandWindows`（TOML 也接受 `command_windows`）【官方】(O6) | Windows 可用 `commandWindows` |
| timeout | 預設 600 秒；prompt 30、agent 60；`UserPromptSubmit` 30；`SessionEnd` 共用 1.5 秒預算（可放寬到 60）【官方】(C11) | 預設 600 秒；`SessionEnd`、`Interrupt` 預設 1 秒，上限 3 秒【官方】(O6) | `SessionEnd` 的 timeout 壓到 ≤3 秒 |
| 輸入 | 共同欄位，subagent 內另有 `agent_id`／`agent_type`【官方】(C11) | `session_id`（subagent 用 parent 的）、`transcript_path`、`cwd`、`hook_event_name`、`model`、`turn_id`、`permission_mode`【官方】(O6) | 腳本以 `PLUGIN_ROOT` 是否存在判斷是不是 Codex【推論】 |
| 阻擋語意 | exit 2 一律阻擋，JSON 也無法覆蓋；決策欄位依事件不同【官方】(C11) | `PreToolUse`：`permissionDecision: "deny"`、舊式 `decision: "block"`、exit 2 都可阻擋；`allow` 加 `updatedInput` 可改寫輸入；`ask` 尚未支援，會被標為失敗後繼續執行【官方】(O6)。`PostToolUse` 可用 `continue:false`；`Stop`、`SubagentStop` 用 `decision:"block"` 讓模型繼續【官方】(O6) | 不要依賴 `ask` |
| 信任與停用 | `disableAllHooks`、`allowManagedHooksOnly`【官方】(C11) | 非 managed hook 要在 `/hooks` 審核信任，信任綁定定義的雜湊；`--dangerously-bypass-hook-trust` 可略過；`features.hooks` 控制總開關【官方】(O6, O7)【本機】(`codex --help`) | Codex 版的 README 要說明「安裝後到 `/hooks` 信任」 |
| 輸出上限 | — | `additionalContext` 預設約 2,500 token，超過會寫到暫存檔【官方】(O6) | — |
| 公開目錄 | — | 含 lifecycle hook 的 plugin 不能上 OpenAI 公開目錄，只能手動安裝【官方】(O13, O15) | — |

## 6. Mods 與 UI 擴充

| 項目 | Claude Code | Codex | 移植做法 |
|---|---|---|---|
| 是什麼 | plugin 裡的 JS／TS 函式 hook，在 Claude Code 行程內執行；可畫 pane、prompt 上方的 band、按鈕、文字框，可改畫內建 UI，可攔截或改寫 tool call 與 request，可加 `/command` 與 tool，可呼叫模型【官方】(C14) | 官方未公布任何 in-process 的 UI／行為擴充 API | Codex 版**省略整個 mod plugin** |
| 檔案形狀 | `hooks/hooks.json` 寫 `{"modules": ["./register.ts"]}`，manifest 可用 `types` 指向 `.d.ts`【官方】(C15, C2)【本機】(`plugins/common-mod`) | Codex 預設把 `hooks/hooks.json` 當 lifecycle hooks 讀【官方】(O13) | 不能直接複製 mod 的 `hooks/` 到 Codex 版【推論】 |
| 執行面 | CLI 終端機與 Desktop Code tab 都會畫；VS Code、`-p`、SDK、雲端 session 只跑 hook、不畫 UI；Desktop 的 WSL session 不載入【官方】(C14 §Where mods run) | — | — |
| 版本 | v2.1.287（2026-10-01）正式推出；Desktop 從 v2.1.286 起【官方】(C17, C14) | — | — |
| 熱重載 | `--plugin-dir` 存檔即重載；`/reload-plugins`【官方】(C15) | — | — |
| 狀態列 | `statusLine`（執行腳本、讀 JSON stdin）；plugin 只能設 `subagentStatusLine`【官方】(C2, C13) | `tui.status_line`：從固定 ID 清單挑選排序，可設 `null` 關閉；用 `/statusline` 互動設定【官方】(O7, O9)。沒有自訂腳本【推論】 | 狀態列功能不移植 |
| 通知 | `PushNotification`；mod 可用 `$.ui.toast`【官方】(C12, C15) | `notify`（外部指令，收 JSON）、`tui.notifications`【官方】(O7) | 可用 `notify` 或 hook 的 `systemMessage` 做最低限度降級【推論】 |
| 其他 UI | Artifacts（claude.ai）【官方】(C12) | Plugin Extensions（MCP Apps）：側欄 app、對話面板、設定、檔案檢視器、composer 提及、表單，都在 ChatGPT 介面裡【官方】(O18) | 要做跨平台的互動 UI，比較接近 Codex 的是 MCP App；但成本很高，跟 mod 是完全不同的架構【推論】 |
| 雙平台建議 | — | — | 1) Codex marketplace（Layout A／B）都不列 mod plugin（本 repo 已這樣做【本機】）。2) Claude README 標明 Claude 專用與最低版本（mods 需 v2.1.287+）。3) mod 按鈕觸發的 skill（例如 `/common:wait-what`、`/common:show-me`）在 Codex 版用 `$common:wait-what` 等方式手動呼叫，在 skill 的 `agents/openai.yaml` 用 `default_prompt` 提示【推論】 |

---

## 7. 近兩個月的變化（約 2026-08-08 至 2026-10-08）

### Claude Code（v2.1.2xx，出自官方 changelog，C17）

| 版本（日期） | 變化 | 對移植的影響 |
|---|---|---|
| 2.1.287（10-01） | Claude Mods 正式推出 | 新增一類 Claude 專用元件（§6） |
| 2.1.292（10-06） | Agent 工具新增 `effort` 參數；agent 名稱最長 256 字元，skill 或 plugin 檔的 `name` 超過會被忽略；`claude plugin install --marketplace <source>` | Codex `spawn_agent` 也有 `reasoning_effort`，可以直接對應 |
| 2.1.290（10-05） | skill 與 command 的 `!` 指令含控制字元時會被拒 | — |
| 2.1.285（09-29） | `claude plugin configure`；`--config <server>.<key>=` | `userConfig` 在 Claude 端越來越重要，但 Codex 完全沒有 |
| 2.1.282–283（09-24/25） | `anthropic-skills`、`claude-ai` 命名空間保留給 claude.ai 同步的 skill | plugin 或 skill 不要用這兩個名稱 |
| 2.1.277（09-18） | 沒有 `CLAUDE.md` 時直接讀 `AGENTS.md`【官方】(C18) | 規則檔的 `CLAUDE.md` → `AGENTS.md` 改寫不再是硬需求；共用一份 `AGENTS.md` 可行 |
| 2.1.275（09-17） | 同步 claude.ai 帳號的 skill 與 plugin；npm 來源改用 `npm pack --ignore-scripts` | — |
| 2.1.271（09-14） | agent frontmatter 新增 `omitClaudeMd`；`Monitor` watch 一律有期限（最長 30 分），移除 `persistent` | — |
| 2.1.269（09-11） | `claude plugin eval` | Claude 版可以跑 eval；Codex 沒有 |
| 2.1.251（08-28） | 新增 `PreModelSwitch`、`PostModelSwitch` hook；`CLAUDE_CODE_SUBAGENT_MODEL` 改成預設值而非強制覆寫 | Codex 沒有對應事件 |
| 2.1.246（08-25） | plugin skill 的 `name` 已帶前綴時不再重複加前綴（C1） | — |
| 2.1.229 / 2.1.224（08-12 / 08-07） | marketplace 新增 `command`、`archive` 來源 | Codex 沒有這兩種來源 |

### Codex（出自 GitHub release notes 與官方 changelog）

| 版本（日期） | 變化 | 對移植的影響 |
|---|---|---|
| 0.147.0（08-07） | 可安裝可攜式 Agent Plugins；可跨本機、個人、workspace、遠端 catalog 搜尋（R） | 根 `plugin.json` 成為建議格式 |
| 0.148.0（08-18） | hook 支援 `async` 與 `mcp_tool`（R） | 跟 Claude 的 async／mcp_tool 對齊 |
| 0.149.0（08-20） | 移除 skill model delegation；可設定 skill catalog 的 token 預算（R） | — |
| 0.150.0（08-26） | 新增 `Interrupt` hook；不受信任的專案不再提供 `AGENTS.md`（R） | — |
| 0.151.0（08-29） | plugin catalog 合併各 repo 的設定；無效的專案 marketplace 只會被回報，不會遮蔽其他有效項目（R） | — |
| 08-11（changelog） | `/import` 可從 Claude Code 匯入 instruction、settings、skills、plugins、hooks、slash commands、subagents（O17, O19） | 官方有了 Claude → Codex 的匯入路徑，可以當對照組，但匯入後要人工複查（O19） |
| 08-24 → 09-05 | `codex mcp-server` 先棄用，後來移除，改用 app-server（O17） | — |
| 0.153.0（09-03） | plugin CLI 支援遠端 marketplace（R） | — |
| 0.154.0（09-09） | 外部升級或回滾 plugin 後，既有 session 會刷新 skill 與 hook（R） | — |
| 0.155.0（09-17） | session-start hook 能分辨 fork 出來的 session（R） | — |
| 0.156.0（09-22） | 揭露 plugin 宣告的 onboarding skill；重寫 v2 `spawn_agent` 的描述（R） | `extensions."com.openai".onboardingSkill`（O13） |
| 0.159.0（09-29） | **移除內建的 `plugin-creator` skill**（R） | 文件裡的 `@plugin-creator` 流程（O13）在 CLI 可能已經不能用【推論】 |
| 0.160.0（10-01） | 快取 manifest 解析結果（R） | — |
| 0.161.0（10-07） | 在 discovery 階段編譯 hook matcher；`Daybreak` 狀態列項目（R） | — |
| 09-14、09-22、09-29（changelog） | GPT-5.3-Codex-Spark 停用；GPT-5.5 將在 10-14 下架；GPT-6 Sol／Luna、GPT-6.1 Sol 上線（O17） | custom agent TOML 若釘了 `model`，要更新 |

---

## 本 repo 現況落差（`codex/plugins/*` 相對於 Codex 0.161 實際支援）

1. **skill 內文仍有 `${CLAUDE_PLUGIN_ROOT}`**【本機】：`codex/plugins/test-utils/skills/gen-e2e-record/SKILL.md`（第 61、174 行）、`gen-e2e-test/SKILL.md`（第 105、185 行）、`gen-e2e-test/references/verify-loop.md`、`linkstart/skills/link-start/SKILL.md`（第 19–32 行）與 `references/claude-code.md`。Codex 不替換這些變數（摘要 #1），只能靠模型自己猜。建議改成相對 `SKILL.md` 的路徑（例如 `../gen-e2e-record/assets/init-test-template.py`）。`common/delegate` 已經用 `DELEGATE_DIR` 解決，可以照抄【本機】。
2. **`codex/plugins/linkstart/monitors/monitors.json` 是無效檔案**【本機】【官方】。Codex 沒有 monitors（O15 要求移除 `experimental.monitors`），而且裡面的指令還用 `${CLAUDE_PLUGIN_ROOT}`。建議從 Codex 版刪除。
3. **`codex/plugins/common-lab/.codex-agents/executor.toml` 已過期**【本機】。Claude 版 `plugins/common-lab` 已經沒有 `agents/`（marketplace 描述寫 0.19.0 退役了 executor agent），Codex 版 skill 也沒有引用它。建議刪除。
4. **manifest 格式**【本機】。五個 Codex plugin 都用 `.codex-plugin/plugin.json`（加 `"skills": "./skills/"`），仍受支援（O13）。但 baransu transfer 的 origin/main 已改成輸出根目錄的可攜式 `plugin.json`，和本 repo 的 `AGENTS.md` 敘述不一致。要嘛統一改成可攜式（OpenAI 設定放進 `extensions."com.openai"`），要嘛在 `AGENTS.md` 明寫「刻意採用相容格式」。改用可攜式時，`interface` 要搬進 `extensions."com.openai".interface`；這個物件存在時，`.codex-plugin` 不再生效（O13）。
5. **內附 agent 的轉接層仍然需要**【官方】。Codex 0.161 的 plugin 仍不會註冊 agent（G-manifest、G-roles），所以 `common/delegate` 的「Codex Port Adapter - Bundled Agent Resolution」不能拿掉。它的做法（讀 TOML 後把 `developer_instructions` 內嵌到 spawn message，不叫子代理自己讀路徑）和 Codex skill 系統提示的規定「Do not delegate reading … skill instructions to a subagent」不衝突【官方】(G-catalog)【推論】。
6. **`codex-metadata/`** 目前還有 `common-lab/estimate/openai.yaml`、`common-lab/wait-what-jever/...`【本機】。其中 `estimate` 已不在 `codex/plugins/common-lab/skills`，殘留檔可以刪除。`AGENTS.md` 所述「transfer 後還原 `openai.yaml`」在改為手動維護後，可以簡化成「`openai.yaml` 直接放在 `codex/plugins/<p>/skills/<s>/agents/` 並手動維護」。
7. **`AGENTS.md` 的流程描述已過時**【本機】。使用者不再用 transfer 腳本自動移植，但 `AGENTS.md` 仍寫「Do not hand-edit generated files under `codex/`…Regenerate … with the `codex-skill-transfer` script」。這要改成「`codex/` 為手動維護的 Codex 版，以本文件為對照清單」。
8. **Layout A／B 兩份 catalog**【本機】。兩份都只列 5 個 plugin，`common-mod` 正確排除。只要 Layout A 存在，Codex 就不會退回讀 `.claude-plugin/marketplace.json`（G-marketplace），所以 Layout A 不能刪【推論】。
9. **本機 Codex 安裝落後**【本機】。`~/.codex/plugins/cache/common-dev/common/1.40.1`，repo 已是 1.41.0。要 `codex plugin marketplace upgrade common-dev` 才會更新，這也印證版本號就是快取目錄名。
10. **`linkstart` 的 Codex 版本字串是 `0.3.0+codex.20260828033021`**【本機】。含 `+` 的版本字串能否當快取目錄名：官方未公布（`validate_plugin_version_segment` 的規則在 `codex_core_plugin_common` crate，本次沒有讀到）。建議改成純 semver，或安裝後實測確認。

---

## 對 codex-skill-transfer 的修改建議

前提：使用者已不打算用這支 skill 自動移植本 repo。建議把 skill 的定位從「轉換器」改成「對照表加移植檢查清單」，`transfer.py` 改為選用；手動維護時，以各 reference 作為逐項核對的依據。以下逐段對應 origin/main（`10e7bfe`）的內容。

### SKILL.md

- **description、Outcome Contract**：目前寫「Ports … one-way」，`Done when` 要求跑 `transfer.py`。建議改成兩種模式：(a) **checklist 模式**（預設），輸入一對 Claude／Codex 目錄，輸出落差報告，條目照本文 §1–§6 的「移植做法」欄；(b) **generate 模式**（選用），才跑 `transfer.py`。「Direction is one-way… never edit it by hand」一節要改，因為手動維護時 Codex 版本身就是正本。
- **Step 1 表格**：補一條「Codex 也接受 `.claude-plugin/plugin.json` 與 `.claude-plugin/marketplace.json` 當 fallback（G-manifest、G-marketplace），所以 Layout A 不存在時 Codex 會吃到 Claude 版」。
- **Step 3 的刷新清單**：文件網址改成目前的權威位置：`learn.chatgpt.com/docs/{build-skills,hooks,agent-configuration/subagents,config-file/config-reference,import}.md`、`developers.openai.com/plugins/build/plugins.md`、`developers.openai.com/plugins/guides/submit-claude-plugin.md`。原始碼基準從 `rust-v0.156.1` 更新到 `rust-v0.161.0`。另外新增「OpenAI 官方 Claude 移植指引（O15）」作為第一參考。
- **新增「Claude-only 元件」段落**：mods（`hooks/hooks.json` 含 `modules`、manifest `types`）、`monitors/`、`lspServers`、`outputStyles`、`themes`、`workflows`、`bin/`、`channels`、`userConfig`、`dependencies`、`settings.json`。整個 plugin 都是 mod 時，Codex 版直接省略；只有部分元件屬於 Claude 專用時，刪掉並在 README 記錄。
- **Boundaries**：「Never auto-write to user config dirs」維持不變，但要補選項 C（`[agents.<name>] config_file`）作為使用者可自行設定的替代方案（O7）。

### references/skill-mapping.md

- **Quick lookup 表格**：加一欄「Codex 讀取？」並依 G-parser 標明：只有 `name`、`description`、`metadata.short-description` 會被讀。`license`、`compatibility`、`allowed-tools` 的「Pass through」改寫成「保留無害，Codex 忽略」。
- **新增列**：`disallowed-tools`、`background`、`shell`、`paths` 已在 Claude 文件中（C1），補成明確的列，不要只放在「any other key」。
- **`when_to_use` 列**：「before the 1024-char trim」改成：Codex parser 對 description 沒有長度上限（G-parser），真正的限制是 catalog 預算（2%／8,000 字元，O1；`skills.max_context_tokens` ≤10,000，O7）。1024 是 agentskills.io 規範與 `agents/openai.yaml` 的 `short_description` 上限（G-interface）。
- **§2 openai.yaml**：補上完整欄位：`icon_small`、`icon_large`、`brand_color`、`default_prompt`、`dependencies.tools[]`（O1），以及 `policy.products`（只解析、不強制，G-model）。
- **§6 工具表**：
  - `AskUserQuestion` 列保留，並補上 schema 細節（1–3 題、選項需 `label` 與 `description`、只在允許的 mode 下可用，G-rui）。
  - `Task tool` 改成 `Agent` 工具（C12 已是 `Agent`），並加入 v2 參數（`task_name`、`fork_turns`）與 v1 參數（`fork_context`）（G-spawn）。
  - `TodoWrite` 列註明 Claude 預設已停用，改用 `TaskCreate` 系列（C12）。
  - `WebFetch` 列改成「Codex 沒有 fetch 工具，只有 hosted `web_search`，預設 cached（O9）」。
  - 新增 `Monitor`、`CronCreate`、`ScheduleWakeup`、`PushNotification`、`Artifact`、`Workflow`、`SendMessage` 各一列，Codex 對應為「無／降級方式」。
  - `CLAUDE.md` 列：Claude v2.1.277 起會直接讀 `AGENTS.md`（C18），改寫成「建議共用 `AGENTS.md`」。原文的「32 KiB combined cap」在本次讀到的 Codex 文件中沒有找到，應標為待查，或刪除。
- **§8 `copy_aux`**：「Skill-root orphan directories … NOT copied」與官方不符。Codex 文件只是列舉 `scripts/`、`references/`、`assets/`、`agents/`（O1），沒有說其他目錄會被拒。這條規則造成本 repo `templates/` 被丟掉、需要手動還原（見 `AGENTS.md`）。建議改成預設複製所有子目錄，只排除 Claude 專用的檔案。
- **`CLAUDE_PLUGIN_ROOT` 段落**：目前只「flag for manual review」。建議寫成明確規則：skill 或 reference 內文改成相對 `SKILL.md` 的路徑（G-catalog）；hook command 才改成 `${PLUGIN_ROOT}`（O6）。

### references/plugin-mapping.md

- **§1**：補充 `.claude-plugin/plugin.json` 是 Codex 第三順位的 fallback（G-manifest），並說明「為何不直接用」：內文的 Claude token 不會被改寫。
- **§2 欄位表**：補 `extensions."com.openai".onboardingSkill`、`apps`（O13）。補 Claude 欄位的去向：`displayName` → `interface.displayName`；`defaultEnabled` → marketplace 的 `policy.installation`；`userConfig`、`dependencies`、`settings`、`types`、`channels`、`metadata`、`icon`、各種 URL 欄位 → 刪除（O15）。
- **§3 元件表**：補 `monitors/`、`output-styles/`、`themes/`、`workflows/`、`bin/`、`settings.json`、`.lsp.json` 各一列，標為刪除並記錄（O15、C2）。補「`hooks/hooks.json` 含 `modules`（mod）→ 不可複製；整個 mod plugin 從 Codex catalog 省略」。
- **§3 hooks**：事件集合新增 `Interrupt`（Codex 專有，Claude 沒有，所以移植時用不到，但對照表要完整）。新增欄位 `additionalContextLimit`、`async` 上限 8 個並行（O6）。補「含 hook 的 plugin 不能上公開目錄」（O13、O15）。
- **§5**：`lspServers` 之外，補上 `outputStyles`、`experimental.themes`、`experimental.monitors`、`channels`（O15）。
- **§6 bundled agent**：寫明 Codex 0.161 仍不會註冊 plugin agent（G-roles），所以 resolver 仍需要。三個選項並列：A 併入 skill（官方建議，O15）、B package 內 TOML 加 resolver（現行）、C 使用者自行設定 `[agents.x] config_file`（O7）。
- **新增「版本」段落**：Codex 快取目錄名就是 manifest `version`，缺少時是 `local`（O13、G-store）；兩邊都要 bump。版本字串避免 `+`，因為合法性官方未公布。

### references/agent-mapping.md

- **§1 Path 1**：`agents.max_threads` 等設定已正確。補上 spawn 工具的實際參數（v1：`fork_context`；v2：`fork_turns`、`task_name`，G-spawn），以及本機現況：`multi_agent` 開、`multi_agent_v2` 關【本機】。`context: fork` 想要乾淨 context 時，指示寫 `fork_turns="none"` 或 `fork_context=false`。
- **§2 表格**：`agent: Explore` → `explorer`、`general-purpose` → `default` 都正確（O5）。`effort` 改成同時列出「spawn 參數 `reasoning_effort`」與「TOML 的 `model_reasoning_effort`」。補上 Claude agent 欄位 `isolation: worktree`、`maxTurns`、`memory`、`omitClaudeMd`、`color`、`initialPrompt` → 沒有對應（C10）。
- **§4**：resolver 文字補一句：把 `developer_instructions` 內嵌到 spawn message（本 repo `delegate` 的做法），比叫子代理自己讀 TOML 更穩，也不違反 Codex 的「不要把 skill 指示交給子代理讀」規定（G-catalog）。
- 在 model 的指引裡註明：custom agent 若釘了 `gpt-5.5` 或 `gpt-5.3-codex-spark` 要更新（O17）。

### references/marketplace-mapping.md

- **§1**：補上 Codex 的讀取順序（四個路徑，取第一個存在的；G-marketplace），以及「Layout A 存在才能擋住 `.claude-plugin/marketplace.json` fallback」。
- **§3 entry**：補 `policy.products`、`ON_USE`、`NOT_AVAILABLE`、`INSTALLED_BY_DEFAULT`（G-marketplace）；補「其他欄位會被當作後備 manifest 欄位」（G-marketplace）；補來源對照：Claude `github` → Codex `url`，`archive`／`command` 沒有對應。
- **§8**：「Resolved (2026-09, loader `rust-v0.156.1`)」的結論在 0.161 仍成立【官方】(G-marketplace)，更新基準版本即可。補上安裝後的啟用方式：Codex CLI 沒有 enable／disable，要改 `config.toml`（O13）【本機】。

### references/CODEX_PORT_PLAN.md、loop-pauses.md

- T0-1（`request_user_input`）：補上 v2 schema 細節（G-rui），並注意 feature 狀態仍是 under development【本機】。
- T0-2（隔離）：補上 `fork_turns="none"`（v2）或 `fork_context=false`（v1）可取得乾淨 context（G-spawn）。這可以減少需要另開 session 的情況，但仍要實測【推論】。

### assets/

- `codex-plugin.template.json`：補 `onboardingSkill` 的佔位欄位（選填）。不要加 `skills` 欄位，因為可攜式格式會自動探索 `skills/`（O13）。
- `codex-marketplace.template.json`：與 O13 一致，不需要改。

### scripts/transfer.py（若保留）

- `CODEX_HOOK_EVENTS` 加入 `Interrupt`，維持完整性。
- 遇到 `hooks/hooks.json` 含 `modules` 時，整個 plugin 標為「Claude-only mod，不輸出」，而不是當成 hook 移植。
- `copy_aux` 改成複製全部子目錄（見 skill-mapping §8）。
- 內文 `${CLAUDE_PLUGIN_ROOT}/skills/<self>/x` 改寫成相對路徑；這和 §6.1 的 repo 路徑改寫是同一套規則。

---

## 來源清單

擷取路徑皆相對於本 repo 根目錄；「(C/O/G/R 代號)」對應上文引用。

### Claude Code（官方）

| 代號 | URL | 擷取路徑 |
|---|---|---|
| C1 | https://code.claude.com/docs/en/skills.md | `.claude/read/material/extend-claude-with-skills/index.md` |
| C2 | https://code.claude.com/docs/en/plugins/manifest-reference.md | `.claude/read/material/plugin-manifest-reference/index.md` |
| C3 | https://code.claude.com/docs/en/plugins/marketplace-reference.md | `.claude/read/material/marketplace-reference/index.md` |
| C4 | https://code.claude.com/docs/en/plugins/components.md | `.claude/read/material/add-components-to-a-plugin/index.md` |
| C5 | https://code.claude.com/docs/en/plugins/cli-reference.md | `.claude/read/material/plugin-commands-reference/index.md` |
| C6 | https://code.claude.com/docs/en/plugins/dependencies.md | `.claude/read/material/plugin-dependencies/index.md` |
| C7 | https://code.claude.com/docs/en/plugins/loading.md | `.claude/read/material/plugin-loading-reference/index.md` |
| C8 | https://code.claude.com/docs/en/plugins/install.md | `.claude/read/material/install-and-manage-plugins/index.md` |
| C9 | https://code.claude.com/docs/en/plugins/host-marketplace.md | `.claude/read/material/host-and-maintain-a-marketplace/index.md` |
| C10 | https://code.claude.com/docs/en/sub-agents.md | `.claude/read/material/create-custom-subagents_v2/index.md` |
| C11 | https://code.claude.com/docs/en/hooks.md | `.claude/read/material/hooks-reference/index.md` |
| C12 | https://code.claude.com/docs/en/tools-reference.md | `.claude/read/material/tools-reference/index.md` |
| C13 | https://code.claude.com/docs/en/statusline.md | `.claude/read/material/customize-your-status-line/index.md` |
| C14 | https://code.claude.com/docs/en/plugins/mods/overview.md | `.claude/read/material/mods-overview/index.md` |
| C15 | https://code.claude.com/docs/en/plugins/mods/reference.md | `.claude/read/material/mods-reference/index.md` |
| C16 | https://code.claude.com/docs/en/plugins/mods/interface.md | `.claude/read/material/draw-in-the-interface-with-a-mod/index.md` |
| C17 | https://code.claude.com/docs/en/changelog.md | `.claude/read/material/claude-code-changelog/index.md` |
| C18 | https://code.claude.com/docs/en/memory.md | `.claude/read/material/how-claude-remembers-your-project/index.md` |
| — | https://code.claude.com/docs/llms.txt（索引，僅用來找頁面） | 未存檔 |

### Codex／OpenAI（官方）

| 代號 | URL | 擷取路徑 |
|---|---|---|
| O1 | https://learn.chatgpt.com/docs/build-skills.md | `.claude/read/material/build-skills/index.md` |
| O2 | https://learn.chatgpt.com/docs/build-plugins.md | `.claude/read/material/build-plugins/index.md` |
| O3 | https://learn.chatgpt.com/docs/plugins.md | `.claude/read/material/plugins/index.md`（另有重複擷取 `plugins_v2`） |
| O4 | https://learn.chatgpt.com/docs/skills-and-plugins.md | `.claude/read/material/skills-plugins/index.md` |
| O5 | https://learn.chatgpt.com/docs/agent-configuration/subagents.md | `.claude/read/material/subagents_v2/index.md` |
| O6 | https://learn.chatgpt.com/docs/hooks.md | `.claude/read/material/hooks/index.md` |
| O7 | https://learn.chatgpt.com/docs/config-file/config-reference.md | `.claude/read/material/configuration-reference/index.md` |
| O8 | https://learn.chatgpt.com/docs/cli-customization.md | `.claude/read/material/cli-customization/index.md` |
| O9 | https://learn.chatgpt.com/docs/developer-commands.md?surface=cli | `.claude/read/material/developer-commands/index.md` |
| O10 | https://learn.chatgpt.com/docs/custom-prompts.md | `.claude/read/material/custom-prompts/index.md` |
| O11 | https://learn.chatgpt.com/docs/customization/overview.md | `.claude/read/material/customization/index.md` |
| O12 | https://learn.chatgpt.com/docs/enterprise/skills.md | `.claude/read/material/skill-controls/index.md` |
| O13 | https://developers.openai.com/plugins/build/plugins.md | `.claude/read/material/package-your-plugin/index.md` |
| O14 | https://developers.openai.com/plugins/build/skills.md | `.claude/read/material/build-skills_v2/index.md` |
| O15 | https://developers.openai.com/plugins/guides/submit-claude-plugin.md | `.claude/read/material/submit-your-claude-code-plugin-to-openai/index.md` |
| O16 | https://developers.openai.com/plugins/concepts/plugins.md | `.claude/read/material/plugin-architecture/index.md` |
| O17 | https://developers.openai.com/codex/changelog（轉址到 learn.chatgpt.com/docs/changelog） | `.claude/read/material/chatgpt-codex-changelog/index.md` |
| O18 | https://developers.openai.com/plugins/build/extensions.md | `.claude/read/material/plugin-extensions/index.md` |
| O19 | https://learn.chatgpt.com/docs/import.md | `.claude/read/material/import-from-another-agent/index.md` |
| — | https://developers.openai.com/codex/llms.txt、https://developers.openai.com/plugins/llms.txt（索引） | 未存檔 |

### openai/codex 原始碼（tag `rust-v0.161.0`，sparse clone 到 session scratchpad 閱讀，未存進 `.claude/read/`）

| 代號 | 路徑 |
|---|---|
| G-parser | https://github.com/openai/codex/blob/rust-v0.161.0/codex-rs/skills/src/parser.rs |
| G-interface | https://github.com/openai/codex/blob/rust-v0.161.0/codex-rs/skills/src/interface.rs |
| G-model | https://github.com/openai/codex/blob/rust-v0.161.0/codex-rs/skills/src/model.rs |
| G-mentions | https://github.com/openai/codex/blob/rust-v0.161.0/codex-rs/skills/src/mentions.rs |
| G-namespace | https://github.com/openai/codex/blob/rust-v0.161.0/codex-rs/core-plugins/src/test_support.rs（`format!("{}:{}", root.plugin_namespace, parsed.name)`）、`codex-rs/utils/plugins/src/plugin_namespace.rs` |
| G-catalog | https://github.com/openai/codex/blob/rust-v0.161.0/codex-rs/ext/skills/src/catalog_prompt.rs |
| G-manifest | https://github.com/openai/codex/blob/rust-v0.161.0/codex-rs/core-plugins/src/manifest.rs、`codex-rs/utils/plugins/src/plugin_namespace.rs`（`find_plugin_manifest_path`） |
| G-marketplace | https://github.com/openai/codex/blob/rust-v0.161.0/codex-rs/core-plugins/src/marketplace.rs |
| G-store | https://github.com/openai/codex/blob/rust-v0.161.0/codex-rs/core-plugins/src/store.rs |
| G-cmdmig | https://github.com/openai/codex/blob/rust-v0.161.0/codex-rs/core-plugins/src/command_migration.rs |
| G-roles | https://github.com/openai/codex/blob/rust-v0.161.0/codex-rs/agent-roles/src/loader.rs、`discovery.rs` |
| G-spawn | https://github.com/openai/codex/blob/rust-v0.161.0/codex-rs/core/src/tools/handlers/multi_agents_spec.rs |
| G-rui | https://github.com/openai/codex/blob/rust-v0.161.0/codex-rs/core/src/tools/handlers/request_user_input_spec.rs |
| G-tools | https://github.com/openai/codex/tree/rust-v0.161.0/codex-rs/core/src/tools/handlers（`plan_spec.rs` 的 `update_plan` 等） |
| G-hookenv | https://github.com/openai/codex/blob/rust-v0.161.0/codex-rs/hooks/src/engine/discovery.rs |
| R | https://github.com/openai/codex/releases（stable 版 rust-v0.146.1 至 v0.161.0 的 release notes，以 `gh api` 取得） |

### 本機證據

- `claude --version` → `2.1.293`；`claude --help`、`claude plugin --help`、`claude plugin install --help`、`claude plugin marketplace --help`、`claude plugin update --help`
- `codex --version` → `codex-cli 0.161.0`；`codex --help`、`codex plugin --help`、`codex plugin marketplace --help`、`codex plugin add --help`、`codex features list`
- `~/.codex/config.toml`（marketplace 與 plugin 段落）、`~/.codex/plugins/cache/*`
- 本 repo：`AGENTS.md`、`.claude-plugin/marketplace.json`、`.agents/plugins/marketplace.json`、`codex/.agents/plugins/marketplace.json`、`plugins/*`、`codex/plugins/*`、`codex-metadata/*`、`plugins/common-mod/{.claude-plugin/plugin.json,hooks/hooks.json}`
- baransu `origin/main`（`10e7bfe`）：`plugins/baransu/skills/codex-skill-transfer/{SKILL.md, references/*.md, assets/*.json, scripts/transfer.py}`（以 `git show` 讀取，未改動工作目錄）
