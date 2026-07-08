# Review Pack

## Who This Is For

Engineers reviewing pull requests, performing security audits, or assessing code quality before merge. Suitable for tech leads, senior engineers, and security-conscious reviewers.

## Included Skills

| Skill | Purpose |
|-------|---------|
| `code-review` | Evidence-based reviews for correctness, regressions, maintainability |
| `security-review` | Auth, authorization, injection, secrets, SSRF, unsafe data handling |
| `testing-and-debugging` | Verification that changes include proper test coverage |
| `production-readiness` | Deployment safety, configuration, migrations, monitoring |

## Recommended Commands

- `/review` — review code with structured findings
- `/debug` — investigate reported issues before signing off
- `/plan` — plan the scope of changes before deep review
- `/safe-apply` — verify applied changes match the review

## Best Use Cases

- Reviewing a pull request before merge
- Performing a security audit on a new feature
- Assessing whether a change is production-ready
- Reviewing database migrations for safety
- Checking that tests cover the changed behavior

## Example Prompts

```
Use review-pack to review the new assignment submission endpoint for correctness, security, and production readiness.
```

```
Use review-pack to perform a security audit on the user authentication flow.
```

```
Use review-pack to assess whether the database migration is safe to deploy.
```

## Installation

```bash
npx skills add Sayem7456/opencode-engineering-skills \
  --skill code-review \
  --skill security-review \
  --skill testing-and-debugging \
  --skill production-readiness \
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

- Writing new code (use backend-pack or frontend-pack instead)
- Investigating a confirmed bug (use testing-and-debugging directly)
- Simple changes with no security or production risk
