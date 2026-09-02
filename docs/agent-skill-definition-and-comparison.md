# Agent 与 Skill：定义、标准与跨工具对比

> 适用于 GitHub Copilot (VS Code)、Claude Code、OpenCode 及任何支持 Agent Skills 的 AI 编程工具
>
> 整理自 Fei Skills Hub 调研：VS Code 官方文档、agentskills.io 规范、Anthropic Agent Skills、OpenCode 官方文档、awesome-copilot
>
> 最后更新：2026-09-03

---

## 目录

- [1. 核心概念](#1-核心概念)
- [2. Agent 定义格式对比（Copilot / Claude Code / OpenCode）](#2-agent-定义格式对比)
- [3. Agent Skills 标准协议](#3-agent-skills-标准协议)
- [4. Skill vs Agent 能力边界](#4-skill-vs-agent-能力边界)
- [5. 跨工具兼容方案](#5-跨工具兼容方案)
- [6. Subagent 编排模式参考](#6-subagent-编排模式参考)
- [7. 实操建议](#7-实操建议)

---

## 1. 核心概念

### Agent（代理）

独立的执行体，有自己的**上下文窗口、工具集、模型配置**。由用户选择，或被编排器委派处理子任务。

- **Primary Agent（主代理）**：用户在会话中直接交互的助手，生命周期贯穿整个会话
- **Subagent（子代理）**：由主代理临时启动的专职 worker，只为某个委派任务存在，拥有独立的隔离上下文，返回压缩结果给父代理综合

**关键价值**：上下文隔离。子代理"永远清醒"（每个都带全新上下文），父代理保持全局判断力不被实现细节污染。

### Skill（技能）

按需加载的**知识包 + 流程指令**。本质是"教 agent 如何做特定任务"，而非独立的执行体。

### Agent vs Skill 一句话区分

> **Agent 是会做事的"员工"（独立执行体），Skill 是教员工做事方法的"操作手册"（知识+流程）。**

---

## 2. Agent 定义格式对比

### 2.1 存放位置

| 工具 | 项目级 | 用户级 |
|------|--------|--------|
| **Copilot (VS Code)** | `.github/agents/*.agent.md` | `~/Library/Application Support/Code/User/prompts/agents/` |
| **Claude Code** | `.claude/agents/*.md`（可递归子目录） | `~/.claude/agents/` |
| **OpenCode** | `.opencode/agents/*.md` | `~/.config/opencode/agents/` |
| **.agents 协议** | `.agents/agents/<name>/agent.md` | `~/.agents/agents/` |

### 2.2 Frontmatter 字段差异

| 能力 | Copilot (VS Code) | Claude Code | OpenCode |
|------|-------------------|-------------|----------|
| 必填 | `name` + `description` | `name` + `description` | `description`（**文件名即 agent 名**） |
| 工具白名单 | `tools: ['read','edit','search']`（**别名数组**） | `tools: Read, Grep, Bash`（**PascalCase 工具名**） | `permission: { edit: deny, bash: ask }`（**权限系统**，`tools` 已废弃） |
| 工具黑名单 | ❌ 无 | `disallowedTools: Write, Edit` | `permission` 的 `deny` |
| 委派白名单 | `agents: ['x','y']` | `tools: Agent(worker, researcher)` | `permission.task: { "orchestrator-*": allow }` |
| 控制台可见性 | `user-invocable: false` + `disable-model-invocation` | @-mention / `--agent` 调用 | `mode: subagent` + `hidden: true` |
| 模型 | `model: "Claude Sonnet 4"` | `model: sonnet/opus/haiku`（别名）或完整 ID | `model: "anthropic/claude-sonnet-4-20250514"`（provider/model 格式） |
| 权限模式 | ❌ 无 | `permissionMode: acceptEdits/auto/plan...` | `mode: primary/subagent/all` |
| 采样参数 | ❌ 无 | ❌ 无 | `temperature`、`top_p`、`steps` |
| 独有能力 | `handoffs`、`argument-hint` | `memory`、`isolation: worktree`、`background`、`skills` 预载 | `color`、`disable`、`prompt: {file:...}` |

### 2.3 同一 Agent 的三种写法示例

**Copilot (VS Code)**
```yaml
---
name: code-reviewer
description: "Reviews code for quality. Use when..."
tools: [read, search]
user-invocable: false
---
You are a code reviewer...
```

**Claude Code**
```yaml
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Grep, Glob, Bash
model: sonnet
---
You are a code reviewer...
```

**OpenCode**
```yaml
---
description: Reviews code for quality and best practices
mode: subagent
permission:
  edit: deny
  bash: deny
---
You are a code reviewer...
```

**结论：frontmatter 完全不同，不能直接互用；Markdown 正文（system prompt）三家通用，可 100% 复用。**

### 2.4 工具别名映射表（跨工具转换用）

| Copilot | Claude Code | OpenCode permission |
|---------|-------------|---------------------|
| `read` | `Read` | `read` |
| `edit` | `Edit`, `Write` | `edit` |
| `search` | `Grep`, `Glob` | `grep`, `glob` |
| `execute` | `Bash` | `bash` |
| `web` | `WebFetch`, `WebSearch` | `webfetch`, `websearch` |
| `todo` | `TodoWrite` | `todowrite` |
| `agent` | `Agent` | `task` |

---

## 3. Agent Skills 标准协议

### 3.1 来源与生态

- 由 **Anthropic 发起**、开源的开放标准（[agentskills.io](https://agentskills.io/)）
- 已获广泛采纳：**VS Code / GitHub Copilot / Claude Code / OpenCode / Cursor / Gemini CLI / Codex / Roo Code** 等（官方 Client Showcase）
- 这是目前**跨工具兼容性最好**的标准——skill 比 agent 更容易跨工具复用

### 3.2 结构

```
skill-name/
├── SKILL.md          # 必需：frontmatter + 指令
├── scripts/          # 可选：可执行代码
├── references/       # 可选：按需加载的文档
├── assets/           # 可选：模板、静态资源
└── ...
```

### 3.3 Frontmatter 字段（标准全部字段）

| 字段 | 必填 | 约束 |
|------|------|------|
| `name` | ✅ | 1-64 字符，小写字母数字+连字符，须与文件夹同名 |
| `description` | ✅ | 1-1024 字符，写清"做什么 + 何时用"，含触发关键词 |
| `license` | ❌ | 许可证名或引用许可证文件 |
| `compatibility` | ❌ | 环境要求（如"需 git/docker/联网"），1-500 字符 |
| `metadata` | ❌ | 任意键值映射（如 `author`、`version`） |
| `allowed-tools` | ❌ | **实验性**：空格分隔的预批准工具串，如 `Bash(git:*) Read` |

### 3.4 渐进式加载（Progressive Disclosure）

1. **发现**（~100 tokens）：只加载 `name` + `description`
2. **激活**（<5000 tokens 推荐）：任务匹配时才加载完整 `SKILL.md`
3. **执行**（按需）：按需读 references、跑 scripts

建议：SKILL.md 保持在 500 行以内，详细内容拆到 references/。

### 3.5 工具扩展字段（标准之外，各工具"加料"）

| 扩展字段 | 谁在用 | 用途 |
|---------|--------|------|
| `argument-hint` | VS Code | 斜杠调用输入提示 |
| `user-invocable` | VS Code | 是否显示为斜杠命令 |
| `disable-model-invocation` | VS Code / Claude Code | 禁止模型自动加载，仅手动调用 |
| frontmatter `hooks:` | Claude Code | 生命周期事件（`PreToolUse` 等）挂 shell 命令，实现**硬性权限控制** |
| `permission:` | OpenCode | 直接在 skill frontmatter 声明工具权限 |
| `skills:` 预载 / `context: fork` | Claude Code | 控制 skill 在哪个上下文运行 |

---

## 4. Skill vs Agent 能力边界

| 维度 | Agent (`.agent.md`) | Skill (`SKILL.md`) |
|------|---------------------|--------------------|
| 本质 | 独立的执行体（独立上下文、工具集、模型） | 按需加载的知识 + 流程 |
| 工具/mode/permission | ✅ **有**：`tools:` / `agents:` / `user-invocable` 等 | ❌ **标准层没有**，只能靠指令建议 |
| 生命周期 | 会话中可被委派、长期存在 | 激活后执行完即用即走 |
| 跨工具标准 | ❌ 无统一标准（各家 frontmatter 不同） | ✅ **Agent Skills 是统一标准** |
| 权限控制强度 | 声明式（hard） | 建议性（soft） |

### 关键结论

- **标准 Skill 协议层面不能定义 mode / permission**。唯一相关字段 `allowed-tools` 只是"预批准"（experimental），不是"严格限制"，且各工具实现不一。
- **Skill 对工具/权限的控制是"建议性"的**（agent 读了指令后"倾向于"那样做），权限拦截要靠 Agent 层的 `tools:` / `permission:` 或 Hook 硬性保证。
- 想要"带权限/模式控制的组件"→ 做成 **Agent**；想要"跨工具复用的流程知识"→ 做成 **Skill**，权限部分丢给调用方的 Agent 或 Hook。

---

## 5. 跨工具兼容方案

目前**没有官方标准能让一份 agent 文件被三个工具同时原生读取**。实践中有以下方案（按可靠度排序）：

### 方案 A：单一源 + 转换脚本（推荐）

`.agents/` 目录作为唯一 source of truth，用脚本生成各工具格式副本：

```
.agents/agents/<name>/agent.md    # 源（dot-agents 格式）
    ↓  sync-agents.sh 自动转换
.github/agents/<name>.agent.md    # Copilot 格式
.claude/agents/<name>.md          # Claude Code 格式
.opencode/agents/<name>.md        # OpenCode 格式
```

- 正文（system prompt）三家通用，只转 frontmatter
- 可进 CI 校验，防止副本漂移

### 方案 B：`.agents` 协议桥接

- 定位是"配置汇聚点"，统一放 MCP/AGENTS.md/Skills/Sub-Agents
- **未解决 frontmatter 翻译问题**；VS Code Copilot 原生**不读** `.agents/`（只认 `.github/agents/`）
- 仍处 DRAFT 阶段

### 方案 C：单文件"超集 frontmatter" + 多位置放置（有坑）

利用三工具都忽略未知字段的特性写超集，但 `tools` 格式冲突（数组 vs 逗号串）、能力映射不精确、难以排查，**不推荐**。

### 方案 D：符号链接

只解决位置，不解决格式和 `.agent.md` vs `.md` 命名差异，**不推荐**。

---

## 6. Subagent 编排模式参考

### 6.1 关键配置（VS Code）

```yaml
---
name: Coordinator
tools: ['agent', 'read', 'search', 'edit']
agents: ['Planner', 'Implementer', 'Reviewer']  # 委派白名单
---
```

- `agents:` 是**白名单**，`[]` = 谁也不许
- `user-invocable: false` → 从选择器隐藏，仅作 subagent
- `disable-model-invocation: true` → 禁止被其他 agent 委派
- 嵌套默认关闭：`chat.subagents.allowInvocationsFromSubagents`（默认 false）

### 6.2 经典编排模式

| 模式 | 说明 |
|------|------|
| **Coordinator and worker** | 一个编排者委派给窄专长的 worker（planner/implementer/reviewer） |
| **Multi-perspective review** | 并行跑 correctness/security/quality 多个视角，再综合 |
| **Research, then act** | 一个 subagent 收集事实，另一个基于事实实施 |
| **RUG (Repeat Until Good)** | 分解 → todo → 派活 → 独立验证 subagent → 失败重派，直到通过 |

### 6.3 参考实现

- `agents/rug-orchestrator.agent.md`：纯编排器，只用 `agent` + `todo` 两个工具，`agents: ['SWE', 'QA']`
- `agents/ai-team-*.agent.md`：AI Team Dev 三件套（Dev=实现 / Producer=规划不写码 / QA=独立验证）
- `agents/context7.agent.md`：VS Code `handoffs` 示例
- `agents/gem-orchestrator.agent.md`：`user-invocable` + `disable-model-invocation` 调用控制示例

---

## 7. 实操建议

1. **跨工具复用**：优先用 Skill（标准统一）；agent 用"单一源 + 转换脚本"模式
2. **描述即发现**：`description` 是触发入口，务必用"Use when..."模式 + 具体关键词，否则不会被委派/激活
3. **YAML 陷阱**：description 含冒号必须加引号；`name` 与文件夹不一致会静默失败
4. **最小工具集**：agent 只给职责所需工具，过多工具稀释专注度
5. **本仓库现状**：`.agents/agents/` 下已安装 AI Team 三件套 + RUG 编排器（双格式：`.agents/` 协议版 + `.github/agents/` VS Code 版）；`.agents/skills/` 下已有多个符合 Agent Skills 标准的 skill

---

## 参考链接

- [VS Code Agent Skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills)
- [VS Code Custom Agents](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
- [Agent Skills 规范](https://agentskills.io/specification)
- [Anthropic Skills 仓库](https://github.com/anthropics/skills)
- [OpenCode Agents](https://opencode.ai/docs/agents/)
- [Claude Code Sub-agents](https://code.claude.com/docs/en/sub-agents)
- [awesome-copilot](https://github.com/github/awesome-copilot)
- [.agents 协议](https://dotagentsprotocol.com/)
