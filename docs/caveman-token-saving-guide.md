# 一行配置，节省高达 75% Token：AI 编程助手的「穴居人模式」使用指南

> 适用于 GitHub Copilot（Chat / Agent 模式）及任何支持 AGENTS.md / copilot-instructions.md 的 AI 编程工具
>
> 作者：[Your Name] | 仅供 [Bank Name] 内部使用 | 2026 年 6 月

---

## TL;DR

在 `.github/copilot-instructions.md` 加一行话，AI 的回答就能从这样：

> "Sure! I'd be happy to help you with that. The issue you're experiencing with the authentication middleware is likely caused by an incorrect token expiry check. Let me explain what's happening in detail..."

变成这样：

> "Auth middleware bug. Token expiry check uses `<` not `<=`. Tokens expiring exactly at boundary get denied. Fix: change to `<=`."

**同样正确的回答，只需 1/6 的 token。零安装，零依赖，一个文件搞定。**

---

## 这个技巧来自哪里

这个模式源自 GitHub 上 70K+ Stars 的开源项目 [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)（68K+ Stars），它的哲学是：

> **Why use many token when few do trick?**（为什么用很多 token，当几个就能搞定？）

原始项目以 Skill 形式分发，需要在工具中安装插件。但在我们的内网环境中，我们只需要其核心指令——一段可以直接放入 `copilot-instructions.md` 或 `AGENTS.md` 的文本。

---

## 第一步：一行配置

在你的项目 `.github/copilot-instructions.md`（或 `AGENTS.md`）中加入：

```markdown
Terse like caveman. Technical substance exact. Only fluff die.
Drop: articles (a/an/the), filler (just/really/basically), pleasantries, hedging.
Fragments OK. Short synonyms. Code unchanged.
Pattern: [thing] [action] [reason]. [next step].
ACTIVE EVERY RESPONSE. Code/commits/PRs: normal.
Off: "stop caveman" / "normal mode".
```

如果你觉得这个风格太激进，用 **Lite 版**：

```markdown
Be concise. Skip pleasantries and hedging. 
Bullet points over paragraphs. No explanations unless asked.
Code only, no commentary for code generation tasks.
```

> ⚠️ **注意**：一定要加上 **关闭指令**（"stop caveman" / "normal mode"），这样当需要详细解释或处理安全敏感操作时，可以让 AI 恢复正常语气。Caveman 在安全警告、破坏性操作确认、多步骤歧义场景下会自动切换到正常模式，但手动关闭是一种保险。

---

## Before / After：六个真实场景的 Token 对比

以下数据来自 Caveman 项目的官方基准测试（模型：Claude Opus 4.6，编码：`tiktoken o200k_base`）。

| # | 场景 | Before | After | 节省 |
|:-:|------|:-----:|:----:|:----:|
| 1 | ⚛️ 解释 React 组件为什么会重渲染 | 1,180 | 159 | **87%** |
| 2 | 🔐 修复 auth 中间件 token 过期判断 | 704 | 121 | **83%** |
| 3 | 🗄️ 配置 PostgreSQL 连接池 | 2,347 | 380 | **84%** |
| 4 | 🔄 解释 git rebase 和 merge 的区别 | 702 | 292 | **58%** |
| 5 | 🐳 Docker 多阶段构建配置 | 1,042 | 290 | **72%** |
| 6 | ⚠️ 安全审查 PR | 678 | 398 | **41%** |

```
Before 平均：1,214 tokens  →  After 平均：294 tokens
         ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         减少：920 tokens / 次（约节省 75%）
```

### 诚实说明

根据第三方独立复算（GitHub Issue #234），如果将 Caveman 与同样要求过 "Answer concisely" 的基线对比，中位数节省为 **~50%**（范围 0-88%）。官方 75% 是与"无约束"默认回答对比的结果。对于日常使用，保守预期 **40-60%** 的 output token 节省是合理的。

