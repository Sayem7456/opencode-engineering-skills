# OpenCode Engineering Skills

A curated collection of reusable engineering skills and slash commands for OpenCode.

These skills provide structured workflows and engineering standards for:

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* Next.js
* React
* TypeScript
* JavaScript
* UI/UX design
* Testing and debugging
* Code review
* Security review
* Production readiness

The package helps OpenCode produce more consistent, maintainable, secure, and production-aware results across backend and frontend projects.

## Available Skills

| Skill                   | Purpose                                                                                                            |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `python-quality`        | Production-quality Python, typing, error handling, logging, testing, and maintainability                           |
| `fastapi-backend`       | FastAPI endpoints, validation, authentication, authorization, background jobs, and API reliability                 |
| `sqlalchemy-postgres`   | SQLAlchemy sessions, transactions, PostgreSQL, connection pooling, migrations, concurrency, and query safety       |
| `nextjs-frontend`       | Next.js, React, TypeScript, Server Components, Client Components, data fetching, caching, and frontend reliability |
| `ui-ux-design`          | Accessible, responsive, polished, and user-centered interface design                                               |
| `testing-and-debugging` | Reproduction, root-cause analysis, regression tests, and systematic verification                                   |
| `security-review`       | Authentication, authorization, input handling, secrets, injection, uploads, SSRF, and security risks               |
| `code-review`           | Evidence-based reviews focused on correctness, regressions, security, data integrity, and maintainability          |
| `production-readiness`  | Deployment safety, configuration, migrations, observability, health checks, rollback, and reliability              |

## Available Commands

| Command      | Purpose                                                     |
| ------------ | ----------------------------------------------------------- |
| `/review`    | Review selected code without modifying it                   |
| `/fix`       | Fix a confirmed defect and add regression coverage          |
| `/debug`     | Investigate a bug and identify its root cause               |
| `/implement` | Implement a new feature using existing project conventions  |
| `/refactor`  | Refactor existing code while preserving observable behavior |

## Repository Structure

```text
opencode-engineering-skills/
├── README.md
├── LICENSE
├── CHANGELOG.md
├── skills/
│   ├── python-quality/
│   │   └── SKILL.md
│   ├── fastapi-backend/
│   │   └── SKILL.md
│   ├── sqlalchemy-postgres/
│   │   └── SKILL.md
│   ├── nextjs-frontend/
│   │   └── SKILL.md
│   ├── ui-ux-design/
│   │   └── SKILL.md
│   ├── testing-and-debugging/
│   │   └── SKILL.md
│   ├── security-review/
│   │   └── SKILL.md
│   ├── code-review/
│   │   └── SKILL.md
│   └── production-readiness/
│       └── SKILL.md
├── commands/
│   ├── review.md
│   ├── fix.md
│   ├── debug.md
│   ├── implement.md
│   └── refactor.md
├── scripts/
│   ├── install-opencode.sh
│   ├── uninstall-opencode.sh
│   └── validate-skills.sh
└── tests/
    └── validate_skills.py
```

# Installation

## Prerequisites

You need:

* OpenCode
* Node.js with `npx`
* Git for manual installation
* Bash for installing the included slash commands

Check your installations:

```bash
opencode --version
node --version
npx --version
git --version
```

## Option 1: Install All Skills with the Skills CLI

Replace `YOUR_GITHUB_USERNAME` with the repository owner.

```bash
npx skills add YOUR_GITHUB_USERNAME/opencode-engineering-skills \
  --skill '*' \
  --agent opencode \
  --global
```

For non-interactive installation:

```bash
npx skills add YOUR_GITHUB_USERNAME/opencode-engineering-skills \
  --skill '*' \
  --agent opencode \
  --global \
  --yes
```

This installs the skills globally for OpenCode.

## Option 2: Install Selected Skills

Install only the skills relevant to your work:

```bash
npx skills add YOUR_GITHUB_USERNAME/opencode-engineering-skills \
  --skill python-quality \
  --skill fastapi-backend \
  --skill sqlalchemy-postgres \
  --agent opencode \
  --global
```

For Next.js development:

```bash
npx skills add YOUR_GITHUB_USERNAME/opencode-engineering-skills \
  --skill nextjs-frontend \
  --skill ui-ux-design \
  --skill testing-and-debugging \
  --agent opencode \
  --global
```

For reviews and release checks:

