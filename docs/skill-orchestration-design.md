# Skill Orchestration Design

Reduce overlapping instructions between skills without removing useful guidance.

## Problem Summary

The following skill pairs share overlapping content:

| Pair | Overlap Area |
|------|-------------|
| `python-quality` + `testing-and-debugging` | Error handling, async rules, concurrency checks, test patterns, verification commands |
| `fastapi-backend` + `sqlalchemy-postgres` | Session lifecycle, transaction boundaries, connection handling, retry logic, idempotency |
| `code-review` + `security-review` | Finding format, severity levels, security checks, auth verification |
| `nextjs-frontend` + `ui-ux-design` | Components, forms, accessibility, responsive design, loading/error/empty states |
| `production-readiness` + `security-review` | Security readiness checks, auth validation, secret handling |
| `token-saver` + `context-engineering` | Selective reading, context summarization, handoff preparation, status output |

Loading both skills in a pair simultaneously duplicates instructions and consumes context without new information.

## Orchestration Metadata

Every skill now includes an `orchestration` block in its YAML frontmatter with three fields:

| Field | Type | Purpose |
|-------|------|---------|
| `lead_for` | list | Task types this skill can lead (e.g. `bug-fix`, `code-review`) |
| `support_for` | list | Task types where this skill adds value as a supporting skill |
| `conflicts_with` | list | Skills with significant overlap — avoid activating both simultaneously |

The skill-orchestrator uses this metadata to build a skill plan at task start, selecting the correct lead, filtering applicable supports, and suppressing conflicting pairs.

Example:
```yaml
orchestration:
  lead_for:
    - python-cleanup
  support_for:
    - fastapi-feature
    - bug-fix
  conflicts_with:
    - testing-and-debugging
    - fastapi-backend
```

See `ready-api.md` for the full skill-to-skill routing table and orchestration guide.

## Design Principles

1. **Every task has one lead skill.** The lead defines the approach, output format, and depth. Supporting skills fill domain-specific gaps.
2. **Supporting skills are scoped to their specialty.** They do not re-state guidance the lead already covers.
3. **Cross-cutting skills avoid repeating broad guidance.** `python-quality` and `code-review` do not re-state FastAPI- or SQLAlchemy-specific rules when those stack skills are loaded.
4. **Security is activated deeply only on security impact.** For tasks that do not touch auth, user input, files, or secrets, `security-review` is excluded.
5. **Production-readiness is activated deeply only for release/deployment work.** For feature implementation or bug fixes, it is excluded unless the change affects deployment.
6. **Token-saving reduces verbosity, not correctness.** `token-saver` never skips required verification, error handling, or safety checks.
7. **Output is concise unless the task requires detail.** Default output level is `concise`. Escalate to `detailed` only for security audits, production assessments, or code review.
8. **Critical safety, testing, and verification requirements are never removed.** No orchestration decision suppresses regression tests, rollback checks, or security validation.

## Skill Orchestration Model

Each active skill in a session belongs to one of four roles:

### Lead

One skill per task. It defines:

- **Task structure** — the workflow steps the agent follows
- **Output format** — how results are reported (finding format, summary style, verbosity)
- **Depth** — how deep to inspect (surface, focused, deep)
- **Verification scope** — which tests and checks are required

The lead skill is loaded first and its instructions take precedence when overlapping with supporting skills on the same topic.

### Supporting

Zero or more skills that fill domain-specific gaps the lead does not cover. Supporting skills:

- Activate only their unique sections
- Do not re-state guidance the lead already covers
- Apply to specific layers (database, frontend, API) without redefining the overall workflow

A supporting skill is excluded when its domain is not touched by the task.

### Optional Guardrail

Zero or one skill activated only when specific conditions are met:

| Guardrail | Activation Trigger |
|-----------|-------------------|
| `security-review` | Task touches authentication, authorization, user input, file upload, secrets, PII, external APIs, or AI/LLM output |
| `production-readiness` | Task is a release, deployment, migration, or infrastructure change |
| `token-saver` | Repository is large (>500 files), session is long (>10 turns), or context limits are a known constraint |
| `context-engineering` | Task spans multiple sessions, requires handoff, or involves >5 interconnected files |

Guardrail skills add checklist items and verification steps but do not change the lead skill's workflow or output format.

### Excluded

Skills explicitly excluded because their domain is not relevant to the current task. Exclusion prevents context waste from overlapping or irrelevant instructions.

## Overlapping Pair Resolution

### python-quality + testing-and-debugging

