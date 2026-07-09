# Advanced Roadmap

This document tracks past, present, and planned improvements for the skill ecosystem.

## Completed — 1.2.0

- `skill-orchestrator` skill with lead/support/guardrail role model
- `docs/skill-orchestration-design.md` — full orchestration model, overlapping-pair resolution, 11 task categories
- `docs/skill-routing-matrix.md` — quick-reference task-to-skill routing table
- `/choose-skills` — skill plan generation before starting work
- `/smart-review` — review with one lead skill and scoped supporting skills
- `/smart-fix` — fix with minimum necessary skills and focused verification
- Overlap control sections added to all 7 existing commands
- README Overlap Mitigation section with bad/better prompt examples
- Documentation recommended files validation in both shell and Python validators

## Planned Enhancements

- **Automated context budget tracking** — estimate and report token consumption per session turn based on active skill set and file reads
- **Skill subset preloading** — agent automatically activates only the lead + necessary support skills without explicit prompt instructions
- **Skill dependency graph** — machine-readable metadata declaring which skills each skill complements, overlaps with, or conflicts with
- **Compressed session export** — generate a minimal replay document from a handoff summary for debugging or review
- **Per-skill token cost estimates** — add estimated token ranges to skill metadata so the orchestrator can budget accurately

## Contribution Ideas

- Create a session replay utility from handoff summaries
- Add validation for handoff completeness across sessions
- Build a skill dependency graph for automatic loading
- Add `orchestration` field to skill frontmatter (lead-for, support-for, conflicts-with)

## Versioning

See `CHANGELOG.md` for the release history and `README.md` for installation instructions.
