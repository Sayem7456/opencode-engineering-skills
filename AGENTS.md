# AGENTS.md

This repository ships reusable OpenCode skills, slash commands, and custom tools. It does not contain application code.

## Quick start

```bash
# Validate before committing
./scripts/validate-skills.sh
python tests/validate_skills.py

# Run all tests
python -m pytest tests/

# Single test file
python -m pytest tests/test_repo_map.py

# Install all skills globally
npx skills add Sayem7456/opencode-engineering-skills --skill '*' --agent opencode --global

# Install skills + commands + tools (from clone)
./scripts/install-opencode.sh

# Install a role-based pack (skills only)
./scripts/install-pack.sh backend
```

## First-time setup (custom tools)

Custom tools in `opencode-tools/` require `@opencode-ai/plugin`. After cloning, run:

```bash
npm install
```

Then verify tools load correctly:

```bash
opencode run "Say hello"
```

If you see an `UnknownError`, check server logs with `--print-logs --log-level DEBUG` to confirm the module is resolvable.

## Structure

| Path | Purpose |
|---|---|
| `skills/<name>/SKILL.md` | Skill file with YAML frontmatter plus guidance body |
| `commands/<name>.md` | Slash command definition, references `$ARGUMENTS` |
| `opencode-tools/*.ts` | Custom tool TS wrappers (import from `@opencode-ai/plugin`) |
| `tools/*.py` | Python backend scripts for custom tools |
| `tests/` | Pytest tests: `validate_skills.py` + 4 tool-specific tests |
| `packs/` | Role-based skill pack docs |
| `scripts/` | Installers, validators, uninstaller |

## Conventions

- Skill folder name and frontmatter `name` must match exactly, lowercase with hyphens only.
- Required frontmatter: `name`, `description`, `license` (MIT), `compatibility` (opencode), `metadata` (category, stack, version).
- Command `.md` files must reference `$ARGUMENTS` in the body.
- Custom tool `.ts` files: `snake_case` filenames, `import { tool } from "@opencode-ai/plugin"`, `export default tool(...)`, must have `description`, `args`, `execute`.
- Ruff: line-length 88, target py310, select E/F/W/I.
- Python tools: PyYAML only dependency. Required tool scripts: `repo_map.py`, `diff_summarizer.py`, `context_compressor.py`, `prompt_budget.py`.

## Validation order

1. `./scripts/validate-skills.sh` — shell-level checks (frontmatter, naming, tool presence)
2. `python tests/validate_skills.py` — Python-level checks (YAML parsing, README sync, pack validation)
3. `python -m pytest tests/` — Python tool unit tests

## CI

`.github/workflows/validate.yml` runs shell validator, Python validator, and `npx skills add . --list` on push/PR to main.

## Installing

- Skills installed by `npx skills add` land in `~/.agents/skills/` (not `~/.config/opencode/skills/`).
- Shell installer (`scripts/install-opencode.sh`) uses symlinks to `~/.config/opencode/skills/` for skills, commands, and tools.
- Reminder: `npx skills remove` only removes skills installed via `npx skills add`. Use `scripts/uninstall-opencode.sh` for symlinked installs.
