# Changelog

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
