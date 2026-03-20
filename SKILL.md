---
name: openclaw-setup
description: OpenClaw 交互式配置向导。四步引导完成初始配置：权限开通 → 模型调优 → 能力扩展 → 安全加固。解决新部署 agent 权限过低无法工作、上下文窗口与模型不匹配导致卡死等常见问题。触发场景：(1) 用户说"配置openclaw"、"setup openclaw"、"openclaw配置" (2) 用户说"配置模型"、"配置权限"、"配置上下文"、"调优模型" (3) 用户说"添加MCP"、"配置MCP Server"、"安装MCP" (4) 用户说"openclaw安全配置"、"技能安全策略"、"安全加固" (5) 用户提到"openclaw-setup"或"配置向导"。注意：这是 OpenClaw 部署的第二步，建议在 openclaw-soul BOOTSTRAP 完成后使用。
---

# OpenClaw Setup — 交互式配置向导

四步引导：权限 → 模型调优 → 能力扩展 → 安全加固。每步都可单独执行，已完成的步骤自动跳过。

> **绝对禁止事项**：此技能在执行配置变更时，**绝对不能执行 `systemctl restart`、`systemctl stop`、`kill`、`pkill` 等任何会重启或停止 openclaw-gateway 的操作**。所有通过 `openclaw config set` 写入的配置会被 Gateway 自动热加载（config file watch），无需手动重启。重启 Gateway 会导致正在处理的消息丢失、用户等待超时。

---

## §1 [GATE] 环境检测

**每次触发此技能时，必须先执行环境检测。不允许跳过。**

运行检测脚本：

```bash
python3 scripts/setup_check.py
```

> 脚本路径相对于此 SKILL.md 所在目录。

解析 JSON 输出后，向用户展示当前状态总览：

```
OpenClaw 配置状态
━━━━━━━━━━━━━━━━
版本: {version}   工作区: {workspace_path}

权限:
  read: {✓/✗/—}  write: {✓/✗/—}  exec: {✓/✗/—}
  web:  {✓/✗/—}  mcp:   {✓/✗/—}  admin: {✓/✗/—}

模型:
  主模型: {primary or "未配置"}
  Fallback: {fallbacks list or "无"}
  contextTokens: {value or "未配置"}
  thinkingDefault: {value or "未配置"}

压缩: {compaction.mode or "未配置"}
心跳: {heartbeat.every or "未配置"}
MCP Servers: {count} 个
Cron Jobs: {count} 个

安全:
  DM策略: {dmPolicy or "未配置"}
  技能白名单: {skills.allowBundled or "未配置"}

openclaw-soul: {installed ? "已安装" : "未安装"}
```

图例：✓ = 已配置/已开启，✗ = 已配置为关闭，— = 未配置

**如果 `blocking: true`**（openclaw CLI 未找到）→ 告知用户需要先安装 OpenClaw，提供安装命令，终止本技能。

**如果 `ready: true`** → 继续进入 §2。

---

## §2 [REQUIRED] 欢迎与配置菜单

根据 §1 的检测结果，智能推荐需要配置的步骤。

用 AskUserQuestion 展示四步配置清单，支持多选：

```
AskUserQuestion:
  question: "以下是配置步骤，选择你要配置的项目（可多选）："
  header: "配置"
  multiSelect: true
  options:
    - label: "Step 1: 权限"
      description: "{当前权限摘要}。配置 agent 的读写/执行/联网/MCP/管理权限"
    - label: "Step 2: 模型调优"
      description: "{当前模型摘要}。配置主模型、fallback链、contextTokens、压缩模式、心跳"
    - label: "Step 3: 能力扩展"
      description: "{当前扩展摘要}。clawhub 技能、MCP Servers、Cron 定时任务、GitHub 同步"
    - label: "Step 4: 安全加固"
      description: "{当前安全摘要}。DM策略、Thinking级别、技能白名单"
```

