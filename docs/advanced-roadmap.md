# Advanced Roadmap

This document tracks past, present, and planned improvements for the skill ecosystem.

## Completed — 1.6.0 (current)

- Standardised `$ARGUMENTS` placement to end of all 15 command files
- Deduplicated overlap control blocks (10-rule → 3-rule + single-line skill selection) across 8 commands
- Converted output format from code blocks to markdown headings in 3 commands (`choose-skills`, `smart-fix`, `smart-review`)
- Added custom tool fallback section to `discover.md`
- Merged redundant "Improvement Opportunities" section in `discover.md`
- Added example prompts for all 14 commands in README (lifecycle-ordered, using `@` file references)
- Updated `discover` command description and tools column in README
- Script fixes: tools install uses symlinks (was `cp`), ai-engineer pack updated with 6 missing skills, dead `PLANNED_SKILLS` code removed, grep patterns made portable for BSD/macOS
- Updated `docs/advanced-roadmap.md` with full version history

## Completed — 1.5.0

- `system-architecture` skill — general system architecture design and review
- `/architecture` command — produces context, components, data flow, trade-offs, and implementation sequence
- `/discover` command — identifies gaps, missing features, and improvement opportunities in any repository, project, feature, or service
- Generalized `discover.md` workflow and output to cover features and services (not only repositories)
- `plan.md` reverted to universal implementation planning (discovery mode replaced by `/discover`)

## Completed — 1.4.0

- `ai-system-architecture` skill — end-to-end AI system architecture design and review

## Completed — 1.3.0

- 4 OpenCode custom tools (TypeScript wrappers + Python backends):
  - `repo_map` — compact repository map with language/framework detection
  - `diff_summarizer` — git diff summarisation with per-file risk classification
  - `context_compressor` — session context compression preserving exact errors, paths, and commands
  - `prompt_budget` — token/character estimation with reading strategy recommendations
- All 15 command files updated with custom tool references and Python fallback instructions
- Custom tool validation in both shell and Python validators
- Install and uninstall support for `~/.config/opencode/tools/`

## Completed — 1.2.0

- `skill-orchestrator` skill with lead/support/guardrail role model
- `docs/skill-orchestration-design.md` — full orchestration model, overlapping-pair resolution, 11 task categories
- `docs/skill-routing-matrix.md` — quick-reference task-to-skill routing table
- `/choose-skills` — skill plan generation before starting work
- `/smart-review` — review with one lead skill and scoped supporting skills
- `/smart-fix` — fix with minimum necessary skills and focused verification
- Overlap control sections added to all existing commands
- Documentation recommended files validation in both shell and Python validators

## Planned Enhancements

- **Automated context budget tracking** — Estimate and report token consumption per session turn based on active skill set and file reads
- **Per-skill token cost estimates** — Add estimated token ranges to skill metadata so the orchestrator can budget accurately
- **Skill dependency graph** — Machine-readable metadata declaring which skills each skill complements, overlaps with, or conflicts with
- **Compressed session export** — Generate a minimal replay document from a handoff summary for debugging or review
- **Command `$ARGUMENTS` validation** — Upgrade from warning to error in validate-skills.sh so every command must reference `$ARGUMENTS`

## Contribution Ideas

- Create a session replay utility from handoff summaries
- Add validation for handoff completeness across sessions
- Build a skill dependency graph for automatic loading
- Add `orchestration` field to skill frontmatter (lead-for, support-for, conflicts-with)
- End-to-end command smoke tests — integration tests that verify each command's output template matches its documentation
- Context budget tracking tool — extend `prompt_budget` to estimate context cost per active skill

## Versioning

See `CHANGELOG.md` for the release history and `README.md` for installation instructions.
