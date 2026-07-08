# Production Pack

## Who This Is For

Engineers preparing a service for production deployment. Suitable for DevOps engineers, platform teams, and backend developers responsible for deploying and operating services.

## Included Skills

| Skill | Purpose |
|-------|---------|
| `production-readiness` | Deployment safety, configuration, health checks, rollback |
| `security-review` | Auth, authorization, secrets, network security, rate limiting |
| `sqlalchemy-postgres` | Connection pooling, migration safety, query performance |
| `testing-and-debugging` | Verification that production checks are tested |
| `token-saver` | Efficient reading when reviewing large production configs |
| `context-engineering` | Structured context for multi-faceted production reviews |

## Recommended Commands

- `/review` — review production configuration and setup
- `/debug` — investigate production incidents
- `/plan` — plan the deployment sequence and rollback steps
- `/context-audit` — audit whether current investigation is focused
- `/compress-context` — compress findings into a deployment summary

## Best Use Cases

- Pre-deployment readiness assessment
- Reviewing database migration plans for production
- Auditing environment configuration and secrets management
- Investigating production incidents with structured context
- Planning rollback strategies for risky deployments

## Example Prompts

```
Use production-pack to assess whether the new assignment service is ready for production deployment.
```

```
Use production-pack to review the database migration plan and connection pool configuration.
```

```
Use production-pack to investigate why the production endpoint is returning 502 errors under load.
```

## Installation

```bash
npx skills add Sayem7456/opencode-engineering-skills \
  --skill production-readiness \
  --skill security-review \
  --skill sqlalchemy-postgres \
  --skill testing-and-debugging \
  --skill token-saver \
  --skill context-engineering \
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

- Writing new feature code (use backend-pack or frontend-pack instead)
- Routine code reviews (use review-pack instead)
- Early-stage development before production concerns are relevant
