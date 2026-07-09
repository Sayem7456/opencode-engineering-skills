# OpenCode Engineering Skills

A curated collection of reusable engineering skills and slash commands for OpenCode.

These skills provide structured workflows and engineering standards for:

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* Next.js
* React
* TypeScript
* JavaScript
* UI/UX design
* Testing and debugging
* Code review
* Security review
* Production readiness

The package helps OpenCode produce more consistent, maintainable, secure, and production-aware results across backend and frontend projects.

## Available Custom Tools

This repository includes four OpenCode custom tools (`.ts` wrappers) backed by Python scripts. They help the agent save tokens, understand diffs, navigate repositories, and compress context.

| Tool | Purpose | Python Fallback |
|------|---------|-----------------|
| `repo_map` | Generate a compact repository map with language/framework detection | `python tools/repo_map.py` |
| `diff_summarizer` | Summarize git diffs with per-file risk classification, symbol detection, and skill/test suggestions | `python tools/diff_summarizer.py` |
| `context_compressor` | Compress logs, stack traces, and session context while preserving exact errors, paths, and commands | `python tools/context_compressor.py` |
| `prompt_budget` | Estimate context size (chars/tokens) and recommend reading strategies | `python tools/prompt_budget.py` |

These tools are installed as symlinks to `~/.config/opencode/tools/` by the installer. If a custom tool is unavailable, the Python scripts in `tools/` can be run directly from the cloned repository.

## Token Saving and Context Compression

This release introduces skills and commands focused on reducing token waste during OpenCode sessions. These are guidance skills: they instruct the agent on efficient reading, summarization, and context handoff. They do not automatically compress context or inject tooling — they change how the agent uses the tools it already has.

The three new skills work together:

* **`token-saver`** — teaches selective file reading, lazy context loading, compact reporting, and avoiding unnecessary output.
* **`context-engineering`** — builds and preserves a structured context model across complex multi-step tasks, with compression and handoff guidance.
* **`repository-navigation`** — explores unfamiliar repositories efficiently: build a repo map, find relevant files, trace callers, skip generated files.

The five new slash commands invoke these skills directly:

* `/compress-context` — produce a compressed working summary.
* `/context-audit` — audit the current session for wasted context.
* `/handoff-summary` — prepare a handoff for a new session.
* `/plan` — create a compact implementation plan before editing.
* `/safe-apply` — apply a planned change with verification checks.

### Measured Savings

Token savings measured against this repository (76 files, ~158k tokens):

| Scenario | Naive Approach | Token-Saver Approach | Saved |
|---|---|---|---|
| Explore repo from scratch | Full directory read: ~158k tokens | `repo_map` + `prompt_budget` + 4 essential files: ~10.6k tokens | **93%** |
| Inspect a large skill file | Full read (1,672 lines): ~7.9k tokens | `grep` + first 30 lines: ~142 tokens | **98%** |
| Review a feature branch diff | Raw diff (28k bytes) | `diff_summarizer` summary (3.1k bytes) | **89%** |
| Debug with long session log | Full log read (500+ lines) | `context_compressor` with error/path preservation | Varies |

The `token-saver`, `context-engineering`, and `repository-navigation` skills teach the agent to achieve these savings automatically by reading selectively, using `grep`/`glob` before full reads, and keeping compact context summaries.

## Available Skills

