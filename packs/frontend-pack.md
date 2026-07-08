# Frontend Pack

## Who This Is For

Frontend developers building Next.js applications with React and TypeScript. Suitable for UI engineers, frontend specialists, and designers implementing production interfaces.

## Included Skills

| Skill | Purpose |
|-------|---------|
| `nextjs-frontend` | Next.js, React, Server/Client Components, data fetching, caching |
| `ui-ux-design` | Accessible, responsive, polished user interfaces |
| `testing-and-debugging` | Reproduction, root-cause analysis, regression tests |
| `code-review` | Evidence-based reviews for correctness and regressions |
| `security-review` | Auth, XSS, CSRF, secrets, client-side safety |

## Recommended Commands

- `/review` — review frontend code before PR
- `/debug` — investigate a frontend rendering or data-fetching bug
- `/fix` — fix a confirmed frontend defect
- `/implement` — implement a new page or component
- `/refactor` — refactor components without changing behavior
- `/plan` — plan frontend changes before editing
- `/safe-apply` — apply planned changes with verification

## Best Use Cases

- Building a new Next.js page with data fetching
- Debugging a hydration mismatch or stale cache
- Adding loading, error, and empty states to a dashboard
- Reviewing a frontend PR for accessibility and correctness
- Refactoring a Client Component to a Server Component

## Example Prompts

```
Use frontend-pack to implement a responsive student dashboard page with server-side data fetching and loading states.
```

```
Use frontend-pack to debug why the assignment list component shows stale data after a mutation.
```

```
Use frontend-pack to review the new settings page for accessibility and state handling.
```

## Installation

```bash
npx skills add Sayem7456/opencode-engineering-skills \
  --skill nextjs-frontend \
  --skill ui-ux-design \
  --skill testing-and-debugging \
  --skill code-review \
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

- Backend-only API work (use backend-pack instead)
- Static sites with no interactivity or data fetching
- Projects not using Next.js or React
