# Code Cup Evaluation Skill — 代码审查报告

| 项目 | 值 |
|---|---|
| 审查对象 | `.agents/skills/code-cup-evaluation-skill/` |
| 版本 | 0.1.0 (draft) |
| 审查日期 | 2026-09-19 |
| 审查范围 | `SKILL.md`、`README.md`、`IMPLEMENTATION-PLAN.md`、`code/`（13 个模块 + 5 个测试套件）、`templates/`（6 个）、`references/`（5 个）、`.agents/agents/codecup-eval-*` 三个 agent 定义 |
| 代码总量 | 6,764 行 |
| 审查方式 | 静态阅读 + 实际执行（prepare/merge 端到端复现 + 全部测试套件跨版本运行） |

---

## 1. 总体结论

这是一个**设计水准明显高于实现水准**的项目。

架构思路（确定性优先、两阶段 prepare/merge、程序拥有全部算术、评测者只判定性维度、默认拒绝的网络白名单、无 LLM 生成 HTML）是正确且成熟的，文档质量很高，措辞诚实（甚至主动记录了 4 个已修复缺陷和已知局限）。测试套件是标准库实现，在 Python 3.9 / 3.11 / 3.14 上**全部通过**。

但是，**两阶段工作流的核心数据契约在 `merge` 中被破坏**：`merge` 会用评测者返回的分数整体覆盖程序计算出的确定性分数（D1/D2/D4/D5），而随附的提示词模板恰恰引导评测者把这四个维度填成 `0`。结果是：**同一份代码库，总分可能在 100 与 45 之间摆动，取决于评测者是否"顺手"复述了它本不该管的维度。**

这属于评分正确性缺陷，不是风格问题。当前状态下该 skill 不能用于真实评审。

### 严重程度汇总

| 编号 | 问题 | 级别 | 状态 |
|---|---|---|---|
| C1 | `merge` 用评测分数覆盖确定性分数，评分不可复现 | **P0 阻断** | 已复现 |
| C2 | 提示词模板要求评测全部 7 个维度，与 header / agent 定义直接矛盾 | **P0 阻断** | 已复现 |
| C3 | `merge` 覆盖置信度，使"评审发现过多"的降级规则失效 | **P1 高** | 已复现 |
| C4 | `templates/result.schema.json` 无任何代码校验 | **P1 高** | 静态确认 |
| C5 | `aggregator.py` 的多轮中位数 / 分歧降级逻辑未接线（死代码） | **P1 高** | 静态确认 |
| C6 | 文档声称的抖动退避（jitter）未实现 | **P2 中** | 静态确认 |
| C7 | 出处（provenance）字段在完整运行后仍是 `unversioned` / `not-run` | **P2 中** | 已复现 |
| C8 | 外发通道模块与"不需要外部端点"的主叙事冲突，无调用方 | **P3 低** | 静态确认 |

---

## 2. P0 — 阻断级问题

### C1. `merge` 用评测者返回的分数覆盖确定性分数

**位置**：`code/judge_io.py:212-232`

```python
judge_scores = agent.get("scores") or {}
combined = dict(record.get("scores") or {})

for key in SCORE_KEYS:          # SCORE_KEYS = 全部 7 个维度
    if key in judge_scores:
        combined[key] = judge_scores[key]     # ← 无条件覆盖，不区分维度归属
```

`judge_adapter.parse_and_validate` 要求返回对象**必须包含全部 7 个维度键**（缺少任一即抛 `JudgeValidationError: Missing score key: d1_security_and_compliance`）。因此评测者**必然**会返回 D1/D2/D4/D5 的取值，而 `merge` **必然**会用这些值覆盖程序算出的确定性分数。

程序的确定性计算（`prepare` 阶段的结果、`deterministic_rationales`、`deterministic_evidence`）在 `merge` 之后仍保留在记录里，但**已经不参与任何计算**，只作为展示用的死数据。

**复现（已实际执行）**

构造一份 D4/D5 本应满分的仓库：`SKILL.md` + 3,007 字节 README + 5 个测试文件。

`prepare` 阶段的确定性结果：

```
scores:  {d1: 5, d2: 5, d4: 5, d5: 5, d3: 0, d6: 0, d7: 0}
pending: ['d3_code_quality', 'd6_business_value', 'd7_innovation']
D4: "README present with 2 doc file(s), 3007 bytes"
D5: "5 test file(s) detected"
```