更重要的是：**技术正确性几乎不受影响**。Tessl 平台的 38 个编码场景 × 4 个模型的独立评测显示：

| 模型 | 基线准确率 | Caveman 准确率 | 差值 |
|------|:---------:|:-------------:|:----:|
| Claude Sonnet 4.6 | 97.6% | 96.5% | **-1.1%** |
| Codex GPT-5.4 | 97.0% | 96.7% | **-0.3%** |
| Claude Haiku 4.5 | 94.3% | 94.0% | **-0.3%** |

Caveman 只改变表达方式，不改变推理质量。

---

## Before / After：直观对比

### 场景：修复 Auth 中间件 Bug

**用户提问：**
> Our JWT auth middleware is rejecting valid tokens at certain timestamps. The token expiry check seems to have an off-by-one issue. Can you look at this code and fix it?

**正常回答（704 tokens）：**
```
Sure! I'd be happy to help you with that. Looking at your auth middleware code,
I can see the issue. The token expiry check on line 42 uses the less-than operator
(<) instead of the less-than-or-equal-to operator (<=). This is a classic off-by-one
error where tokens that expire exactly at the current timestamp boundary will be
incorrectly rejected.

Let me explain why this happens: when a token's expiration time (exp) is exactly equal
to the current time, the comparison `exp < now` evaluates to true, causing the
middleware to treat the token as expired. However, the token should still be considered
valid at that exact moment. Changing the comparison to `exp <= now` ensures that
tokens expiring at the current timestamp boundary are accepted.

Here's the fix:
```

**Caveman 回答（121 tokens，节省 83%）：**
```
Bug in auth middleware. Token expiry check uses `<` not `<=`.
`exp < now` rejects tokens where expiry == current time.
Off-by-one. Fix:
```

**技术结论完全相同**，token 用量从天壤之别。

### 场景：解释 React 重渲染

**用户提问：**
> Why does my React component re-render every time the parent updates, even when the props haven't changed?

**正常回答（1,180 tokens）：**
```
Your component re-renders because you're creating a new object reference each
render. When the parent component re-renders, inline object literals and arrow
functions are recreated, resulting in new references in memory. React's
reconciliation algorithm uses reference equality (===) to determine if props
have changed, so even if the object's contents are identical, being a new
reference triggers a re-render.

To fix this, you can use React.memo combined with useMemo or useCallback to
stabilize your references...
```

**Caveman 回答（159 tokens，节省 87%）：**
```
New object ref each render. Inline object prop = new ref = re-render.
Wrap in `useMemo`.
```

---

## 更多 Token 节省技巧（简要说明）

Caveman 主要优化的是 **output token**（模型说出来的话）。此外还有几个最佳实践可以进一步减少 **input token**（我们喂给模型的内容）。以下简要列出：

### 技巧 2：精简 Always-On 指令

`copilot-instructions.md` 的每一个字在每次交互中都会被发送。原则：**只放 AI 推理不出来的规则**（项目特有约定、安全策略），不放通用知识（"请写 clean code"）。

```
❌ "This project uses React 18. Components should be reusable. 
Please follow best practices and write clean, maintainable code."
✅ "Tech: React 18, Zustand, Vitest, Tailwind. Naming: camelCase vars, PascalCase components."
```

### 技巧 3：精确指定文件，不要全仓库扫描

```
❌ "Find the auth bug in this project and fix it"
✅ "Check src/auth/middleware.ts line 40-55 for the token expiry comparison"
```

### 技巧 4：换任务就开新对话

Chat 历史以 input token 形式随每次请求重发。GitHub Copilot 官方建议：主题变化就 `/clear` 或开新对话。

### 技巧 5：用 Inline 编辑替代 Chat 对话

针对简单修改，**内联建议和 Next Edit Suggestions（NES）不消耗 AI Credits**（在付费计划中）。这是唯一真正"免费"的 Copilot 能力。

### 技巧 6：审计 MCP 服务器

