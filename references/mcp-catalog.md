# MCP Server 推荐目录

MCP（Model Context Protocol）Servers 为 agent 提供外部工具和数据源接入能力。以下是常用 MCP Server 及其配置方法。

---

## GitHub

**用途**：操作 GitHub 仓库——创建/审查 PR、管理 Issues、搜索代码、查看 CI 状态。

**安装**：
```bash
npm install -g @anthropic/mcp-server-github
```

**所需凭证**：
- GitHub Personal Access Token（需 `repo`, `read:org` 权限）
- 生成地址：https://github.com/settings/tokens

**配置 JSON**（写入 openclaw.json 的 `mcp.servers`）：
```json
{
  "github": {
    "command": "mcp-server-github",
    "env": {
      "GITHUB_TOKEN": "ghp_xxxxxxxxxxxxxxxxxxxx"
    }
  }
}
```

**验证**：
```bash
openclaw mcp test github
# 或手动测试：
echo '{"method":"tools/list"}' | mcp-server-github
```

**常用操作**：
- 创建 PR：`gh pr create`（通过 exec 权限调用 gh CLI 也可以）
- 搜索 Issues：GitHub MCP 的 `search_issues` 工具
- 查看 CI 状态：`get_check_runs` 工具

---

## Google Calendar

**用途**：查看/创建/修改日历事件，帮 agent 感知用户的时间安排。

**安装**：
```bash
npm install -g @anthropic/mcp-server-google-calendar
```

**所需凭证**：
- Google OAuth 2.0 Client ID + Client Secret
- 配置地址：https://console.cloud.google.com/apis/credentials
- 需启用 Google Calendar API

**配置 JSON**：
```json
{
  "google-calendar": {
    "command": "mcp-server-google-calendar",
    "env": {
      "GOOGLE_CLIENT_ID": "xxxxx.apps.googleusercontent.com",
      "GOOGLE_CLIENT_SECRET": "GOCSPX-xxxxxxxxxxxx",
      "GOOGLE_REDIRECT_URI": "http://localhost:3000/callback"
    }
  }
}
```

**验证**：
```bash
openclaw mcp test google-calendar
```

**注意**：首次使用需要在浏览器中完成 OAuth 授权流程。

---

## PostgreSQL / SQLite

**用途**：查询数据库、执行 SQL、分析数据。

### PostgreSQL

**安装**：
```bash
npm install -g @anthropic/mcp-server-postgres
```

**配置 JSON**：
```json
{
  "postgres": {
    "command": "mcp-server-postgres",
    "env": {
      "DATABASE_URL": "postgresql://user:password@host:5432/dbname"
    }
  }
}
```

### SQLite

**安装**：
```bash
npm install -g @anthropic/mcp-server-sqlite
```

**配置 JSON**：
```json
{
  "sqlite": {
    "command": "mcp-server-sqlite",
    "args": ["--db", "/path/to/database.sqlite"]
  }
}
```

**验证**：
```bash
openclaw mcp test postgres   # 或 sqlite
```

---

## Filesystem（扩展文件访问）

**用途**：让 agent 访问 workspace 以外的指定目录。默认情况下 agent 只能读写 `~/.openclaw/workspace/`，通过 Filesystem MCP 可以安全地扩展访问范围。

**安装**：
```bash
npm install -g @anthropic/mcp-server-filesystem
```

**配置 JSON**：
```json
{
  "filesystem": {
    "command": "mcp-server-filesystem",
    "args": [
      "--allowed-dirs", "/home/user/projects,/home/user/documents"
    ]
  }
}
```

**验证**：
```bash
openclaw mcp test filesystem
```

**安全说明**：`--allowed-dirs` 严格限制可访问的目录。不在列表中的路径一律拒绝。

---

## Brave Search

**用途**：替代内置 WebSearch 的搜索引擎。Brave Search 注重隐私，不追踪用户。

**安装**：
```bash
npm install -g @anthropic/mcp-server-brave-search
```

**所需凭证**：
- Brave Search API Key
- 申请地址：https://brave.com/search/api/

**配置 JSON**：
```json
{
  "brave-search": {
    "command": "mcp-server-brave-search",
    "env": {
      "BRAVE_API_KEY": "BSAxxxxxxxxxxxxxxxxxxxx"
    }
  }
}
```

**验证**：
```bash
openclaw mcp test brave-search
```

---

## Memory（向量记忆）

**用途**：为 agent 的长期记忆提供语义检索能力。基于 embedding 的向量搜索，比文件名匹配更智能。

**安装**：
```bash
npm install -g @anthropic/mcp-server-memory
```

**配置 JSON**：
```json
{
  "memory": {
    "command": "mcp-server-memory",
    "args": [
      "--storage-dir", "~/.openclaw/workspace/memory/vectors"
    ]
  }
}
```

**验证**：
```bash
openclaw mcp test memory
```

---

## 通用配置方法

### 添加 MCP Server 到 openclaw.json

MCP Server 配置在 `mcp.servers` 下，每个 key 是 server 名称：

```json
{
  "mcp": {
    "servers": {
      "github": { "command": "...", "env": { ... } },
      "postgres": { "command": "...", "env": { ... } }
    }
  }
}
```

### 通过命令行添加

```bash
# 设置 MCP Server
openclaw config set mcp.servers.github '{"command":"mcp-server-github","env":{"GITHUB_TOKEN":"ghp_xxx"}}'

# 查看已配置的 MCP Servers
openclaw config get mcp.servers

# 测试连接
openclaw mcp test <server-name>

# 列出 MCP Server 提供的工具
openclaw mcp tools <server-name>
```

### 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `command not found` | npm 全局 bin 不在 PATH | `export PATH="$(npm config get prefix)/bin:$PATH"` |
| `ECONNREFUSED` | 服务未启动或端口错误 | 检查 command 路径和参数 |
| `unauthorized` | Token/Key 无效或过期 | 重新生成凭证 |
| `timeout` | 网络问题或服务响应慢 | 检查网络，增加超时配置 |