| Context | Lead | Supporting | Notes |
|---------|------|------------|-------|
| Writing new code | `python-quality` | — | testing-and-debugging is not needed for construction |
| Bug investigation | `testing-and-debugging` | `python-quality` | testing-and-debugging drives the workflow; python-quality ensures the fix meets quality standards |
| Code review | `code-review` | — | Neither is lead; code-review covers both angles |

When both are loaded, `testing-and-debugging` owns the reproduction workflow and root-cause analysis. `python-quality` owns the fix structure (type hints, error handling, resource cleanup). They do not duplicate test pattern guidance.

### fastapi-backend + sqlalchemy-postgres

| Context | Lead | Supporting | Notes |
|---------|------|------------|-------|
| Route/endpoint work | `fastapi-backend` | — | sqlalchemy-postgres excluded unless queries or models are modified |
| Database model/query | `sqlalchemy-postgres` | `fastapi-backend` | fastapi-backend relevant only if route handlers are also touched |
| Transaction debugging | `sqlalchemy-postgres` | `fastapi-backend` | fastapi-backend provides route/session context |
| Full service layer | `fastapi-backend` | `sqlalchemy-postgres` | sqlalchemy-postgres activated for database sections only |

When both are loaded, `fastapi-backend` owns route structure, DI, auth, and status codes. `sqlalchemy-postgres` owns session lifecycle, engine config, migrations, queries, and constraints. Neither re-states the other's session or transaction guidance.

### code-review + security-review

| Context | Lead | Supporting | Guardrail |
|---------|------|------------|-----------|
| General PR review | `code-review` | — | `security-review` only if auth/user-input/secrets touched |
| Security audit | `security-review` | — | `code-review` excluded (security-review covers its own format) |
| Changes touching auth/PII/files | `code-review` | — | `security-review` activated as guardrail |

When both are loaded, `code-review` owns the finding format and severity scale. `security-review` deep-dives only on security-related findings. `code-review` does not duplicate security checks that `security-review` covers.

### nextjs-frontend + ui-ux-design

| Context | Lead | Supporting | Notes |
|---------|------|------------|-------|
| Implementing a page/component | `nextjs-frontend` | `ui-ux-design` | ui-ux-design provides visual hierarchy, spacing, color guidance |
| UI redesign | `ui-ux-design` | `nextjs-frontend` | nextjs-frontend ensures implementation feasibility |
| Accessibility fix | `nextjs-frontend` | `ui-ux-design` | ui-ux-design adds WCAG depth |

When both are loaded, `nextjs-frontend` owns Server/Client Component boundaries, data fetching, caching, TypeScript, and security. `ui-ux-design` owns visual hierarchy, typography, color, spacing, microcopy, and user flows. They do not duplicate accessibility or state guidance — each has distinct aspects of it.

### production-readiness + security-review

| Context | Lead | Supporting | Guardrail |
|---------|------|------------|-----------|
| Release assessment | `production-readiness` | — | `security-review` is a built-in checklist section; no separate load needed |
| Security-critical release | `production-readiness` | `security-review` | security-review deep-dives on security controls; production-readiness retains the overall format |

When both are loaded, `production-readiness` owns the readiness level, blocker identification, deployment/rollback plan, and output format. `security-review` deepens the "Security Readiness" section but does not re-state findings in its own format.

### token-saver + context-engineering

| Context | Lead | Supporting | Notes |
|---------|------|------------|-------|
| Token-sensitive session | `token-saver` | — | context-engineering excluded unless multi-step |
| Complex multi-step task | `context-engineering` | — | token-saver excluded unless context limits are a constraint |
| Both constraints apply | `context-engineering` | `token-saver` | context-engineering owns the context model; token-saver adds file-reading tactics |

When both are loaded, `context-engineering` owns the structured context model (goal, constraints, hypotheses, decisions). `token-saver` provides tactical file-reading guidance (selective reads, grep before reading, avoid full-file dumps). They do not duplicate handoff or summarization guidance — `context-engineering` owns both with its structured template.

## Output Verbosity Levels

| Level | Description | Used When |
|-------|-------------|-----------|
| `minimal` | One-liner result, file list, pass/fail only | Trivial single-file changes, confirmed quick fixes |
| `concise` | Summary with key findings, no preamble | Default for all tasks unless overridden |
| `detailed` | Full findings with severity, location, impact, fix, verification | Code review, security review, production assessment |
| `exhaustive` | Complete trace including rejected approaches and all commands tried | Complex debugging, handoff preparation |

Lead skill sets the default level. Supporting skills do not escalate verbosity beyond the lead's level.

## Verification Levels

