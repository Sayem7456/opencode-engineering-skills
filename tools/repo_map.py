#!/usr/bin/env python3
"""Generate a compact repository map with language and framework detection."""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

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

LANGUAGE_PATTERNS: Dict[str, List[str]] = {
    "Python": ["*.py", "*.pyi", "*.pyx"],
    "TypeScript": ["*.ts", "*.tsx"],
    "JavaScript": ["*.js", "*.jsx", "*.mjs"],
    "Rust": ["*.rs"],
    "Go": ["*.go"],
    "Ruby": ["*.rb"],
    "Java": ["*.java"],
    "Kotlin": ["*.kt", "*.kts"],
    "Swift": ["*.swift"],
    "Shell": ["*.sh", "*.bash"],
    "C": ["*.c", "*.h"],
    "CPP": ["*.cpp", "*.hpp", "*.cc", "*.cxx"],
    "HTML": ["*.html", "*.htm"],
    "CSS": ["*.css", "*.scss", "*.less"],
    "SQL": ["*.sql"],
    "YAML": ["*.yml", "*.yaml"],
    "Markdown": ["*.md", ".mdx"],
    "Docker": ["Dockerfile*"],
    "TOML": ["*.toml"],
    "JSON": ["*.json"],
}

PACKAGE_MANAGER_FILES: Dict[str, str] = {
    "package.json": "npm/yarn/pnpm",
    "pnpm-lock.yaml": "pnpm",
    "yarn.lock": "yarn",
    "package-lock.json": "npm",
    "Cargo.toml": "cargo",
    "Cargo.lock": "cargo",
    "pyproject.toml": "pip/poetry",
    "Pipfile": "pipenv",
    "Pipfile.lock": "pipenv",
    "poetry.lock": "poetry",
    "requirements.txt": "pip",
    "go.mod": "go modules",
    "go.sum": "go modules",
    "Gemfile": "bundler",
    "Gemfile.lock": "bundler",
    "build.gradle": "gradle",
    "pom.xml": "maven",
}

FRAMEWORK_PATTERNS: Dict[str, List[str]] = {
    "FastAPI": ["**/fastapi/**", "**/main.py"],
    "Django": ["**/django/**", "manage.py"],
    "Flask": ["**/flask/**", "**/app.py"],
    "Next.js": ["next.config.js", "next.config.mjs", "next.config.ts"],
    "React": ["**/react/**", "**/*.tsx", "**/*.jsx"],
    "Vue": ["**/vue/**", "**/*.vue"],
    "Svelte": ["**/*.svelte"],
    "Express": ["**/express/**"],
    "Fastify": ["**/fastify/**"],
    "Spring Boot": ["**/spring-boot/**"],
    "Actix": ["**/actix/**"],
    "Axum": ["**/axum/**"],
    "SQLAlchemy": ["**/sqlalchemy/**"],
    "Django ORM": ["**/models.py"],
    "Prisma": ["schema.prisma"],
    "Pydantic": ["**/pydantic/**"],
    "Pytest": ["**/conftest.py", "pytest.ini", "pyproject.toml"],
}

CONFIG_FILES: List[str] = [
    "package.json",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "tsconfig.json",
    ".eslintrc.js",
    ".eslintrc.json",
    ".prettierrc",
    ".prettierrc.json",
    "ruff.toml",
    ".ruff.toml",
    "pytest.ini",
    ".coveragerc",
    "Dockerfile",
    "docker-compose.yml",
    "Makefile",
    "Justfile",
    ".env.example",
    "AGENTS.md",
    "README.md",
    ".github/workflows/*.yml",
]

SECRET_PATTERNS: List[re.Pattern] = [
    re.compile(r"(?i)(?:api[_-]?key|secret|password|token|credential)\s*[=:]\s*\S+"),
    re.compile(r"(?i)sk-[a-zA-Z0-9]{20,}"),
    re.compile(r"(?i)pk-[a-zA-Z0-9]{20,}"),
]


def _is_ignored_dir(name: str) -> bool:
    return name in IGNORED_DIRS or name.endswith(".egg-info")


def _should_ignore(name: str) -> bool:
    if name.startswith(".") and name not in (".", ".."):
        return name not in {
            ".env.example",
            ".gitignore",
            ".gitattributes",
            ".dockerignore",
        }
    return _is_ignored_dir(name)


def _detect_languages(root: Path) -> Dict[str, int]:
    counts: Dict[str, int] = defaultdict(int)
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        parts = relative.parts
        if any(_is_ignored_dir(p) for p in parts):
            continue
        for lang, patterns in LANGUAGE_PATTERNS.items():
            for pattern in patterns:
                if path.match(pattern):
                    counts[lang] += 1
                    break
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