```bash
npx skills add YOUR_GITHUB_USERNAME/opencode-engineering-skills \
  --skill code-review \
  --skill security-review \
  --skill production-readiness \
  --agent opencode \
  --global
```

## Option 3: List Skills Before Installing

```bash
npx skills add YOUR_GITHUB_USERNAME/opencode-engineering-skills --list
```

## Option 4: Install from the Full GitHub URL

```bash
npx skills add \
  https://github.com/YOUR_GITHUB_USERNAME/opencode-engineering-skills \
  --agent opencode \
  --global
```

## Option 5: Install One Skill Directly

```bash
npx skills add \
  https://github.com/YOUR_GITHUB_USERNAME/opencode-engineering-skills/tree/main/skills/fastapi-backend \
  --agent opencode \
  --global
```

## Install Skills and Slash Commands

The Skills CLI installs the skills. To install both skills and the included OpenCode slash commands, clone the repository and run the installer:

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/opencode-engineering-skills.git
cd opencode-engineering-skills

chmod +x scripts/install-opencode.sh
./scripts/install-opencode.sh
```

The installer places or links content into:

```text
~/.config/opencode/skills/
~/.config/opencode/commands/
```

Restart OpenCode or open a new session after installation.

## Manual Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/opencode-engineering-skills.git
cd opencode-engineering-skills
```

Create the OpenCode directories:

```bash
mkdir -p ~/.config/opencode/skills
mkdir -p ~/.config/opencode/commands
```

Copy the skills:

```bash
cp -R skills/* ~/.config/opencode/skills/
```

Copy the commands:

```bash
cp commands/*.md ~/.config/opencode/commands/
```

Restart OpenCode after copying the files.

# Verify Installation

List installed skill files:

```bash
find ~/.config/opencode/skills \
  -maxdepth 2 \
  -name SKILL.md \
  -print
```

List installed commands:

```bash
find ~/.config/opencode/commands \
  -maxdepth 1 \
  -name '*.md' \
  -print
```

Check the beginning of every installed skill:

```bash
for file in ~/.config/opencode/skills/*/SKILL.md; do
  echo "===== $file ====="
  head -n 10 "$file"
done
```

Each skill should contain valid frontmatter:

```yaml
---
name: fastapi-backend
description: Build, review and debug production FastAPI services.
license: MIT
compatibility: opencode
metadata:
  category: backend
  stack: python-fastapi
  version: "1.0.0"
---
```

The folder name and frontmatter `name` should match exactly.

Example:

```text
Folder: fastapi-backend
Name:   fastapi-backend
```

# Updating

## Update Skills Installed with the Skills CLI

```bash
npx skills update
```

List globally installed skills:

```bash
npx skills list --global
```

## Update a Git Clone Installation

Enter the cloned repository:

```bash
cd opencode-engineering-skills
git pull
```

If the installer copies files rather than creating symbolic links, run it again:

```bash
./scripts/install-opencode.sh
```

# Uninstallation

## Remove an Individual Skill

```bash
npx skills remove fastapi-backend
```

## Remove Skills Installed by This Repository

From the cloned repository:

```bash
chmod +x scripts/uninstall-opencode.sh
./scripts/uninstall-opencode.sh
```

To manually remove selected skills:

```bash
rm -rf ~/.config/opencode/skills/python-quality
rm -rf ~/.config/opencode/skills/fastapi-backend
rm -rf ~/.config/opencode/skills/sqlalchemy-postgres
```

Remove the included commands manually:

```bash
rm -f ~/.config/opencode/commands/review.md
rm -f ~/.config/opencode/commands/fix.md
rm -f ~/.config/opencode/commands/debug.md
rm -f ~/.config/opencode/commands/implement.md
rm -f ~/.config/opencode/commands/refactor.md
```

# How Skills Work

OpenCode discovers the skills and makes them available to its agent.

It does not need to inject the complete content of every skill into every request. The agent can select relevant skills based on their names and descriptions.

For a FastAPI database task, relevant skills may include:

```text
python-quality
fastapi-backend
sqlalchemy-postgres
testing-and-debugging
```

For a Next.js dashboard task:

```text
nextjs-frontend
ui-ux-design
testing-and-debugging
```

For a pull request review:

```text
code-review
security-review
```

For a deployment assessment:

```text
production-readiness
security-review
```

You can explicitly name skills in your prompt when you want deterministic selection.

# Benefits

## 1. Consistent Engineering Standards

Without reusable skills, coding behavior may vary between sessions, models, and projects.

