# Changelog

## 1.6.0 (2026-07-11)

### Removed

- `commands/choose-skills.md` — removed; redundant with `skill-orchestrator` skill plan output at task start

### Added

- Example prompts for all 14 commands in README Command Usage Guide (lifecycle-ordered, using `@` file references)
- Explicit standalone skill selection note to `skill-orchestrator` SKILL.md

### Changed

- Standardised `$ARGUMENTS` placement to end of all command files
- Deduplicated overlap control blocks (10-rule → 3-rule + single-line skill selection) across 8 commands
- Converted output format from code blocks to markdown headings in `smart-fix.md`, `smart-review.md`
- Generalised `discover.md` to cover features and services (not only repositories); added `repo_map`/`prompt_budget` tool fallback; merged redundant Improvement Opportunities section
- `README.md` — updated `/discover` description and tools column; updated command count (15→14); removed repository tree entry for `choose-skills.md`
- `scripts/install-opencode.sh` — tools now install as symlinks (were `cp`), matching skills/commands/docs pattern
- `scripts/install-pack.sh` — ai-engineer pack updated with 6 missing skills; removed dead `PLANNED_SKILLS` code
- `scripts/validate-skills.sh` — grep patterns changed from `\s` to `[[:space:]]` for BSD/macOS portability
- `docs/advanced-roadmap.md` — updated with full version history (1.2.0–1.6.0), revised planned enhancements, new contribution ideas

## 1.5.0 (2026-07-10)

### Added

- `system-architecture` — general system architecture design and review skill covering system context, components, service boundaries, data flow, communication patterns, queues, event-driven design, caching, consistency, availability, scalability, fault tolerance, rate limiting, deployment topology, observability, disaster recovery, capacity planning and cost trade-offs
- `commands/architecture.md` — architecture design command producing context, components, data flow, trade-offs, and implementation sequence
- `commands/discover.md` — discovery command identifying gaps, missing features, and improvement opportunities in any repository

### Changed

- `commands/plan.md` — reverted to universal implementation planning; removed repo-specific discovery mode (replaced by `/discover`)
- `commands/discover.md` — generalized workflow and output to cover any repository (not just OpenCode skills packages); added Improvement Opportunities section
- `README.md` — simplified Command Usage Guide to a single unified decision table sorted by goal; fixed repository tree indentation and added missing skills (fine-tuning, mcp-development, multi-agent-orchestration); compacted Installation section into Quick start → Skills only → Role packs → Verify flow; removed duplicate Verify section
- `skills/skill-orchestrator/SKILL.md` — added New Skill Distinctness Test (inventory-first, compare by responsibility, overlap thresholds, decision rules)
- `README.md` — added `system-architecture` to Available Skills table and repository tree diagram
- `docs/skill-routing-matrix.md` — added routing row for `system-architecture`

## 1.4.0 (2026-07-10)

### Added

- `ai-system-architecture` — end-to-end AI system architecture design and review skill covering problem framing, model vs. rule decisions, LLM/RAG/ML pipelines, ingestion, retrieval, orchestration, evaluation, serving, safety, privacy, lifecycle, drift, observability, and failure modes

### Changed

- `README.md` — added `ai-system-architecture` to Available Skills table and repository tree diagram
- `packs/ai-engineer-pack.md` — added `ai-system-architecture` to pack table, install command, and recent additions

## 1.3.0 (2026-07-09)

### Added

- 4 OpenCode custom tools (TypeScript wrappers + Python backends):
  - `repo_map` — compact repository map with language/framework detection
  - `diff_summarizer` — git diff summarization with per-file risk classification and secret redaction
  - `context_compressor` — session context compression preserving exact errors, paths, and commands
  - `prompt_budget` — token/character estimation with reading strategy recommendations
- `opencode-tools/` directory containing 4 `.ts` wrapper files
- `tools/` directory containing 4 Python backend scripts
- 4 test files: `tests/test_repo_map.py`, `tests/test_diff_summarizer.py`, `tests/test_context_compressor.py`, `tests/test_prompt_budget.py`
- Custom tool validation in `tests/validate_skills.py` and `scripts/validate-skills.sh`
- Install/uninstall support for `~/.config/opencode/tools/` in shell installer