随后对**同一份仓库**，只改变 `judge-scores.json` 中 D1/D2/D4/D5 的取值：

| 评测者返回的 D1/D2/D4/D5 | 最终总分 |
|---|---|
| `5, 5, 5, 5`（复述了正确值） | **100.0** |
| `0, 0, 0, 0`（按模板填写） | **45.0** |

**同一份代码库，总分相差 55 分。** 而且第二种情况下，记录里同时存在互相矛盾的数据：

```
scores['d4_documentation']              = 0
deterministic_rationales['d4_documentation'] = "README present with 2 doc file(s), 3007 bytes"
```

报表会显示 D4 = 0 分，同时旁边写着"README 存在，3,007 字节"。审计轨迹自相矛盾。

**根因**：`judge_adapter.JudgeRequest` 确实携带了 `deterministic_scores` 字段（`judge_io.py:113`），但 `build_prompt` 的替换表里**没有它** —— 确定性分数从未被渲染进提示词。评测者看不到 D1/D2/D4/D5 的正确答案，只能自己猜或填 0；而 `merge` 又无条件采纳。

`references/judge-prompt-assembly.md` 明确要求 bundle 应包含"the deterministic statistics already computed by the static layer"，`codecup-eval-scorer` 也说"Copy them through unchanged if the request shows them" —— 但请求文件里根本没有这些数据。

**影响**：违反 `SKILL.md` 的核心承诺"Deterministic-first pipeline"、"the program owns all arithmetic"、"reproducible and auditable"。同时违反 `IMPLEMENTATION-PLAN.md` §7.4 中声称已修复的 Defect 2（"the deterministic-first design was not implemented"）——该缺陷在 `prepare` 中修好了，在 `merge` 中又漏了回来。

**建议修复**（三处，缺一不可）

1. `judge_io.merge`：只覆盖 `judge_dimensions_pending` 中列出的维度，其余保持程序算出的值：

```python
judge_dims = set(record.get("judge_dimensions_pending") or [])
for key in SCORE_KEYS:
    if key in judge_scores and key in judge_dims:
        combined[key] = judge_scores[key]
```

2. `judge_adapter.build_prompt`：把确定性分数渲染进提示词（模板加 `{{deterministic_scores}}`），并明确标注"只读、不要修改"。可参照 `codecup-eval-scorer` 的既有措辞。

3. 校验层：`parse_and_validate` 应接受**仅包含待判维度**的响应，或在 `merge` 中拒绝评测者对非待判维度给出的、与程序结果不一致的值。当前"必须返回全部 7 个键"的规则，本身就是 C2 的成因之一。

---

### C2. 提示词模板与 header、agent 定义三方矛盾

**位置**：`templates/judge-prompt-template.md:36-49`

模板的 `## Scoring Dimensions` 段落要求评测者给**全部 7 个维度**打分，`## Required Output JSON` 的示例也是 7 个键齐全。

但同一个请求文件的 header 写着：

```
<!-- dimensions_to_score: d3_code_quality, d6_business_value, d7_innovation -->
```

而 `codecup-eval-scorer/agent.md` 明确指示：

> You do **not** score D1, D2, D4, or D5. Those are already computed by the program from repository facts. Copy them through unchanged if the request shows them; do not re-judge them.

实测 `judge-requests/TEAM_001.md` 的 `## Scoring Dimensions` 段落确实列出全部 D1–D7。

**影响**：提示词是评分行为的第一驱动。模板要求 7 个维度，header 与 agent 定义要求 3 个维度，且没有任何地方告诉评测者 D1/D2/D4/D5 的正确取值。评测者的行为因此不确定 —— 这正是 C1 造成分数摆动的直接触发条件。同时，模板要求评测 D1（安全合规），与"安全维度由无 LLM 的静态门禁决定"的设计原则冲突。

**建议修复**：让模板由 `dimensions_to_score` 驱动，只渲染待判维度；`## Required Output JSON` 示例改为只含待判维度；若 C1 的修复方案 3 未被采纳，则在模板中显式给出确定性分数并要求原样复述。

---

## 3. P1 — 高优先级问题

### C3. `merge` 覆盖置信度，静态发现降级规则失效

**位置**：`code/judge_io.py:243`

```python
record["confidence"] = agent.get("confidence", record.get("confidence", "medium"))
```