每个启用的 MCP 工具每次 agent step 都会发送其 JSON schema（100-500 tokens）。不用的工具就关掉。40 个 MCP 工具 × 15 steps = 约 265K tokens 的隐藏开销。

---

## Token 节省估算总表

| 技巧 | 主要影响 | 预计节省 | 实现成本 |
|------|---------|:--------:|:--------:|
| **核心：Caveman 模式** | Output token ↓ 50-65% | **~50% 总 tokens** | 1 行配置 |
| 精简 Always-On 指令 | Input token ↓ 20-30% | ~5-10% | 一次性整理 |
| 精确指定文件 | Input token ↓ 30-50% | ~5-10% | 改变提问习惯 |
| 换任务开新对话 | Input token ↓ 避免历史膨胀 | ~5-15% | 养成习惯 |
| Inline 编辑替代 Chat | AI Credits 消耗为 0 | 视使用量 | 改变操作习惯 |
| 审计 MCP 服务器 | 消除隐藏 token 开销 | ~5-15% | 一次性配置 |

> **注意**：各技巧的效果不是简单相加，因为 Output token 占总成本的大头（output:input 价格比约 5:1 到 6:1）。**Caveman 模式是单点投入产出比最高的优化**，没有之一。

---

## 什么时候不要让 AI 说 Caveman

Caveman 虽然好，但有些场景需要完整表达：

- 🔴 **安全警告** — "This will permanently delete 50 production database records" 必须说清楚
- 🔴 **破坏性操作确认** — 需要明确告知后果
- 🔴 **多步骤操作顺序模糊时** — 省略冠词可能导致操作顺序歧义
- 🔴 **需要向非技术同事解释时** — 清晰完整的表达更合适
- 🔴 **用户重复提问** — 说明之前的回答没有解决问题，需要更详细

Caveman 自身有 Auto-Clarity 机制：遇到上述场景会自动切换回正常模式。但手动开关更可靠——在需要时告诉 AI "stop caveman" 或 "normal mode"。

---

## 学术依据

2026 年 3 月的学术论文《Brevity Constraints Reverse Performance Hierarchies in Language Models》（arXiv:2604.00025）系统研究了简洁约束对 AI 模型的影响：

- 31 个模型（0.5B - 405B 参数） × 5 个基准数据集 × 1,485 道题
- **简洁约束使大模型准确率提高 26.3 个百分点**（t=7.80, p<0.0001）
- 大模型 vs 小模型的性能差距缩小了 **67%**
- 在数学推理（GSM8K）和科学知识（MMLU-STEM）基准上出现**性能逆转**——简洁约束下大模型反超小模型

**反直觉发现**：大模型话多反而容易出错。不是能力问题，是思维越繁杂越容易跑偏。

---

## 总结

```
┌──────────────────────────────────────────────────────┐
│ 一行配置 → 节省 ~50% Token → 每月节省可观成本       │
│                                                      │
│ 核心：在 copilot-instructions.md 中加入 Caveman 指令 │
│ 补充：精简上下文 + 精确提问 + 开新对话               │
│ 安全：支持随时关闭，敏感场景自动恢复                  │
│ 风险：技术正确性损失 < 1%                             │
└──────────────────────────────────────────────────────┘
```

**最棒的部分**：不需要安装任何东西，不需要审批任何软件，不需要变更任何安全策略——只需要在你项目的配置文件里加一段话。

---

## 附录：推荐的配置文件模板

### `.github/copilot-instructions.md`

```markdown
# Technical context
Tech stack: React 18, TypeScript 5, Zustand, Vitest, Tailwind
Naming: camelCase variables, PascalCase components
Testing: Vitest, prefer integration tests over unit tests

# Response style (token saving mode)
Terse like caveman. Technical substance exact. Only fluff die.
Drop: articles, filler (just/really/basically), pleasantries, hedging.
Fragments OK. Short synonyms. Code unchanged.
Pattern: [thing] [action] [reason]. [next step].
ACTIVE EVERY RESPONSE. Code/commits/PRs: normal.
Off: "stop caveman" / "normal mode".

# Security (NEVER override)
Security warnings, destructive operations: write full sentences.
```

