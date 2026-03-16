# OpenClaw 技能安全策略与审核规则

## 三种安装策略

当 agent 需要安装新技能时，安全策略决定了审核严格程度。

### 策略 1: Self-Build Only（最严格）

只允许安装用户自己创建或本地已有的技能。禁止从 clawhub 或任何远程来源安装。

```bash
openclaw config set security.skillPolicy self-build-only
```

**适用场景**：高安全要求环境、不信任第三方技能、仅使用自建技能。

**行为**：
- `clawhub install <skill>` → 拒绝
- 本地 `skills/` 目录的技能 → 允许
- fallback 目录的离线技能 → 允许

### 策略 2: clawhub with Audit（推荐）

允许从 clawhub 安装技能，但必须先审核。agent 下载技能后不立即启用，而是先运行安全检查，展示审核报告，等用户确认后才安装。

```bash
openclaw config set security.skillPolicy clawhub-audit
```

**适用场景**：日常使用，在便利性和安全性之间取得平衡。

**行为**：
- `clawhub install <skill>` → 下载到临时目录 → 运行审核 → 展示报告 → 用户确认 → 安装
- 审核不通过 → 展示风险详情，用户可以强制安装或拒绝

### 策略 3: Trust Verified（最宽松）

信任 clawhub 上标记为 verified 的技能，自动安装。未 verified 的技能仍需审核。

```bash
openclaw config set security.skillPolicy trust-verified
```

**适用场景**：追求效率，信任 clawhub 的审核流程。

**行为**：
- verified 技能 → 自动安装
- 未 verified 技能 → 走 clawhub-audit 流程

---

## 内置审核规则

以下规则用于评估技能的安全性。clawhub-audit 和 trust-verified 策略都使用这套规则。

### Red Flags（危险信号）

在技能的 `scripts/` 目录中检测以下模式。命中任何一条即标记为高风险。

#### 危险命令

| 模式 | 说明 | 风险 |
|------|------|------|
| `exec(` / `eval(` | 动态代码执行 | 可能执行任意代码 |
| `rm -rf` / `rmdir` | 递归删除 | 可能删除重要文件 |
| `curl` / `wget` | 下载远程内容 | 可能引入恶意内容 |
| `nc` / `netcat` / `ncat` | 网络连接工具 | 可能建立反向 shell |
| `chmod 777` | 开放全部权限 | 安全配置被破坏 |
| `>/dev/tcp/` | Bash 网络重定向 | 数据外传 |
| `pip install` + 非标准源 | 安装未知 Python 包 | 供应链攻击 |

#### 混淆技术

| 模式 | 说明 | 风险 |
|------|------|------|
| `base64 -d` / `base64.b64decode` | Base64 解码执行 | 隐藏恶意代码 |
| `\\x` 转义序列 >50 字符 | Hex 编码字符串 | 混淆真实内容 |
| `$'\x...'` Bash ANSI-C 引用 | Shell 转义 | 绕过关键词检测 |
| `gzip -d` + `eval` | 压缩+执行链 | 隐藏 payload |

#### 凭证访问

| 模式 | 说明 | 风险 |
|------|------|------|
| 读取 `~/.ssh/` | SSH 密钥 | 密钥泄露 |
| 读取 `~/.aws/` / `~/.config/gcloud/` | 云凭证 | 云账户被接管 |
| 读取 `*.env` / `.env.*` | 环境变量文件 | 泄露 API keys |
| 读取 `openclaw.json` 中的 token/key | OpenClaw 凭证 | agent 被劫持 |
| 读取 `~/.gitconfig` + credential | Git 凭证 | 仓库被入侵 |

### 权限分析

比较技能声明需要的权限和实际操作需要的权限。

**过度请求**：技能声明需要 `admin` 权限，但实际只有读写操作 → 可疑
**权限升级**：技能尝试修改 `openclaw.json` 的 permissions 部分 → 严格禁止
**隐式需求**：技能没有声明需要 `web` 权限，但脚本中有 `curl` 调用 → 标记

