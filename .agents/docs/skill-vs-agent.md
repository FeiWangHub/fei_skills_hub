# Skill vs Agent：如何为一套跨系统自动化流程选型

> 场景：用 AI 全自动化打通企业 SDLC 流程（GitHub / Jenkins / Jira / SonarQube / CyberFlow 等），
> 核心问题是——应该全部用 Skill 实现，还是为每个工具建一个 Agent（Git Agent、Jenkins Agent、CyberFlow Agent……）？

## 核心区分

常被混淆的技术事实，它决定了答案：

- **Skill**：按需加载的"知识与流程"（progressive disclosure），注入**当前**上下文，和主 Agent 共享会话、共享记忆。
- **Agent（子代理）**：一个**独立上下文窗口**，有自己的 system prompt、工具集、权限甚至模型；作为工具被调用，只把**摘要**回传给主上下文。

所以二者的本质区别不是"能干什么"，而是**上下文边界**和**执行隔离**。

## 直接结论

**不要"一个工具一个 Agent"。** 正确姿势是分三层：工具层 → Skill 层 → 薄 Agent 层。

Jira / GitHub / Jenkins / Sonar / CyberFlow 这类东西，本质是"API 调用 + 少量领域约定"，属于 **Skill + MCP/CLI** 的范畴，不是 Agent。

## 为什么"一工具一 Agent"是反模式

1. 每个 Agent 都开新上下文、重载 system prompt 和工具定义 → **纯开销**。
2. Agent 之间**不共享记忆**：Jira Agent 不知道 GitHub Agent 刚建的 PR，编排成本全压回主线程。
3. 跨系统的关联信息（ticket 号 ↔ 分支 ↔ commit ↔ 构建号）无法自然流转。
4. 更贵、更慢、更笨。

## 什么时候用 Skill / 什么时候用 Agent

| 维度 | Skill | Agent |
|---|---|---|
| 用途 | 程序性知识、SOP、约定、模板 | 自包含的多步"任务/角色" |
| 上下文 | 与主流程共享 | 隔离，只回摘要 |
| 成本 | 低（按需加载） | 高（新上下文 + 重读 + 摘要） |
| 并行 | 天然串行 | 可并行 N 个 |
| 权限 | 继承主会话 | 可最小权限（如只读） |
| 模型 | 跟随主会话 | 可换便宜/专用模型 |
| 典型 | "怎么调 Jira API、怎么写 commit" | "扫这个仓库并给出安全结论" |

**用 Agent 的四个正当理由：**

1. 上下文隔离（大 diff、长日志不想污染主线程）
2. 并行（同时处理 N 个 PR / 仓库 / ticket）
3. 权限最小化（安全闸门 Agent 只读）
4. 换模型（体力活交便宜模型）

## Token 消耗

- **Agent 单次调用总体 token 通常更高**：新的 system prompt + 工具定义 + 重新读文件 + 结果摘要，全是额外成本。
- 但它**节省的是主上下文预算**，并换来并行与隔离。
- **判据**：一次性 API 调用用 Agent = 纯浪费；大型调查 / 并行 / 需要隔离的场景用 Agent = 划算。
- Skill 按需加载，开销远小于 Agent；但单个 Skill 过长也会持续占用上下文，要拆分。

## 推荐的 SDLC 自动化架构

三层：

1. **工具层**：Jira MCP、GitHub MCP（`gh`）、Jenkins MCP/API、Sonar、CyberFlow —— 提供原子工具。
2. **Skill 层（主投资点）**：每个领域一个 Skill，写清认证、约定、SOP、错误处理、典型流程。这是"怎么做"。
3. **Agent 层（薄，按任务切）**：
   - **Release Orchestrator** —— 编排 ticket→branch→PR→CI→闸门→merge→deploy
   - **Security Gate** —— 只读，聚合 Sonar + CyberFlow 结果给结论
   - **PR Review / Triage** —— 读大 diff，回摘要
   - **Incident** —— 独立排查

关键原则：**Agent 的边界画在"任务/职责"上，不是"工具"上。** 每个 Agent 内部照样调用这些 Skill 和工具。

## 一句话总结

**Skill 是能力与知识，Agent 是上下文与并行。** 这套流程 80% 的价值在 Skill 层，Agent 只在需要隔离、并行、限权时才加。
