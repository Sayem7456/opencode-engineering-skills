---
description: Fix a confirmed defect and add regression coverage
---

Fix the requested issue using the relevant global skills.

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

Workflow:

1. Inspect the relevant execution path.
2. Reproduce the failure when possible.
3. Confirm the root cause with evidence.
4. Add or update a focused regression test.
5. Apply the smallest safe fix.
6. Run the focused test.
7. Run relevant lint, type, and broader tests.

Do not:

- rewrite unrelated code
- weaken validation or typing
- hide errors with broad exception handling
- add arbitrary sleeps
- add retries without checking idempotency
- claim success without verification

At the end report:

- root cause
- files changed
- fix applied
- regression test
- commands run
- remaining limitations

Issue:

$ARGUMENTS