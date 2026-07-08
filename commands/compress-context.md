---
description: Compress the current session context into a concise but complete working summary
---

Compress the current session context using token-saver and context-engineering.

Preserve exactly:

- task goal
- constraints and assumptions
- exact error messages and stack frames
- files changed and their paths
- files inspected and summaries
- commands run and their exit status
- decisions made and rejected alternatives
- verification status
- remaining risks and open questions
- next action

Do not invent information.
Do not keep exploration that led nowhere.
Do not keep redundant or repeated content.
Do not remove exact error messages, file paths, or commands.

Remove or summarize:

- repeated log patterns
- irrelevant exploration branches
- framework-internal stack frames
- verbose explanations of decisions
- information that has been superseded

Return:

Context:
[Compressed summary covering all preserved fields above.]

Next action:
[Single next step.]

$ARGUMENTS
