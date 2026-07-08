---
description: Create a handoff summary for continuing in a new OpenCode session
---

Create a handoff summary using context-engineering so a new session can continue without reading prior conversation.

Include:

- goal
- current state of the work
- files changed and their paths
- important facts discovered
- commands run and results
- test results and verification status
- next steps in priority order
- warnings and remaining risks
- any environment or configuration requirements

Do not:
- omit commands that need to be re-run
- assume the next session has prior knowledge
- leave unresolved questions undocumented

Return:

Handoff summary:

Goal:
[Single sentence.]

Current state:
[What has been done and what remains.]

Files changed:
[Path — one-line change summary.]

Important facts:
[Key findings, decisions, error messages, configuration.]

Commands run:
[Command — exit status — summary of output.]

Test results:
[What passed, what failed, what is untested.]

Next steps:
[Ordered list with the first step to take.]

Warnings:
[Anything that could cause failure or confusion.]

$ARGUMENTS
