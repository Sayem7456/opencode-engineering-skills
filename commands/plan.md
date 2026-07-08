---
description: Create a compact implementation plan before editing code
---

Create a compact implementation plan using repository-navigation and the relevant stack-specific skills.

Before writing any code, inspect:

- the entry point and related files
- existing similar features for patterns
- relevant models, schemas, routes, services, and tests

Include in the plan:

- scope: what will and will not be changed
- files likely affected
- risks: what could go wrong
- tests: what test files will be added or updated
- validation commands: exact commands to run after implementation
- rollback considerations: how to revert if the change fails
- migration considerations if applicable

Do not start editing until the plan is approved.

Return:

Plan:

Scope:
[What will change and what will not.]

Files likely affected:
[Path — reason.]

Risks:
[What could break and how to mitigate.]

Tests:
[Test files to add or update.]

Validation:
[Exact commands to run after implementation.]

Rollback:
[How to revert if needed.]

$ARGUMENTS