| Level | Scope | Used When |
|-------|-------|-----------|
| `none` | No verification | Trivial docs-only changes |
| `focused` | Single test, lint, typecheck on changed file only | Simple single-file bug fix |
| `module` | Full test file, lint, typecheck | Feature implementation, refactor |
| `full` | All tests, lint, typecheck, build | Deployment, release, production change |

The lead skill selects the verification level based on task risk and scope. No orchestration rule can downgrade verification below `focused` for code changes.

## Task Categories

### bug-fix

| Field | Value |
|-------|-------|
| Lead | `testing-and-debugging` |
| Supporting | Stack-specific skill if applicable (`fastapi-backend`, `sqlalchemy-postgres`, `nextjs-frontend`) |
| Guardrail | `security-review` if bug touches auth, input, or data |
| Excluded | `production-readiness`, `code-review`, `token-saver` (unless large repo), `context-engineering` (unless multi-turn) |
| Output verbosity | `concise` |
| Verification | `focused` (single test confirms fix, plus lint+typecheck) |

### code-review

| Field | Value |
|-------|-------|
| Lead | `code-review` |
| Supporting | Stack-specific skill if review touches that layer (`fastapi-backend`, `sqlalchemy-postgres`, `nextjs-frontend`) |
| Guardrail | `security-review` if diff touches auth, user input, secrets, files, or PII |
| Excluded | `testing-and-debugging`, `python-quality`, `token-saver`, `context-engineering`, `production-readiness` |
| Output verbosity | `detailed` |
| Verification | `none` (review does not execute code) |

### security-review

| Field | Value |
|-------|-------|
| Lead | `security-review` |
| Supporting | Stack-specific skill for domain depth (`fastapi-backend`, `sqlalchemy-postgres`, `nextjs-frontend`) |
| Guardrail | — |
| Excluded | `code-review`, `testing-and-debugging`, `python-quality`, `production-readiness`, `token-saver`, `context-engineering` |
| Output verbosity | `detailed` |
| Verification | `none` (review does not execute code) |

### fastapi-feature

| Field | Value |
|-------|-------|
| Lead | `fastapi-backend` |
| Supporting | `sqlalchemy-postgres` if database models/queries changed; `python-quality` for general Python quality |
| Guardrail | `security-review` if feature touches auth, user input, files, or PII |
| Excluded | `nextjs-frontend`, `ui-ux-design`, `code-review`, `production-readiness` (unless release-bound) |
| Output verbosity | `concise` |
| Verification | `module` (route tests + service tests + lint + typecheck) |

### database-issue

| Field | Value |
|-------|-------|
| Lead | `sqlalchemy-postgres` |
| Supporting | `fastapi-backend` if routes or DI layers are involved; `python-quality` for general Python |
| Guardrail | — |
| Excluded | `nextjs-frontend`, `ui-ux-design`, `code-review`, `security-review` (unless data contains PII), `production-readiness`, `token-saver`, `context-engineering` |
| Output verbosity | `concise` |
| Verification | `focused` (migration test + query test + lint + typecheck) |

### nextjs-feature

| Field | Value |
|-------|-------|
| Lead | `nextjs-frontend` |
| Supporting | `ui-ux-design` for UI decisions (visual hierarchy, spacing, color, microcopy) |
| Guardrail | `security-review` if feature touches auth, user input, secrets, or files |
| Excluded | `python-quality`, `fastapi-backend`, `sqlalchemy-postgres`, `production-readiness` (unless release-bound), `code-review` |
| Output verbosity | `concise` |
| Verification | `module` (component test + lint + typecheck + build) |

### ui-review

| Field | Value |
|-------|-------|
| Lead | `ui-ux-design` |
| Supporting | `nextjs-frontend` for implementation feasibility and accessibility depth |
| Guardrail | — |
| Excluded | `python-quality`, `fastapi-backend`, `sqlalchemy-postgres`, `code-review`, `security-review` (unless UI handles sensitive data), `production-readiness` |
| Output verbosity | `detailed` |
| Verification | `none` (review does not modify code) |

### refactor

| Field | Value |
|-------|-------|
| Lead | `code-review` |
| Supporting | Stack-specific skill (`fastapi-backend`, `sqlalchemy-postgres`, `nextjs-frontend`) for domain-level structural guidance |
| Guardrail | `testing-and-debugging` if behavioral changes are risky |
| Excluded | `security-review` (unless refactor touches auth boundaries), `production-readiness`, `ui-ux-design` (unless UI refactor), `token-saver` (unless large repo) |
| Output verbosity | `concise` |
| Verification | `module` (characterization tests + existing tests + lint + typecheck) |