| Skill                   | Purpose                                                                                                            |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `python-quality`        | Production-quality Python, typing, error handling, logging, testing, and maintainability                           |
| `fastapi-backend`       | FastAPI endpoints, validation, authentication, authorization, background jobs, and API reliability                 |
| `sqlalchemy-postgres`   | SQLAlchemy sessions, transactions, PostgreSQL, connection pooling, migrations, concurrency, and query safety       |
| `nextjs-frontend`       | Next.js, React, TypeScript, Server Components, Client Components, data fetching, caching, and frontend reliability |
| `ui-ux-design`          | Accessible, responsive, polished, and user-centered interface design                                               |
| `testing-and-debugging` | Reproduction, root-cause analysis, regression tests, and systematic verification                                   |
| `security-review`       | Authentication, authorization, input handling, secrets, injection, uploads, SSRF, and security risks               |
| `code-review`           | Evidence-based reviews focused on correctness, regressions, security, data integrity, and maintainability          |
| `production-readiness`  | Deployment safety, configuration, migrations, observability, health checks, rollback, and reliability              |
| `token-saver`           | Selective file reading, lazy context loading, compact reporting, and avoiding unnecessary output                   |
| `context-engineering`   | Build, compress, and reuse task context across sessions without losing decisions or verification state             |
| `repository-navigation` | Efficient repository exploration, repo map building, caller tracing, and skipping generated files                  |
| `skill-orchestrator` | Select the right lead skill and supporting skills, reduce overlap, control verbosity, and avoid unnecessary activation |
| `structured-output-reliability` | JSON schemas, validation, retries, repair strategies, contracts, and downstream safety for LLM structured output |
| `llm-app-security` | Review and harden LLM apps against prompt injection, data leakage, unsafe tool use, insecure retrieval and untrusted output |
| `prompt-injection-defense` | Design, review and implement defenses against direct and indirect prompt injection in LLM applications |
| `rag-quality-review` | Review and improve retrieval-augmented generation systems for chunking, retrieval, grounding, citations, evaluation and safety |
| `ai-evaluation` | Design and review evaluation workflows for LLM, RAG and AI systems, including test sets, metrics, judge prompts, reliability and regression testing |
| `ai-cost-optimization` | Optimize LLM and AI application cost through prompt efficiency, caching, model routing, batching, retrieval control and safe fallback strategies |
| `model-serving-production` | Design, review and harden production AI model-serving systems, including APIs, batching, latency, monitoring, fallback, drift and deployment safety |
| `mcp-development` | Build, test, debug and deploy MCP servers for tools, resources and prompts using the Model Context Protocol |
| `multi-agent-orchestration` | Design and debug multi-agent workflows with subagent decomposition, parallel execution, context isolation and error recovery |
| `fine-tuning` | Fine-tune LLMs with Axolotl, Unsloth, TRL or LLaMA-Factory, covering data prep, training config, LoRA/QLoRA, evaluation and deployment |
| `llm-observability` | Design and implement observability for LLM applications, including tracing, metrics, cost tracking, online evaluation, alerting and dashboards |
| `prompt-engineering` | Design, test, and optimize prompts for LLMs, including system prompts, few-shot, chain-of-thought, template management, technique selection and versioning |

## Available Commands

| Command      | Purpose                                                                                     | Uses Custom Tool |
| ------------ | ------------------------------------------------------------------------------------------- | ---------------- |
| `/review`            | Review selected code without modifying it                                      | `diff_summarizer` |
| `/fix`               | Fix a confirmed defect and add regression coverage                             | `diff_summarizer` |
| `/debug`             | Investigate a bug and identify its root cause                                  | `diff_summarizer`, `repo_map` |
| `/implement`         | Implement a new feature using existing project conventions                     | `repo_map`, `prompt_budget` |
| `/refactor`          | Refactor existing code while preserving observable behavior                    | `repo_map`, `diff_summarizer` |
| `/choose-skills`     | Select the best lead and supporting skills while avoiding overlapping instructions | — |
| `/smart-review`      | Review code with one lead review skill and only necessary supporting skills    | `diff_summarizer` |
| `/smart-fix`         | Fix a bug using minimum necessary skills and focused verification              | `diff_summarizer` |
| `/compress-context`  | Compress the current session context into a concise working summary            | `context_compressor`, `prompt_budget` |
| `/context-audit`     | Audit the current session for wasted context and missing information           | `prompt_budget`, `context_compressor` |
| `/handoff-summary`   | Create a handoff summary for continuing in a new OpenCode session              | `context_compressor`, `prompt_budget` |
| `/plan`              | Create a compact implementation plan before editing code                       | `repo_map`, `prompt_budget` |
| `/safe-apply`        | Apply a planned change safely with diff inspection and verification            | `diff_summarizer` |

## Skill Packs

