#!/usr/bin/env python3
"""Compress logs, stack traces, notes, or session context preserving critical details."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

ERROR_PATTERN = re.compile(
    r"(?:"
    r"(?:Traceback|Error|Exception|Warning|Fatal|FAILED|Failure)"
    r"|"
    r"(?:raise\s+\w+(?:Error|Exception|Warning))"
    r"|"
    r"(?:[A-Za-z_]\w*(?:Error|Exception|Warning)\s*:)"
    r")",
    re.IGNORECASE,
)

PATH_LINE_PATTERN = re.compile(
    r'File\s+"([^"]+)",\s*line\s*(\d+)(?:,\s*in\s+(\w+))?'
)

COMMAND_PATTERN = re.compile(
    r"(?:"
    r"(?:^|\s)(?:python|python3|pytest|npm|npx|yarn|pnpm|"
    r"ruff|mypy|black|flake8|docker|docker-compose|make|"
    r"cargo|go|rustc|node|bun|deno|curl|wget|git)\s+"
    r")",
    re.IGNORECASE,
)

HTTP_PATTERN = re.compile(
    r"(GET|POST|PUT|PATCH|DELETE|OPTIONS)\s+/(?:[^\s]+)",
    re.IGNORECASE,
)

TABLE_PATTERN = re.compile(
    r"(?:create_table|drop_table|alter_table|add_column|"
    r"drop_column|rename_column|ALTER TABLE|CREATE TABLE)",
    re.IGNORECASE,
)

ENV_VAR_PATTERN = re.compile(
    r"(?:[A-Z_]{3,})\s*[=:]\s*(?:\S+)",
)

TEST_FAIL_PATTERN = re.compile(r"(FAILED|PASSED|ERRORS|FAILURES)", re.IGNORECASE)

REPEATED_LOG_PATTERN = re.compile(
    r"^\s*(?:INFO|WARN|ERROR|DEBUG|TRACE|WARNING|CRITICAL|FATAL)\s+.*",
    re.IGNORECASE,
)


def _classify_line(line: str) -> str:
    stripped = line.strip()
    if not stripped:
        return "empty"
    if PATH_LINE_PATTERN.search(line):
        return "path_line"
    if ERROR_PATTERN.search(line):
        return "error"
    if COMMAND_PATTERN.search(line):
        return "command"
    if HTTP_PATTERN.search(line):
        return "http_route"
    if TABLE_PATTERN.search(line):
        return "schema_migration"
    if ENV_VAR_PATTERN.match(stripped):
        return "env_var"
    if TEST_FAIL_PATTERN.search(line):
        return "test_result"
    if REPEATED_LOG_PATTERN.match(stripped):
        return "log_entry"
    return "prose"


def compress_text(
    text: str,
    max_lines: int = 60,
    preserve_errors: bool = True,
    preserve_paths: bool = True,
) -> str:
    if not text.strip():
        return ""

    lines = text.splitlines()
    total_lines = len(lines)

    if total_lines <= max_lines:
        return text

    classified: List[Tuple[str, str, int]] = []
    for i, line in enumerate(lines):
        ctype = _classify_line(line)
        classified.append((ctype, line, i))

    preserved_lines: List[str] = []
    errors: List[str] = []
    path_lines: List[str] = []
    commands: List[str] = []
    http_routes: List[str] = []
    schema_migrations: List[str] = []
    env_vars: List[str] = []
    test_results: List[str] = []
    log_entries: List[str] = []
    prose_lines: List[str] = []

    for ctype, line, _ in classified:
        stripped = line.strip()
        if not stripped:
            continue
        if ctype == "error":
            errors.append(stripped)
        elif ctype == "path_line":
            path_lines.append(stripped)
        elif ctype == "command":
            commands.append(stripped)
        elif ctype == "http_route":
            http_routes.append(stripped)
        elif ctype == "schema_migration":
            schema_migrations.append(stripped)
        elif ctype == "env_var":
            env_vars.append(stripped)
        elif ctype == "test_result":
            test_results.append(stripped)
        elif ctype == "log_entry":
            log_entries.append(stripped)
        else:
            prose_lines.append(stripped)

    output: List[str] = []
    output.append("# Compressed Context")
    output.append(f"**Original:** {total_lines} lines  **Compressed:** (output follows)")
    output.append("")

    if errors and preserve_errors:
        output.append("## Exact Errors Preserved")
        for e in errors:
            output.append(f"```\n{e}\n```" if "\n" in e else f"- `{e}`")
        output.append("")

    if path_lines and preserve_paths:
        output.append("## Files and Locations")
        seen_paths: Set[str] = set()
        for p in path_lines:
            m = PATH_LINE_PATTERN.search(p)
            if m:
                path_str = m.group(1)
                if path_str not in seen_paths:
                    seen_paths.add(path_str)
                    line_num = m.group(2)
                    func = m.group(3)
                    entry = f"`{path_str}:{line_num}`"
                    if func:
                        entry += f" in `{func}`"
                    output.append(f"- {entry}")
            else:
                output.append(f"- `{p}`")
        output.append("")

    if commands:
        output.append("## Commands Mentioned")
        seen_cmds: Set[str] = set()
        for c in commands:
            if c not in seen_cmds:
                seen_cmds.add(c)
                output.append(f"- `{c}`")
        output.append("")

    if http_routes:
        output.append("## HTTP Routes Mentioned")
        seen_routes: Set[str] = set()
        for r in http_routes:
            if r not in seen_routes:
                seen_routes.add(r)
                output.append(f"- `{r}`")
        output.append("")

    if schema_migrations:
        output.append("## Schema / Migration Changes")
        seen_schema: Set[str] = set()
        for s in schema_migrations:
            if s not in seen_schema:
                seen_schema.add(s)
                output.append(f"- `{s}`")
        output.append("")

    if env_vars:
        output.append("## Environment Variables Mentioned")
        seen_env: Set[str] = set()
        for e in env_vars:
            key = e.split("=")[0].split(":")[0].strip()
            if key and key not in seen_env:
                seen_env.add(key)
                output.append(f"- `{key}`=[REDACTED]")
        output.append("")

    if test_results:
        output.append("## Test Results")
        for t in test_results:
            output.append(f"- `{t}`")
        output.append("")

    if log_entries:
        output.append("## Log Entries (deduplicated)")
        counts = Counter(log_entries)
        for log_line, count in counts.most_common(15):
            if count > 1:
                output.append(f"- `{log_line}` (repeated {count}x)")
            else:
                output.append(f"- `{log_line}`")
        output.append("")

    uncertainty_lines = [
        l for ctype, l, _ in classified
        if ctype == "prose" and any(kw in l.lower()
                                   for kw in ("uncertain", "unknown", "not sure", "might", "maybe",
                                              "wonder", "suspect", "unclear", "unlikely"))
    ]

    empty_count = sum(1 for ctype, _, _ in classified if ctype == "empty")
    log_repeated = sum(c - 1 for c in Counter(log_entries).values() if c > 1)
    uncertainty_shown = min(len(uncertainty_lines), 3)
    prose_dropped = len(prose_lines) - uncertainty_shown
    total_removed = empty_count + log_repeated + prose_dropped
    if total_removed > 0:
        output.append(f"## Repeated or Low-Value Content Removed")
        output.append(f"Removed approximately {total_removed} lines: "
                       f"{log_repeated} repeated log, "
                       f"{prose_dropped} prose, "
                       f"{empty_count} blank.")
        output.append("")

    output.append("## Next Suggested Reads")
    all_paths = (
        [m.group(1) for p in path_lines if (m := PATH_LINE_PATTERN.search(p))]
        if preserve_paths else []
    )
    if all_paths:
        most_common_paths = Counter(all_paths).most_common(5)
        for path_str, cnt in most_common_paths:
            output.append(f"- `{path_str}` (mentioned {cnt}x)")
    else:
        output.append("- Review the errors above for file references")
    output.append("")

    output.append("## Uncertainty")
    if uncertainty_lines:
        for u in uncertainty_lines[:3]:
            output.append(f"- *{u.strip()}*")
    else:
        output.append("- No explicit uncertainty statements detected in compressed content.")
    output.append("")

    final_output = "\n".join(output)
    final_lines = final_output.splitlines()

    if len(final_lines) > max_lines:
        truncated = final_lines[:max_lines]
        truncated.append(f"")
        truncated.append(f"*[Truncated to {max_lines} lines; original had {total_lines} lines]*")
        return "\n".join(truncated)

    return final_output


def _parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compress logs, stack traces, notes, or session context.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  cat log.txt | python tools/context_compressor.py --stdin\n"
            "  python tools/context_compressor.py --file log.txt --max-lines 80\n"
            "  python tools/context_compressor.py --stdin --preserve-errors\n"
        ),
    )
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "--file",
        type=str,
        default=None,
        help="Path to a text file to compress",
    )
    input_group.add_argument(
        "--stdin",
        action="store_true",
        help="Read text from stdin",
    )
    parser.add_argument(
        "--max-lines",
        type=int,
        default=60,
        help="Target maximum output lines (default: 60)",
    )
    parser.add_argument(
        "--preserve-errors",
        action="store_true",
        default=True,
        help="Preserve error lines verbatim (default: true)",
    )
    parser.add_argument(
        "--preserve-paths",
        action="store_true",
        default=True,
        help="Preserve file path lines verbatim (default: true)",
    )
    return parser.parse_args(argv)


def run(argv: List[str]) -> str:
    args = _parse_args(argv)
    text = ""

    if args.stdin:
        try:
            text = sys.stdin.read()
        except KeyboardInterrupt:
            return "ERROR: Interrupted."
    elif args.file:
        path = Path(args.file)
        if not path.is_file():
            return f"ERROR: File not found: {path}"
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return f"ERROR: Could not read file: {exc}"
    else:
        return "ERROR: Provide --stdin or --file."

    return compress_text(
        text,
        max_lines=args.max_lines,
        preserve_errors=args.preserve_errors,
        preserve_paths=args.preserve_paths,
    )


def main() -> None:
    try:
        result = run(sys.argv[1:])
        sys.stdout.write(result + "\n")
    except BrokenPipeError:
        pass
    except Exception as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()