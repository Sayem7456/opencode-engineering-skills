---
description: Apply a planned change safely with verification
---

Apply the planned change safely using testing-and-debugging and the relevant stack-specific skills.

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
