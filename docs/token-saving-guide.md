# Token Saving Guide

This guide explains how the `token-saver`, `context-engineering`, and `repository-navigation` skills work together to reduce token waste during OpenCode sessions.

## How the Skills Interact

| Skill | Role |
|-------|------|
| `token-saver` | Selective file reading, lazy loading, compact reporting, avoiding unnecessary output |
| `context-engineering` | Building and preserving structured context across long tasks |
| `repository-navigation` | Efficient repo exploration using grep/glob before reading |

## When to Use Token-Saving Skills

- Large repositories with many files
- Long-running multi-step tasks
- Sessions with limited context windows
- Handoff between sessions or agents

## Recommended Combinations

See the README for full combination tables. Common patterns:

- Bug investigation: `token-saver + context-engineering + repository-navigation + testing-and-debugging`
- Large refactor: `token-saver + context-engineering + repository-navigation + code-review`
- Pre-deployment: `token-saver + context-engineering + production-readiness + security-review`

## Slash Commands

| Command | Description |
|---------|-------------|
| `/compress-context` | Compress session into a working summary |
| `/context-audit` | Audit current session for wasted context |
| `/handoff-summary` | Prepare handoff for a new session |
| `/plan` | Create compact implementation plan |
| `/safe-apply` | Apply planned change with verification |
