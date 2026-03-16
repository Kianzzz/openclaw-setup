# OpenClaw 权限配置详解

## 权限一览

OpenClaw 有 6 项独立权限，控制 agent 能执行哪些类型的操作。

| 权限 | 用途 | 风险等级 | 默认 |
|------|------|---------|------|
| `read` | 读取工作区文件、记忆、配置 | 低 | `true` |
| `write` | 创建/修改文件、更新记忆和日志 | 中 | `false` |
| `exec` | 执行 shell 命令（npm, git, python 等）| 高 | `false` |
| `web` | 访问互联网（fetch URL、WebSearch）| 中 | `false` |
| `mcp` | 连接 MCP Servers（GitHub, Calendar 等）| 中 | `false` |
| `admin` | 管理操作（修改配置、安装技能、管理 cron）| 高 | `false` |

---

## 各权限详解

### read（文件读取）

**控制范围**：读取 workspace 下所有文件，包括 SOUL.md、记忆文件、日志等。

**为什么需要**：这是 agent 的基础能力。没有读取权限，agent 无法加载自己的身份、记忆和上下文，基本等于失忆状态。

**风险**：低。只读操作不会修改任何内容。

**建议**：始终开启。

### write（文件写入）

**控制范围**：创建新文件、修改已有文件、更新记忆系统（working-memory.md、daily notes、entities）。

**为什么需要**：agent 的学习和成长依赖写入能力。没有写入权限，agent 无法记住对话内容、无法更新目标、无法沉淀经验。每次对话都从零开始。

**风险**：中。agent 可能意外覆盖重要文件。但 OpenClaw 有 workspace 沙盒限制，写入范围仅限 `~/.openclaw/workspace/`。

**建议**：强烈建议开启。配合 `exec` 权限一起使用。

### exec（命令执行）

**控制范围**：在服务器上执行 shell 命令，包括 npm、git、python、系统工具等。

**为什么需要**：技能安装（`clawhub install`）、定时任务、文件操作、外部工具调用都依赖此权限。没有 exec 权限，agent 只能读写文件，无法与系统交互。

**风险**：高。理论上可以执行任何系统命令。但 OpenClaw 的 exec 沙盒会限制危险操作（如 `rm -rf /`、直接修改系统文件等）。

**建议**：建议开启。如果担心安全，可以配合 `security.execAllowlist` 限制可执行的命令集。

### web（网络访问）

**控制范围**：发起 HTTP/HTTPS 请求，使用 WebSearch 搜索引擎，抓取网页内容。

**为什么需要**：联网搜索最新信息、获取 API 数据、下载资源。对于需要时效性信息的场景（新闻、技术文档、版本查询）不可或缺。

**风险**：中。agent 可能访问恶意 URL 或泄露信息到外部服务。

**建议**：建议开启。如需限制，可配置 `security.webAllowlist` 指定允许的域名。

### mcp（MCP Server 连接）

**控制范围**：连接和使用 MCP（Model Context Protocol）Servers，如 GitHub、Google Calendar、数据库等。

**为什么需要**：MCP 是 agent 的能力扩展接口。通过 MCP，agent 可以操作 GitHub PR、管理日历、查询数据库。

**风险**：中。取决于所连接的 MCP Server 的权限范围。GitHub MCP 可以创建 PR，Calendar MCP 可以修改日程。

**建议**：按需开启。开启后还需要单独配置每个 MCP Server。

### admin（管理操作）

**控制范围**：修改 openclaw.json 配置、安装/卸载技能、管理 cron 定时任务、修改权限（不能升级自己）。

**为什么需要**：agent 自主管理能力的基础。有 admin 权限的 agent 可以自己安装新技能、调整配置。没有 admin 权限时，所有配置变更都需要人类手动操作。

**风险**：高。agent 可能修改关键配置导致服务异常。但 admin 权限有硬性限制：不能修改自己的权限等级、不能删除 SOUL.md。

**建议**：信任 agent 后开启。初始阶段可以暂不开启，通过 openclaw-setup 手动配置。

---

## 推荐组合

### 最小权限（保守型）

适合刚部署、还不信任 agent 的阶段。agent 可以读写文件和记忆，但不能执行命令或联网。

```bash
openclaw config set permissions.read true
openclaw config set permissions.write true
openclaw config set permissions.exec false
openclaw config set permissions.web false
openclaw config set permissions.mcp false
openclaw config set permissions.admin false
```

**能做到**：读取/写入记忆和文件、参与对话、记住上下文
**做不到**：安装技能、联网搜索、执行脚本、连接 MCP

### 标准权限（推荐）

适合日常使用。agent 可以读写、执行命令、联网，但不能自行安装技能或修改配置。

```bash
openclaw config set permissions.read true
openclaw config set permissions.write true
openclaw config set permissions.exec true
openclaw config set permissions.web true
openclaw config set permissions.mcp false
openclaw config set permissions.admin false
```

**能做到**：上述 + 执行 shell 命令、联网搜索、运行脚本
**做不到**：安装/卸载技能、修改配置、连接 MCP Server

### 完整权限（信任型）

适合已经磨合成熟、完全信任的 agent。解锁全部能力。

```bash
openclaw config set permissions.read true
openclaw config set permissions.write true
openclaw config set permissions.exec true
openclaw config set permissions.web true
openclaw config set permissions.mcp true
openclaw config set permissions.admin true
```

**能做到**：全部操作
**注意**：即使完整权限，OpenClaw 仍有硬性安全底线（不能改自身权限、不能删 SOUL.md）

---

## 配置命令

```bash
# 查看当前权限
openclaw config get permissions

# 设置单项权限
openclaw config set permissions.<key> true|false

# 批量设置（JSON）
openclaw config set permissions '{"read":true,"write":true,"exec":true,"web":true,"mcp":false,"admin":false}'

# 使用预设
openclaw config set permissions.preset minimal   # read + write
openclaw config set permissions.preset standard   # read + write + exec + web
openclaw config set permissions.preset full       # 全部开启
```

---

## 权限与技能的关系

技能安装需要 `admin` 权限。但安装后的技能在运行时使用的权限取决于技能本身的操作：

| 技能操作 | 需要的权限 |
|---------|-----------|
| 读取参考文件 | `read` |
| 写入结果文件 | `write` |
| 运行 Python 脚本 | `exec` |
| 联网搜索 | `web` |
| 调用 GitHub MCP | `mcp` |
| 修改 openclaw.json | `admin` |

如果技能需要的权限未开启，该操作会被拦截并记录到日志。agent 会收到权限不足的错误提示。