**智能推荐逻辑**：
- 如果 write/exec 都是 false → description 中加 "（推荐）"
- 如果 primary 模型为 null → Step 2 加 "（推荐）"
- 如果所有安全配置为 null → Step 4 加 "（建议）"

用户选择后，按顺序执行选中的步骤。跳过未选中的步骤。

---

## §3 [REQUIRED] Step 1: 权限配置

### §3a 展示当前权限

读取 §1 检测结果中的 permissions，展示 6 项权限的当前状态和用途：

```
当前权限状态:
┌──────────┬────────┬──────────────────────────┐
│ 权限     │ 状态   │ 用途                      │
├──────────┼────────┼──────────────────────────┤
│ read     │ ✓ 开启 │ 读取工作区文件、记忆、配置 │
│ write    │ ✗ 关闭 │ 创建/修改文件、更新记忆     │
│ exec     │ ✗ 关闭 │ 执行 shell 命令            │
│ web      │ ✗ 关闭 │ 联网搜索和 URL 访问        │
│ mcp      │ — 未配 │ 连接 MCP Servers           │
│ admin    │ — 未配 │ 管理配置、安装技能          │
└──────────┴────────┴──────────────────────────┘
```

### §3b 用户选择等级

用 AskUserQuestion 展示三种预设组合：

```
AskUserQuestion:
  question: "选择权限等级："
  header: "权限"
  options:
    - label: "最小权限"
      description: "read + write。agent 只能读写文件，不能执行命令或联网。适合试用阶段。"
    - label: "标准权限（推荐）"
      description: "read + write + exec + web。agent 可以读写、执行命令、联网搜索。日常使用推荐。"
    - label: "完整权限"
      description: "全部 6 项开启。解锁 MCP 连接和管理操作。适合已建立信任的 agent。"
```

用户也可以在 Other 中输入自定义组合（如"read write exec mcp"）。

### §3c 生成命令

**权限配置是鸡生蛋问题**：agent 可能没有 admin 权限来修改自己的权限配置。所以这一步**必须生成命令让用户手动执行**，而不是 agent 自己执行。

根据用户选择的等级，生成 `openclaw config set` 命令：

```
请在服务器上执行以下命令：

ssh user@host << 'EOF'
openclaw config set permissions.read true
openclaw config set permissions.write true
openclaw config set permissions.exec true
openclaw config set permissions.web true
openclaw config set permissions.mcp false
openclaw config set permissions.admin false
EOF

执行完成后告诉我，我会验证配置是否生效。
```

**注意**：如果用户选了"完整权限"，提醒 admin 权限意味着 agent 可以自行安装技能和修改配置。

### §3d 验证

用户确认执行后，重新运行 `setup_check.py` 的权限检测部分，比对结果：

- 全部匹配 → "权限配置成功！" 进入下一步
- 部分不匹配 → 列出不匹配项，提供修复命令

权限详情参考 `references/permissions-guide.md`。

---

## §4 [REQUIRED] Step 2: 模型调优

权限开通后（至少有 exec），agent 可以通过 `openclaw config set` 直接配置，不再需要用户手动操作。

### §4a 模型链配置

读取当前模型配置。如果已有模型且用户满意 → 跳过。

如果需要配置，用 AskUserQuestion：

```
AskUserQuestion:
  question: "选择模型方案："
  header: "模型"
  options:
    - label: "高质量链（推荐）"
      description: "sonnet-4-5 → haiku-4-5 → gpt-4o-mini。推理强，有跨厂商保底。"
    - label: "性价比链"
      description: "sonnet-4-5 → gemini-2.5-flash。日常够用，降级成本低。"
    - label: "经济链"
      description: "haiku-4-5 → gpt-4o-mini → gemini-2.5-flash。全部用经济型模型。"
```

用户也可以 Other 中指定自定义模型。

配置命令（agent 自动执行）：

```bash
openclaw config set agents.defaults.model '{"primary":"claude-sonnet-4-5","fallbacks":["claude-haiku-4-5","gpt-4o-mini"]}'
```

