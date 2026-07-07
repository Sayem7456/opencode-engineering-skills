---
description: Refactor existing code while preserving observable behavior
---

Refactor the specified feature using code-review, testing-and-debugging, and relevant stack-specific skills.

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