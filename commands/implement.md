---
description: Implement a new feature using existing project conventions
---

Implement this feature using the relevant global skills.

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