With skills, OpenCode receives consistent guidance about:

* typing
* validation
* error handling
* transactions
* authorization
* testing
* accessibility
* security
* production safety

## 2. Less Prompt Repetition

Instead of repeatedly writing long requirements, you can reference the appropriate skills:

```text
Use fastapi-backend, sqlalchemy-postgres, and testing-and-debugging to fix this endpoint.
```

## 3. Better Root-Cause Analysis

The debugging skill encourages OpenCode to:

1. Reproduce the failure.
2. Identify the smallest failing path.
3. Separate symptoms from root causes.
4. Confirm the cause with evidence.
5. Add regression coverage.
6. Apply the smallest safe fix.
7. Verify the result.

This reduces superficial fixes that only hide symptoms.

## 4. Safer Database Changes

The SQLAlchemy and PostgreSQL skill emphasizes:

* correct session lifecycle
* rollback after failure
* explicit transaction ownership
* fresh sessions for retries
* idempotency
* concurrency safety
* migration safety
* realistic connection-pool sizing

## 5. Better Code Reviews

The code-review skill prioritizes:

* correctness
* security
* data integrity
* concurrency
* API compatibility
* realistic regressions

It discourages low-value comments based only on personal style.

## 6. Better Frontend Quality

The Next.js and UI/UX skills encourage:

* correct server/client boundaries
* complete loading and error states
* responsive design
* runtime validation
* accessibility
* clear visual hierarchy
* safe caching
* usable forms

## 7. Better Production Readiness

The production-readiness skill checks more than whether tests pass.

It also considers:

* environment configuration
* deployment order
* database migrations
* health checks
* observability
* rollback
* background workers
* capacity
* failure handling

## 8. Reusable Across Projects

The global installation makes the same skills available across multiple repositories without copying instructions into each project.

Project-specific rules can still be defined separately in the project’s own `AGENTS.md`.

# Practical Difference by Skill

| Skill                   | Without the Skill                                                                                                  | With the Skill                                                                                                                           |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `python-quality`        | Code may run but contain weak typing, broad exceptions, resource leaks, or inconsistent structure                  | Stronger typing, focused functions, safer errors, cleaner resources, and structured verification                                         |
| `fastapi-backend`       | Routes may contain business logic, authorization may be incomplete, and request sessions may be reused incorrectly | Thin routes, explicit schemas, server-side authorization, controlled transactions, and safer background processing                       |
| `sqlalchemy-postgres`   | Fixes may focus only on pool settings or retries                                                                   | Session state, rollback, transaction boundaries, ambiguous commits, concurrency, constraints, and migrations are considered              |
| `nextjs-frontend`       | Pages may implement only the success state or misuse Client Components                                             | Better server/client boundaries, loading and error states, runtime validation, cache safety, and build verification                      |
| `ui-ux-design`          | An interface may be visually attractive but unclear, inaccessible, or inconsistent                                 | Better hierarchy, spacing, responsiveness, forms, accessibility, feedback, and design consistency                                        |
| `testing-and-debugging` | OpenCode may guess at the cause or apply several speculative changes                                               | Reproduction, hypothesis testing, root-cause evidence, regression tests, and focused verification                                        |
| `security-review`       | Security checks depend heavily on the prompt                                                                       | Authentication, authorization, secrets, injection, uploads, SSRF, tenant isolation, and unsafe data handling are reviewed systematically |
| `code-review`           | Reviews may focus on formatting, naming, or subjective preferences                                                 | Findings focus on realistic defects, impact, severity, minimal fixes, and regression coverage                                            |
| `production-readiness`  | Passing tests may be treated as sufficient for deployment                                                          | Configuration, migrations, health checks, monitoring, failure recovery, capacity, and rollback are also assessed                         |

# Advantages

* Reusable across multiple projects
* Reduces repeated prompt instructions
* Encourages evidence-based debugging
* Encourages focused regression tests
* Improves database and transaction safety
* Improves security review consistency
* Improves frontend accessibility and state handling
* Encourages smaller and more reviewable changes
* Provides structured code-review output
* Encourages production verification
* Works well with OpenCode’s built-in repository and shell tools
* Can be versioned and updated through Git

# Limitations and Disadvantages

## 1. Skills Do Not Guarantee Correctness

A skill improves the model’s process, but it cannot guarantee:

* correct implementation
* complete security
* passing tests
* correct architecture
* zero hallucinations
* production safety

