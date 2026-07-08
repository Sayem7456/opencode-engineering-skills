# Fullstack Pack

## Who This Is For

Engineers working across the entire stack — backend APIs, frontend UIs, database, deployment, and everything in between. Suitable for full-stack developers, solo developers building complete features, and small teams.

## Included Skills

| Skill | Purpose |
|-------|---------|
| `python-quality` | Production-quality Python, typing, error handling |
| `fastapi-backend` | FastAPI endpoints, validation, auth, background jobs |
| `sqlalchemy-postgres` | SQLAlchemy sessions, transactions, PostgreSQL, migrations |
| `nextjs-frontend` | Next.js, React, Server/Client Components, data fetching |
| `ui-ux-design` | Accessible, responsive, polished user interfaces |
| `testing-and-debugging` | Reproduction, root-cause analysis, regression tests |
| `security-review` | Auth, authorization, injection, secrets, XSS |
| `code-review` | Evidence-based reviews for correctness and regressions |
| `production-readiness` | Deployment safety, configuration, health checks |
| `token-saver` | Efficient reading for large full-stack investigations |
| `context-engineering` | Structured context for multi-layer debugging |
| `repository-navigation` | Efficient exploration of unfamiliar codebases |

## Recommended Commands

- `/review` — review full-stack changes before PR
- `/debug` — investigate bugs that span backend and frontend
- `/fix` — fix confirmed defects across the stack
- `/implement` — implement end-to-end features
- `/refactor` — refactor backend or frontend safely
- `/plan` — plan full-stack changes before editing
- `/safe-apply` — apply planned changes with verification
- `/context-audit` — audit context when investigating cross-stack issues
- `/compress-context` — compress session for handoff
- `/handoff-summary` — prepare handoff for another developer

## Best Use Cases

- Building an end-to-end feature from database to UI
- Debugging a bug that spans the API layer and the frontend
- Implementing authentication flow from backend tokens to frontend guards
- Reviewing a full-stack pull request
- Refactoring API contracts and their frontend consumers together

## Example Prompts

```
Use fullstack-pack to implement a complete assignment submission feature with database model, API endpoint, and submission form.
```

```
Use fullstack-pack to debug why the dashboard shows incorrect data — trace from the frontend API call to the database query.
```

```
Use fullstack-pack to review the new authentication flow including backend JWT handling and frontend route protection.
```

## Installation

```bash
npx skills add Sayem7456/opencode-engineering-skills \
  --skill python-quality \
  --skill fastapi-backend \
  --skill sqlalchemy-postgres \
  --skill nextjs-frontend \
  --skill ui-ux-design \
  --skill testing-and-debugging \
  --skill security-review \
  --skill code-review \
  --skill production-readiness \
  --skill token-saver \
  --skill context-engineering \
  --skill repository-navigation \
  --agent opencode \
  --global
```

To also install the slash commands:

```bash
git clone https://github.com/Sayem7456/opencode-engineering-skills.git
cd opencode-engineering-skills
chmod +x scripts/install-opencode.sh
./scripts/install-opencode.sh
```

## When Not to Use

- Backend-only API work with no frontend component (use backend-pack)
- Frontend-only UI work (use frontend-pack instead)
- Simple single-file changes that don't need the full stack context