如果使用自定义代理（从 §1 检测到 proxy 配置），提示用户确认代理地址是否正确。

### §4b 上下文窗口配置

根据选择的主模型，自动推荐 contextTokens：

| 模型 | 上下文窗口 | 推荐 contextTokens |
|------|-----------|-------------------|
| claude-sonnet-4-5 | 200K | 128K |
| claude-opus-4 | 200K | 128K |
| claude-haiku-4-5 | 200K | 128K |
| gpt-4o / gpt-4o-mini | 128K | 80K |
| gemini-2.5-pro/flash | 1M | 200K |

展示推荐值并询问是否调整：

```
根据你选择的主模型 claude-sonnet-4-5（200K 上下文），推荐 contextTokens = 128000。
这个值可以吗？如果需要调整请告诉我。
```

用户确认后执行：
```bash
openclaw config set agents.defaults.contextTokens 128000
```

### §4c 压缩策略

检查当前压缩配置。如果未配置：

```
AskUserQuestion:
  question: "上下文压缩模式："
  header: "压缩"
  options:
    - label: "default（推荐）"
      description: "智能压缩：自动摘要旧对话，保留关键信息，释放上下文空间。"
    - label: "safeguard"
      description: "安全模式：更保守的压缩策略，优先保留原始对话细节。"
    - label: "暂不配置"
      description: "使用系统默认行为"
```

配置命令：
```bash
openclaw config set agents.defaults.compaction.mode default
openclaw config set agents.defaults.compaction.maxHistoryShare 0.5
openclaw config set agents.defaults.compaction.model claude-haiku-4-5
```

### §4d 心跳配置

检查当前心跳配置。如果未配置：

```
AskUserQuestion:
  question: "心跳（定期自动唤醒）配置："
  header: "心跳"
  options:
    - label: "1小时（推荐）"
      description: "每小时自动整理记忆、检查状态。用 haiku 模型节省成本（约 $0.36/月）。"
    - label: "30分钟"
      description: "更频繁的自检。适合需要快速响应的场景。成本约 $0.72/月。"
    - label: "暂不配置"
      description: "不启用心跳，agent 仅在被召唤时活跃"
```

配置命令：
```bash
openclaw config set agents.defaults.heartbeat.every 1h
openclaw config set agents.defaults.heartbeat.target last
openclaw config set agents.defaults.heartbeat.model claude-haiku-4-5
openclaw config set agents.defaults.heartbeat.directPolicy allow
```

每项配置后立即 read-back 验证（`openclaw config get <key>`），确认写入成功。

模型详情参考 `references/model-reference.md`。

---

## §5 [OPTIONAL] Step 3: 能力扩展

这是选配步骤。用 AskUserQuestion 让用户选择要配置的扩展项：

```
AskUserQuestion:
  question: "选择要配置的扩展能力（可多选）："
  header: "扩展"
  multiSelect: true
  options:
    - label: "clawhub 技能安装"
      description: "从 clawhub 安装社区技能。需要 clawhub CLI。"
    - label: "MCP Servers"
      description: "连接外部工具（GitHub、Calendar、数据库等）。需要 mcp 权限。"
    - label: "Cron 定时任务"
      description: "设置定期执行的自动化任务。"
    - label: "GitHub 同步"
      description: "将 workspace 与 GitHub 仓库关联，版本控制配置文件。"
```

### §5a clawhub 技能安装

检查 clawhub CLI 状态（从 §1 检测结果获取）。

**clawhub 不可用** → 提供安装命令：
```bash
npm install -g clawhub
```

**clawhub 可用** → 使用 AskUserQuestion 让用户选择：

```
AskUserQuestion:
  question: "选择要安装的 clawhub 技能（可多选）："
  header: "Skills"
  multiSelect: true
  options:
    - label: "evoclaw"
      description: "自我进化身份框架（openclaw-soul 核心依赖）"
    - label: "self-improving"
      description: "自我反思和学习系统（openclaw-soul 核心依赖）"
    - label: "multi-search-engine"
      description: "多平台搜索引擎（Google、Bing、DuckDuckGo 等）"
```

