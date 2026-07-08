# Changelog

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