Generated changes still require verification and human review.

## 2. Large Skills Consume Context

When a detailed skill is loaded, it uses part of the model’s context window.

Avoid activating every skill for every task.

Prefer relevant combinations.

## 3. Overlapping Instructions

Some skills intentionally overlap.

For example:

* `python-quality` and `testing-and-debugging`
* `fastapi-backend` and `sqlalchemy-postgres`
* `code-review` and `security-review`
* `nextjs-frontend` and `ui-ux-design`

Too many simultaneously active skills may make the agent overly cautious or verbose.

## 4. Repository Conventions Still Matter

These skills provide general standards. A project may have different:

* architecture
* transaction ownership
* testing tools
* framework versions
* deployment model
* naming conventions

OpenCode should inspect the current repository before applying generic patterns.

## 5. Skills Do Not Replace Documentation

Framework behavior changes over time.

Use current official documentation for version-specific behavior involving:

* FastAPI
* Pydantic
* SQLAlchemy
* PostgreSQL
* Next.js
* React
* TypeScript

## 6. Skills Do Not Replace Tests

A plausible-looking code change is not proof that a problem is solved.

Relevant tests, linting, type checks, builds, and runtime verification are still required.

## 7. Skills Can Be Too Strict for Small Tasks

A tiny change may not require:

* a full security review
* broad production-readiness analysis
* extensive architecture inspection
* the entire test suite

Use judgment and keep verification proportional to risk.

# Recommended Skill Combinations

## Python Bug Fix

```text
python-quality
testing-and-debugging
```

## FastAPI Endpoint

```text
python-quality
fastapi-backend
testing-and-debugging
```

## FastAPI Database Issue

```text
fastapi-backend
sqlalchemy-postgres
testing-and-debugging
```

## Next.js Feature

```text
nextjs-frontend
ui-ux-design
testing-and-debugging
```

## Pull Request Review

```text
code-review
security-review
```

## Refactoring

```text
code-review
testing-and-debugging
relevant stack-specific skill
```

## Pre-Deployment Assessment

```text
production-readiness
security-review
testing-and-debugging
```

# Example Prompts

## Review Python Code

```text
Review this Python module using:

- python-quality
- code-review
- security-review
- testing-and-debugging

Inspect related callers and tests before reporting findings.

Focus on:

- correctness
- typing
- error handling
- resource cleanup
- security
- edge cases
- missing regression coverage

For each finding, provide:

- severity
- file and line
- evidence
- realistic impact
- smallest safe fix
- regression-test recommendation

Do not modify the code.
Do not report style-only issues.

Target:
src/services/document_processor.py
```

## Review FastAPI and SQLAlchemy Code

```text
Review this feature using:

- fastapi-backend
- sqlalchemy-postgres
- code-review
- security-review

Check:

- request and response validation
- authentication
- object-level authorization
- database session lifecycle
- rollback and commit behavior
- transaction ownership
- duplicate requests
- concurrency
- tenant or branch isolation
- background task safety
- API compatibility
- error handling

Inspect related routes, services, schemas, models, migrations, and tests.

Do not edit files.
Return only evidence-based findings.
```

## Review a Next.js Page

```text
Review this page using:

- nextjs-frontend
- ui-ux-design
- code-review
- security-review

Check:

- Server and Client Component boundaries
- data fetching
- caching
- runtime validation
- authentication and authorization
- loading, empty, error, and unauthorized states
- responsive behavior
- accessibility
- duplicate submission
- frontend and backend contract mismatches
- secret exposure

Do not redesign the page unnecessarily.
Report findings by severity with exact file locations.

Target:
app/dashboard/students/page.tsx
```

## Find a Bug

```text
Investigate this bug using:

- testing-and-debugging
- relevant stack-specific skills

Reported behavior:
[Describe the problem.]

Expected behavior:
[Describe the expected result.]

Actual behavior:
[Describe the actual result.]

Relevant error or logs:
[Paste the error.]

Tasks:

1. Trace the complete execution path.
2. Reproduce the smallest failing case.
3. Separate symptom, trigger, root cause, and contributing conditions.
4. Inspect callers, state changes, database operations, and error handling.
5. Confirm the root cause with evidence.
6. Do not modify code until sufficient evidence is available.
7. Propose the smallest safe fix and regression test.

Do not present an unverified hypothesis as a confirmed cause.
```

## Fix a Bug