def _detect_package_managers(root: Path) -> Dict[str, str]:
    found: Dict[str, str] = {}
    for filename, manager in PACKAGE_MANAGER_FILES.items():
        if (root / filename).is_file():
            found[filename] = manager
    return found


def _detect_frameworks(root: Path) -> List[str]:
    found: List[str] = []
    for framework, patterns in FRAMEWORK_PATTERNS.items():
        for pattern in patterns:
            if "**" in pattern or "*" in pattern:
                matches = list(root.glob(pattern))
                if matches:
                    found.append(framework)
                    break
            else:
                if (root / pattern).is_file():
                    found.append(framework)
                    break
    return sorted(set(found))


def _find_config_files(root: Path) -> List[Path]:
    found: List[Path] = []
    for pattern in CONFIG_FILES:
        if "*" in pattern:
            found.extend(sorted(root.glob(pattern)))
        else:
            candidate = root / pattern
            if candidate.is_file():
                found.append(candidate)
    return sorted(set(found))


def _find_backend_files(root: Path) -> List[Path]:
    patterns = [
        "**/routes/**/*",
        "**/router*.py",
        "**/services/**/*",
        "**/service*.py",
        "**/models/**/*",
        "**/model*.py",
        "**/schemas/**/*",
        "**/schema*.py",
        "**/api/**/*",
        "**/endpoints/**/*",
        "**/controllers/**/*",
        "**/handlers/**/*",
        "**/middleware/**/*",
    ]
    found: Set[Path] = set()
    for pattern in patterns:
        for match in root.glob(pattern):
            if match.is_file() and not any(
                _is_ignored_dir(p) for p in match.relative_to(root).parts
            ):
                found.add(match)
    return sorted(found)


def _find_frontend_files(root: Path) -> List[Path]:
    patterns = [
        "**/components/**/*",
        "**/pages/**/*",
        "**/app/**/*",
        "**/layouts/**/*",
        "**/views/**/*",
        "**/*.tsx",
        "**/*.jsx",
        "**/*.vue",
        "**/*.svelte",
    ]
    found: Set[Path] = set()
    for pattern in patterns:
        for match in root.glob(pattern):
            if match.is_file() and not any(
                _is_ignored_dir(p) for p in match.relative_to(root).parts
            ):
                found.add(match)
    return sorted(found)


def _find_database_migration_files(root: Path) -> List[Path]:
    patterns = [
        "**/migrations/**",
        "**/alembic/**",
        "**/migrations/*.py",
        "**/prisma/**",
        "**/schema.prisma",
        "**/migration/**",
        "**/db/**",
        "**/database/**",
    ]
    found: Set[Path] = set()
    for pattern in patterns:
        for match in root.glob(pattern):
            if match.is_file() and not any(
                _is_ignored_dir(p) for p in match.relative_to(root).parts
            ):
                found.add(match)
    return sorted(found)


def _find_test_files(root: Path) -> List[Path]:
    patterns = [
        "**/test_*.py",
        "**/*_test.py",
        "**/test_*.ts",
        "**/*.test.ts",
        "**/*.test.tsx",
        "**/*.spec.ts",
        "**/*.spec.js",
        "**/tests/**",
        "**/__tests__/**",
        "**/*.test.js",
    ]
    found: Set[Path] = set()
    for pattern in patterns:
        for match in root.glob(pattern):
            if match.is_file() and not any(
                _is_ignored_dir(p) for p in match.relative_to(root).parts
            ):
                found.add(match)
    return sorted(found)


def _relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return path.name