### 模式识别

#### 外部通信

| 模式 | 说明 | 风险等级 |
|------|------|---------|
| 硬编码外部 URL（非 localhost） | 技能连接外部服务 | 中 |
| 动态构造 URL（字符串拼接） | 运行时才能确定目标 | 高 |
| WebSocket 连接 | 持久化外部通信 | 高 |
| DNS 查询（非标准端口） | 可能的数据通道 | 高 |

#### 数据外传模式

| 模式 | 说明 | 风险等级 |
|------|------|---------|
| 读取文件 → 编码 → HTTP POST | 经典外传模式 | 高 |
| 读取环境变量 → 写入远程 | 凭证收集 | 高 |
| 收集系统信息 → 发送 | 侦察行为 | 中 |

---

## 风险等级与决策

审核完成后，根据命中的规则数量和严重程度，给出风险等级和处理建议。

### 无风险

**条件**：没有命中任何 Red Flag，权限声明与实际一致，无外部通信。

**处理**：自动安装，不需要用户确认。

**展示**：
```
[SAFE] skill-name — 审核通过，无安全风险
  - 0 Red Flags
  - 权限匹配: read, write
  - 无外部通信
```

### 低风险

**条件**：命中 1-2 条非关键规则（如使用了 `curl` 但目标是知名 API），或权限有轻微过度请求。

**处理**：列出风险点，询问用户是否继续安装。

**展示**：
```
[LOW RISK] skill-name — 发现 2 个关注点
  1. scripts/fetch.py:12 — 使用 curl 访问 api.github.com
  2. 声明需要 exec 权限（实际仅用于运行 Python 脚本）

  是否继续安装？[y/n]
```

### 高风险

**条件**：命中关键 Red Flag（凭证访问、代码混淆、数据外传模式），或命中 3+ 条规则。

**处理**：明确警告，列出所有风险，**默认不安装**。用户必须显式确认才能安装。

**展示**：
```
[HIGH RISK] skill-name — 发现 4 个安全风险
  1. [CRITICAL] scripts/init.sh:8 — base64 解码后执行: base64 -d <<< "..." | bash
  2. [CRITICAL] scripts/collect.py:23 — 读取 ~/.ssh/id_rsa
  3. [HIGH] scripts/report.py:45 — POST 数据到 http://unknown-domain.com/collect
  4. [MEDIUM] 声明需要 admin 权限但无明显管理操作

  ⚠️ 强烈建议不要安装此技能。
  如果你确定信任来源，输入 CONFIRM 强制安装。
```

### 阻止

**条件**：检测到权限升级尝试（修改自身权限），或明确的恶意行为模式（反向 shell、加密货币挖矿特征）。

**处理**：**拒绝安装**，无法绕过。

**展示**：
```
[BLOCKED] skill-name — 检测到恶意行为，拒绝安装
  1. [CRITICAL] 尝试修改 permissions.admin = true（权限升级）
  2. [CRITICAL] 建立到 45.33.xx.xx:4444 的反向连接

  此技能已被阻止安装。如果你认为这是误判，请联系技能作者或在 GitHub 上报告。
```

---

## 配置命令汇总

```bash
# 查看当前安全策略
openclaw config get security

# 设置技能安装策略
openclaw config set security.skillPolicy <self-build-only|clawhub-audit|trust-verified>

# 设置 DM 策略（谁可以给 agent 发消息）
openclaw config set dm.policy <allowlist|open|blocklist>

# 设置 API 限额（月度美元上限）
openclaw config set security.spendingLimit 50

# 设置 Thinking 级别
openclaw config set thinking.level <none|low|medium|high>

# 设置日志脱敏
openclaw config set security.logSanitize true

# 查看技能审核日志
openclaw security audit-log
```
