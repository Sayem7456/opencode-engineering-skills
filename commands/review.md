---
description: Review the requested code without modifying it
---

Review the requested code using the relevant global skills.

Use the `diff_summarizer` custom tool to summarize git diffs with per-file risk classification, symbol detection, and skill/test suggestions.

If the custom tool is unavailable, use the Python script directly from the cloned repository:
- python tools/diff_summarizer.py [--file <path> or --stdin]

Do not skip required code inspection or tests just to save tokens.
Do not summarize away security, schema, migration, or API contract details.

## Overlap control

1. Start with `skill-orchestrator` when task scope is broad or ambiguous.
2. Select exactly one lead skill (`code-review`, `security-review`, or `production-readiness`).
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

Inspect related files, callers, tests, schemas, models, migrations, and API consumers before reporting findings.

Focus on:

- correctness
- security
- authorization
- transaction safety
- async and concurrency issues
- edge cases
- API compatibility
- performance
- missing regression tests

Report only evidence-based findings.

For each finding include:

1. Severity
2. File and location
3. Problem
4. Realistic impact
5. Smallest safe fix
6. Regression-test recommendation

Do not edit files.
Do not report formatting or personal style preferences.

Target:

$ARGUMENTS