```text
Fix this issue using:

- testing-and-debugging
- python-quality
- relevant stack-specific skills

Workflow:

1. Reproduce the failure.
2. Identify and confirm the root cause.
3. Add or update a focused regression test.
4. Apply the smallest safe change.
5. Run the focused test.
6. Run relevant lint, type, and broader tests.

Do not:

- rewrite unrelated code
- weaken validation
- weaken types
- add arbitrary sleeps
- add retries without checking idempotency
- hide errors with broad exception handling
- claim success without verification

At the end, report:

- root cause
- files changed
- fix applied
- regression test
- commands run
- remaining limitations

Issue:
[Describe the issue.]
```

## Fix a SQLAlchemy Connection Failure

```text
Fix this FastAPI and SQLAlchemy connection issue using:

- fastapi-backend
- sqlalchemy-postgres
- testing-and-debugging
- python-quality

Pay special attention to:

- failed session state
- rollback
- session replacement
- transaction boundaries
- ambiguous commit outcomes
- idempotency
- duplicate processing
- request-scoped sessions passed to background tasks
- connection-pool behavior

Do not solve the problem only by increasing pool size or adding retries.

A retry must use a fresh session and must only be added when the operation is safe to retry.

Add focused regression coverage and run the relevant tests.
```

## Implement a FastAPI Feature

```text
Implement this feature using:

- fastapi-backend
- sqlalchemy-postgres
- python-quality
- testing-and-debugging
- security-review

Feature:
[Describe the feature.]

Required API:

- endpoint:
- method:
- request schema:
- response schema:
- permissions:
- database changes:
- background processing:
- expected failures:

Requirements:

- inspect the existing architecture first
- follow existing repository conventions
- keep route handlers thin
- use explicit request and response schemas
- enforce object-level authorization
- make transaction ownership explicit
- add database constraints for critical invariants
- make duplicate requests safe
- create migrations when required
- add API and service tests
- update documentation where necessary

Do not pass request-scoped sessions into background jobs.
Do not expose raw database or provider errors.

Run focused tests, lint, type checks, and relevant broader checks.
```

## Implement a Next.js Feature

```text
Implement this feature using:

- nextjs-frontend
- ui-ux-design
- testing-and-debugging
- security-review

Feature:
[Describe the feature.]

User flow:

1. [First step]
2. [Second step]
3. [Completion step]

Requirements:

- inspect the existing design system and architecture
- follow the current App Router or Pages Router structure
- prefer Server Components unless interactivity requires a Client Component
- validate API and form data at runtime
- implement loading, empty, error, unauthorized, and success states
- make the interface responsive
- preserve keyboard accessibility
- prevent duplicate form submission
- do not expose server secrets
- verify caching for user-specific data
- reuse existing components and design tokens

Add tests for the critical flow.

Run lint, type checking, focused tests, and the production build.
```

## Refactor an Existing Feature

```text
Refactor this feature using:

- code-review
- testing-and-debugging
- relevant stack-specific skills

Target:
[Feature or files]

Refactoring goals:

- improve clarity
- remove proven duplication
- improve testability
- improve structure

Constraints:

- preserve observable behavior
- preserve API contracts
- preserve database behavior
- preserve permissions
- do not introduce unnecessary dependencies
- do not change unrelated modules
- keep the patch reviewable

Workflow:

1. Inspect all callers and consumers.
2. Identify the existing public contract.
3. Add or confirm characterization tests.
4. Refactor in small steps.
5. Run focused tests after meaningful changes.
6. Run broader checks at completion.

Report:

- reason for the refactor
- structural changes
- behavior preserved
- tests and checks run
- remaining technical debt
```

## Perform a Security Review

```text
Review this feature using:

- security-review
- code-review
- relevant stack-specific skills

Check:

- authentication
- object-level authorization
- tenant isolation
- input validation
- SQL injection
- command injection
- path traversal
- SSRF
- unsafe file uploads
- secrets
- sensitive logging
- CORS and CSRF
- token handling
- rate limiting
- duplicate requests
- unsafe background processing
- untrusted LLM output

Report confirmed findings separately from items requiring verification.

Do not modify files.
Do not expose real secret values.
Do not inflate severity.
```

## Assess Production Readiness

