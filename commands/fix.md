---
description: Fix a confirmed defect and add regression coverage
---

Fix the requested issue using the relevant global skills.

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