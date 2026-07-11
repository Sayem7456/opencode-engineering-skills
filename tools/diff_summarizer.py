#!/usr/bin/env python3
"""Summarize git diffs with per-file risk and skill suggestions."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

REDACT_PATTERNS: List[re.Pattern] = [
    re.compile(r'(?i)(?:api[_-]?key|secret|password|token|credential|auth[_-]?token)'
               r'\s*[=:]\s*[\'"]?\S+'),
    re.compile(r"(?i)sk-[a-zA-Z0-9]{20,}"),
    re.compile(r"(?i)pk-[a-zA-Z0-9]{20,}"),
    re.compile(r"(?i)(?:AKIA|ASIA)[A-Z0-9]{16}"),
    re.compile(r"(?i)(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{30,}"),
    re.compile(r"(?i)(?:-----BEGIN [A-Z ]+-----)"),
    re.compile(r'(?i)(?:DATABASE_URL|DB_URL|REDIS_URL|AMQP_URL)'
               r'\s*[=:]\s*\S+'),
]

HIGH_RISK_KEYWORDS: Set[str] = {
    "migrat",
    "drop_table",
    "alter_table",
    "delete",
    "truncate",
    "grant",
    "revoke",
    "security",
    "auth",
    "password",
    "token",
    "secret",
    "ssl_mode",
    "bypass_rls",
    "set role",
    "superuser",
}

MEDIUM_RISK_KEYWORDS: Set[str] = {
    "refactor",
    "rename",
    "change_column",
    "add_column",
    "remove",
    "deprecat",
    "timeout",
    "retry",
    "fallback",
    "default",
    "null",
    "nullable",
    "cascade",
    "on_delete",
    "on_update",
    "foreign_key",
    "index",
    "unique",
}


@dataclass
class Hunk:
    start_old: int
    start_new: int
    lines: List[str] = field(default_factory=list)


@dataclass
class FileDiff:
    path: str
    added: int = 0
    removed: int = 0
    hunks: List[Hunk] = field(default_factory=list)
    is_new: bool = False
    is_deleted: bool = False


def _redact_line(line: str) -> str:
    for pattern in REDACT_PATTERNS:
        line = pattern.sub("[REDACTED]", line)
    return line


def _parse_diff(diff_text: str) -> List[FileDiff]:
    files: List[FileDiff] = []
    current_file: Optional[FileDiff] = None
    current_hunk: Optional[Hunk] = None

    for raw_line in diff_text.splitlines():
        line = _redact_line(raw_line)

        if line.startswith("diff --git"):
            if current_file and current_hunk:
                current_file.hunks.append(current_hunk)
                current_hunk = None
            if current_file:
                files.append(current_file)

            parts = line.split()
            a_path = parts[2] if len(parts) > 2 else ""
            b_path = parts[3] if len(parts) > 3 else ""
            path = b_path.removeprefix("b/") if b_path else a_path.removeprefix("a/")
            current_file = FileDiff(path=path)

        elif line.startswith("--- /dev/null"):
            if current_file:
                current_file.is_new = True
        elif line.startswith("+++ /dev/null"):
            if current_file:
                current_file.is_deleted = True

        elif line.startswith("@@") and current_file:
            if current_hunk:
                current_file.hunks.append(current_hunk)

            m = re.search(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
            start_new = int(m.group(1)) if m else 0
            current_hunk = Hunk(start_old=0, start_new=start_new)

        elif current_hunk is not None and current_file is not None:
            current_hunk.lines.append(line)
            if line.startswith("+"):
                current_file.added += 1
            elif line.startswith("-"):
                current_file.removed += 1

    if current_hunk and current_file:
        current_file.hunks.append(current_hunk)
    if current_file:
        files.append(current_file)

    return files


def _detect_symbols(lines: List[str]) -> List[str]:
    symbols: List[str] = []
    for line in lines:
        m = re.search(r"(?:^|\s)(async def|def|class|fn|func|function)\s+([a-zA-Z_]\w*)", line)
        if m:
            symbols.append(m.group(2))
        m = re.search(r"(?:^|\s)(?:export\s+(?:default\s+)?)?(?:const|let|var|function)\s+([a-zA-Z_]\w*)", line)
        if m:
            symbols.append(m.group(2))
        m = re.search(r"\b(app|router|api)\.(get|post|put|patch|delete|options)\s*\(\s*['\"]([^'\"]+)['\"]", line, re.IGNORECASE)
        if m:
            symbols.append(f"{m.group(1)}.{m.group(2).upper()} /{m.group(3)}")
    return symbols


def _classify_risk(path: str, lines: List[str]) -> str:
    lower_path = path.lower()
    added_lines = [line for line in lines if line.startswith("+")]
    lower_lines = " ".join(added_lines).lower()
    if any(kw in lower_lines for kw in ("security", "auth", "password", "token", "secret")):
        return "High"
    if any(kw in lower_lines for kw in ("migrat", "drop_table", "grant", "revoke")):
        return "High"
    if "db/" in lower_path or "/migration" in lower_path:
        return "Medium-High"
    if "migration" in lower_path or "alembic" in lower_path:
        return "Medium-High"
    if any(kw in lower_lines for kw in ("refactor", "change_column", "nullable", "cascade", "foreign_key")):
        return "Medium"
    if "test_" in lower_path:
        return "Low"
    if lower_path.endswith(".md"):
        return "Low"
    return "Info"


def _suggest_skills(path: str) -> List[str]:
    skills: List[str] = []
    lower_path = path.lower()
    if "test_" in lower_path:
        skills.extend(["testing-and-debugging", "python-quality"])
    if "migration" in lower_path or "alembic" in lower_path or "db/" in lower_path:
        skills.extend(["sqlalchemy-postgres", "testing-and-debugging"])
    if "security" in lower_path or "auth" in lower_path:
        skills.extend(["security-review", "code-review"])
    if "route" in lower_path or "api" in lower_path or "handler" in lower_path:
        skills.append("fastapi-backend")
    if "model" in lower_path or "schema" in lower_path:
        skills.append("python-quality")
    if "component" in lower_path or "page" in lower_path or lower_path.endswith((".tsx", ".jsx")):
        skills.extend(["nextjs-frontend", "ui-ux-design"])
    if "docker" in lower_path or "deploy" in lower_path:
        skills.append("production-readiness")
    if not skills:
        skills.append("python-quality") if "py" in lower_path else skills.append("code-review")
    return skills


def _suggest_tests(path: str) -> List[str]:
    tests: List[str] = []
    lower_path = path.lower()
    if lower_path.endswith(".py"):
        test_path = "test_" + Path(lower_path).stem + ".py"
        tests.append(f"python -m pytest tests/{test_path} -q")
    elif lower_path.endswith((".ts", ".tsx")):
        base = Path(lower_path).stem
        if not base.startswith("test_") and not base.endswith((".test", ".spec")):
            tests.append(f"npm test -- {base}")
        else:
            tests.append(f"npm test -- {base}")
    if "migration" in lower_path or "alembic" in lower_path:
        tests.append("pytest tests/ -q (full suite)")
    return tests


def summarize_diff(diff_text: str, max_files: int = 0) -> str:
    files = _parse_diff(diff_text)

    if not files:
        return "No changes found in diff."

    if max_files > 0:
        files = files[:max_files]

    lines: List[str] = []
    lines.append("## Diff Summary")
    lines.append("")

    total_added = sum(f.added for f in files)
    total_removed = sum(f.removed for f in files)
    lines.append(f"**Files changed:** {len(files)}")
    lines.append(f"**Lines added:** {total_added}  **Lines removed:** {total_removed}")
    lines.append("")

    for f in files:
        added = f.added or 0
        removed = f.removed or 0
        status = ""
        if f.is_new:
            status = " (new file)"
        elif f.is_deleted:
            status = " (deleted)"

        lines.append(f"### `{f.path}`{status}")
        lines.append(f"+{added} / -{removed} | {len(f.hunks)} hunk(s)")

        all_diff_lines = []
        for h in f.hunks:
            all_diff_lines.extend(h.lines)

        symbols = _detect_symbols(all_diff_lines)
        if symbols:
            seen: Set[str] = set()
            unique_symbols = []
            for s in symbols:
                if s not in seen:
                    seen.add(s)
                    unique_symbols.append(s)
            lines.append(f"- **Detected:** {', '.join(unique_symbols)}")

        risk = _classify_risk(f.path, all_diff_lines)
        lines.append(f"- **Risk category:** {risk}")

        skills = _suggest_skills(f.path)
        if skills:
            lines.append(f"- **Suggested skills:** {', '.join(skills)}")

        suggested_tests = _suggest_tests(f.path)
        if suggested_tests:
            lines.append(f"- **Suggested tests:** `{'` `'.join(suggested_tests)}`")

        lines.append("")

    return "\n".join(lines)


def _get_diff_from_git(cwd: Optional[Path] = None) -> str:
    cmd = ["git", "diff"]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(cwd) if cwd else None,
            timeout=30,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()
            if "not a git repository" in stderr:
                return "ERROR: Not a git repository."
            return f"ERROR: git diff failed: {stderr}"
        return result.stdout
    except FileNotFoundError:
        return "ERROR: Git not found. Install git."
    except subprocess.TimeoutExpired:
        return "ERROR: git diff timed out."


def _parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize git diffs with per-file analysis.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  git diff | python tools/diff_summarizer.py --stdin\n"
            "  python tools/diff_summarizer.py --file changes.diff\n"
            "  python tools/diff_summarizer.py\n"
        ),
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read diff from stdin",
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Path to a diff file",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=20,
        help="Maximum files to show (default: 20)",
    )
    return parser.parse_args(argv)


def run(argv: List[str]) -> str:
    args = _parse_args(argv)
    diff = ""

    if args.stdin:
        try:
            diff = sys.stdin.read()
        except KeyboardInterrupt:
            return "ERROR: Interrupted."
    elif args.file:
        path = Path(args.file)
        if not path.is_file():
            return f"ERROR: File not found: {path}"
        try:
            diff = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return f"ERROR: Could not read file: {exc}"
    else:
        diff = _get_diff_from_git()

    if diff.startswith("ERROR:"):
        return diff

    if not diff.strip():
        return "No changes found in working tree."

    return summarize_diff(diff, max_files=args.max_files)


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