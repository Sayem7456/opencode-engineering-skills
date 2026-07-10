# Skill Routing Matrix

Choose skills without causing overlap or excessive verbosity.

## Core Rule

Use **one lead skill**. Add supporting skills only when needed. Do not activate all skills by default.

## Skill Roles

| Role | Description |
|------|-------------|
| **Lead** | One per task. Defines workflow, output format, inspection depth, and verification scope. Its instructions take precedence on overlapping topics. |
| **Support** | Fills domain-specific gaps the lead does not cover. Activates only its unique sections. Excluded when its domain is not touched. |
| **Guardrail** | Activated only when specific conditions are met (e.g., security-sensitive areas, deployment changes). Adds checklist items but does not change the lead's workflow. |
| **Verification** | Runs tests, lint, type checks, and builds. Usually `testing-and-debugging` when active. The lead defines verification depth. |
| **Documentation** | Defines output formatting, finding structure, or summary templates. The lead's output format takes precedence. |

## Task Routing Table

| Task | Lead Skill | Supporting Skills | Guardrail Skills | Avoid Unless Needed | Verification Depth |
|------|-----------|-------------------|------------------|---------------------|-------------------|
| Python bug | `testing-and-debugging` | Stack skill (`fastapi-backend`, `sqlalchemy-postgres`, etc.) | `security-review` if auth, secrets, files, SQL, or external calls involved | `production-readiness`, `code-review`, `ui-ux-design` | focused |
| FastAPI endpoint | `fastapi-backend` | `python-quality` | `security-review` if auth, file upload, tenant, or untrusted input | `production-readiness`, `nextjs-frontend`, `ui-ux-design` | module |
| SQLAlchemy issue | `sqlalchemy-postgres` | `testing-and-debugging` | — | `nextjs-frontend`, `ui-ux-design`, `security-review` (unless data contains PII) | focused |
| Alembic migration | `sqlalchemy-postgres` | — | `production-readiness` if migration affects production | `security-review`, `code-review`, `testing-and-debugging` | focused |
| Next.js page | `nextjs-frontend` | `ui-ux-design` for visual/UX decisions | `security-review` if auth, cookies, secrets, or private data | `python-quality`, `fastapi-backend`, `sqlalchemy-postgres` | module |
| UI redesign | `ui-ux-design` | `nextjs-frontend` for feasibility | — | `python-quality`, `fastapi-backend`, `sqlalchemy-postgres`, `security-review` (unless sensitive data UI) | none (review) |
| Pull request review | `code-review` | Stack skill for changed stack | `security-review` if diff touches auth, input, secrets, files, or PII | `testing-and-debugging`, `python-quality`, `production-readiness` | none (review) |
| Security review | `security-review` | `code-review`, stack skill for technical context | — | `testing-and-debugging`, `python-quality`, `production-readiness` | none (review) |
| Production release | `production-readiness` | Stack skills as needed for infrastructure | `security-review` | `code-review`, `nextjs-frontend` (unless Next.js-specific), `ui-ux-design` | full |
| Large refactor | `code-review` | `testing-and-debugging`, relevant stack skill | `production-readiness` if deployment behavior changes | `security-review` (unless auth boundaries touched), `ui-ux-design` (unless UI refactor) | module |
| RAG feature | `rag-quality-review` | `python-quality` | `security-review` for untrusted input | `fastapi-backend`, `sqlalchemy-postgres`, `nextjs-frontend`, `ui-ux-design` (unless those layers exist) | module |
| Structured LLM output | `structured-output-reliability` | `python-quality` | `security-review` for untrusted input | `fastapi-backend`, `sqlalchemy-postgres`, `nextjs-frontend` | module |
| AI system architecture | `ai-system-architecture` | — | `security-review` if auth, PII, or external APIs are in scope | `testing-and-debugging`, `production-readiness` (unless implementation phase) | none (review) |
| System architecture review | `system-architecture` | — | `security-review` if auth, PII, or external APIs in the architecture | `testing-and-debugging`, `sqlalchemy-postgres` (unless those layers touched) | none (review) |
| Token compression | `token-saver` or `context-engineering` | `repository-navigation` if repo exploration needed | — | All stack skills, `code-review`, `security-review`, `production-readiness` | none |

## Examples

### Bad prompt (activates too many skills)

```text
Use python-quality, fastapi-backend, sqlalchemy-postgres, nextjs-frontend,
ui-ux-design, testing-and-debugging, security-review, code-review,
and production-readiness to fix the login endpoint timeout.
```

Problem: 9 skills activated for a focused bug fix. Most add no value.
- `nextjs-frontend` and `ui-ux-design` are irrelevant (no frontend change)
- `code-review` duplicates `testing-and-debugging` on finding format
- `production-readiness` is not needed for a bug fix
- `python-quality` overlaps with `fastapi-backend` on error handling guidance

### Better prompt (lead / support separation)

```text
Use testing-and-debugging as lead, fastapi-backend as support,
and security-review as guardrail to fix the login endpoint timeout.
```

Rationale:
- Lead: `testing-and-debugging` drives the reproduction and root-cause workflow
- Support: `fastapi-backend` provides FastAPI-specific debugging (DI, auth deps, session lifetime)
- Guardrail: `security-review` because login touches auth and secrets
- Excluded: `nextjs-frontend`, `ui-ux-design`, `sqlalchemy-postgres` (no DB change), `code-review`, `production-readiness`, `python-quality` (covered by fastapi-backend)

## Output Verbosity Guidance

| Level | When to Use |
|-------|-------------|
| `concise` | Small changes, confirmed quick fixes, routine updates |
| `standard` | Normal feature implementation, typical debugging |
| `detailed` | Code review, security review, production assessment, complex debugging, or when the user asks for detail |

Default: `standard`.

## Safety Note

Overlap reduction must not skip critical checks. The following are never removed by orchestration:

- Regression tests for changed behavior
- Security validation for auth, input, secrets, or PII touches
- Rollback planning for migration or deployment changes
- Verification commands (lint, typecheck, test, build) appropriate to the task risk

If a guardrail skill's activation conditions are met, it must be included. If a task touches security-sensitive areas, `security-review` is required regardless of verbosity level.