Skill packs are curated groups of skills organized by role and workflow. They are documentation recommendations — not a separate installer or CLI feature. Use them as a reference when selecting skills for a task or setting up a new development environment.

| Pack | Role | Skills | Best For |
|------|------|--------|----------|
| `backend-pack` | Backend developer | python-quality, fastapi-backend, sqlalchemy-postgres, testing-and-debugging, security-review | FastAPI APIs, database work, backend services |
| `frontend-pack` | Frontend developer | nextjs-frontend, ui-ux-design, testing-and-debugging, code-review, security-review | Next.js pages, components, UI |
| `review-pack` | Reviewer | code-review, security-review, testing-and-debugging, production-readiness | PR review, security audit |
| `production-pack` | DevOps / platform | production-readiness, security-review, sqlalchemy-postgres, testing-and-debugging, token-saver, context-engineering | Deployment assessment, incident investigation |
| `ai-engineer-pack` | AI/ML engineer | python-quality, testing-and-debugging, token-saver, context-engineering, structured-output-reliability, llm-app-security, prompt-injection-defense, rag-quality-review, ai-evaluation, ai-cost-optimization, model-serving-production, mcp-development, multi-agent-orchestration, fine-tuning, llm-observability, prompt-engineering | LLM apps, RAG pipelines, model serving, MCP servers, multi-agent workflows, fine-tuning, LLM observability, prompt engineering |
| `fullstack-pack` | Full-stack developer | python-quality, fastapi-backend, sqlalchemy-postgres, nextjs-frontend, ui-ux-design, testing-and-debugging, security-review, code-review, production-readiness, token-saver, context-engineering, repository-navigation | End-to-end features, cross-stack debugging |

### Installation

Install a pack using the pack installer:

```bash
# Install the backend pack
./scripts/install-pack.sh backend

# Install non-interactively
./scripts/install-pack.sh fullstack --yes
```

Or install the individual skills directly:

```bash
npx skills add Sayem7456/opencode-engineering-skills \
  --skill python-quality \
  --skill fastapi-backend \
  --skill sqlalchemy-postgres \
  --skill testing-and-debugging \
  --skill security-review \
  --agent opencode \
  --global
```

Each pack file in `packs/` includes its own installation command.

All pack files are located in the `packs/` directory at the repository root.

## Repository Structure

```text
opencode-engineering-skills/
├── README.md
├── AGENTS.md
├── .gitignore
├── LICENSE
├── CHANGELOG.md
├── pyproject.toml
├── requirements.txt
├── .github/
│   └── workflows/
│       └── validate.yml
├── skills/
│   ├── python-quality/
│   │   └── SKILL.md
│   ├── fastapi-backend/
│   │   └── SKILL.md
│   ├── sqlalchemy-postgres/
│   │   └── SKILL.md
│   ├── nextjs-frontend/
│   │   └── SKILL.md
│   ├── ui-ux-design/
│   │   └── SKILL.md
│   ├── testing-and-debugging/
│   │   └── SKILL.md
│   ├── security-review/
│   │   └── SKILL.md
│   ├── code-review/
│   │   └── SKILL.md
│   ├── llm-app-security/
│   │   └── SKILL.md
│   ├── prompt-injection-defense/
│   │   └── SKILL.md
│   ├── rag-quality-review/
│   │   └── SKILL.md
│   ├── ai-evaluation/
│   │   └── SKILL.md
│   ├── ai-cost-optimization/
│   │   └── SKILL.md
│   ├── model-serving-production/
│   │   └── SKILL.md
│   ├── production-readiness/
│   │   └── SKILL.md
│   ├── token-saver/
│   │   └── SKILL.md
│   ├── context-engineering/
│   │   └── SKILL.md
    │   ├── repository-navigation/
    │   │   └── SKILL.md
    │   ├── skill-orchestrator/
    │   │   └── SKILL.md
    │   └── structured-output-reliability/
│       └── SKILL.md
│   ├── llm-observability/
│   │   └── SKILL.md
│   ├── prompt-engineering/
│   │   └── SKILL.md
├── commands/
│   ├── review.md
│   ├── fix.md
│   ├── debug.md
│   ├── implement.md
│   ├── refactor.md
│   ├── compress-context.md
│   ├── context-audit.md
│   ├── handoff-summary.md
│   ├── plan.md
│   ├── safe-apply.md
│   ├── choose-skills.md
│   ├── smart-review.md
│   └── smart-fix.md
├── opencode-tools/
│   ├── repo_map.ts
│   ├── diff_summarizer.ts
│   ├── context_compressor.ts
│   └── prompt_budget.ts
├── tools/
│   ├── repo_map.py
│   ├── diff_summarizer.py
│   ├── context_compressor.py
│   └── prompt_budget.py
├── scripts/
│   ├── install-opencode.sh
│   ├── install-pack.sh
│   ├── uninstall-opencode.sh
│   └── validate-skills.sh
├── packs/
│   ├── backend-pack.md
│   ├── frontend-pack.md
│   ├── review-pack.md
│   ├── production-pack.md
│   ├── ai-engineer-pack.md
│   └── fullstack-pack.md
├── tests/
│   ├── validate_skills.py
│   ├── test_repo_map.py
│   ├── test_diff_summarizer.py
│   ├── test_context_compressor.py
│   └── test_prompt_budget.py
└── docs/
    ├── token-saving-guide.md
    ├── opencode-custom-tools-design.md
    ├── advanced-roadmap.md
    ├── skill-orchestration-design.md
    └── skill-routing-matrix.md
```

