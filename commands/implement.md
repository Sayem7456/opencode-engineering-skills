---
description: Implement a new feature using existing project conventions
---

Implement this feature using the relevant global skills.

## Overlap control

1. Start with `skill-orchestrator` when task scope is broad or ambiguous.
2. Select exactly one lead skill (normally `fastapi-backend`, `nextjs-frontend`, or a stack-specific skill).
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

Before coding:

1. Inspect the repository architecture.
2. Find related features and reusable abstractions.
3. Confirm installed framework and dependency versions.
4. Identify affected APIs, models, schemas, UI, permissions, migrations, and tests.
5. Define the smallest implementation consistent with the existing architecture.

Requirements:

- preserve unrelated behavior
- validate untrusted input
- enforce authentication and authorization
- handle errors and edge cases
- keep transaction boundaries explicit
- avoid duplicate abstractions
- add focused tests
- update documentation where necessary

After implementation run:

- focused tests
- lint
- type checking
- relevant broader tests
- production build when applicable

Report changed files and verification results.

Feature:

$ARGUMENTS