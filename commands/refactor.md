---
description: Refactor existing code while preserving observable behavior
---

Refactor the specified feature using code-review, testing-and-debugging, and relevant stack-specific skills.

## Overlap control

1. Start with `skill-orchestrator` when task scope is broad or ambiguous.
2. Select exactly one lead skill (normally `code-review`).
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

Goals:

- improve clarity
- remove proven duplication
- improve testability
- improve structure
- preserve public behavior

Before changing code:

1. Inspect all callers and consumers.
2. Identify the current public contract.
3. Add or confirm characterization tests.
4. Identify risks involving API responses, transactions, permissions, and state.

Constraints:

- do not change API contracts unless explicitly requested
- do not change database behavior unintentionally
- do not introduce unnecessary dependencies
- do not rewrite unrelated modules
- keep the patch reviewable

Run focused tests after meaningful steps and broader checks at completion.

Target:

$ARGUMENTS