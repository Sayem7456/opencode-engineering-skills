---
description: Audit whether the current task is wasting context and identify improvements
---

Audit the current session context using token-saver and context-engineering.

Identify:

- irrelevant files that were read but not needed
- repeated outputs or redundant explanations
- oversized logs or full-file dumps
- stale assumptions that no longer apply
- missing critical context that should be loaded
- skills loaded but not needed for the current step
- generated or transient files read unnecessarily

For each waste item found, include:

- what was wasted
- estimated impact on context
- how to avoid it going forward

Return:

Waste found:
[List of items with impact estimates.]

Missing context:
[Critical information that should be loaded.]

Next minimal reads:
[The smallest set of files or commands needed to fill gaps.]

$ARGUMENTS
