# Backend Pack

## Who This Is For

Python backend developers building FastAPI services with SQLAlchemy and PostgreSQL. Suitable for API developers, service engineers, and backend-focused full-stack developers.

## Included Skills

| Skill | Purpose |
|-------|---------|
| `python-quality` | Production-quality Python, typing, error handling |
| `fastapi-backend` | FastAPI endpoints, validation, auth, background jobs |
| `sqlalchemy-postgres` | SQLAlchemy sessions, transactions, PostgreSQL, migrations |
| `testing-and-debugging` | Reproduction, root-cause analysis, regression tests |
| `security-review` | Auth, authorization, input handling, injection, secrets |

## Recommended Commands

- `/review` — review backend code before PR
- `/debug` — investigate a backend failure
- `/fix` — fix a confirmed backend defect
- `/implement` — implement a new endpoint or service
- `/refactor` — refactor backend logic safely
- `/plan` — plan backend changes before editing
- `/safe-apply` — apply planned changes with verification

## Best Use Cases

- Building a new FastAPI CRUD API
- Debugging a SQLAlchemy transaction failure
- Adding authentication and authorization to existing routes
- Reviewing a backend PR for correctness and security
- Refactoring business logic out of route handlers

## Example Prompts

```
Use backend-pack to implement a paginated teacher dashboard endpoint with branch-level access control.
```

```
Use backend-pack to debug why the assignment submission endpoint fails with a SQLAlchemy OperationalError.
```

```
Use backend-pack to review the new user registration endpoint for security and correctness.
```

## Installation

```bash
npx skills add Sayem7456/opencode-engineering-skills \
  --skill python-quality \
  --skill fastapi-backend \
  --skill sqlalchemy-postgres \
  --skill testing-and-debugging \
  --skill security-review \
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

- Frontend-only work (use frontend-pack instead)
- Simple single-file scripts that don't touch a database
- Projects using a different stack (Node.js, Go, etc.)
