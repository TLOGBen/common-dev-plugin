# 安裝與管理

回到 [文件索引](README.md)。

`common-dev` 以 Claude Code marketplace（id：`common-dev`）形式發佈，並附 Codex 版本。五個穩定 plugin（`common`、`analysis-estimation`、`test-utils`、`linkstart`、`common-mod`）都設為 `defaultEnabled: true`；Claude 與 Codex marketplace 另提供需自行安裝、裝後即啟用的 `Common Lab（實驗性）`，不會取代穩定版 Common。`common-mod` 只有 Claude Code 版本。

## Claude Code

### 加入 marketplace

```text
/plugin marketplace add https://github.com/TLOGBen/common-dev-plugin.git
```

### 安裝個別 plugin

預設啟用的 plugin 加入 marketplace 後即可使用。若既有安裝尚未包含某個 plugin，可明確安裝：

```text
/plugin install test-utils@common-dev
/plugin install analysis-estimation@common-dev
/plugin install linkstart@common-dev
/plugin install common@common-dev
/plugin install common-lab@common-dev   # 實驗版
/plugin install common-mod@common-dev   # Claude Code mod（Claude 專屬）
```

### 停用

不需要的套件可個別停用：

```text
claude plugin disable <plugin-name>
```

例如 `claude plugin disable common-lab`。

### 更新

Claude Code 會快取 plugin，所以 repo 每次散佈變更都會 bump 對應 plugin 的 `version`；更新 marketplace 後，新版本號才會讓快取刷新。

### 呼叫方式

Claude skill 以 `/<plugin>:<skill>` 呼叫，例如 `/common:delegate`、`/common-lab:jev-gate`。`common-mod` 沒有 slash command，安裝後直接出現在介面上。

## Codex

### 從 git URL 安裝

```bash
codex plugin marketplace add https://github.com/TLOGBen/common-dev-plugin.git
codex plugin add test-utils@common-dev
codex plugin add analysis-estimation@common-dev
codex plugin add common@common-dev
codex plugin add common-lab@common-dev
codex plugin add linkstart@common-dev
```

Codex 沒有 `common-mod` 的對應版本。Codex skill 以 `$<skill>` 呼叫，例如 `$delegate`、`$link-start`。

### 確認已安裝的版本

```bash
codex plugin list --available --json
```

### Marketplace 佈局

Codex 有兩份手工維護的 catalog，marketplace id 都是 `common-dev`，都列出所有 Codex plugin：

| 佈局 | 檔案 | plugin 路徑 | 用途 |
|------|------|-------------|------|
| Layout A | `.agents/plugins/marketplace.json` | `./codex/plugins/<name>` | git URL 安裝入口（上面的指令走這份） |
| Layout B | `codex/.agents/plugins/marketplace.json` | `./plugins/<name>` | 以 `codex/` 為根的自包含佈局，供本機路徑安裝 |

### 用暫存 Codex home 試裝

驗證本機改動時，不要動到自己的 Codex 設定，改用暫存 home（與 [`AGENTS.md`](../AGENTS.md) 的驗證流程相同）：

```bash
mkdir -p /tmp/common-dev-plugin-codex-test
env HOME=/tmp/common-dev-plugin-codex-test CODEX_HOME=/tmp/common-dev-plugin-codex-test codex plugin marketplace add /path/to/common-dev-plugin --json
env HOME=/tmp/common-dev-plugin-codex-test CODEX_HOME=/tmp/common-dev-plugin-codex-test codex plugin list --available --json
env HOME=/tmp/common-dev-plugin-codex-test CODEX_HOME=/tmp/common-dev-plugin-codex-test codex plugin add test-utils@common-dev --json
```

暫存安裝成功不代表另一個 App／Host 已載入新版；重新開啟對話後，再確認實際載入的技能名稱與版本。

## 各 plugin 的額外相依

| Plugin | 需要 |
|--------|------|
| `test-utils` | Node.js；`dev-browser` 另需外部 CLI，見 [test-utils 相依](plugins/test-utils.md#相依) |
| `common-lab` | TypeSafe Jev 金鑰 `TYPESAFE_API_KEY`，用 `init-jev` 設定，見 [common-lab](plugins/common-lab.md) |
| `linkstart` | 不需另外安裝；plugin 內嵌 exact Runtime binary，見 [linkstart](plugins/linkstart.md#runtime-來源) |
| `common-mod` | 只支援 Claude Code（CLI 與桌面版 Code 分頁），見 [common-mod](plugins/common-mod.md) |
