# OpenClaw 模型与上下文参考

## 常见模型一览

| 模型 | 提供商 | 上下文窗口 | 推荐 contextTokens | 定价档位 | 特点 |
|------|--------|-----------|---------------|---------|------|
| claude-sonnet-4-5 | Anthropic | 200K | 128K | $$ | 性价比首选，推理强 |
| claude-opus-4 | Anthropic | 200K | 128K | $$$$ | 最高质量，复杂任务 |
| claude-haiku-4-5 | Anthropic | 200K | 128K | $ | 速度快，轻量任务 |
| gpt-4o | OpenAI | 128K | 80K | $$$ | 多模态强，通用 |
| gpt-4o-mini | OpenAI | 128K | 80K | $ | 快速轻量 |
| o3 | OpenAI | 200K | 100K | $$$$ | 深度推理 |
| o4-mini | OpenAI | 200K | 100K | $$ | 推理型性价比 |
| gemini-2.5-pro | Google | 1M | 200K | $$$ | 超长上下文 |
| gemini-2.5-flash | Google | 1M | 200K | $ | 速度极快 |

> 定价档位：$ = 经济 / $$ = 适中 / $$$ = 较贵 / $$$$ = 昂贵

---

## contextTokens 计算原则

`contextTokens` 控制单次对话的最大 token 数。设置过高会浪费额度（模型倾向填满窗口），设置过低会导致 agent 在复杂任务中途截断。

### 推荐公式

```
推荐 contextTokens = 模型上下文窗口 × 60~75%
```

**为什么不是 100%？**
- 系统提示（AGENTS.md + SOUL.md + 技能）占用约 10-20% 的上下文
- 留出余量避免触发上下文压缩过早介入
- 模型在接近上下文边界时质量下降

### 具体建议

| 上下文窗口 | 保守 (60%) | 推荐 (65%) | 激进 (75%) |
|-----------|-----------|-----------|-----------|
| 128K | 76K | 83K | 96K |
| 200K | 120K | 130K | 150K |
| 1M | 600K | 650K | 750K |

**配置命令**：
```bash
openclaw config set agents.defaults.contextTokens 128000
```

---

## 推荐模型链

模型链（Model Chain）是 primary + fallback 的组合。primary 模型不可用时（限流、故障），自动降级到 fallback。

### 高质量链（复杂任务优先）

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "claude-sonnet-4-5",
        "fallbacks": ["claude-haiku-4-5", "gpt-4o-mini"]
      },
      "contextTokens": 128000
    }
  }
}
```

- **主力**：claude-sonnet-4-5 — 推理强、性价比高
- **降级 1**：claude-haiku-4-5 — 同厂商，速度快
- **降级 2**：gpt-4o-mini — 跨厂商保底

### 性价比链（日常使用）

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "claude-sonnet-4-5",
        "fallbacks": ["gemini-2.5-flash"]
      },
      "contextTokens": 128000
    }
  }
}
```

- **主力**：claude-sonnet-4-5
- **降级**：gemini-2.5-flash — 速度极快、成本低

### 经济链（控制成本）

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "claude-haiku-4-5",
        "fallbacks": ["gpt-4o-mini", "gemini-2.5-flash"]
      },
      "contextTokens": 80000
    }
  }
}
```

- **主力**：claude-haiku-4-5 — 最便宜的高质量模型
- **降级**：gpt-4o-mini、gemini-2.5-flash — 都是经济型

---

## 压缩策略（Compaction）

当对话接近 contextTokens 上限时，OpenClaw 会压缩早期对话以释放上下文空间。

### 策略选项

| 策略 | 说明 | 适用场景 |
|------|------|---------|
| `default` | 将旧对话摘要为简短总结 | 通用（推荐） |
| `truncate` | 直接截断最早的对话 | 不需要历史的简单任务 |
| `sliding` | 滑动窗口，保留最近 N 轮 | 固定格式的重复性任务 |

### 配置示例

```bash
# 推荐：默认压缩模式
openclaw config set agents.defaults.compaction.mode default
openclaw config set agents.defaults.compaction.maxHistoryShare 0.5

# maxHistoryShare: 历史对话最多占上下文的比例（0.5 = 50%）
```

### 压缩模型

压缩操作本身也需要调用模型。可以指定一个轻量模型来降低压缩成本：

```bash
openclaw config set agents.defaults.compaction.model claude-haiku-4-5
```

如果不指定，默认使用 primary 模型进行压缩（成本较高）。

---

## 心跳（Heartbeat）配置

心跳是 agent 定期自动执行的任务。用于记忆整理、状态更新、主动关怀等。

### 核心参数

| 参数 | 说明 | 推荐值 |
|------|------|-------|
| `every` | 执行间隔 | `1h`（1小时） |
| `target` | 目标渠道 | `last`（最后活跃的渠道） |
| `model` | 心跳使用的模型 | `claude-haiku-4-5`（节省成本） |
| `directPolicy` | DM 发送策略 | `allow` |

### 配置示例

```bash
openclaw config set agents.defaults.heartbeat.every 1h
openclaw config set agents.defaults.heartbeat.target last
openclaw config set agents.defaults.heartbeat.directPolicy allow
```

### 心跳模型节省策略

心跳通常执行简单任务（整理记忆、发送问候），不需要高端模型。使用轻量模型可以大幅降低成本：

```bash
# 心跳用便宜模型
openclaw config set agents.defaults.heartbeat.model claude-haiku-4-5

# 主对话用高质量模型
openclaw config set agents.defaults.model.primary claude-sonnet-4-5
```

**成本对比**（假设每小时 1 次心跳，每次约 2000 tokens）：
- claude-sonnet-4-5: ~$0.006/次 → ~$4.3/月
- claude-haiku-4-5: ~$0.0005/次 → ~$0.36/月
- gemini-2.5-flash: ~$0.0003/次 → ~$0.22/月

---

## 自定义代理（Custom Proxy）

如果通过自建代理访问模型 API：

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "claude-sonnet-4-5"
      },
      "proxy": {
        "url": "https://your-proxy.example.com:3000",
        "apiKey": "your-api-key"
      }
    }
  }
}
```

代理模式下，所有模型请求通过指定 URL 转发，API key 附加在请求头中。
