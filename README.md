# openclaw-setup

OpenClaw Interactive Configuration Wizard / OpenClaw 交互式配置向导

[English](#english) | [中文](#中文)

---

## English

### Overview

openclaw-setup is an interactive configuration wizard for OpenClaw deployment. It guides you through a 4-step setup process to configure permissions, models, extensions, and security settings.

### Features

- **Step 1: Permissions** - Configure 6 permission types (read/write/exec/web/mcp/admin) with 3 preset combinations
- **Step 2: Model Tuning** - Set up primary/fallback models, maxTokens, compaction strategy, and heartbeat
- **Step 3: Extensions** - Install clawhub skills, MCP servers, cron jobs, and GitHub sync
- **Step 4: Security** - Configure DM policy, API limits, thinking level, and skill security policy

### Installation

#### Method 1: Via clawhub (Recommended)

```bash
clawhub install openclaw-setup
```

#### Method 2: Clone from GitHub

```bash
cd ~/.openclaw/workspace/skills/
git clone https://github.com/Kianzzz/openclaw-setup.git
```

### Usage

Trigger the wizard by saying:

```
configure openclaw
setup openclaw
configure permissions
configure models
add MCP
openclaw security
```

Or directly: `/openclaw-setup`

### Workflow

1. **§1 Environment Detection** - Run `setup_check.py` to scan current configuration
2. **§2 Welcome Menu** - Select which steps to configure (multi-select supported)
3. **§3 Permissions** - Configure agent permissions (manual execution required)
4. **§4 Model Tuning** - Set up models, maxTokens, compaction, heartbeat (auto-configured)
5. **§5 Extensions** - Install clawhub skills, MCP servers, cron jobs (optional)
6. **§6 Security** - Configure DM policy, API limits, thinking level (optional)
7. **§7 Summary** - Verify all configurations and show before/after comparison

### Files

- `SKILL.md` (547 lines) - Main workflow with §1-§7
- `scripts/setup_check.py` (316 lines) - Environment detector
- `references/permissions-guide.md` (167 lines) - 6 permissions + 3 presets
- `references/model-reference.md` (209 lines) - Model table + maxTokens formula
- `references/mcp-catalog.md` (260 lines) - 6 MCP servers with config examples
- `references/security-rules.md` (211 lines) - 3 install strategies + audit rules

### Recommended MCP Servers

- **GitHub** - Manage repositories, PRs, issues
- **Google Calendar** - Schedule awareness
- **PostgreSQL/SQLite** - Database queries
- **Filesystem** - Extended file access beyond workspace
- **Brave Search** - Privacy-focused search
- **Memory** - Vector-based semantic memory

### Permission Presets

**Minimal** (read + write)
- Agent can read/write files and memory
- Cannot execute commands or access network

**Standard** (read + write + exec + web) - Recommended
- Agent can execute commands and search the web
- Cannot install skills or modify config

**Full** (all 6 permissions)
- Unlock all capabilities including MCP and admin operations
- Suitable for trusted agents

### Use with openclaw-soul

openclaw-setup is designed to run after [openclaw-soul](https://github.com/Kianzzz/openclaw-soul) BOOTSTRAP completes:

```
openclaw-soul (soul framework + BOOTSTRAP)
    ↓
openclaw-setup (permissions + models + extensions + security)
    ↓
Ready to use
```

### Version

Current version: v1.0.0

### License

MIT License

### Author

Kianzzz

### Links

- GitHub: https://github.com/Kianzzz/openclaw-setup
- openclaw-soul: https://github.com/Kianzzz/openclaw-soul

---

## 中文

### 简介

openclaw-setup 是 OpenClaw 的交互式配置向导，通过 4 步引导完成权限、模型、扩展和安全配置。

### 功能

- **步骤 1：权限配置** - 配置 6 项权限（read/write/exec/web/mcp/admin），提供 3 种预设组合
- **步骤 2：模型调优** - 设置主模型/fallback 链、maxTokens、压缩策略、心跳
- **步骤 3：能力扩展** - 安装 clawhub 技能、MCP Servers、Cron 定时任务、GitHub 同步
- **步骤 4：安全加固** - 配置 DM 策略、API 限额、Thinking 级别、技能安全策略

### 安装

#### 方式 1：通过 clawhub（推荐）

```bash
clawhub install openclaw-setup
```

#### 方式 2：从 GitHub 克隆

```bash
cd ~/.openclaw/workspace/skills/
git clone https://github.com/Kianzzz/openclaw-setup.git
```

### 使用

通过以下方式触发配置向导：

```
配置openclaw
setup openclaw
配置权限
配置模型
添加MCP
openclaw安全配置
```

或直接调用：`/openclaw-setup`

### 工作流程

1. **§1 环境检测** - 运行 `setup_check.py` 扫描当前配置状态
2. **§2 欢迎菜单** - 选择要配置的步骤（支持多选）
3. **§3 权限配置** - 配置 agent 权限（需要用户手动执行命令）
4. **§4 模型调优** - 设置模型、maxTokens、压缩、心跳（自动配置）
5. **§5 能力扩展** - 安装 clawhub 技能、MCP Servers、Cron 任务（可选）
6. **§6 安全加固** - 配置 DM 策略、API 限额、Thinking 级别（可选）
7. **§7 总结验证** - 验证所有配置并展示前后对比

### 文件结构

- `SKILL.md`（547 行）- 主工作流，包含 §1-§7
- `scripts/setup_check.py`（316 行）- 环境检测脚本
- `references/permissions-guide.md`（167 行）- 6 项权限 + 3 种预设
- `references/model-reference.md`（209 行）- 模型表格 + maxTokens 计算公式
- `references/mcp-catalog.md`（260 行）- 6 个 MCP Server 配置示例
- `references/security-rules.md`（211 行）- 3 种安装策略 + 审核规则

### 推荐的 MCP Servers

- **GitHub** - 管理仓库、PR、Issues
- **Google Calendar** - 日程感知
- **PostgreSQL/SQLite** - 数据库查询
- **Filesystem** - 扩展 workspace 外的文件访问
- **Brave Search** - 隐私优先的搜索引擎
- **Memory** - 基于向量的语义记忆

### 权限预设

**最小权限**（read + write）
- Agent 可以读写文件和记忆
- 不能执行命令或访问网络

**标准权限**（read + write + exec + web）- 推荐
- Agent 可以执行命令和联网搜索
- 不能安装技能或修改配置

**完整权限**（全部 6 项）
- 解锁全部能力，包括 MCP 和管理操作
- 适合已建立信任的 agent

### 配合 openclaw-soul 使用

openclaw-setup 设计为在 [openclaw-soul](https://github.com/Kianzzz/openclaw-soul) BOOTSTRAP 完成后运行：

```
openclaw-soul（灵魂框架 + BOOTSTRAP）
    ↓
openclaw-setup（权限 + 模型 + 扩展 + 安全）
    ↓
开始使用
```

### 版本

当前版本：v1.0.0

### 许可

MIT License

### 作者

Kianzzz

### 相关链接

- GitHub: https://github.com/Kianzzz/openclaw-setup
- openclaw-soul: https://github.com/Kianzzz/openclaw-soul
