# Top 100 Popular AI Coding Skills

Compiled from popular tools, repos, and prompt patterns across the AI coding ecosystem.
URLs link to the closest equivalent open-source repo, tool, or pattern. Many skills are
prompt-based patterns without a single canonical repository.

---

## Development Workflow (20)

| # | Skill | Risk | URL / Source |
|---|-------|------|-------------|
| 1 | **Code Review** | - | [google/complete-ability](https://github.com/google/eng-practices/blob/master/review/) (Google eng practices) |
| 2 | **Git Commit Message Generator** | - | [commitizen/cz-cli](https://github.com/commitizen/cz-cli) |
| 3 | **PR Description Writer** | - | [release-drafter/release-drafter](https://github.com/release-drafter/release-drafter) |
| 4 | **Changelog Generator** | - | [github-changelog-generator/github-changelog-generator](https://github.com/github-changelog-generator/github-changelog-generator) |
| 5 | **Code Refactoring** | - | Prompt pattern — no single repo |
| 6 | **Dead Code Finder** | - | [jshiell/checkstyle-idea](https://github.com/jshiell/checkstyle-idea) + prompt pattern |
| 7 | **Code Smell Detector** | - | [SonarSource/sonarqube](https://github.com/SonarSource/sonarqube) |
| 8 | **Boilerplate Generator** | - | Prompt pattern — no single repo |
| 9 | **Git Rebase Helper** | - | [newren/git-filter-repo](https://github.com/newren/git-filter-repo) |
| 10 | **Merge Conflict Resolver** | - | [sbdchd/merge-bot](https://github.com/anthropics/codereview.nvim) (similar pattern) |
| 11 | **Blame Investigation** | - | Git built-in (`git blame`), prompt pattern |
| 12 | **Branch Strategy Advisor** | - | [nvie/gitflow](https://github.com/nvie/gitflow) / Prompt pattern |
| 13 | **Release Tagging** | - | [semantic-release/semantic-release](https://github.com/semantic-release/semantic-release) |
| 14 | **Monorepo Dependency Graph** | 🔴 Risky | [nrwl/nx](https://github.com/nrwl/nx) |
| 15 | **Test File Generator** | - | Prompt pattern — no single repo |
| 16 | **TODO Tracker** | - | [todo-comments.nvim](https://github.com/folke/todo-comments.nvim) |
| 17 | **Documentation Generator** | - | [tealdeer-rs/tealdeer](https://github.com/mitsuhiko/mkdocs-autoclean) / [pydocmd](https://github.com/NiklasRosenstein/pydoc-markdown) |
| 18 | **Type Migration** | - | [microsoft/TypeScript](https://www.typescriptlang.org/docs/handbook/migrating-from-javascript.html) |
| 19 | **API Version Manager** | - | Prompt pattern — no single repo |
| 20 | **Patch Note Summarizer** | - | [release-drafter/release-drafter](https://github.com/release-drafter/release-drafter) |

## Testing & QA (12)

| # | Skill | Risk | URL / Source |
|---|-------|------|-------------|
| 21 | **Unit Test Writer** | - | [codium-ai/pr-agent](https://github.com/Codium-ai/pr-agent) |
| 22 | **Integration Test Builder** | - | Prompt pattern — no single repo |
| 23 | **E2E Test Generator** | - | [playwright-ai](https://playwright.dev/) / [cypress-io/cypress](https://github.com/cypress-io/cypress) |
| 24 | **Test Coverage Auditor** | - | [istanbuljs/nyc](https://github.com/istanbuljs/nyc) / [coveragepy](https://github.com/nedbat/coveragepy) |
| 25 | **Mock/Fake Generator** | - | [MockK/mockk](https://github.com/mockk/mockk) / [pytest-mock](https://github.com/pytest-dev/pytest-mock) |
| 26 | **Property-Based Test Builder** | - | [HypothesisWorks/hypothesis](https://github.com/HypothesisWorks/hypothesis) |
| 27 | **Fuzz Test Generator** | - | [google/oss-fuzz](https://github.com/google/oss-fuzz) |
| 28 | **Performance Test Scenario Builder** | - | [grafana/k6](https://github.com/grafana/k6) |
| 29 | **Mutation Test Runner** | 🔴 Risky | [stryker-mutator/stryker-js](https://github.com/stryker-mutator/stryker-js) |
| 30 | **Regression Test Detector** | - | Prompt pattern — no single repo |
| 31 | **Snapshots Test Updater** | 🔴 Risky | [facebook/jest](https://github.com/facebook/jest#snapshot-testing) |
| 32 | **Test Data Seeder** | - | Prompt pattern — no single repo |

## Backend Development (12)

| # | Skill | Risk | URL / Source |
|---|-------|------|-------------|
| 33 | **REST API Scaffolder** | - | [swagger-api/swagger-codegen](https://github.com/swagger-api/swagger-codegen) |
| 34 | **GraphQL Schema Builder** | - | [graphql/graphql-code-generator](https://github.com/dotansimha/graphql-codegen) |
| 35 | **Database Migration Creator** | - | [golang-migrate/migrate](https://github.com/golang-migrate/migrate) |
| 36 | **API Contract Test Generator** | - | [pact-foundation/pact-js](https://github.com/pact-foundation/pact-js) |
| 37 | **Error Handler Standardizer** | - | Prompt pattern — no single repo |
| 38 | **Middleware Generator** | - | Prompt pattern — no single repo |
| 39 | **Event Handler Builder** | - | [Particular/NServiceBus](https://github.com/Particular/NServiceBus) / Prompt pattern |
| 40 | **Job Scheduler Setup** | - | [node-cron/node-cron](https://github.com/node-cron/node-cron) |
| 41 | **Rate Limiter Implementer** | - | [ulule/limiter](https://github.com/ulule/limiter) |
| 42 | **Pagination Builder** | - | Prompt pattern — no single repo |
| 43 | **Webhook Handler Generator** | - | [svix/svix-webhooks](https://github.com/svix/svix-webhooks) |
| 44 | **Idempotency Pattern** | - | Prompt pattern — no single repo |

## Frontend Development (10)

| # | Skill | Risk | URL / Source |
|---|-------|------|-------------|
| 45 | **React Component Generator** | - | [codemod-dev](https://github.com/codemod-dev/codemod) / [vitejs/vite](https://github.com/vitejs/vite) |
| 46 | **Accessible UI Builder** | - | [reach/reach-ui](https://github.com/reach/reach-ui) / [radix-ui](https://github.com/radix-ui) |
| 47 | **CSS/Tailwind Styler** | - | [tailwindlabs/tailwindcss](https://github.com/tailwindlabs/tailwindcss) |
| 48 | **Form Builder + Validator** | - | [react-hook-form](https://github.com/react-hook-form/react-hook-form) / [colinhacks/zod](https://github.com/colinhacks/zod) |
| 49 | **State Management Scaffolder** | - | [pmndrs/zustand](https://github.com/pmndrs/zustand) / [reduxjs/redux-toolkit](https://github.com/reduxjs/redux-toolkit) |
| 50 | **Router Configurer** | - | [remix-run/react-router](https://github.com/remix-run/react-router) |
| 51 | **i18n Extractor** | - | [i18next/i18next](https://github.com/i18next/i18next) |
| 52 | **Design Token Sync** | - | [amzn/style-dictionary](https://github.com/amzn/style-dictionary) |
| 53 | **Bundle Analyzer** | 🔴 Risky | [webpack-contrib/webpack-bundle-analyzer](https://github.com/webpack-contrib/webpack-bundle-analyzer) |
| 54 | **Animation Generator** | - | [motiondivision/motion](https://github.com/motiondivision/motion) / [css-animation](https://github.com/css-animation/css-animation-book) |

## DevOps & Infrastructure (12)

| # | Skill | Risk | URL / Source |
|---|-------|------|-------------|
| 55 | **CI Pipeline Builder** | - | [actions/starter-workflows](https://github.com/actions/starter-workflows) |
| 56 | **Dockerfile Optimizer** | - | [hadolint/hadolint](https://github.com/hadolint/hadolint) |
| 57 | **K8s Manifest Generator** | - | [kubernetes-sigs/kustomize](https://github.com/kubernetes-sigs/kustomize) |
| 58 | **Terraform Module Scaffolder** | - | [hashicorp/terraform](https://github.com/hashicorp/terraform) |
| 59 | **Secrets Scanner** | - | [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) |
| 60 | **Deployment Rollback Guide** | - | Prompt pattern — no single repo |
| 61 | **Infrastructure Diff** | - | [gruntwork-io/terragrunt](https://github.com/gruntwork-io/terragrunt) |
| 62 | **Container Health Check** | - | Prompt pattern — no single repo |
| 63 | **Log Aggregator Config** | - | [elastic/beats](https://github.com/elastic/beats) |
| 64 | **Service Mesh Config** | - | [istio/istio](https://github.com/istio/istio) |
| 65 | **DNS/CDN Setup Advisor** | - | Prompt pattern — no single repo |
| 66 | **Monitoring Dashboard Creator** | - | [grafana/grafana](https://github.com/grafana/grafana) |

## Security (10)

| # | Skill | Risk | URL / Source |
|---|-------|------|-------------|
| 67 | **Secret Leaks Scanner** | - | [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) / [trufflesecurity/trufflehog](https://github.com/trufflesecurity/trufflehog) |
| 68 | **Dependency CVE Auditor** | 🔴 Risky | [dependabot/dependabot-core](https://github.com/dependabot/dependabot-core) |
| 69 | **OWASP Compliance Checker** | - | [OWASP/owasp-mstg](https://github.com/OWASP/owasp-mstg) |
| 70 | **PII Detector** | - | [presidio-analyzer](https://github.com/microsoft/presidio) |
| 71 | **JWT/Token Analyzer** | 🔴 Risky | [auth0/node-jsonwebtoken](https://github.com/auth0/node-jsonwebtoken) |
| 72 | **CORS Policy Auditor** | - | Prompt pattern — [Mozilla CORS docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) |
| 73 | **Input Validation Builder** | - | [colinhacks/zod](https://github.com/colinhacks/zod) / [hapijs/joi](https://github.com/hapijs/joi) |
| 74 | **Security Headers Config** | - | [helmetjs/helmet](https://github.com/helmetjs/helmet) |
| 75 | **SAST Rule Customizer** | - | [SonarSource/sonarqube](https://github.com/SonarSource/sonarqube) / [semgrep/semgrep](https://github.com/semgrep/semgrep) |
| 76 | **Threat Model Generator** | 🔴 Risky | [tm4n/tm4n](https://github.com/OWASP/threat-dragon) |

## Data & AI (8)

| # | Skill | Risk | URL / Source |
|---|-------|------|-------------|
| 77 | **ETL Pipeline Builder** | - | [apache/airflow](https://github.com/apache/airflow) |
| 78 | **SQL Query Optimizer** | 🔴 Risky | [pganalyze/pg_stat_statements](https://github.com/pganalyze/pg_stat_statements) |
| 79 | **Data Quality Validator** | - | [great-expectations/great_expectations](https://github.com/great-expectations/great_expectations) |
| 80 | **ML Model Trainer** | 🔴 Risky | [huggingface/transformers](https://github.com/huggingface/transformers) |
| 81 | **Feature Store Setup** | - | [feast-dev/feast](https://github.com/feast-dev/feast) |
| 82 | **Model Eval Dashboard** | - | [wandb/weave](https://github.com/wandb/wandb) |
| 83 | **Data Migration Validator** | - | Prompt pattern — no single repo |
| 84 | **Embedding Pipeline** | 🔴 Risky | [sentence-transformers](https://github.com/UKPLab/sentence-transformers) |

## Productivity & Meta (8)

| # | Skill | Risk | URL / Source |
|---|-------|------|-------------|
| 85 | **Code Review Assistant** | - | [github/codeql](https://github.com/github/codeql) |
| 86 | **Onboarding Guide Generator** | - | Prompt pattern — no single repo |
| 87 | **Architecture Diagram Builder** | 🔴 Risky | [mermaid-js/mermaid](https://github.com/mermaid-js/mermaid) / [adrai/flowchart.js](https://github.com/adrai/flowchart.js) |
| 88 | **Dependency Graph Mapper** | 🔴 Risky | [nrwl/nx](https://github.com/nrwl/nx) / [madge](https://github.com/pahen/madge) |
| 89 | **Tech Debt Auditor** | - | Prompt pattern — no single repo, inspired by [SonarQube](https://github.com/SonarSource/sonarqube) |
| 90 | **API Documentation Writer** | - | [Redocly/redoc](https://github.com/Redocly/redoc) / [stoplightio/elements](https://github.com/stoplightio/elements) |
| 91 | **Error Log Analyzer** | - | Prompt pattern — no single repo |
| 92 | **Runbook Generator** | - | Prompt pattern — no single repo |

## Niche & Specialized (8)

| # | Skill | Risk | URL / Source |
|---|-------|------|-------------|
| 93 | **Smart Contract Auditor** | 🔴 Risky | [trailofbits/manticore](https://github.com/trailofbits/manticore) |
| 94 | **Mobile App Scaffolder** | - | [expo/expo](https://github.com/expo/expo) / [flutter/flutter](https://github.com/flutter/flutter) |
| 95 | **Microservice Communication Mapper** | - | Prompt pattern — no single repo |
| 96 | **Feature Flag Manager** | - | [unleash/unleash](https://github.com/unleash/unleash) / [launchdarkly](https://launchdarkly.com/) |
| 97 | **Localization Tester** | - | [i18next/i18next](https://github.com/i18next/i18next) |
| 98 | **GraphQL to REST Adapter** | - | Prompt pattern — no single repo |
| 99 | **Performance Profiler** | 🔴 Risky | [brendangrigg/FlameGraph](https://github.com/brendangregg/FlameGraph) |
|100 | **Chaos Test Scenario Builder** | 🔴 Risky | [chaos-mesh/chaos-mesh](https://github.com/chaos-mesh/chaos-mesh) |

---

## Risk Summary

### 🔴 Risky Skills (15 of 100)

| # | Skill | Risk Reason | URL |
|---|-------|-------------|-----|
| 14 | **Monorepo Dependency Graph** | Heavy file traversal, may execute build tools | [nrwl/nx](https://github.com/nrwl/nx) |
| 29 | **Mutation Test Runner** | Needs execution in test environment | [stryker-mutator/stryker-js](https://github.com/stryker-mutator/stryker-js) |
| 31 | **Snapshots Test Updater** | Auto-updates files, can hide regressions | [facebook/jest](https://github.com/facebook/jest) |
| 53 | **Bundle Analyzer** | Spawns build processes | [webpack-bundle-analyzer](https://github.com/webpack-contrib/webpack-bundle-analyzer) |
| 68 | **Dependency CVE Auditor** | Calls external vulnerability DBs | [dependabot/dependabot-core](https://github.com/dependabot/dependabot-core) |
| 71 | **JWT/Token Analyzer** | May decode/validate tokens, security-sensitive | [auth0/node-jsonwebtoken](https://github.com/auth0/node-jsonwebtoken) |
| 76 | **Threat Model Generator** | May expose attack surface details | [OWASP/threat-dragon](https://github.com/OWASP/threat-dragon) |
| 78 | **SQL Query Optimizer** | May run analysis on live databases | [pg_stat_statements](https://github.com/pganalyze/pg_stat_statements) |
| 80 | **ML Model Trainer** | Requires GPU, data privacy concerns | [huggingface/transformers](https://github.com/huggingface/transformers) |
| 84 | **Embedding Pipeline** | May call external embedding APIs | [sentence-transformers](https://github.com/UKPLab/sentence-transformers) |
| 87 | **Architecture Diagram Builder** | May send code to external diagram services | [mermaid-js/mermaid](https://github.com/mermaid-js/mermaid) |
| 88 | **Dependency Graph Mapper** | Heavy file traversal, may execute build tools | [madge](https://github.com/pahen/madge) |
| 93 | **Smart Contract Auditor** | Financial risk, may execute analysis tools | [trailofbits/manticore](https://github.com/trailofbits/manticore) |
| 99 | **Performance Profiler** | Spawns profiling processes, may slow systems | [brendangregg/FlameGraph](https://github.com/brendangregg/FlameGraph) |
| 100 | **Chaos Test Scenario Builder** | Intentionally injects failures | [chaos-mesh/chaos-mesh](https://github.com/chaos-mesh/chaos-mesh) |

---

## Notes

- Skills labeled **"Prompt pattern — no single repo"** are widely known workflow patterns that circulate in the developer community but don't have a dedicated package or repo. They're implemented as text prompts, slash commands, or custom instructions.
- URLs point to the **closest equivalent open-source tool or repo** that implements or inspires the skill.
- The risk assessment is from an **enterprise intranet perspective**: skills that spawn processes, make external API calls, or handle security-sensitive data are flagged.