用户选择后，逐个执行安装：
```bash
clawhub install <selected-skill>
```

安装前告知："正在安装 {skill}，可能需要 10-30 秒，请稍候..."

如果 openclaw-soul 检测到已安装 evoclaw 和 self-improving → 从选项中移除这两个，只显示 multi-search-engine。

### §5b MCP Servers

检查 mcp 权限是否开启。未开启 → 提示需要先在 Step 1 开启 mcp 权限。

已开启 → 展示 MCP Server 目录：

```
AskUserQuestion:
  question: "选择要安装的 MCP Server（可多选）："
  header: "MCP"
  multiSelect: true
  options:
    - label: "GitHub"
      description: "操作 GitHub 仓库：PR、Issues、CI 状态。需要 GitHub Token。"
    - label: "Filesystem（扩展文件访问）"
      description: "让 agent 安全访问 workspace 以外的指定目录。"
    - label: "Brave Search"
      description: "隐私优先的搜索引擎，替代内置 WebSearch。需要 API Key。"
```

用户选择后，逐个引导配置。对于需要凭证的 MCP Server，告知用户在哪里获取凭证，等用户提供后再配置。

每个 MCP Server 配置后运行 `openclaw mcp test <name>` 验证。

MCP Server 详情参考 `references/mcp-catalog.md`。

### §5c Cron 定时任务

展示 cron 概念和常用示例：

```
Cron 定时任务示例：
  - 每天早 9 点整理记忆："0 9 * * *"
  - 每周一发送周报："0 10 * * 1"
  - 每 6 小时检查状态："0 */6 * * *"

需要配置定时任务吗？如果需要请描述你想要的任务。
```

### §5d GitHub 同步

如果 GitHub MCP 已配置 → 可以设置 workspace 与 Git 仓库的关联：

```bash
cd ~/.openclaw/workspace && git init
git remote add origin <repo-url>
```

如果 GitHub MCP 未配置 → 提示先配置 GitHub MCP 或提供 SSH 仓库地址。

---

## §6 [OPTIONAL] Step 4: 安全加固

选配步骤。用 AskUserQuestion 让用户选择要配置的安全项：

```
AskUserQuestion:
  question: "选择要配置的安全选项（可多选）："
  header: "安全"
  multiSelect: true
  options:
    - label: "DM 策略"
      description: "控制谁可以给 agent 发消息。当前：{dmPolicy or '未配置'}"
    - label: "Thinking 级别"
      description: "控制 agent 的思考深度（影响 token 消耗）。当前：{thinkingDefault or '未配置'}"
    - label: "技能白名单"
      description: "控制哪些技能可用。当前：{skills.allowBundled or '未配置'}"
```

### §6a DM 策略

DM 策略是 **channel-scoped** 配置，需要指定通道名称。

```
AskUserQuestion:
  question: "DM 策略（谁可以给 agent 发私信）："
  header: "DM"
  options:
    - label: "pairing（推荐）"
      description: "仅配对用户可发消息。最安全的默认选项。"
    - label: "allowlist"
      description: "只允许白名单中的用户发消息。"
    - label: "open"
      description: "任何人都可以发消息。适合客服型 agent。"
    - label: "disabled"
      description: "禁用 DM。agent 不接受任何私信。"
```

配置（需要指定通道，如 feishu）：
```bash
openclaw config set channels.feishu.dmPolicy pairing
```

### §6b Thinking 级别

```
AskUserQuestion:
  question: "Agent 思考深度："
  header: "Thinking"
  options:
    - label: "adaptive（推荐）"
      description: "自动判断：复杂问题深度思考，简单问题快速回答。Claude 4.6 默认值。"
    - label: "medium"
      description: "固定中等思考深度。平衡质量和成本。"
    - label: "high"
      description: "所有问题都深度思考。质量最高但 token 消耗大。"
    - label: "off"
      description: "不使用思考模式。最快但可能影响推理质量。"
```

