# OpenCode Custom Tools — Design Document

## 1. Overview

Four custom tools that reduce LLM context waste without sacrificing coding-agent output quality. Each tool pairs a TypeScript file (the OpenCode tool definition) with a Python script (the implementation), following the official [OpenCode Custom Tools](https://opencode.ai/docs/custom-tools/) pattern: `import { tool } from "@opencode-ai/plugin"`, `Bun.$` for child process invocation, and `tool.schema` (Zod) for typed arguments.

### Naming Convention

| Directory | Purpose |
|-----------|---------|
| `tools/` | Python implementation scripts |
| `opencode-tools/` | TypeScript tool definitions (deployed to `~/.config/opencode/tools/`) |

Tool names use a `ctx_` prefix to avoid collision with built-in OpenCode tools (`read`, `write`, `bash`, `grep`, `glob`, `edit`, etc.).

---

## 2. Tool: `ctx_repo_map`

| Field | Value |
|-------|-------|
| **TypeScript file** | `opencode-tools/ctx_repo_map.ts` |
| **OpenCode tool name** | `ctx_repo_map` |
| **Python script** | `tools/repo_map.py` |
| **Invocation** | `Bun.$`python3 ${script} ${path} ${depth}`` |
| **Deploy path** | `~/.config/opencode/tools/ctx_repo_map.ts` |

### Purpose

Build a compact repository map (2–3 levels deep) that lets the coding agent skip full-tree exploration. The output is a Markdown tree of only directories that contain source files, excluding generated/vendor directories.

### Arguments

```ts
args: {
  path: tool.schema.string().describe("Absolute path to repository root"),
  depth: tool.schema.number().default(3).describe("Tree depth (default 3, max 6)"),
}
```

### Output Format

```
## Repo Map: /home/user/project

src/
├── routes/       [assignments.py, users.py]
├── services/     [assignment_service.py]
├── models/       [assignment.py, user.py]
└── schemas/      [assignment.py, user.py]
tests/
├── test_routes/  [test_assignments.py]
└── test_services/[test_assignment_service.py]
migrations/
└── versions/     [001_create_users.py, 002_create_assignments.py]
```

### Safety Rules

- Read-only: never creates, modifies, or deletes files.
- Respects `.gitignore` so generated dirs (`node_modules`, `__pycache__`, `.next`) are excluded.
- Depth capped at 6 to prevent explosion on deep monorepos.
- Path must exist and be a directory; otherwise returns error.

### Failure Behavior

| Scenario | Behavior |
|----------|----------|
| Path does not exist | Returns `ERROR: Path not found: <path>` |
| Path is a file, not directory | Returns `ERROR: Path is not a directory: <path>` |
| Permission denied | Returns `ERROR: Permission denied: <path>` |
| Python not found | Returns `ERROR: Python not found. Install python3.` |
| Script not found | Returns `ERROR: repo_map.py not found at <script_path>` |
| Depth outside 1–6 | Clamps silently to valid range |

### Test Strategy

| Test | What it validates |
|------|-------------------|
| `test_repo_map_valid_path` | Returns tree for valid repo |
| `test_repo_map_invalid_path` | Returns error for nonexistent path |
| `test_repo_map_file_path` | Returns error for file (not directory) |
| `test_repo_map_depth_0` | Works with depth=0 (just root) |
| `test_repo_map_depth_6` | Works with depth=6 (max) |
| `test_repo_map_ignored` | `.gitignore` patterns excluded |

Test via: `pytest tests/test_repo_map.py -q`

### Installer Integration

- `scripts/install-opencode.sh` gains a new section to symlink `opencode-tools/*.ts` → `~/.config/opencode/tools/`.
- `scripts/uninstall-opencode.sh` removes only symlinks originating from `opencode-tools/`.

### Uninstall

```bash
rm ~/.config/opencode/tools/ctx_repo_map.ts
```

### README Documentation

Add a section "Custom Tools" under the existing "Available Commands" table:

| Tool | Description |
|------|-------------|
| `ctx_repo_map` | Compact repository tree for efficient navigation |
| `ctx_diff_summary` | Summarize git diffs without dumping full diff |
| `ctx_compress` | Compress logs/context preserving critical details |
| `ctx_prompt_budget` | Estimate context size and recommend savings |

---

## 3. Tool: `ctx_diff_summary`

### Field | Value
|-------|-------|
| **TypeScript file** | `opencode-tools/ctx_diff_summary.ts` |
| **OpenCode tool name** | `ctx_diff_summary` |
| **Python script** | `tools/diff_summarizer.py` |
| **Invocation** | `Bun.spawn(["git", "diff", ...])` piped as input to the Python script |
| **Deploy path** | `~/.config/opencode/tools/ctx_diff_summary.ts` |

### Purpose

Summarize a git diff into file-level changes, function/section-level modifications, and a line-count summary. The coding agent gets enough context to understand what changed without reading the full diff.

### Arguments

```ts
args: {
  base: tool.schema.string().default("HEAD").describe("Base ref (default HEAD)"),
  head: tool.schema.string().optional().describe("Head ref (optional, uses working tree if omitted)"),
  path: tool.schema.string().optional().describe("Subdirectory or file path to scope the diff"),
  max_files: tool.schema.number().default(20).describe("Max files to show (default 20)"),
}
```

### Output

```markdown
## Diff Summary: base..head

### Files changed: 3

**src/routes/assignments.py** | +12 / -4
- Added `POST /assignments/{id}/grade` (line 45)
- Updated input validation on `create_assignment` (line 22)
- Removed deprecated `bulk_create` (line 89)

**src/services/assignment_service.py** | +8 / -1
- Added `grade_assignment()` method (line 67)
- Existing `create_assignment()` signature unchanged

**tests/test_assignments.py** | +25 / -0
- `test_grade_assignment_success` (line 120)
- `test_grade_assignment_invalid_score` (line 145)
```

### Safety Rules

- Read-only: does not modify files or git state.
- Uses `git diff` (no `-R`, no `--cached` write ops).
- Respects `max_files` to cap output size.
- Input `base` and `head` validated against `git rev-parse`.
- Never reveals secrets or environment variables.

### Python Script Design

`tools/diff_summarizer.py` reads git diff XML output from stdin and produces the summary by:

1. Parsing `git diff` output line by line.
2. Grouping by file, counting `+`/`-` lines.
3. Using hunks and proximity to `def`/`class`/`function` keywords to label function sections.
4. Truncating to `max_files` files.
5. Outputting Markdown.

### Failure Behavior

| Scenario | Behavior |
|----------|----------|
| Not a git repo | Returns `ERROR: Not a git repository: <path>` |
| `base` ref invalid | Returns `ERROR: Unknown revision: <base>` |
| `head` ref invalid | Returns `ERROR: Unknown revision: <head>` |
| No changes found | Returns `No changes between <base> and <head>` |
| Diff too large | Truncates at `max_files` with `+N more files truncated` |

### Test Strategy

| Test | What it validates |
|------|-------------------|
| `test_diff_summary_basic` | Summarizes a simple commit |
| `test_diff_summary_empty` | No changes between identical refs |
| `test_diff_summary_new_file` | New file detected with `+` only |
| `test_diff_summary_deleted_file` | Deleted file detected |
| `test_diff_summary_max_files` | Truncation with warning |
| `test_diff_summary_not_git` | Error for non-repo path |

Test via: `pytest tests/test_diff_summarizer.py -q`

### Installer Integration

Same as `ctx_repo_map` — `install-opencode.sh` symlinks `opencode-tools/ctx_diff_summary.ts`.

### Uninstall

```bash
rm ~/.config/opencode/tools/ctx_diff_summary.ts
```

### README Documentation

Output format and example usage in the Custom Tools table.

---

## 4. Tool: `ctx_compress`

### Field | Value
|-------|-------|
| **TypeScript file** | `opencode-tools/ctx_compress.ts` |
| **OpenCode tool name** | `ctx_compress` |
| **Python script** | `tools/context_compressor.py` |
| **Invocation** | `Bun.$`python3 ${script}`` with text piped via stdin |
| **Deploy path** | `~/.config/opencode/tools/ctx_compress.ts` |

### Purpose

Compress logs, stack traces, notes, or pasted context into a condensed summary that preserves exact errors, file paths, function names, and other critical details. This is the tool equivalent of the `token-saver` and `context-engineering` skills' compression guidance.

### Central Design Constraint — What Must NEVER Be Removed

The compressor must preserve these categories **verbatim** (no truncation, no summarization, no ellipsis):

| Category | Examples | Why |
|----------|----------|-----|
| Exact errors | `FileNotFoundError: /etc/config.yml` | Debugging relies on exact error text |
| File paths | `src/services/assignment_service.py:88` | Navigation depends on exact paths |
| Function names | `def grade_assignment()`, `class AssignmentService` | Code locations need exact names |
| API contracts | `POST /api/v1/assignments`, `{"grade": int, "max_score": int}` | Breaking changes must be visible |
| Schema changes | Column additions, type changes, nullable flips | Migration correctness |
| Migration details | Migration file names, `upgrade()`, `downgrade()` | Rollback safety |
| Security constraints | `@requires_role("admin")`, `@authenticated` | Security must never be hidden |
| Commands run | `pytest tests/ -q`, `ruff check .` | Verification reproducibility |
| Test results | `3 passed, 1 FAILED test_create_assignment` | Regression detection |
| Unresolved uncertainty | "I do not know why this fails" | Hiding uncertainty causes wrong fixes |

### Arguments

```ts
args: {
  text: tool.schema.string().describe("Text to compress (logs, stack trace, context notes)"),
  max_lines: tool.schema.number().default(60).describe("Target max output lines (default 60)"),
  preserve: tool.schema.string().optional().describe("Comma-separated additional keywords to preserve verbatim"),
}
```

### Output

```markdown
## Compressed Context (45 lines, from 312)

### Errors (preserved verbatim)
```
ValueError: score must be between 0 and 100
  File "src/services/assignment_service.py", line 88, in grade_assignment
    if not 0 <= score <= 100:
```

### Key Files
- `src/routes/assignments.py:42` — POST handler
- `src/models/assignment.py:25` — Assignment model
- `tests/test_assignments.py:120` — test_create_assignment

### Summary
[Function-level summary of non-critical adjacent context]
```

### Compression Algorithm

1. Parse input into sections (errors, file references, commands, test results, prose).
2. Preserve error lines, path+line references, commands, and test results verbatim.
3. Summarize log repeated lines: "Logged 14 times: [pattern]".
4. Summarize adjacent prose/reasoning to preserve meaning but reduce tokens.
5. Clip at `max_lines` with `[... truncated N lines ...]` marker, but NEVER clip across an error or security constraint.

### Safety Rules

- Read-only: never modifies files.
- Never removes error messages, file paths, function names, API contracts, schema changes, migration details, security constraints, commands run, test results, or unresolved uncertainty.
- `preserve` argument lets the caller designate additional keywords to keep verbatim.
- Returns full input if compression would discard protected content (prefer verbosity to data loss).

### Python Script Design

`tools/context_compressor.py`:

```
Input: stdin (text), env or CLI args for max_lines, preserve_list
1. Split into lines → classify each line (error, path+line, empty, prose, repeated, command, test_result)
2. Preserve protected categories verbatim
3. Deduplicate repeated log lines: count + representative line
4. Summarize prose: keep subject+verb+outcome, drop modifiers
5. Assemble in priority order: errors → protected items → summary
6. If output > max_lines, drop non-protected sections but never errors or constraints
```

### Failure Behavior

| Scenario | Behavior |
|----------|----------|
| Empty input | Returns empty string |
| Text shorter than max_lines | Returns original text unchanged |
| Text entirely protected categories | Returns full text (no compression possible without data loss) |
| Encoding issues | Returns `ERROR: Invalid input encoding` |

### Test Strategy

| Test | What it validates |
|------|-------------------|
| `test_compress_short_text` | Returns text unchanged when under max_lines |
| `test_compress_long_log` | Repeated lines compressed to count+pattern |
| `test_compress_error_preserved` | Error lines never removed |
| `test_compress_path_preserved` | File:line references never removed |
| `test_compress_command_preserved` | Commands never removed |
| `test_compress_security_preserved` | Security annotations never removed |
| `test_compress_empty` | Empty input returns empty |
| `test_compress_preserve_extra` | Custom preserve keywords kept verbatim |

Test via: `pytest tests/test_context_compressor.py -q`

### Installer Integration

Same as other tools — `install-opencode.sh` symlinks `opencode-tools/ctx_compress.ts`.

### Uninstall

```bash
rm ~/.config/opencode/tools/ctx_compress.ts
```

### README Documentation

Needs the "what is never removed" table prominently. This is the most important tool for the token-saver+context-engineering skill pair — it is the executable counterpart of their guidance.

---

## 5. Tool: `ctx_prompt_budget`

### Field | Value
|-------|-------|
| **TypeScript file** | `opencode-tools/ctx_prompt_budget.ts` |
| **OpenCode tool name** | `ctx_prompt_budget` |
| **Python script** | `tools/prompt_budget.py` |
| **Invocation** | `Bun.$`python3 script`` with text piped via stdin |
| **Deploy path** | `~/.config/opencode/tools/ctx_prompt_budget.ts` |

### Purpose

Estimate how many tokens a given text consumes and recommend a token-saving strategy. This gives the coding agent a concrete budget before it starts reading files or generating output.

### Arguments

```ts
args: {
  text: tool.schema.string().describe("Text to estimate token count for"),
  model: tool.schema.enum(["gpt-4", "claude-3", "default"]).default("default").describe("Model to estimate for"),
}
```

### Token Estimation

Uses the `tiktoken` Python library for accurate tokenization of supported models, falling back to `len(text) / 4` heuristic for unknown models.

| Model | Encoder |
|-------|---------|
| `gpt-4` | `cl100k_base` |
| `claude-3` | Approximate via `cl100k_base` |
| `default` | `cl100k_base` |

### Output

```markdown
## Prompt Budget

**Input chars:** 12,400
**Estimated tokens:** ~3,100 (model: gpt-4)
**Max capacity:** 128,000 tokens (model max)
**Usage:** 2.4%

### Recommendation
**Status: ✅ Under budget**

Context is well within limits. No compression needed.

### Token-Saving Suggestions
- This file uses ~3,100 tokens. Consider reading only imports/signatures (~200 tokens).
- Logs can be compressed with ctx_compress.
- Consider /compress-context for session-level compression.
```

When over an estimated threshold, recommendations change:

```markdown
**Usage:** 87.5%

### Recommendation
**Status: ⚠️ High usage**

### Token-Saving Actions
1. Run `ctx_compress` on the input text.
2. Use `ctx_repo_map` instead of scanning directories.
3. Consider /handoff-summary to start a fresh session.
4. Strip verbose logs; keep only error lines and paths.
```

### Safety Rules

- Read-only. Never sends text to external APIs.
- Estimation is approximate — the tool states "~" on every estimate.
- Never modifies input.
- Model enum only; not extensible at runtime to avoid injection.

### Python Script Design

`tools/prompt_budget.py`:

```
Input: stdin (text), sys.argv for model
1. Try: from tiktoken import encoding_for_model; enc = encoding_for_model(args.model)
2. Except: use cl100k_base
3. Except: tokens = len(text) // 4 (heuristic)
4. Output: JSON with chars, tokens, model, model_max, usage_pct, recommendation_key
```

### Output Format (internal, consumed by TypeScript wrapper)

```json
{
  "chars": 12450,
  "tokens": 3100,
  "model": "gpt-4",
  "model_max": 128000,
  "usage_pct": 2.4,
  "recommendation": "ok"
}
```

### Failure Behavior

| Scenario | Behavior |
|----------|----------|
| `tiktoken` not installed | Falls back to `len(text)//4` heuristic, warns in output |
| Empty input | Returns 0 tokens, 100% available |
| Unsupported model | Falls back to `cl100k_base`, notes the model used |

### Test Strategy

| Test | What it validates |
|------|-------------------|
| `test_prompt_budget_empty` | Returns 0 tokens for empty text |
| `test_prompt_budget_short` | Accurate token count for known text |
| `test_prompt_budget_long` | Token count scales proportionally |
| `test_prompt_budget_heuristic` | Fallback works without tiktoken |
| `test_prompt_budget_recommendation_ok` | Returns ok recommendation under threshold |
| `test_prompt_budget_recommendation_high` | Returns high-usage recommendation |

Test via: `pytest tests/test_prompt_budget.py -q`

### Installer Integration

Same as other tools.

### Uninstall

```bash
rm ~/.config/opencode/tools/ctx_prompt_budget.ts
```

### README Documentation

Include the model support table. Mention that `tiktoken` should be in `requirements.txt`.

---

## 6. Installer Integration Details

### Changes to `scripts/install-opencode.sh`

Add a section after the existing doc installation block:

```bash
# --------------------------------------------------
# Install custom tools (TypeScript → ~/.config/opencode/tools/)
# --------------------------------------------------

TOOLS_SOURCE_DIR="$REPO_ROOT/opencode-tools"
TOOLS_TARGET_DIR="$OPENCODE_CONFIG_DIR/tools"

if [[ -d "$TOOLS_SOURCE_DIR" ]]; then
    mkdir -p "$TOOLS_TARGET_DIR"

    for tool_file in "$TOOLS_SOURCE_DIR"/*.ts; do
        [[ -f "$tool_file" ]] || continue

        tool_filename="$(basename "$tool_file")"
        tool_name="${tool_filename%.ts}"
        target="$TOOLS_TARGET_DIR/$tool_filename"

        if [[ -L "$target" ]]; then
            echo "Replacing existing symlink: tool/$tool_name"
            rm "$target"
        elif [[ -e "$target" ]]; then
            echo "Warning: tool/$tool_name already exists and is not a symlink. Skipping."
            continue
        fi

        ln -s "$tool_file" "$target"
        echo "Installed tool: $tool_name"
        installed_tools=$((installed_tools + 1))
    done
fi
```

### Changes to `scripts/uninstall-opencode.sh`

Add a section to remove only symlinks from `opencode-tools/`:

```bash
# --------------------------------------------------
# Remove custom tools
# --------------------------------------------------
if [[ -d "$TOOLS_SOURCE_DIR" ]]; then
    for tool_file in "$TOOLS_SOURCE_DIR"/*.ts; do
        ...
        # Same resolve_path + symlink origin check pattern as skills section
    done
fi
```

### `requirements.txt` Additions

```text
tiktoken>=0.7.0
```

The `tiktoken` library is optional — `prompt_budget.py` falls back to heuristic if missing. But for accuracy it should be recommended.

### Python `pyproject.toml` Dependencies

```toml
dependencies = [
    "PyYAML>=6.0",
    "tiktoken>=0.7.0",
]
```

(Optional dep is fine; `import` is guarded.)

---

## 7. File Manifest

```
opencode-engineering-skills/
├── tools/
│   ├── repo_map.py               # Build directory tree with .gitignore
│   ├── diff_summarizer.py         # Parse git diff → section-level summary
│   ├── context_compressor.py      # Preserve-critical compression
│   └── prompt_budget.py           # Token estimation with tiktoken
├── opencode-tools/
│   ├── ctx_repo_map.ts            # Wrapper for repo_map.py
│   ├── ctx_diff_summary.ts        # Wrapper for diff_summarizer.py
│   ├── ctx_compress.ts            # Wrapper for context_compressor.py
│   └── ctx_prompt_budget.ts      # Wrapper for prompt_budget.py
├── tests/
│   ├── test_repo_map.py
│   ├── test_diff_summarizer.py
│   ├── test_context_compressor.py
│   └── test_prompt_budget.py
├── docs/
│   └── opencode-custom-tools-design.md  # This document
├── scripts/
│   ├── install-opencode.sh        # Updated: also install tools
│   └── uninstall-opencode.sh       # Updated: also remove tools
└── requirements.txt               # +tiktoken (optional)
```

---

## 8. Quality Rules — What Token-Saving Must Never Remove

This section is a cross-reference for the token-saver and context-engineering skills. Every tool in this set conforms to these rules.

| Category | Preserve verbatim? | Why not summarize? |
|----------|-------------------|--------------------|
| Exact errors | YES | Debugging requires exact error text and traceback |
| File paths | YES | Navigation requires exact paths |
| Function names | YES | Code locations depend on exact names |
| API contracts | YES | Breaking changes must be visible |
| Schema changes | YES | Migration correctness depends on exact diffs |
| Migration details | YES | Rollback safety depends on exact order |
| Security constraints | YES | Hiding security risks causes vulnerabilities |
| Commands run | YES | Reproducibility needs exact commands |
| Test results | YES | Regression detection needs exact pass/fail |
| Unresolved uncertainty | YES | Hiding uncertainty causes false fixes |

These rules are enforced by `ctx_compress` and referenced in the `token-saver` skill.

---

## 9. Design Decisions

### Why TypeScript tools invoke Python (not inline)

| Consideration | Decision |
|--------------|----------|
| Token estimation | `tiktoken` only has a Python API |
| Compression | String manipulation is simpler in Python |
| Git diff parsing | `git diff` returns text, Python parsing is mature |
| Directory walking | Python `os.walk` + `pathlib` + `gitignore` combining is simpler |
| Performance | Subprocess overhead is negligible for these operations (<50ms) |

### Why `ctx_` prefix

OpenCode built-in tools: `read`, `write`, `edit`, `bash`, `grep`, `glob`. The `ctx_` prefix avoids collisions while being short and meaningful (context tools).

### Why plugin pattern vs standalone tools

The official OpenCode docs support both:

1. **Standalone tool files** (`.opencode/tools/<name>.ts`) — simpler, one file per tool.
2. **Plugin-based tools** (`.opencode/plugins/<name>.ts` with `tool:` hook) — groups tools.

This design uses **standalone tool files** because:
- Easier to install (just copy/symlink).
- Easier to uninstall (delete one file).
- Simpler user mental model (one file = one tool).
- Official docs recommend this for simple tools.

### Why defaults are conservative

- `depth` defaults to 3 (not 6) to avoid flooding context.
- `max_files` defaults to 20 to cap diff summary size.
- `max_lines` defaults to 60 to keep compress output compact.
- All can be overridden when the agent needs more detail.

---

## 10. Test Configuration

Add to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

Tool tests follow the naming convention `test_<tool_name>.py` and use pytest fixtures to create temporary directories and git repos.

### Fixture Strategy

| Fixture | Used by | Purpose |
|---------|---------|---------|
| `tmp_repo` | `test_diff_summarizer` | Creates a temp git repo with commits |
| `tmp_project` | `test_repo_map` | Creates a temp project tree |
| `long_log_text` | `test_context_compressor` | Pre-made long log with repeated lines |
| `mixed_text` | `test_context_compressor` | Text with errors, paths, commands, prose |

---

## 11. README Documentation Plan

### New "Custom Tools" Section (in `README.md`)

After the existing "Available Commands" table, add:

```markdown
## Custom Tools

These tools are installed as OpenCode custom tools (TypeScript + Python pair). They help the agent conserve context without reducing output quality.

| Tool | Purpose | Invokes | Install path |
|-----|---------|---------|-------------|
| `ctx_repo_map` | Compact repository tree | `tools/repo_map.py` | `~/.config/opencode/tools/ctx_repo_map.ts` |
| `ctx_diff_summary` | Summarize git diffs | `tools/diff_summarizer.py` | `~/.config/opencode/tools/ctx_diff_summary.ts` |
| `ctx_compress` | Compress context while preserving errors/paths | `tools/context_compressor.py` | `~/.config/opencode/tools/ctx_compress.ts` |
| `ctx_prompt_budget` | Estimate token count and recommend savings | `tools/prompt_budget.py` | `~/.config/opencode/tools/ctx_prompt_budget.ts` |

### Quality Guarantee

These tools never remove:
- Exact error messages and stack traces
- File paths and line numbers
- Function names
- API contracts
- Schema or migration changes
- Security constraints
- Commands run or test results
- Unresolved uncertainty
```

### Update `docs/token-saving-guide.md`

Add a reference to `ctx_compress` and `ctx_prompt_budget` as runtime tools that implement the same rules as the `token-saver` skill.

### Update `docs/advanced-roadmap.md`

Mark "Automated context budget tracking" from "Planned" to "In progress" with a reference to `ctx_prompt_budget`.