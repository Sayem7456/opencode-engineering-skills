---
description: Discover genuinely new capabilities for any repository without recommending existing or duplicate functionality
---
Before starting, load and use these installed global OpenCode skills:

* skill-orchestrator
* repository-navigation
* context-engineering
* token-saver

Use one lead skill and only necessary supporting skills.

Analyze:

$ARGUMENTS

Workflow:

1. Detect the repository type from actual files and configuration.
2. Build a compact inventory of existing features, components, patterns, and architecture.
3. Compare items semantically, not only by filename or name.
4. Exclude:

   * existing features and patterns
   * planned work (from docs, tickets, comments)
   * aliases or alternative names for the same thing
   * simple renames of existing functionality
   * substantial duplicates
5. Identify genuine gaps and improvement opportunities relevant to this repository.
6. For each potential addition or improvement, verify:

   * why current code is insufficient
   * nearest existing feature or pattern
   * distinct value it would add
   * expected impact (quality, performance, maintainability, etc.)
   * implementation scope
7. Prefer extending an existing pattern when a separate addition is not justified.
8. Rank validated recommendations:

   * High priority
   * Medium priority
   * Experimental
9. List rejected duplicates explicitly.
10. Do not modify files.

Required output:

# Repository Discovery

## Repository Type

## Current State Summary

## Confirmed Gaps

## Recommended New Capabilities or Features

For each recommendation:

* Name:
* Type:
* Why it is new:
* Nearest existing feature:
* Distinct value:
* Priority:

## Improvement Opportunities

For each improvement:

* Component or area:
* Current problem:
* Suggested improvement:
* Expected impact:
* Priority:

## Rejected Duplicates

## Recommended Roadmap

Do not recommend existing functionality as new.
Do not invent repository capabilities.
Keep the result proportional to the repository and request.