### Changed

- All 13 command files updated to reference the relevant custom tools with Python fallback instructions
- `README.md` — added Available Custom Tools table, updated command table with tool mapping, updated repo diagram, added tool installation/verification/uninstallation, condensed Beginner Quickstart / Example Prompts / Slash Command Examples into single Command Usage Guide

## 1.2.0 (2026-07-09)

### Added

- `skill-orchestrator` — lead/support/guardrail skill selection model with verbosity and verification depth control
- `docs/skill-orchestration-design.md` — full orchestration model, overlapping-pair resolution, 11 task categories
- `docs/skill-routing-matrix.md` — quick-reference task-to-skill routing table with 13 task types
- 3 new slash commands:
  - `/choose-skills` — produce a skill plan before starting work
  - `/smart-review` — review with one lead skill and scoped supporting skills
  - `/smart-fix` — fix with minimum necessary skills and focused verification
- Overlap control sections added to 7 existing commands (`review`, `fix`, `debug`, `implement`, `refactor`, `plan`, `safe-apply`)

### Changed

- `README.md` — added Overlap Mitigation section, updated Limitations, linked to skill-routing-matrix, added `/choose-skills`/`/smart-review`/`/smart-fix` to command table
- `packs/fullstack-pack.md` — added `skill-orchestrator` to included skills and installation command
- `tests/validate_skills.py` — added recommended documentation validation (WARNING if missing)
- `scripts/validate-skills.sh` — added documentation validation section
- Removed duplicate "Fix a Bug" example prompt from README

## 1.1.0 (2026-07-08)

### Added

- 5 new AI engineering skills, completing the AI engineer pack:
  - `prompt-injection-defense` — input classification, structural separation, output validation, and layered defense against direct and indirect prompt injection
  - `rag-quality-review` — ingestion, chunking, search, reranking, evaluation, and security review for RAG pipelines
  - `ai-evaluation` — golden test sets, LLM-as-judge calibration, inter-rater reliability, statistical comparison, and CI evaluation gates
  - `ai-cost-optimization` — token budgeting, model routing, caching, batching, deduplication, and cost regression testing
  - `model-serving-production` — FastAPI serving, batch/real-time/background inference, cold start, fallback, canary deployment, and drift monitoring
- Skill Packs (`packs/`) with 6 curated role-based packs (backend, frontend, review, production, ai-engineer, fullstack)
- Pack installer (`scripts/install-pack.sh`) with portable bash implementation

### Changed

- All 5 AI engineer planned skills promoted to Available; no planned skills remain
- README updated with skill entries, pack tables, repository tree, and description table for all new skills
- `packs/ai-engineer-pack.md` updated with skill entries and installation command
- `scripts/install-pack.sh` updated with all new skills; `PLANNED_SKILLS` list emptied

## 1.0.0 (2026-07-08)

Initial stable release of OpenCode Engineering Skills.

### Added

- 12 reusable engineering skills:
  - `python-quality`, `fastapi-backend`, `sqlalchemy-postgres` — Python/FastAPI/SQLAlchemy
  - `nextjs-frontend`, `ui-ux-design` — Next.js, React, frontend
  - `testing-and-debugging` — root-cause analysis and regression
  - `code-review`, `security-review` — evidence-based reviews
  - `production-readiness` — deployment safety assessment
  - `token-saver`, `context-engineering`, `repository-navigation` — token efficiency
- 10 slash commands:
  - `review`, `fix`, `debug`, `implement`, `refactor` — core workflows
  - `compress-context`, `context-audit`, `handoff-summary` — context management
  - `plan`, `safe-apply` — planned implementation
- Shell installer (`scripts/install-opencode.sh`) with symlink-based installation
- Shell uninstaller (`scripts/uninstall-opencode.sh`) with safe symlink removal
- Shell validation script (`scripts/validate-skills.sh`) for frontmatter and structure
- Python validation suite (`tests/validate_skills.py`) with YAML frontmatter verification
- CI workflow (`.github/workflows/validate.yml`) running shell validation and CLI discovery
- Documentation: `README.md`, `docs/token-saving-guide.md`, `docs/advanced-roadmap.md`
- MIT License
