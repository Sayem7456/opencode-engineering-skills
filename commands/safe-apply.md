---
description: Apply findings or recommended changes from a review safely with per-finding verification
---

Apply findings or planned changes safely. When consuming review output, apply each finding's
recommended fix and regression test independently using `testing-and-debugging` and stack-specific skills.

Use the `diff_summarizer` custom tool to inspect the diff before applying, classify per-file risk, and detect affected symbols.

If the custom tool is unavailable, use the Python script directly from the cloned repository:
- python tools/diff_summarizer.py [--file <path> or --stdin]

Do not skip required code inspection or tests just to save tokens.
Do not summarize away security, schema, migration, or API contract details.

## Input

This command accepts either:
- **Review findings** — output from `/review` or `/smart-review` containing items each with a Severity, File, Problem, Impact, Fix, and Test recommendation
- **Planned changes** — a standalone description of changes to make

When findings are provided, treat each finding as a work item. Do not batch them into one change.

## Per-finding workflow

For each finding or change:

1. Locate the affected file and understand the context
2. Apply the smallest safe fix scoped to this item
3. Add or update the recommended regression test
4. Run focused verification for this item
5. Report status before moving to the next item

If a finding's fix introduces a new issue, stop and report before proceeding.

## Overlap control

Keep output proportional to task risk. Prefer concise findings over broad checklists.
Do not activate skills unrelated to the task scope.
Use supporting skills only when the lead skill does not cover the area.

Skill selection — Lead: `testing-and-debugging`. Support: Guardrail: Excluded: Reason:

Requirements:

- inspect the diff before applying
- consume review findings (severity, location, fix, test recommendation)
- apply each finding independently
- add or update focused tests per finding
- run focused verification per finding
- run broader checks after all items pass
- report per-item and overall status

Do not:

- skip diff inspection
- make changes outside the approved scope
- batch findings into one unfocused change
- skip tests to save time
- skip verification steps
- claim success without running the planned validation commands

If verification fails:

- stop and report the failure
- do not apply additional speculative fixes
- identify the root cause before making further changes

## Output format

**Input source:** [review findings / planned changes]

**Items resolved:**

- [Severity] Title — File:
  Fix applied:
  Test added:
  Verification:
  Status: [Pass / Fail]

...

**Skipped items:**

[Items not applied and why.]

**Broader verification:**

[Commands run and results after all items.]

**Status:**

[Pass or Fail with details.]