`orchestrator.py:171-178` 在 `prepare` 阶段根据静态发现计算了置信度（>2 个 review 级发现 → `low`），但 `merge` 直接用评测者自报的置信度覆盖了它。

`SKILL.md` 的规则是："`low`: judge reported `low`, **or more than two review-severity findings**" —— 后半句在 `merge` 之后完全失效。

**实测证据**（来自一次 `codecup-eval-sample` 运行；该样例运行数据已不再随仓库提交）：

| 提交 | review 级发现数 | 记录中的置信度标签 |
|---|---|---|
| TEAM_001 | **12** | **high** |
| TEAM_002 | 15 | medium |
| TEAM_003 | 34 | medium |

TEAM_001 有 12 条待人工复核的静态发现，却带着 `high` 置信度标签，并且以第 1 名出现在仪表盘上。目前它恰好仍被 `human_review_required: True` 拦住（因为 `prepare` 阶段已置位且 `merge` 用 `or` 保留了），所以**没有直接导致漏审**，但置信度这个标签本身已经不可信 —— 而 `SKILL.md` 规定"low confidence + high rank 必须转人工"，这条规则现在是靠另一条路径兜住的，属于侥幸而非设计。

**建议修复**：置信度取程序与评测者的**较差**值，而不是让评测者覆盖：

```python
_ORDER = {"low": 0, "medium": 1, "high": 2}
program_conf = record.get("confidence", "medium")
judge_conf = agent.get("confidence", program_conf)
record["confidence"] = min(program_conf, judge_conf, key=_ORDER.get)
```

### C4. 结果 schema 存在但从未被校验

`templates/result.schema.json` 定义了完整的字段契约，`SKILL.md` 称其为"the authoritative field-level contract"并要求"orchestrator must reject any result object that violates the contract"。

但代码中**没有任何地方引用或加载该文件**（全仓库检索 `result.schema.json` 只命中文档与 schema 自身）。`orchestrator` 从不校验产出对象。

实际后果已经可见：`execution-state.json` 中的记录带有 `classification`、`deterministic_rationales`、`judge_evidence`、`metrics`、`scoring_status`、`judge_request` 等 schema 未定义的字段（schema 缺少 `additionalProperties: false`，所以严格来说不算违规，但也说明 schema 与实现已各自演化）。更实质的是，schema 的 `required` 列表中包含 `human_review_required` 与 `evidence`，而 `hard-failed` 记录确实包含这些字段 —— 这一点是对的，说明 schema 是按实现反推的，而非反过来约束实现。

**建议修复**：在 `merge` 与 `scan-only` 写盘前，用 schema 校验每条记录（可用 `jsonschema`，或在受限环境下写一个轻量校验函数，与项目"零依赖"取向一致）。同时给 schema 补 `additionalProperties: false`，或明确标注哪些字段是允许的扩展。

### C5. 多轮评测的中位数与分歧降级逻辑未接线

`aggregator.py` 提供了 `reconcile_passes`（多轮取中位数、计算 spread、合并证据）与 `derive_confidence`（按 spread 降级），`test_pipeline.py` 也对它们做了测试。

但这两个函数**只被测试调用，不被生产代码调用**。`judge_io.merge` 自行实现了单轮逻辑（`weighted = sum(...)`），从未处理 `passes` 列表。

`IMPLEMENTATION-PLAN.md` §7.3 声称已验证"a two-pass judge disagreement of 4 bands produced a median score with `low` confidence" —— 该行为只在测试中存在，实际管道无法产生。

**影响**：`SKILL.md` 描述的"两个评测 pass 用中位数调和、分歧降低置信度"这一风险控制手段，在当前实现中不存在。评测者是一个单点，其偏差没有任何交叉校验（`codecup-eval-verifier` 只查证据是否成立，不提供第二个分数）。

**建议修复**：要么在 `merge` 中接入 `aggregate()` 以支持多 pass（`judge-scores.json` 已可承载数组形式），要么从文档和测试中移除该能力描述，避免"文档承诺了不存在的控制措施"。

---

## 4. P2 / P3 — 中低优先级问题

### C6. 文档声称的抖动退避未实现

`SKILL.md`（Concurrency and Throughput Design → Required queue behaviors）写明需要 "exponential backoff and jittered retry"。

`judge_transport.py:139-141` 的实现：