# Installation

## Prerequisites

You need:

* OpenCode
* Node.js with `npx`
* Git for manual installation
* Bash for installing the included slash commands

Check your installations:

```bash
opencode --version
node --version
npx --version
git --version
```

## Option 1: Install All Skills with the Skills CLI


```bash
npx skills add Sayem7456/opencode-engineering-skills \
  --skill '*' \
  --agent opencode \
  --global
```

For non-interactive installation:

```bash
npx skills add Sayem7456/opencode-engineering-skills \
  --skill '*' \
  --agent opencode \
  --global \
  --yes
```

This installs the skills globally for OpenCode.

## Option 2: Install Selected Skills

Install only the skills relevant to your work:

```bash
npx skills add Sayem7456/opencode-engineering-skills \
  --skill python-quality \
  --skill fastapi-backend \
  --skill sqlalchemy-postgres \
  --agent opencode \
  --global
```

For Next.js development:

```bash
npx skills add Sayem7456/opencode-engineering-skills \
  --skill nextjs-frontend \
  --skill ui-ux-design \
  --skill testing-and-debugging \
  --agent opencode \
  --global
```

For reviews and release checks:

```bash
npx skills add Sayem7456/opencode-engineering-skills \
  --skill code-review \
  --skill security-review \
  --skill production-readiness \
  --agent opencode \
  --global
```

## Option 3: List Skills Before Installing

```bash
npx skills add Sayem7456/opencode-engineering-skills --list
```

## Option 4: Install from the Full GitHub URL

```bash
npx skills add \
  https://github.com/Sayem7456/opencode-engineering-skills \
  --agent opencode \
  --global
```

## Option 5: Install One Skill Directly

```bash
npx skills add \
  https://github.com/Sayem7456/opencode-engineering-skills/tree/main/skills/fastapi-backend \
  --agent opencode \
  --global
```

## Install Skills and Slash Commands

The Skills CLI installs skills only (to `~/.agents/skills/`). It does not install slash commands.

To install both skills and the included OpenCode slash commands, clone the repository and run the installer:

```bash
git clone https://github.com/Sayem7456/opencode-engineering-skills.git
cd opencode-engineering-skills

chmod +x scripts/install-opencode.sh
./scripts/install-opencode.sh
```

The installer symlinks content into:

```text
~/.config/opencode/skills/
~/.config/opencode/commands/
~/.config/opencode/tools/
```

It installs all skills, command files, and TypeScript custom tool wrappers from this repository.

**Summary:**

