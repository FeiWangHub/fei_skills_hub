# 10 — Industry Rubrics & Sources

Evidence base for this rubric design. Use it to defend the chosen dimensions/weights.

## 1. Existing skill-evaluation tools (benchmark of approaches)

| Tool | Scoring model | Max | Deterministic / LLM | Key focus |
|---|---|---|---|---|
| `softaworks/agent-toolkit` · `skill-judge` (⭐2,460) | 8 dimensions | 120 | LLM judge | **Knowledge delta** (expert knowledge − what the model already knows); mindset, anti-patterns, progressive disclosure |
| `Terryc21/skill-reviewer` (⭐53) | multi-lens, no single grade | — | LLM judge | file:line citations, severity cards |
| `agentskill-sh/ags` · `review-skill` (⭐37) | 10 dimensions | 50 | LLM/rubric | description-as-trigger, conciseness, freedom calibration |
| `UseAI-pro/openclaw-skills-security` · `skill-vetter` (⭐72) | 4-tier verdict | SAFE/WARN/DANGER/BLOCK | prompt-only | security vetting |
| `jkeskikangas/skills` · `reviewing-skills` (⭐11) | 7 weighted dims, archetype profiles | 1.0–5.0 | hybrid (+ `score.py`) | mathematical formula, critical caps |
| `halfmoon-mind/rubric-evaluator` (⭐7) | 6 sections / 31 items | S–F | hybrid (17 rules + 14 model) | BLOCKER/MAJOR/MINOR gates |
| `webkong/skill-quality-check` (⭐2) | 5 dimensions | 100 ±5 | static + rubric | description 40% / body 40% |
| `NVIDIA/SkillEvaluator` | 3 tiers | 0–100 + Lift | multi-tier engine | Tier1 quality weights + Tier3 **Skill Lift** |
| `sayed3li97/skillscore` (⭐4) | 7 categories A–G | 100 (−15 penalty) | deterministic | 27 lint rules, safety penalty |
| `sakhilchawla/skillkit` | 20 lint rules / 4 cats | pass/fail + bench | deterministic | spec, security, best practices |
| `elonmust26/skillcheck` | penalty + Jaccard collision | 100 | deterministic | trigger quality + collisions |

**Notable weights borrowed for this rubric:**
- NVIDIA Tier-1 quality weights: Correctness .35 / Discoverability .25 / Reliability .25 / Efficiency .15.
- NVIDIA Skill Lift bands: ≥ +5% PASS, −10%..+5% NEUTRAL, ≤ −10% FAIL.
- `jkeskikangas` deterministic formula and critical-check caps.
- `rubric-evaluator` severity gates (BLOCKER → F).

## 2. Industry frameworks

| Framework | Use in this rubric |
|---|---|
| Enterprise hackathon 5-pillar rubric (Business impact 25 / Technical 25 / Innovation 20 / Security 15 / Feasibility 15) | Starting point for macro weights |
| SPACE framework (Satisfaction, Performance, Activity, Communication, Efficiency) | Business-value/ROI phrasing |
| Forrester TEI (time saved × frequency × rate; error/rework avoidance) | Business-value quantification checklist |
| Static code health (cyclomatic < 15, duplication < 3%, test coverage, bus factor ≥ 2, conventional commits) | Source-project D3/D5 inputs |

## 3. Security frameworks

| Source | Finding / use |
|---|---|
| OWASP Top 10 for LLM Applications | LLM01/02/06/07/10 checklist (`04`) |
| OWASP Top 10 for Agentic AI (ASI01–ASI10) | Agent-specific checklist (`04`) |
| Snyk "ToxicSkills" (2026) | 36.8% of public skills vulnerable; 13.4% critical; NL-instruction attack pattern → motivates judge isolation |
| Least privilege / air-gap rules | Hard-fail gates for external calls, credential access, unpinned remote fetch |

## 4. Token & context economy

- Idle context tax = Σ tokens(description) across installed skills.
- Progressive disclosure: L1 metadata (~100 tokens) / L2 body (<500 lines) / L3 lazy.
- Knowledge-delta density target: Expert > 70%, Activation ≈ 20%, Redundant ≈ 0.
- Trigger collision: keep Jaccard similarity between descriptions < 0.40.

## 5. Sources (for audit trail)

- Agent Skills spec: agentskills.io/specification · github.com/anthropics/skills
- GitHub Copilot custom agents: docs.github.com/en/copilot (custom agents configuration)
- OpenCode agents: opencode.ai/docs/agents · /permissions · /config
- Skill-eval tools: the GitHub repos in §1
- OWASP GenAI Security Project: genai.owasp.org
- Snyk ToxicSkills research (2026)