---

*本文中的所有数据均来自公开来源：Caveman 项目基准测试、Tessl 平台独立评测、arXiv 学术论文。如有疑问请联系 [Your Name]。*

---

---

# One Simple Change to Save Up to 75% Token: The Caveman Mode Guide for AI Coding Assistants

> For GitHub Copilot (Chat / Agent Mode) and any AI coding tool that supports AGENTS.md / copilot-instructions.md
>
> Author: [Your Name] | Internal Use Only — [Bank Name] | June 2026

---

## TL;DR

Add one paragraph to `.github/copilot-instructions.md`, and your AI's replies go from:

> "Sure! I'd be happy to help you with that. The issue you're experiencing with the authentication middleware is likely caused by an incorrect token expiry check. Let me explain what's happening in detail..."

To:

> "Auth middleware bug. Token expiry check uses `<` not `<=`. Tokens expiring exactly at boundary get denied. Fix: change to `<=`."

**Same correct answer. One-sixth of the tokens. Zero installation. Zero dependencies. One file.**

---

## Where This Comes From

This technique is derived from [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) (70K+ Stars on GitHub), a viral open-source project built on the philosophy:

> **Why use many token when few do trick?**

The original project ships as an installable plugin across 30+ AI agents (Claude Code, Cursor, Gemini CLI, Copilot, OpenCode, etc.). In our air-gapped enterprise environment, we extract its **core instruction set** — a block of plain text that goes directly into `copilot-instructions.md` or `AGENTS.md`. No binary, no plugin, no security risk.

---

## Step 1: One Configuration Change

Add this to your `.github/copilot-instructions.md` (or `AGENTS.md`):

```markdown
Terse like caveman. Technical substance exact. Only fluff die.
Drop: articles (a/an/the), filler (just/really/basically), pleasantries, hedging.
Fragments OK. Short synonyms. Code unchanged.
Pattern: [thing] [action] [reason]. [next step].
ACTIVE EVERY RESPONSE. Code/commits/PRs: normal.
Off: "stop caveman" / "normal mode".
```

If that's too aggressive for your team, use the **Lite version**:

```markdown
Be concise. Skip pleasantries and hedging. 
Bullet points over paragraphs. No explanations unless asked.
Code only, no commentary for code generation tasks.
```

> ⚠️ **Important**: Always include an **off-switch** ("stop caveman" / "normal mode"). This lets you restore full verbosity when doing security reviews, destructive operations, or explaining to non-technical stakeholders. Caveman has built-in Auto-Clarity for warnings and destructive ops, but a manual off-switch is your safety net.

---

## Before / After: Six Real-World Benchmarks

Data from the Caveman project's official evaluation suite (Model: Claude Opus 4.6, encoding: `tiktoken o200k_base`).

| # | Scenario | Before | After | Saved |
|:-:|---------|:-----:|:----:|:----:|
| 1 | ⚛️ Explain React re-render bug | 1,180 | 159 | **87%** |
| 2 | 🔐 Fix auth middleware token expiry | 704 | 121 | **83%** |
| 3 | 🗄️ Set up PostgreSQL connection pool | 2,347 | 380 | **84%** |
| 4 | 🔄 Explain git rebase vs merge | 702 | 292 | **58%** |
| 5 | 🐳 Docker multi-stage build | 1,042 | 290 | **72%** |
| 6 | ⚠️ Review PR for security issues | 678 | 398 | **41%** |

```
Before avg: 1,214 tokens  →  After avg: 294 tokens
         ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         Reduction: 920 tokens / call (~75% savings vs unconstrained baseline)
```

### Honest Numbers