| What you want                    | Command                                                           |
| -------------------------------- | ----------------------------------------------------------------- |
| Skills only                      | `npx skills add Sayem7456/opencode-engineering-skills --skill '*'` |
| Skills by role pack              | `scripts/install-pack.sh <pack-name>`                             |
| Skills + slash commands + tools  | `scripts/install-opencode.sh`                                     |
| Selected skills only             | `npx skills add ... --skill token-saver --skill context-engineering` |

Restart OpenCode or open a new session after installation.

## Install by Pack

Install a curated skill pack for your role using `scripts/install-pack.sh`:

```bash
# Install the backend pack
./scripts/install-pack.sh backend

# Install the fullstack pack non-interactively
./scripts/install-pack.sh fullstack --yes
```

This runs `npx skills add` with all skills in the selected pack. It installs skills only — slash commands still require a separate step:

```bash
# After installing skills, also install commands
./scripts/install-opencode.sh
```

Available packs and their included skills:

| Pack | Skills |
|------|--------|
| `backend` | python-quality, fastapi-backend, sqlalchemy-postgres, testing-and-debugging, security-review |
| `frontend` | nextjs-frontend, ui-ux-design, testing-and-debugging, code-review, security-review |
| `review` | code-review, security-review, testing-and-debugging, production-readiness |
| `production` | production-readiness, security-review, sqlalchemy-postgres, testing-and-debugging, token-saver, context-engineering |
| `ai-engineer` | python-quality, testing-and-debugging, token-saver, context-engineering, structured-output-reliability, llm-app-security, prompt-injection-defense, rag-quality-review, ai-evaluation, ai-cost-optimization, model-serving-production, fine-tuning, mcp-development, multi-agent-orchestration, llm-observability, prompt-engineering |
| `fullstack` | python-quality, fastapi-backend, sqlalchemy-postgres, nextjs-frontend, ui-ux-design, testing-and-debugging, security-review, code-review, production-readiness, token-saver, context-engineering, repository-navigation |

Pack files in `packs/` contain detailed guidance for each pack including example prompts, best use cases, and when not to use.

## Manual Installation

Clone the repository:

```bash
git clone https://github.com/Sayem7456/opencode-engineering-skills.git
cd opencode-engineering-skills
```

Create the OpenCode directories:

```bash
mkdir -p ~/.config/opencode/skills
mkdir -p ~/.config/opencode/commands
```

Copy the skills:

```bash
cp -R skills/* ~/.config/opencode/skills/
```

Copy the commands:

```bash
cp commands/*.md ~/.config/opencode/commands/
```

Restart OpenCode after copying the files.

# Verify Installation

List installed skill files:

```bash
find ~/.config/opencode/skills \
  -maxdepth 2 \
  -name SKILL.md \
  -print
```

List installed commands:

```bash
find ~/.config/opencode/commands \
  -maxdepth 1 \
  -name '*.md' \
  -print
```

List installed custom tools:

```bash
find ~/.config/opencode/tools \
  -maxdepth 1 \
  -name '*.ts' \
  -print
```

Check the beginning of every installed skill:

```bash
for file in ~/.config/opencode/skills/*/SKILL.md; do
  echo "===== $file ====="
  head -n 10 "$file"
done
```

Each skill should contain valid frontmatter:

```yaml
---
name: fastapi-backend
description: Build, review and debug production FastAPI services.
license: MIT
compatibility: opencode
metadata:
  category: backend
  stack: python-fastapi
  version: "1.0.0"
---
```

The folder name and frontmatter `name` should match exactly.

Example:

```text
Folder: fastapi-backend
Name:   fastapi-backend
```

# Updating

## Update Skills Installed with the Skills CLI

```bash
npx skills update
```

List globally installed skills:

```bash
npx skills list --global
```

## Update a Git Clone Installation

Enter the cloned repository:

```bash
cd opencode-engineering-skills
git pull
```

If the installer copies files rather than creating symbolic links, run it again:

```bash
./scripts/install-opencode.sh
```

# Uninstallation

## Remove Skills Installed with npx skills

```bash
npx skills remove token-saver
npx skills remove context-engineering
npx skills remove repository-navigation
```

List installed skills first:

```bash
npx skills list --global
```

The `npx skills remove` command only removes skills installed by `npx skills add`. It does not touch slash commands or skills installed by the shell installer.

