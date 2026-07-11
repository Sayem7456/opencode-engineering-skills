#!/usr/bin/env python3
"""Estimate approximate context size and recommend token-saving strategy."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

IGNORED_EXTENSIONS: Set[str] = {
    ".pyc", ".pyo", ".pyd",
    ".o", ".so", ".dylib",
    ".class", ".jar",
    ".exe", ".dll", ".msi",
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
    ".woff", ".woff2", ".ttf", ".eot",
    ".mp4", ".mp3", ".avi", ".mov",
    ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar",
    ".pdf", ".doc", ".docx",
    ".lock", ".map",
    ".bin",
}

SIGNIFICANT_EXTENSIONS: Set[str] = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".mjs",
    ".rs", ".go", ".rb", ".java", ".kt", ".swift",
    ".c", ".h", ".cpp", ".hpp", ".cc",
    ".html", ".css", ".scss", ".less",
    ".sql", ".prisma", ".graphql",
    ".yaml", ".yml", ".toml", ".json", ".xml",
    ".md", ".rst", ".txt",
    ".sh", ".bash", ".zsh",
    ".env", ".env.example",
    ".dockerfile", "Dockerfile",
}

IGNORED_DIRS: Set[str] = {
    ".git",
    "node_modules",
    ".next",
    "dist",
    "build",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "coverage",
    ".turbo",
    ".ruff_cache",
    ".mypy_cache",
    ".tox",
    "target",
    ".eggs",
}

IGNORED_DIR_SUFFIXES: Set[str] = {".egg-info"}


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _walk_significant_files(directory: Path) -> List[Path]:
    files: List[Path] = []
    try:
        for path in directory.rglob("*"):
            if not path.is_file():
                continue
            try:
                relative = path.relative_to(directory)
            except ValueError:
                continue
            parts = relative.parts
            if any(p in IGNORED_DIRS or any(p.endswith(s) for s in IGNORED_DIR_SUFFIXES) for p in parts):
                continue
            if path.suffix in SIGNIFICANT_EXTENSIONS or path.name in SIGNIFICANT_EXTENSIONS:
                files.append(path)
    except (PermissionError, RecursionError):
        pass
    return files


def analyze_file(path: Path, base: Path | None = None) -> Dict:
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {"path": str(path), "error": "Could not read"}
    char_count = len(content)
    line_count = len(content.splitlines()) if content else 0
    estimated_tokens = estimate_tokens(content)
    if base is not None:
        try:
            display_path = path.relative_to(base)
        except ValueError:
            display_path = path
    else:
        display_path = path
    return {
        "path": str(display_path),
        "chars": char_count,
        "lines": line_count,
        "estimated_tokens": estimated_tokens,
    }


def analyze_directory(directory: Path, top: int = 20) -> Dict:
    files = _walk_significant_files(directory)
    results = [analyze_file(f, base=directory) for f in files]
    results = [r for r in results if "error" not in r]

    total_chars = sum(r["chars"] for r in results)
    total_tokens = max(1, total_chars // 4)

    largest = sorted(results, key=lambda r: -r["chars"])[:top]

    return {
        "path": str(directory),
        "total_files": len(results),
        "total_chars": total_chars,
        "total_tokens": total_tokens,
        "largest": largest,
    }


def build_prompt_budget(
    text: str = "",
    directory: Optional[Path] = None,
    file_path: Optional[Path] = None,
    top: int = 20,
) -> str:
    lines: List[str] = []
    lines.append("# Prompt Budget")
    lines.append("")

    if directory:
        analysis = analyze_directory(directory, top=top)
        lines.append(f"## Directory: {analysis['path']}")
        lines.append("")
        lines.append(f"**Source files discovered:** {analysis['total_files']}")
        lines.append(f"**Total characters:** {analysis['total_chars']:,}")
        lines.append(f"**Estimated tokens (~chars/4):** ~{analysis['total_tokens']:,}")
        lines.append(f"**Max context window (example):** ~128,000 tokens (GPT-4 class)")
        usage_pct = (analysis['total_tokens'] / 128000) * 100
        lines.append(f"**Estimated usage:** ~{usage_pct:.1f}%")
        lines.append("")

        largest = analysis["largest"][:top]
        if largest:
            lines.append("### Largest Files")
            lines.append("| File | Lines | Chars | ~Tokens |")
            lines.append("|------|-------|-------|---------|")
            for f in largest:
                lines.append(
                    f"| `{f['path']}` | {f['lines']} | {f['chars']:,} "
                    f"| ~{f['estimated_tokens']:,} |"
                )
            lines.append("")

            lines.append("### Files to Avoid Reading Fully")
            oversized = [f for f in largest if f["estimated_tokens"] > 5000]
            if oversized:
                lines.append("These files exceed ~5,000 tokens each. Read selectively:")
                for f in oversized[:5]:
                    lines.append(
                        f"- `{f['path']}` (~{f['estimated_tokens']:,} tokens, {f['lines']} lines)"
                    )
            else:
                lines.append("No files exceed ~5,000 tokens. Full read is budget-safe.")
            lines.append("")

        lines.append("### Recommended Reading Strategy")
        if usage_pct > 50:
            lines.append("1. Use `ctx_repo_map` to understand structure before reading files.")
            lines.append("2. Use `grep` to locate specific symbols; do not read entire files.")
            lines.append("3. Read only imports, type signatures, and the targeted function body.")
            lines.append("4. Consider `ctx_compress` for logs or long error output.")
            lines.append("5. If context window is full, start a new session with `/handoff-summary`.")
        elif usage_pct > 20:
            lines.append("1. Read primary files fully; use signatures mode for secondary files.")
            lines.append("2. Use `ctx_compress` only if you encounter verbose logs.")
            lines.append("3. Monitor context growth and consider `/compress-context` mid-session.")
        else:
            lines.append("1. Read files fully as needed.")
            lines.append("2. Budget is well within limits.")
        lines.append("")

        lines.append("### Recommended Skills or Commands")
        if usage_pct > 50:
            lines.append("- Load: `token-saver`, `context-engineering`, `repository-navigation`")
            lines.append("- Run: `/compress-context` at mid-session")
            lines.append("- Run: `ctx_repo_map` before exploring files")
        elif usage_pct > 20:
            lines.append("- Load: `token-saver`")
            lines.append("- Consider: `context-engineering` for complex tasks")
        else:
            lines.append("- Standard skills are safe — no budget constraints")

    elif file_path:
        analysis = analyze_file(file_path)
        if "error" in analysis:
            return f"ERROR: Could not read file: {file_path}"
        lines.append(f"## File: {analysis['path']}")
        lines.append("")
        lines.append(f"**Lines:** {analysis['lines']}")
        lines.append(f"**Characters:** {analysis['chars']:,}")
        lines.append(f"**Estimated tokens (~chars/4):** ~{analysis['estimated_tokens']:,}")
        lines.append("")

        tk = analysis["estimated_tokens"]
        if tk > 10000:
            lines.append("### Recommendation ⚠️")
            lines.append("This file is large. Consider reading only imports, type signatures, and targeted functions.")
            lines.append("- Use `grep` to locate specific symbols before reading.")
            lines.append("- Use signature-only mode for orientation.")
            lines.append("- Run `ctx_repo_map` on the directory for context.")
        elif tk > 2000:
            lines.append("### Recommendation")
            lines.append("Moderate size. Read signatures first, then expand specific functions as needed.")
        else:
            lines.append("### Recommendation")
            lines.append("Small file. Read fully — budget impact is minimal.")

    elif text:
        char_count = len(text)
        token_estimate = estimate_tokens(text)
        lines.append(f"## Text Input")
        lines.append("")
        lines.append(f"**Characters:** {char_count:,}")
        lines.append(f"**Estimated tokens (~chars/4):** ~{token_estimate:,}")
        lines.append(f"**Estimated usage (128k window):** ~{(token_estimate / 128000) * 100:.1f}%")
        lines.append("")
        if token_estimate > 10000:
            lines.append("### Recommendation ⚠️")
            lines.append("This text is large. Run `ctx_compress` before including it in context.")
        else:
            lines.append("### Recommendation")
            lines.append("Text is within reasonable bounds.")

    else:
        return "ERROR: Provide --stdin, --file, or --dir."

    lines.append("")
    lines.append("---")
    lines.append("*Token estimates use `chars / 4` heuristic. Actual tokenizer output may vary by model.*")

    return "\n".join(lines)


def _parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Estimate approximate context size and recommend token-saving strategy.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python tools/prompt_budget.py --stdin < text.txt\n"
            "  python tools/prompt_budget.py --file large_log.txt\n"
            "  python tools/prompt_budget.py --dir /path/to/project --top 10\n"
        ),
    )
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "--file",
        type=str,
        default=None,
        help="Path to a text file to estimate",
    )
    input_group.add_argument(
        "--dir",
        type=str,
        default=None,
        help="Path to a directory to analyze",
    )
    input_group.add_argument(
        "--stdin",
        action="store_true",
        help="Read text from stdin",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Number of largest files to show (default: 20)",
    )
    return parser.parse_args(argv)


def run(argv: List[str]) -> str:
    args = _parse_args(argv)
    if args.stdin:
        try:
            text = sys.stdin.read()
        except KeyboardInterrupt:
            return "ERROR: Interrupted."
        return build_prompt_budget(text=text)
    elif args.file:
        file_path = Path(args.file)
        if not file_path.is_file():
            return f"ERROR: File not found: {file_path}"
        return build_prompt_budget(file_path=file_path)
    elif args.dir:
        directory = Path(args.dir)
        if not directory.is_dir():
            return f"ERROR: Directory not found: {directory}"
        return build_prompt_budget(directory=directory, top=args.top)
    else:
        return "ERROR: Provide --stdin, --file, or --dir."


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