```python
delay = self.config.backoff_seconds * (2**attempt)
self._sleep(delay)
```

是指数退避，但**没有 jitter**，注释里却写着 `# Exponential backoff with jitter to avoid synchronised retries`。注释与代码不符。

同节还提到 "dead-letter queue for permanent failures" —— 未实现（失败后直接抛 `RuntimeError`）。考虑到 `judge_transport` 本就不是主路径，优先级不高，但注释应改正，文档应标注为未实现。

### C7. 完整运行后出处字段仍为未版本化

`orchestrator._provenance()` 是硬编码的：

```python
"rubric_version": "unversioned",
"prompt_version": "unversioned",
"model_version": model_version,   # 默认 "not-run"
```

实测已完整跑完（`judge_merged: 3`, `done: 3`）的 `codecup-eval-sample/execution-state.json`，每条记录仍是：

```
rubric_version: 'unversioned', prompt_version: 'unversioned', model_version: 'not-run'
```

而 `templates/score-rubric.yaml` 首行就是 `version: 1`，`prepare` 也确实构造了 `prompt_version="1"`。

**影响**：`SKILL.md` 把出处信息列为审计与可复现性的关键（"provenance metadata appended to each result: ... rubric_version, prompt_version, model_version ..."），但实际产出全是占位符。`model_version: 'not-run'` 在已判分记录上尤其误导。

**建议修复**：从 rubric 文件读取 `version`，从模板内容哈希派生 `prompt_version`，`merge` 阶段写入真实模型标识。

### C8. 外发通道模块与主叙事冲突

`judge_transport.py`（154 行）是本仓库唯一允许发起网络连接的模块，并在文件头声明"the ONLY module in the pipeline permitted to open a network connection"。

但 `SKILL.md` 与 `references/two-phase-workflow.md` 反复强调"there is no separate LLM API to configure, and the pipeline never calls an endpoint on the primary path"，`README.md` 同样如此。

该模块没有任何生产调用方（`orchestrator` 的四个子命令都不引用它）。对于一家受监管企业的内部工具，保留一个默认拒绝、但确实具备外发能力的模块，会扩大安全评审面。

**建议**：要么将其明确标记为"未接线 / 参考实现"并在 `IMPLEMENTATION-PLAN.md` §7.2 的"Not yet implemented"表中登记（目前该表未列此项），要么在无实际需求时移除，减少安全评审负担。

### 其他次要观察

- `code/.gitignore` 含 `out/`，但 `code/__pycache__/` 已在工作区生成（未被提交，仅提示本地运行痕迹）。
- `aggregator.py` 与 `orchestrator.py` 各自定义了一份 `SCORE_KEYS`（重复定义），`judge_adapter.py` 还定义了第三份。三处需同步修改，是 C1 类缺陷的温床。建议收敛到单一来源。
- `report_generator.render_dashboard` 的表格对长文本列使用 `white-space: nowrap`，配合 `.scroll` 容器可横向滚动，行为正确；但对超长 team name 无截断，建议加 `max-width` + `text-overflow`。
- `IMPLEMENTATION-PLAN.md` §7.4 的缺陷日志（Defect 1–4）写得很好，但 Defect 2 的结论"已修复"与 C1 的现状不符，建议复核该表并补记本次发现。

---

## 5. 已验证通过的部分

以下为实际执行验证，非文档转述。

### 测试套件：全部通过，跨版本兼容

| 套件 | Python 3.9.6 | Python 3.11 | Python 3.14 |
|---|---|---|---|
| `test_gates.py` | PASS | PASS | PASS |
| `test_pipeline.py` | PASS | PASS | PASS |
| `test_deterministic_scorer.py` | PASS | PASS | PASS |
| `test_metrics.py` | PASS | PASS | PASS |
| `test_judge_io.py` | PASS | PASS | PASS |

`SKILL.md` 声明的 "tested_with: Python 3.9 and 3.14" **属实**。测试覆盖质量不错，尤其 `test_merge_is_idempotent`（验证重复 merge 不重复计数 judge stage、证据、token）和 `test_oversized_entry_file_is_truncated_not_dropped`（验证入口文件超限时截断而非丢弃）是有针对性的。