## Remove Skills and Commands Installed by the Shell Installer

From the cloned repository:

```bash
chmod +x scripts/uninstall-opencode.sh
./scripts/uninstall-opencode.sh
```

This removes only symlinks that were created from this repository. It will not delete skills installed by `npx skills add` or any other non-symlink files.

**Summary:**

| Installed via                   | Remove via                            |
| ------------------------------- | ------------------------------------- |
| `npx skills add`                | `npx skills remove <name>`            |
| `scripts/install-opencode.sh`   | `scripts/uninstall-opencode.sh`       |
| Manual copy                     | Manual `rm -rf`                       |

To manually remove selected skills or commands installed by the shell installer:

```bash
rm -rf ~/.config/opencode/skills/token-saver
rm -rf ~/.config/opencode/skills/context-engineering
rm -rf ~/.config/opencode/skills/repository-navigation
```

```bash
rm -f ~/.config/opencode/commands/compress-context.md
rm -f ~/.config/opencode/commands/context-audit.md
rm -f ~/.config/opencode/commands/handoff-summary.md
rm -f ~/.config/opencode/commands/plan.md
rm -f ~/.config/opencode/commands/safe-apply.md
```

```bash
rm -f ~/.config/opencode/tools/repo_map.ts
rm -f ~/.config/opencode/tools/diff_summarizer.ts
rm -f ~/.config/opencode/tools/context_compressor.ts
rm -f ~/.config/opencode/tools/prompt_budget.ts
```

# Practical Difference by Skill

| Skill                   | Without the Skill                                                                                                  | With the Skill                                                                                                                           |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `python-quality`        | Code may run but contain weak typing, broad exceptions, resource leaks, or inconsistent structure                  | Stronger typing, focused functions, safer errors, cleaner resources, and structured verification                                         |
| `fastapi-backend`       | Routes may contain business logic, authorization may be incomplete, and request sessions may be reused incorrectly | Thin routes, explicit schemas, server-side authorization, controlled transactions, and safer background processing                       |
| `sqlalchemy-postgres`   | Fixes may focus only on pool settings or retries                                                                   | Session state, rollback, transaction boundaries, ambiguous commits, concurrency, constraints, and migrations are considered              |
| `nextjs-frontend`       | Pages may implement only the success state or misuse Client Components                                             | Better server/client boundaries, loading and error states, runtime validation, cache safety, and build verification                      |
| `ui-ux-design`          | An interface may be visually attractive but unclear, inaccessible, or inconsistent                                 | Better hierarchy, spacing, responsiveness, forms, accessibility, feedback, and design consistency                                        |
| `testing-and-debugging` | OpenCode may guess at the cause or apply several speculative changes                                               | Reproduction, hypothesis testing, root-cause evidence, regression tests, and focused verification                                        |
| `security-review`       | Security checks depend heavily on the prompt                                                                       | Authentication, authorization, secrets, injection, uploads, SSRF, tenant isolation, and unsafe data handling are reviewed systematically |
| `code-review`           | Reviews may focus on formatting, naming, or subjective preferences                                                 | Findings focus on realistic defects, impact, severity, minimal fixes, and regression coverage                                            |
| `production-readiness`  | Passing tests may be treated as sufficient for deployment                                                          | Configuration, migrations, health checks, monitoring, failure recovery, capacity, and rollback are also assessed                         |
| `token-saver`           | The agent reads entire files, outputs full content, and repeats context across turns                               | Selective reads, compact output, lazy loading, and summarized context preserve tokens without losing information                          |
| `context-engineering`   | Context degrades across long sessions; decisions are re-derived and handoffs lose information                      | Structured context model preserves goal, constraints, decisions, and verification state across complex multi-step tasks                  |
| `repository-navigation` | The agent reads many irrelevant files or guesses file locations                                                    | A compact repo map guides exploration; grep/glob are used before reading; generated files are skipped                                    |
| `structured-output-reliability` | LLM output is trusted without validation; invalid JSON causes crashes; eval introduces RCE risk                    | Schema-first design, library validation, bounded retries, repair prompts, no eval, and golden tests prevent downstream failures         |
| `llm-app-security` | Prompt injection, data exfiltration, and unsafe tool calls pass unnoticed until a breach occurs | Threat modeling, tenant isolation, allowlists, sandboxing, output validation, and red-team testing applied systematically             |
| `prompt-injection-defense` | Applications accept any user input without inspection; indirect injection in RAG data goes undetected | Input classification, structural separation, output validation, instruction hierarchy, and layered defense prevent injection from reaching the model |
| `rag-quality-review` | RAG pipeline produces hallucinated, uncited, or low-quality answers; retrieval quality is unknown | Ingestion, chunking, search, reranking, evaluation, and security are reviewed systematically with metrics before optimization |
| `ai-evaluation` | Evaluation is ad-hoc, unlabeled, or uses LLM judges without calibration; regressions go undetected | Golden test sets, calibrated judges, inter-rater reliability, statistical comparison, and CI gates produce trustworthy quality signals |
| `ai-cost-optimization` | LLM costs grow unbounded; expensive models used for every request; no caching or budget enforcement | Token budgets, model routing, caching, retrieval limits, and cost gates control spend without blind quality reduction |
| `model-serving-production` | Model serving is fragile: no fallback, no monitoring, no capacity planning, and risky deployments | Reliable APIs, cold start mitigations, circuit breakers, canary rollouts, drift monitoring, and evaluation gates ensure production safety |
| `llm-observability` | LLM calls are invisible: you cannot trace which prompt caused which response, attribute cost, or detect quality degradation | Every LLM call is traced, cost-attributed, quality-monitored, and alerted-on without exposing raw PII |
| `prompt-engineering` | Prompts are written ad-hoc in code, untested, unversioned, and optimized for neither cost nor quality | Prompts are versioned, tested, technique-selected, and optimized for token efficiency, latency, and output consistency |