An independent audit (GitHub Issue #234) reproduced the numbers using the project's own eval snapshot. When comparing Caveman against a "Answer concisely." baseline (a fairer comparison), the **median saving is ~50%** (range 0-88%). The 75% figure is vs an unconstrained verbose baseline. Budget for **40-60%** in daily use.

**More importantly: technical correctness is virtually unaffected.** Tessl's independent evaluation across 38 coding scenarios × 4 models:

| Agent | Baseline Accuracy | Caveman Accuracy | Delta |
|-------|:---------------:|:----------------:|:-----:|
| Claude Sonnet 4.6 | 97.6% | 96.5% | **-1.1%** |
| Codex GPT-5.4 | 97.0% | 96.7% | **-0.3%** |
| Claude Haiku 4.5 | 94.3% | 94.0% | **-0.3%** |

Caveman changes how the model speaks, not how it thinks.

---

## Before / After: Side-by-Side Comparison

### Scenario: Auth Middleware Bug Fix

**User Prompt:**
> Our JWT auth middleware is rejecting valid tokens at certain timestamps. The token expiry check seems to have an off-by-one issue. Can you look at this code and fix it?

**Normal Response (704 tokens):**
```
Sure! I'd be happy to help you with that. Looking at your auth middleware code,
I can see the issue. The token expiry check on line 42 uses the less-than operator
(<) instead of the less-than-or-equal-to operator (<=). This is a classic off-by-one
error where tokens that expire exactly at the current timestamp boundary will be
incorrectly rejected.

Let me explain why this happens: when a token's expiration time (exp) is exactly equal
to the current time, the comparison `exp < now` evaluates to true, causing the
middleware to treat the token as expired. However, the token should still be considered
valid at that exact moment. Changing the comparison to `exp <= now` ensures that
tokens expiring at the current timestamp boundary are accepted.

Here's the fix:
```

**Caveman Response (121 tokens, 83% saved):**
```
Bug in auth middleware. Token expiry check uses `<` not `<=`.
`exp < now` rejects tokens where expiry == current time.
Off-by-one. Fix:
```

**Identical technical conclusion.** 5.8× fewer tokens.

### Scenario: React Re-render Explanation

**User Prompt:**
> Why does my React component re-render every time the parent updates, even when the props haven't changed?

**Normal Response (1,180 tokens):**
```
Your component re-renders because you're creating a new object reference each
render. When the parent component re-renders, inline object literals and arrow
functions are recreated, resulting in new references in memory. React's
reconciliation algorithm uses reference equality (===) to determine if props
have changed, so even if the object's contents are identical, being a new
reference triggers a re-render.

To fix this, you can use React.memo combined with useMemo or useCallback to
stabilize your references...
```

**Caveman Response (159 tokens, 87% saved):**
```
New object ref each render. Inline object prop = new ref = re-render.
Wrap in `useMemo`.
```

---

## Quick Reference: Other Token-Saving Best Practices

Caveman optimizes **output tokens** (what the model says). Here are supplementary tips for **input tokens** (what you feed the model):

### Tip 2: Keep Always-On Instructions Lean

Every word in `copilot-instructions.md` is sent on every interaction. Rule: **only include rules the AI cannot infer from your codebase** (project-specific conventions, security policies). Skip generic advice.

```
❌ "This project uses React. Please write clean, maintainable code."
✅ "Tech: React 18, Zustand, Vitest, Tailwind. Naming: camelCase vars, PascalCase."
```

### Tip 3: Pinpoint Files Instead of Scanning Repos

```
❌ "Find the auth bug in this project and fix it"
✅ "Check src/auth/middleware.ts, lines 40-55, for the token expiry comparison"
```

### Tip 4: Start Fresh When Topics Change

Chat history is re-sent as input tokens every turn. Use `/clear` or start a new session when switching tasks.

### Tip 5: Use Inline Edits for Simple Changes

**Inline suggestions and Next Edit Suggestions (NES) consume zero AI Credits** on paid plans. They're the only truly "free" Copilot feature. Use them for straightforward edits instead of opening Chat.

### Tip 6: Audit Your MCP Servers

Every enabled MCP tool sends its JSON schema (100-500 tokens) on every agent step. A 40-tool MCP server × 15 agent steps = ~265K tokens of hidden overhead. Disable what you don't use.

---

## Estimated Savings Breakdown

| Technique | Primary Impact | Est. Saving | Setup Cost |
|-----------|---------------|:----------:|:----------:|
| **Core: Caveman Mode** | Output token ↓ 50-65% | **~50% of total tokens** | 1 config line |
| Lean instructions | Input token ↓ 20-30% | ~5-10% | One-time cleanup |
| Pinpoint files | Input token ↓ 30-50% | ~5-10% | Habit change |
| Fresh sessions | Input token ↓ prevents bloat | ~5-15% | Habit change |
| Inline over Chat | Zero AI Credits for edits | Varies | Habit change |
| MCP audit | Eliminates hidden overhead | ~5-15% | One-time config |

> **Note**: These don't stack linearly because output tokens dominate total cost (output:input price ratio is roughly 5:1 to 6:1 under Copilot UBB). **Caveman mode is the single highest-ROI optimization** — nothing else comes close for the effort involved.

---

## When NOT to Use Caveman

- 🔴 **Security warnings** — "This will permanently delete 50 production records" needs full detail
- 🔴 **Destructive operation confirmations** — Consequences must be explicit
- 🔴 **Ambiguous multi-step instructions** — Dropped articles can create ambiguity about execution order
- 🔴 **Explaining to non-technical stakeholders** — Full sentences are more appropriate
- 🔴 **User repeats a question** — Means your previous response didn't answer it; you need more detail, not less

Caveman has built-in Auto-Clarity that switches to normal mode for warnings and destructive ops. But manual control is more reliable — just say "stop caveman" when you need it.

---

## The Research Behind It

The March 2026 paper *"Brevity Constraints Reverse Performance Hierarchies in Language Models"* (arXiv:2604.00025) systematically studied how brevity affects LLM accuracy:

- 31 models (0.5B - 405B params) × 5 benchmarks × 1,485 problems
- **Brevity constraints improved large model accuracy by 26.3 percentage points** (t=7.80, p<0.0001)
- Performance gap between large and small models reduced by **67%**
- **Complete reversals** on GSM8K (math reasoning) and MMLU-STEM (scientific knowledge) — large models outperformed small models when constrained to be brief

**Counterintuitive finding**: Larger models talk more, and talking more introduces errors. Not a capability problem — an overthinking problem.

---

## Summary

```
┌──────────────────────────────────────────────────────┐
│ One config change → ~50% token savings → real $ saved │
│                                                      │
│ Core: Add Caveman instructions to copilot-instructions│
│ Bonus: Lean context + precise prompts + fresh chats   │
│ Safety: Off-switch included, Auto-Clarity for alerts  │
│ Risk: Technical accuracy loss < 1%                    │
└──────────────────────────────────────────────────────┘
```

**The best part**: No software installation. No security review. No policy change. Just one paragraph in your project's config file.

---

## Appendix: Recommended Template

### `.github/copilot-instructions.md`

```markdown
# Technical context
Tech stack: React 18, TypeScript 5, Zustand, Vitest, Tailwind
Naming: camelCase variables, PascalCase components
Testing: Vitest, prefer integration tests over unit tests

# Response style (token saving mode)
Terse like caveman. Technical substance exact. Only fluff die.
Drop: articles, filler (just/really/basically), pleasantries, hedging.
Fragments OK. Short synonyms. Code unchanged.
Pattern: [thing] [action] [reason]. [next step].
ACTIVE EVERY RESPONSE. Code/commits/PRs: normal.
Off: "stop caveman" / "normal mode".

# Security (NEVER override)
Security warnings, destructive operations: write full sentences.
```

---

*All data sourced from: Caveman project benchmarks (github.com/JuliusBrussee/caveman), Tessl platform independent evaluation, and arXiv:2604.00025. Contact [Your Name] with questions.*