### production-review

| Field | Value |
|-------|-------|
| Lead | `production-readiness` |
| Supporting | Stack-specific skills as needed for infrastructure details |
| Guardrail | `security-review` activated as a supporting skill (not just guardrail) for the security readiness section |
| Excluded | `code-review`, `ui-ux-design`, `nextjs-frontend` (unless Next.js-specific deployment), `token-saver` (unless large output), `context-engineering` (unless handoff needed) |
| Output verbosity | `detailed` |
| Verification | `full` (all tests + lint + typecheck + build + migration check) |

### ai-engineering

| Field | Value |
|-------|-------|
| Lead | Stack-specific AI skill: `structured-output-reliability`, `llm-app-security`, `prompt-injection-defense`, `rag-quality-review`, `ai-evaluation`, `ai-cost-optimization`, or `model-serving-production` |
| Supporting | `python-quality` for Python implementation |
| Guardrail | `security-review` (always activated for AI features touching untrusted input) |
| Excluded | `fastapi-backend`, `sqlalchemy-postgres`, `nextjs-frontend`, `ui-ux-design` (unless those layers exist), `production-readiness` (unless deployment), `token-saver`, `context-engineering` |
| Output verbosity | `concise` |
| Verification | `module` (unit tests + eval tests + lint + typecheck) |

### token-compression

| Field | Value |
|-------|-------|
| Lead | `context-engineering` if multi-step handoff; `token-saver` if session cost reduction |
| Supporting | `repository-navigation` for repo exploration (if applicable) |
| Guardrail | — |
| Excluded | All stack-specific skills, `code-review`, `security-review`, `production-readiness` |
| Output verbosity | `concise` (output is itself a compressed summary) |
| Verification | `none` |

## Category Selection Flow

```
Is this a review? ──► code-review / security-review / ui-review / production-review
Is this a bug fix? ──► bug-fix
Is this a refactor? ──► refactor
Is this a new feature? ──► fastapi-feature / nextjs-feature / ai-engineering
Is this a database-specific issue? ──► database-issue
Is this a token/context task? ──► token-compression
```

## Decision Table: When to Add or Exclude a Skill

| If | Then |
|----|------|
| Task touches authentication, authorization, user input, file upload, secrets, PII, external APIs, or AI/LLM output | Add `security-review` as guardrail |
| Task is a release, deployment, migration, or infrastructure change | Add `production-readiness` as guardrail |
| Repository has >500 files OR session is >10 turns | Add `token-saver` as guardrail |
| Task spans multiple sessions or >5 interconnected files | Add `context-engineering` as guardrail |
| Task is a single-file, no-auth, no-deployment change | Exclude all guardrails and non-stack skills |
| Both skills in an overlapping pair are loaded | Apply the pair-specific resolution table above |
| A supporting skill has no unique sections to contribute | Exclude it |
| A guardrail's activation conditions are not met | Exclude it |
| Output format is not specified | Default to lead skill's format at `concise` verbosity |

## Mapping to Existing Packs

| Pack | Orchestration Strategy |
|------|----------------------|
| `backend-pack` | Lead varies by sub-task: `fastapi-backend` for endpoints, `sqlalchemy-postgres` for DB, `testing-and-debugging` for bugs. `python-quality` and `security-review` are supporting. |
| `frontend-pack` | Lead varies by sub-task: `nextjs-frontend` for implementation, `ui-ux-design` for UI refinements. `testing-and-debugging` and `code-review` and `security-review` supporting. |
| `review-pack` | Lead `code-review` or `security-review` depending on review type. `testing-and-debugging` and `production-readiness` supporting for test coverage and deployment checks. |
| `production-pack` | Lead `production-readiness`. `security-review` deep-dives security. `sqlalchemy-postgres` supports DB sections. `token-saver` and `context-engineering` reduce context waste during assessment. |
| `ai-engineer-pack` | Lead varies by sub-task. `python-quality` supports implementation. `testing-and-debugging` supports evaluation. Token skills support context management. |
| `fullstack-pack` | Active skills always pruned per the decision table. No task uses all 12 skills. The pack covers the full span; orchestration selects the subset. |

## Implementation Notes

- This document describes an orchestration model. It does not modify skill files.
- Skill files retain all existing guidance. The orchestration model limits which skills are activated and how they interact.
- The agent applies these rules when selecting and loading skills at task start.
- Task category selection is determined by the user's request and the agent's analysis of the task type.
- Overlap resolution tables are consulted when two or more skills from an overlapping pair are both active.
- Verification level is a minimum — the agent may escalate based on observed risk during the task.