# Limitations

Skills improve process but do not guarantee correctness, security, or passing tests. Always verify generated changes. Large skills consume context — avoid activating every skill for every task. Repository conventions still matter; inspect the project before applying generic patterns.

# Command Usage Guide

Start any task with `/choose-skills` to produce a skill plan — no need to memorize combinations.

| Step | Command | When to Use | Example |
|------|---------|-------------|---------|
| 1. Plan | `/choose-skills` | Any new task — produces a skill plan before work begins | `/choose-skills Debug why the login endpoint returns 500 after upgrading FastAPI.` |
| 2. Explore | `/plan` | Before implementing — maps affected files and risks | `/plan Add a paginated teacher dashboard endpoint with branch-level access control.` |
| 3. Debug | `/debug` | Root cause is unknown; need investigation | `/debug Assignment submission intermittently fails with an SQLAlchemy OperationalError.` |

**Choose your execution path:**

| Path | Command | When to Use | Example |
|------|---------|-------------|---------|
| Fix (known bug) | `/fix` | Root cause is confirmed; need a fix + regression test | `/fix The background task reuses the request-scoped session after the request completes.` |
| Fix (unknown scope) | `/smart-fix` | Bug report is vague; need skill orchestration + fix | `/smart-fix The user avatar upload fails silently when the file exceeds 5 MB.` |
| Apply planned change | `/safe-apply` | After `/plan` approved; applies with diff inspection + verification | `/safe-apply Apply the approved plan for the paginated teacher dashboard endpoint.` |
| Review (known code) | `/review` | Review specific files; user knows the scope | `/review src/services/assignment_service.py` |
| Review (unknown scope) | `/smart-review` | Review scope is broad; need skill orchestration first | `/smart-review src/routes/users.py` |

**Feature development:**

| Command | When to Use | Example |
|---------|-------------|---------|
| `/implement` | Build a new feature following project conventions | `/implement Add an export-to-CSV endpoint for the analytics dashboard.` |
| `/refactor` | Restructure code preserving public behavior | `/refactor Move assignment scoring logic into a separate service.` |

**Context management:**

