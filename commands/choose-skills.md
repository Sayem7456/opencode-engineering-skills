---
description: Choose the best lead skill and supporting skills for a task while avoiding overlapping instructions.
---

Analyze the task and produce a skill plan. Do not modify files. Do not activate all skills by default.

$ARGUMENTS

Follow these rules:

1. Select exactly one lead skill.
2. Select only necessary supporting skills. A supporting skill must contribute guidance the lead does not cover.
3. Select guardrail skills only when the task justifies them:
   - `security-review` — only if the task touches auth, authorization, user input, file upload, secrets, PII, external APIs, or AI/LLM output
   - `production-readiness` — only if the task is a release, deployment, migration, or infrastructure change
   - `token-saver` — only if the repository is large (>500 files) or the session is long (>10 turns)
   - `context-engineering` — only if the task spans multiple sessions or involves >5 interconnected files
4. Explicitly list skills intentionally not used and explain why.
5. Choose verbosity:
   - `concise` — summary only, for small changes or confirmed quick fixes
   - `standard` — key findings with brief context, for normal tasks
   - `detailed` — full findings with severity and impact, for reviews, debugging, security, production, or user request
6. Choose verification depth:
   - `none` — trivia or docs-only changes
   - `focused` — single test plus lint and typecheck on changed file only
   - `broad` — full test file plus lint, typecheck, and build
   - `production-grade` — all tests, lint, typecheck, build, and migration checks

Output format:

```
Skill plan:
- Task type:
- Lead skill:
- Supporting skills:
- Guardrail skills:
- Skills intentionally not used:
- Why:
- Verbosity:
- Verification depth:
- Suggested next prompt:
```