> 完整可选值：`off` | `minimal` | `low` | `medium` | `high` | `xhigh` | `adaptive`

配置：`openclaw config set agents.defaults.thinkingDefault adaptive`

### §6c 技能白名单

技能控制通过 `skills` 配置节点管理：

```
当前已安装的技能将被列出，你可以选择：
1. 允许全部已安装技能（默认行为）
2. 指定白名单，只允许列出的技能加载
3. 禁用特定技能
```

配置示例：
```bash
# 设置允许加载的内置技能列表
openclaw config set skills.allowBundled '["evoclaw","self-improving"]'

# 禁用特定技能
openclaw config set skills.entries.multi-search-engine.enabled false
```

每项安全配置后 read-back 验证。

安全详情参考 `references/security-rules.md`。

> **安全红线：此技能绝对不能执行 `systemctl restart openclaw-gateway` 或任何重启 Gateway 的操作。** 配置变更通过 `openclaw config set` 写入后，Gateway 会自动热加载（config file watch），无需重启。如果 agent 在配置过程中重启 Gateway，会导致正在处理的消息丢失、用户等待超时。

---

## §7 [REQUIRED] 总结验证

所有选中步骤完成后，执行最终验证。

### §7a 重新检测

重新运行 `setup_check.py`，获取最新状态。

### §7b 展示配置报告

对比 §1（初始状态）和 §7a（最终状态），生成变更表格：

```
OpenClaw 配置完成
━━━━━━━━━━━━━━━━

已配置项目:
┌─────────────────┬───────────┬───────────┐
│ 配置项          │ 之前      │ 现在      │
├─────────────────┼───────────┼───────────┤
│ permissions     │ 仅 read   │ 标准权限  │
│ primary model   │ 未配置    │ sonnet-4-5│
│ fallbacks       │ 无        │ haiku, 4o-mini │
│ contextTokens   │ 未配置    │ 128000    │
│ compaction      │ 未配置    │ default   │
│ heartbeat       │ 未配置    │ 1h        │
│ MCP Servers     │ 0 个      │ 2 个      │
│ thinkingDefault │ 未配置    │ adaptive  │
└─────────────────┴───────────┴───────────┘

未配置项目（可以后续随时配置）:
  - Cron 定时任务
  - GitHub 同步
  - 日志脱敏
```

### §7c 下一步提示

根据 openclaw-soul 的安装状态给出下一步建议：

**openclaw-soul 已安装且有 BOOTSTRAP.md** →
```
配置完成！下一步：agent 将通过 BOOTSTRAP.md 与你进行第一次深度对话，
了解你的工作方式、定义 agent 的个性、选一个名字。
这个过程会自动触发，你只需要正常和 agent 聊天就好。
```

**openclaw-soul 已安装但无 BOOTSTRAP.md** →
```
配置完成！openclaw-soul 已安装且 BOOTSTRAP 已完成。
agent 已经可以正常工作了。
```

**openclaw-soul 未安装** →
```
配置完成！建议下一步安装 openclaw-soul 来赋予 agent 自我进化能力：
  clawhub install openclaw-soul
安装后 agent 会获得身份框架、记忆系统和自我成长能力。
```

---

## 幂等性保证

每个配置步骤开头都检查当前状态。如果某项已配置且值合理：
- 展示当前值
- 询问"是否要修改？"
- 用户说不需要 → 跳过该项
- 用户说要修改 → 正常执行配置流程

这保证了重复运行 setup 不会覆盖已有的合理配置。

---

## 迭代改进

使用此技能后，如发现问题或有改进建议：

1. 描述遇到的具体问题或低效之处
2. 说明期望的行为或改进方向
3. 我会更新 SKILL.md 或相关资源并重新测试