| Command | When to Use | Example |
|---------|-------------|---------|
| `/compress-context` | Session is long; produce a working summary | `/compress-context I am investigating a user-creation endpoint failure under load.` |
| `/context-audit` | Session feels wasteful; find wasted context | `/context-audit I have been debugging this transaction issue for several turns.` |
| `/handoff-summary` | Handing off to a new session | `/handoff-summary I need to hand off this FastAPI migration to a new session.` |

# Best Practices

## Explicitly Name Skills for High-Risk Tasks

For critical database, security, or deployment work, explicitly mention the relevant skills.

Example:

```text
Use sqlalchemy-postgres, testing-and-debugging, and security-review for this task.
```

## Do Not Activate Every Skill Automatically

Use only skills relevant to the task.

Too many skills can:

* consume unnecessary context
* duplicate instructions
* make small tasks overly complex
* produce unnecessarily cautious responses

## Keep Project-Specific Rules in the Project

Global skills should contain reusable engineering guidance.

Place project-specific details in the repository’s own `AGENTS.md`, such as:

* architecture
* test commands
* environment names
* module ownership
* API conventions
* deployment procedures
* prohibited dependencies

## Verify Generated Changes

Always verify important changes with the project’s actual commands.

Typical Python checks:

```bash
ruff check .
ruff format --check .
mypy .
pyright
pytest
```

Typical Next.js checks:

```bash
npm run lint
npm run typecheck
npm test
npm run build
```

Run only commands that exist in the project.

# Validation

Validate the repository before publishing:

```bash
chmod +x scripts/validate-skills.sh
./scripts/validate-skills.sh
```

Run the Python validation test if provided:

```bash
python tests/validate_skills.py
```

Check whether the Skills CLI discovers the local skills:

```bash
npx skills add . --list
```

Validation should confirm:

* every skill directory contains `SKILL.md`
* every file has valid frontmatter
* every `name` matches its folder
* every skill has a description
* skill names use lowercase letters, numbers, and single hyphens
* no duplicate skill names exist
* command files contain valid metadata
* custom tool `.ts` files import `tool` from `@opencode-ai/plugin`, export `default tool(...)`, and contain `description`, `args`, and `execute`
* tool filenames use lowercase with underscores only
* Python tool scripts in `tools/` exist and are non-empty

# Versioning

This project follows semantic versioning.

```text
PATCH:
Wording corrections, minor rule improvements, and documentation fixes.

MINOR:
New skills, commands, or backward-compatible capabilities.

MAJOR:
Breaking changes to skill behavior, repository structure, or installation.
```

Create a release tag:

```bash
git tag -a v1.0.0 -m "Initial stable release"
git push origin v1.0.0
```

# Contributing

Contributions are welcome.

## Contribution Guidelines

1. Fork the repository.
2. Create a focused branch.
3. Update or add the relevant skill.
4. Keep instructions evidence-based and stack-aware.
5. Avoid duplicating rules unnecessarily.
6. Run the validation scripts.
7. Update `CHANGELOG.md`.
8. Open a pull request describing the problem and improvement.

Example:

```bash
git checkout -b improve/sqlalchemy-retry-guidance
./scripts/validate-skills.sh
python tests/validate_skills.py
```

## Skill Quality Requirements

A contributed skill should:

* have a clear purpose
* use valid frontmatter
* describe when it should be used
* define practical workflows
* separate confirmed issues from hypotheses
* discourage unsafe or destructive behavior
* require verification
* avoid unnecessary stack assumptions
* avoid promising guaranteed correctness
* remain reusable across repositories

# Security

Do not report sensitive security issues in a public GitHub issue.

For sensitive reports, contact:

```text
sayem1.ahamed@gmail.com
```

Do not include real:

* API keys
* access tokens
* passwords
* database URLs
* private keys
* production logs containing personal data

# License

This project is licensed under the MIT License.

See `LICENSE` for details.

# Disclaimer

These skills provide guidance to AI coding agents. They do not replace:

* experienced engineering review
* automated tests
* security testing
* current framework documentation
* database backups
* deployment safeguards
* production monitoring
* professional legal or compliance advice

Users are responsible for reviewing, testing, and validating all generated changes before using them in production.
