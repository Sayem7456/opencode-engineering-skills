---
description: Apply a planned change safely with verification
---

Apply the planned change safely using testing-and-debugging skill and the relevant stack-specific skills.

Use the `diff_summarizer` custom tool to inspect the diff before applying, classify per-file risk, and detect affected symbols.

If the custom tool is unavailable, use the Python script directly from the cloned repository:
- python tools/diff_summarizer.py [--file <path> or --stdin]

Do not skip required code inspection or tests just to save tokens.
Do not summarize away security, schema, migration, or API contract details.

## Overlap control

Keep output proportional to task risk. Prefer concise findings over broad checklists.
Do not activate skills unrelated to the task scope.
Use supporting skills only when the lead skill does not cover the area.

Skill selection — Lead: Support: Guardrail: Excluded: Reason:

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
