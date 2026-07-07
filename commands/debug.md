---
description: Investigate and identify the root cause of a bug
---

Investigate this bug using testing-and-debugging and the relevant stack-specific skills.

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