---
description: Apply a planned change safely with verification
---

Apply the planned change safely using testing-and-debugging and the relevant stack-specific skills.

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

Requirements:

- inspect the diff before applying
- make minimal changes scoped to the plan
- add or update focused tests
- run focused verification first
- run broader checks after verification passes
- report results clearly

Do not:

- skip diff inspection
- make changes outside the approved scope
- skip tests to save time
- skip verification steps
- claim success without running the planned validation commands

If verification fails:

- stop and report the failure
- do not apply additional speculative fixes
- identify the root cause before making further changes

Return:

Diff inspected:
[Confirmation or findings from diff review.]

Changes applied:
[Files and summary of each change.]

Tests added or updated:
[Test file — what was added.]

Verification:
[Commands run and results.]

Status:
[Pass or Fail with details.]

$ARGUMENTS
