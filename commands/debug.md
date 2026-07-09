---
description: Investigate and identify the root cause of a bug
---

Investigate this bug using testing-and-debugging and the relevant stack-specific skills.

Use the `diff_summarizer` custom tool to examine recent diffs, classify per-file risk, and detect affected symbols. Use `repo_map` to navigate the repository and find relevant files.

If the custom tool is unavailable, use the Python script directly from the cloned repository:
- python tools/diff_summarizer.py [--file <path> or --stdin]
- python tools/repo_map.py [path]

Do not skip required code inspection or tests just to save tokens.
Do not summarize away security, schema, migration, or API contract details.

## Overlap control

1. Start with `skill-orchestrator` when task scope is broad or ambiguous.
2. Select exactly one lead skill (normally `testing-and-debugging`).
3. Use supporting skills only for specialized checks.
4. Do not activate `security-review` unless the task touches security-sensitive areas.
5. Do not activate `production-readiness` unless the task affects deployment, config, migrations, reliability, or release.
6. Do not activate `ui-ux-design` unless user-facing UI/UX is involved.
7. Do not activate `sqlalchemy-postgres` unless database, session, migration, or query code is involved.
8. Do not repeat generic advice from multiple skills.
9. Keep output proportional to task risk.
10. Prefer concise findings over broad checklists.

Skill selection:
- Lead:
- Support:
- Guardrail:
- Excluded:
- Reason:

Do not modify code until sufficient evidence identifies the likely root cause.

Trace:

- entry point
- callers
- state transitions
- database operations
- async operations
- external services
- frontend consumers
- relevant tests

Separate:

- symptom
- trigger
- root cause
- contributing conditions

Return:

1. Confirmed root cause or clearly labeled hypotheses
2. Evidence
3. Exact failing path
4. Affected files
5. Smallest safe fix
6. Regression-test plan

Bug:

$ARGUMENTS