```text
Assess this application using:

- production-readiness
- security-review
- testing-and-debugging

Review:

- production configuration
- required environment variables
- build and tests
- authentication and authorization
- database migrations
- connection-pool sizing
- background workers
- health and readiness checks
- logging and observability
- external service timeouts
- retries and idempotency
- resource limits
- deployment sequence
- rollback sequence

Classify the release as:

- Ready
- Conditionally ready
- Not ready
- Unable to determine

Separate release blockers from recommended improvements.

Do not deploy or run production migrations automatically.
```

# Slash Command Examples

## Review Code

```text
/review src/services/assignment_service.py
```

## Debug a Failure

```text
/debug Assignment submission intermittently fails with an SQLAlchemy OperationalError after the AI evaluation completes.
```

## Fix a Confirmed Defect

```text
/fix The background task reuses the request-scoped SQLAlchemy session after the request has completed.
```

## Implement a Feature

```text
/implement Add a paginated teacher assignment history endpoint with branch-level authorization and filtering by status.
```

## Refactor a Feature

```text
/refactor Refactor the assignment generation routes so business logic is moved into the service layer without changing the API contract.
```

# Best Practices

## Explicitly Name Skills for High-Risk Tasks

For critical database, security, or deployment work, explicitly mention the relevant skills.

Example:

```text
Use sqlalchemy-postgres, testing-and-debugging, and security-review for this task.
```

## Do Not Activate Every Skill Automatically

Use only skills relevant to the task.

Too many skills can:

* consume unnecessary context
* duplicate instructions
* make small tasks overly complex
* produce unnecessarily cautious responses

## Keep Project-Specific Rules in the Project

Global skills should contain reusable engineering guidance.

Place project-specific details in the repository’s own `AGENTS.md`, such as:

* architecture
* test commands
* environment names
* module ownership
* API conventions
* deployment procedures
* prohibited dependencies

## Verify Generated Changes

Always verify important changes with the project’s actual commands.

Typical Python checks:

```bash
ruff check .
ruff format --check .
mypy .
pyright
pytest
```

Typical Next.js checks:

```bash
npm run lint
npm run typecheck
npm test
npm run build
```

Run only commands that exist in the project.

# Validation

Validate the repository before publishing:

```bash
chmod +x scripts/validate-skills.sh
./scripts/validate-skills.sh
```

Run the Python validation test if provided:

```bash
python tests/validate_skills.py
```

Check whether the Skills CLI discovers the local skills:

```bash
npx skills add . --list
```

Validation should confirm:

* every skill directory contains `SKILL.md`
* every file has valid frontmatter
* every `name` matches its folder
* every skill has a description
* skill names use lowercase letters, numbers, and single hyphens
* no duplicate skill names exist
* command files contain valid metadata

# Versioning

This project follows semantic versioning.

```text
PATCH:
Wording corrections, minor rule improvements, and documentation fixes.

MINOR:
New skills, commands, or backward-compatible capabilities.

MAJOR:
Breaking changes to skill behavior, repository structure, or installation.
```

Create a release tag:

```bash
git tag -a v1.0.0 -m "Initial stable release"
git push origin v1.0.0
```

# Contributing

Contributions are welcome.

## Contribution Guidelines

1. Fork the repository.
2. Create a focused branch.
3. Update or add the relevant skill.
4. Keep instructions evidence-based and stack-aware.
5. Avoid duplicating rules unnecessarily.
6. Run the validation scripts.
7. Update `CHANGELOG.md`.
8. Open a pull request describing the problem and improvement.

Example:

```bash
git checkout -b improve/sqlalchemy-retry-guidance
./scripts/validate-skills.sh
python tests/validate_skills.py
```

## Skill Quality Requirements

A contributed skill should:

* have a clear purpose
* use valid frontmatter
* describe when it should be used
* define practical workflows
* separate confirmed issues from hypotheses
* discourage unsafe or destructive behavior
* require verification
* avoid unnecessary stack assumptions
* avoid promising guaranteed correctness
* remain reusable across repositories

# Security

Do not report sensitive security issues in a public GitHub issue.

For sensitive reports, contact:

```text
sayem1.ahamed@gmail.com
```

Do not include real:

* API keys
* access tokens
* passwords
* database URLs
* private keys
* production logs containing personal data

# License

This project is licensed under the MIT License.

See `LICENSE` for details.

# Disclaimer

These skills provide guidance to AI coding agents. They do not replace:

* experienced engineering review
* automated tests
* security testing
* current framework documentation
* database backups
* deployment safeguards
* production monitoring
* professional legal or compliance advice

Users are responsible for reviewing, testing, and validating all generated changes before using them in production.