> 注：`test_merge_is_idempotent` 中 `_valid_entry()` 返回的是**全部 7 个维度**的完整分数，因此该测试恰好绕过了 C1 —— 测试通过的同时缺陷存在。建议补充一个"评测者只返回待判维度 / 返回 0"的用例。

### 值得肯定的设计

1. **静态扫描的上下文感知分级**（`static_scanner.py`）。把"同一字符串在可执行代码中是风险、在测试夹具与文档中是常态"这一判断显式建模为 `classify_context`，并区分 `hard_fail` / `review` 两档。附带的模块 docstring 用表格说明了映射规则。这是很扎实的工程设计 —— 直接避免了"任何写了安全文档的仓库都被误杀"这一常见失败模式。测试中也专门覆盖了"文档里的 `curl|sh` 不算 hard fail"。

2. **确定性优先的维度拆分**（`deterministic_scorer.py`）。D1/D2/D4/D5 由仓库事实判定，D3/D6/D7 交给评测者，且**每个确定性分数都携带证据与 rationale**，以满足与评测者相同的证据契约。这个"证据契约对程序与模型同等适用"的思路是正确的。

3. **报表生成的安全性**（`report_generator.py`）。全部插值经 `html.escape(quote=True)`，无 CDN、无外部字体、无网络依赖，`referrer` 设为 `no-referrer`。测试验证了恶意 `<script>` 队名被转义、输出中不含 `http://` / `https://`。符合"绝不让 LLM 写 HTML"的原则。

4. **`measured` / `estimated` / `none` 三级 token 标注**（`metrics.py`）。不把启发式估算伪装成计费数据，且 `TokenUsage.merge` 保留**最弱**的证据来源，批次汇总按 stage 而非按记录聚合（避免真实 measured 数据被同一记录中的 estimated 标签掩盖）。这是很多同类工具会做错的地方。

5. **评测阶段时间被单独隔离**。`judge_wall_clock` 明确排除在 `total_elapsed_s` 之外，并说明"包含空闲时间，是上界而非计算时间"。诚实的度量设计。

6. **文档分层清晰**。`SKILL.md`（模型要执行的规则）/ `README.md`（人类决策用）/ `references/`（过长的细节）/ `code/`（可执行逻辑）四层分工明确，且 `README.md` 开头专门说明了为何不把规则写在 README 里（避免漂移）。`references/main-subagent-architecture.md` 还主动更正了自己先前的错误论断（"An earlier version of this document claimed VS Code subagents are blocking... That was wrong."），这种自我纠错在项目文档中很少见。

7. **无凭据存储、无硬编码密钥**。全仓库检索未发现任何真实凭据；`templates/allowlist.json` 与 manifest 模板中的域名均为 `example.internal` 占位符，符合仓库的 air-gapped 安全要求。

---

## 6. 修复优先级建议

**必须修复后才能投入使用**

1. **C1 + C2 一起修**（同一根因）。核心改动是让 `merge` 只采纳待判维度，并让提示词把确定性分数作为只读事实传给评测者。修复后应补充回归测试：评测者返回 0 时，最终总分必须与评测者复述正确值时的总分一致。
2. **C3**：置信度取较差值，恢复静态发现降级规则。

**应在正式评审前完成**

3. **C4**：接入 schema 校验，使"reject any result object that violates the contract"成为事实而非声明。
4. **C5**：接入多轮中位数逻辑，或删除该能力描述与相应测试。

**可排期**

5. C6 修正注释、C7 填充真实出处、C8 明确未接线状态或移除。
6. 收敛 `SCORE_KEYS` 的三处重复定义。

---

## 7. 一句话评价

**架构是 A，文档是 A，实现的核心数据契约是 D。**

`prepare` 阶段的确定性计算做得很好，`merge` 阶段却把自己刚算出来的结果丢掉了 —— 而随附的提示词模板恰好引导评测者用 0 覆盖它们。这个缺陷不会报错、不会崩溃，只会静默地把总分从 100 变成 45，且在报表上留下"README 3,007 字节"与"D4 = 0 分"并存的矛盾记录。测试套件之所以全绿，是因为唯一的端到端测试恰好传入了完整正确的 7 维分数。

修掉 C1/C2/C3 之后，这个 skill 的工程质量与它的设计野心就匹配了。

---

*报告基于 commit `3ac3a15`（分支 `main`）。所有"已复现"结论均通过实际执行 `orchestrator.py prepare/merge` 与运行全部测试套件得出。*