def _scan_tree(root: Path, max_files: int = 0) -> str:
    lines: List[str] = []
    root_name = root.name
    lines.append(f"## Repo Map: {root.absolute()}")
    lines.append("")

    languages = _detect_languages(root)
    if languages:
        lines.append(f"**Languages:** {', '.join(languages.keys())}")
        lines.append("")

    package_managers = _detect_package_managers(root)
    if package_managers:
        managers = ", ".join(sorted(set(package_managers.values())))
        lines.append(f"**Package managers:** {managers}")
        lines.append("")

    frameworks = _detect_frameworks(root)
    if frameworks:
        lines.append(f"**Frameworks:** {', '.join(frameworks)}")
        lines.append("")

    config_files = _find_config_files(root)
    if config_files:
        lines.append("### Important Config Files")
        for cf in config_files[:max_files] if max_files else config_files:
            lines.append(f"- `{_relative_path(cf, root)}`")
        lines.append("")

    backend = _find_backend_files(root)
    if backend:
        lines.append("### Backend-Related Files")
        for bf in backend[:max_files] if max_files else backend:
            lines.append(f"- `{_relative_path(bf, root)}`")
        lines.append("")

    frontend = _find_frontend_files(root)
    if frontend:
        lines.append("### Frontend-Related Files")
        for ff in frontend[:max_files] if max_files else frontend:
            lines.append(f"- `{_relative_path(ff, root)}`")
        lines.append("")

    db_files = _find_database_migration_files(root)
    if db_files:
        lines.append("### Database / Migration Files")
        for df in db_files[:max_files] if max_files else db_files:
            lines.append(f"- `{_relative_path(df, root)}`")
        lines.append("")

    tests = _find_test_files(root)
    if tests:
        lines.append("### Tests")
        for tf in tests[:max_files] if max_files else tests:
            lines.append(f"- `{_relative_path(tf, root)}`")
        lines.append("")

    secrets = _check_secrets(root)
    if secrets:
        lines.append("### Possible Secrets")
        for s in secrets[:max_files] if max_files else secrets:
            lines.append(f"- `{s}`")
        lines.append("")

    ignored_dirs = [d for d in sorted(IGNORED_DIRS) if (root / d).exists()]
    if ignored_dirs:
        lines.append("### Ignored Directories")
        for d in ignored_dirs:
            lines.append(f"- `{d}` (excluded)")
        lines.append("")

    lines.append("### Suggested Next Reads")
    suggestions = _suggest_next_reads(languages, frameworks, config_files)
    lines.extend(suggestions)

    return "\n".join(lines)


def _suggest_next_reads(
    languages: Dict[str, int],
    frameworks: List[str],
    config_files: List[Path],
) -> List[str]:
    suggestions: List[str] = []

    primary_lang = list(languages.keys())[0] if languages else "Unknown"
    if primary_lang in ("Python",):
        suggestions.append("- `pyproject.toml` or `requirements.txt` — dependencies and metadata")
        suggestions.append("- `README.md` — project overview")
        suggestions.append("- `AGENTS.md` — project-specific agent instructions")
        suggestions.append("- `conftest.py` or `pytest.ini` — test configuration")
    elif primary_lang in ("TypeScript", "JavaScript"):
        suggestions.append("- `package.json` — dependencies and scripts")
        suggestions.append("- `tsconfig.json` — TypeScript configuration")
        suggestions.append("- `README.md` — project overview")
        suggestions.append("- `AGENTS.md` — project-specific agent instructions")
    elif primary_lang == "Rust":
        suggestions.append("- `Cargo.toml` — dependencies and metadata")
        suggestions.append("- `README.md` — project overview")
    else:
        suggestions.append("- `README.md` — project overview")
        suggestions.append("- `AGENTS.md` — project-specific agent instructions")

    if "Next.js" in frameworks:
        suggestions.append("- `next.config.js` — Next.js configuration")
    if "FastAPI" in frameworks:
        suggestions.append("- `main.py` or `app.py` — FastAPI entry point")

    if not suggestions:
        suggestions.append("- Start with `README.md` to understand the project")

    return suggestions


def _check_secrets(root: Path) -> List[str]:
    found: List[str] = []
    seen: Set[str] = set()
    patterns = (
        "**/*.py", "**/*.ts", "**/*.js",
        "**/*.env", "**/*.yml", "**/*.yaml",
        "**/*.json", "**/*.toml", "**/*.cfg",
        "**/*.ini", "**/*.conf",
    )
    for pattern in patterns:
        for path in root.glob(pattern):
            if not path.is_file():
                continue
            parts = path.relative_to(root).parts
            if any(_is_ignored_dir(p) for p in parts):
                continue
            rel = _relative_path(path, root)
            if rel in seen:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except (OSError, UnicodeDecodeError):
                continue
            for line in text.splitlines():
                for secret_pattern in SECRET_PATTERNS:
                    if secret_pattern.search(line):
                        found.append(rel)
                        seen.add(rel)
                        break
                if rel in seen:
                    break
    return sorted(found)


def build_repo_map(root: Path, max_files: int) -> str:
    root = root.resolve()
    if not root.exists():
        return f"ERROR: Path not found: {root}"
    if not root.is_dir():
        return f"ERROR: Path is not a directory: {root}"
    try:
        _ = list(root.iterdir())
    except PermissionError:
        return f"ERROR: Permission denied: {root}"

    return _scan_tree(root, max_files=max_files)


def _parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a compact repository map.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python tools/repo_map.py\n"
            "  python tools/repo_map.py /path/to/repo\n"
            "  python tools/repo_map.py . --max-files 500\n"
        ),
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Repository path (default: current directory)",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=300,
        help="Maximum files to list per category (default: 300)",
    )
    return parser.parse_args(argv)


def run(argv: List[str]) -> str:
    args = _parse_args(argv)
    root = Path(args.path)
    return build_repo_map(root, args.max_files)


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