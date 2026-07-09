#!/usr/bin/env python3
"""Validate OpenCode skill and command files in this repository."""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit(
        "PyYAML is required.\n"
        "Install it with:\n"
        "  python -m pip install PyYAML\n"
        "  # or: pip install -r requirements.txt"
    ) from exc

ROOT_DIR = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT_DIR / "skills"
COMMANDS_DIR = ROOT_DIR / "commands"
PACKS_DIR = ROOT_DIR / "packs"
TOOLS_DIR = ROOT_DIR / "opencode-tools"
PYTHON_TOOLS_DIR = ROOT_DIR / "tools"

VALID_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VALID_TOOL_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")

REQUIRED_TOOL_FILES = [
    "repo_map.ts",
    "diff_summarizer.ts",
    "context_compressor.ts",
    "prompt_budget.ts",
]

REQUIRED_PYTHON_TOOL_FILES = [
    "repo_map.py",
    "diff_summarizer.py",
    "context_compressor.py",
    "prompt_budget.py",
]

BUILTIN_TOOL_NAMES = frozenset({
    "bash",
    "read",
    "write",
    "edit",
    "grep",
    "glob",
})

REQUIRED_SKILL_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
}

REQUIRED_METADATA_FIELDS = {
    "category",
    "stack",
    "version",
}

def _discover_skills() -> set[str]:
    """Return all skill directory names found on disk."""
    if not SKILLS_DIR.is_dir():
        return set()
    return {path.name for path in SKILLS_DIR.iterdir() if path.is_dir()}


def _discover_commands() -> set[str]:
    """Return all command stem names found on disk."""
    if not COMMANDS_DIR.is_dir():
        return set()
    return {path.stem for path in COMMANDS_DIR.glob("*.md")}


@dataclass(slots=True)
class ValidationIssue:
    severity: str
    path: Path
    message: str

    def format(self) -> str:
        try:
            relative_path = self.path.relative_to(ROOT_DIR)
        except ValueError:
            relative_path = self.path

        return f"[{self.severity}] {relative_path}: {self.message}"


def extract_frontmatter(path: Path) -> tuple[dict[str, Any] | None, str]:
    """Extract YAML frontmatter and Markdown body from a file."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None, ""

    lines = content.splitlines()

    if not lines or lines[0].strip() != "---":
        return None, content

    closing_index: int | None = None

    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = index
            break

    if closing_index is None:
        return None, content

    frontmatter_text = "\n".join(lines[1:closing_index])
    body = "\n".join(lines[closing_index + 1 :]).strip()

    try:
        parsed = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError:
        return None, body

    if parsed is None:
        parsed = {}

    if not isinstance(parsed, dict):
        return None, body

    return parsed, body


README_PATH = ROOT_DIR / "README.md"
DOCS_DIR = ROOT_DIR / "docs"

RECOMMENDED_DOCS = [
    "skill-orchestration-design.md",
    "skill-routing-matrix.md",
]


def _readme_section(heading: str) -> str:
    """Return the text between the given ##-heading and the next ##-heading."""
    if not README_PATH.is_file():
        return ""
    try:
        content = README_PATH.read_text(encoding="utf-8")
    except OSError:
        return ""
    lines = content.splitlines()
    start = -1
    for i, line in enumerate(lines):
        if line.strip() == f"## {heading}":
            start = i + 1
            break
    if start < 0:
        return ""
    for i in range(start, len(lines)):
        if lines[i].startswith("## ") and i > start:
            return "\n".join(lines[start:i])
    return "\n".join(lines[start:])


def _validate_readme_skill_table() -> list[ValidationIssue]:
    """Check README Available Skills table matches skills on disk."""
    issues: list[ValidationIssue] = []
    section = _readme_section("Available Skills")
    if not section:
        return issues
    pattern = re.compile(r"^\|\s+`([a-z0-9]+(?:-[a-z0-9]+)*)`\s+\|", re.MULTILINE)
    readme_skills = set(pattern.findall(section))
    disk_skills = _discover_skills()
    extra = readme_skills - disk_skills
    missing = disk_skills - readme_skills
    for name in sorted(extra):
        issues.append(ValidationIssue("WARNING", README_PATH, f"Skill '{name}' listed in README but missing on disk."))
    for name in sorted(missing):
        issues.append(ValidationIssue("WARNING", README_PATH, f"Skill '{name}' on disk but missing from README table."))
    return issues


def _validate_readme_command_table() -> list[ValidationIssue]:
    """Check README Available Commands table matches commands on disk."""
    issues: list[ValidationIssue] = []
    section = _readme_section("Available Commands")
    if not section:
        return issues
    pattern = re.compile(r"^\|\s+`/([a-z0-9]+(?:-[a-z0-9]+)*)`\s+\|", re.MULTILINE)
    readme_commands = set(pattern.findall(section))
    disk_commands = _discover_commands()
    extra = readme_commands - disk_commands
    missing = disk_commands - readme_commands
    for name in sorted(extra):
        issues.append(ValidationIssue("WARNING", README_PATH, f"Command '{name}' listed in README but missing on disk."))
    for name in sorted(missing):
        issues.append(ValidationIssue("WARNING", README_PATH, f"Command '{name}' on disk but missing from README table."))
    return issues


def validate_skill_directory(
    skill_dir: Path,
    seen_names: set[str],
) -> list[ValidationIssue]:
    """Validate one skill directory."""
    issues: list[ValidationIssue] = []

    folder_name = skill_dir.name
    skill_file = skill_dir / "SKILL.md"

    if not VALID_NAME_PATTERN.fullmatch(folder_name):
        issues.append(
            ValidationIssue(
                "ERROR",
                skill_dir,
                "Directory name must contain lowercase letters, numbers, "
                "and single hyphens only.",
            )
        )

    if not skill_file.is_file():
        issues.append(
            ValidationIssue(
                "ERROR",
                skill_dir,
                "Missing SKILL.md.",
            )
        )
        return issues

    frontmatter, body = extract_frontmatter(skill_file)

    if frontmatter is None:
        issues.append(
            ValidationIssue(
                "ERROR",
                skill_file,
                "Missing, malformed, or invalid YAML frontmatter.",
            )
        )
        return issues

    missing_fields = REQUIRED_SKILL_FIELDS - set(frontmatter)

    if missing_fields:
        issues.append(
            ValidationIssue(
                "ERROR",
                skill_file,
                "Missing required frontmatter fields: "
                + ", ".join(sorted(missing_fields)),
            )
        )

    name = frontmatter.get("name")

    if not isinstance(name, str) or not name.strip():
        issues.append(
            ValidationIssue(
                "ERROR",
                skill_file,
                "'name' must be a non-empty string.",
            )
        )
    else:
        name = name.strip()

        if name != folder_name:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    skill_file,
                    f"Frontmatter name '{name}' does not match directory "
                    f"name '{folder_name}'.",
                )
            )

        if not VALID_NAME_PATTERN.fullmatch(name):
            issues.append(
                ValidationIssue(
                    "ERROR",
                    skill_file,
                    "'name' must contain lowercase letters, numbers, "
                    "and single hyphens only.",
                )
            )

        if name in seen_names:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    skill_file,
                    f"Duplicate skill name '{name}'.",
                )
            )
        else:
            seen_names.add(name)

    description = frontmatter.get("description")

    if not isinstance(description, str) or not description.strip():
        issues.append(
            ValidationIssue(
                "ERROR",
                skill_file,
                "'description' must be a non-empty string.",
            )
        )
    elif len(description.strip()) < 20:
        issues.append(
            ValidationIssue(
                "WARNING",
                skill_file,
                "Description is very short and may not provide enough "
                "information for automatic skill selection.",
            )
        )

    license_name = frontmatter.get("license")

    if license_name != "MIT":
        issues.append(
            ValidationIssue(
                "WARNING",
                skill_file,
                f"Expected license 'MIT', found {license_name!r}.",
            )
        )

    compatibility = frontmatter.get("compatibility")

    if compatibility != "opencode":
        issues.append(
            ValidationIssue(
                "WARNING",
                skill_file,
                f"Expected compatibility 'opencode', found "
                f"{compatibility!r}.",
            )
        )

    metadata = frontmatter.get("metadata")

    if not isinstance(metadata, dict):
        issues.append(
            ValidationIssue(
                "ERROR",
                skill_file,
                "'metadata' must be a mapping.",
            )
        )
    else:
        missing_metadata = REQUIRED_METADATA_FIELDS - set(metadata)

        if missing_metadata:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    skill_file,
                    "Missing required metadata fields: "
                    + ", ".join(sorted(missing_metadata)),
                )
            )

        for field_name in REQUIRED_METADATA_FIELDS:
            value = metadata.get(field_name)

            if not isinstance(value, str) or not value.strip():
                issues.append(
                    ValidationIssue(
                        "ERROR",
                        skill_file,
                        f"metadata.{field_name} must be a non-empty string.",
                    )
                )

        version = metadata.get("version")

        if isinstance(version, str) and not re.fullmatch(
            r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?",
            version,
        ):
            issues.append(
                ValidationIssue(
                    "WARNING",
                    skill_file,
                    f"metadata.version '{version}' does not appear to use "
                    "semantic versioning.",
                )
            )

    if not body:
        issues.append(
            ValidationIssue(
                "ERROR",
                skill_file,
                "Skill body is empty.",
            )
        )
    else:
        if not re.search(r"^#\s+\S+", body, flags=re.MULTILINE):
            issues.append(
                ValidationIssue(
                    "WARNING",
                    skill_file,
                    "Skill body does not contain a top-level Markdown heading.",
                )
            )

        if len(body.split()) < 50:
            issues.append(
                ValidationIssue(
                    "WARNING",
                    skill_file,
                    "Skill body is very short and may not provide enough "
                    "operational guidance.",
                )
            )

    return issues


def validate_command_file(path: Path) -> list[ValidationIssue]:
    """Validate one OpenCode slash-command Markdown file."""
    issues: list[ValidationIssue] = []

    command_name = path.stem

    if not VALID_NAME_PATTERN.fullmatch(command_name):
        issues.append(
            ValidationIssue(
                "ERROR",
                path,
                "Command filename must contain lowercase letters, numbers, "
                "and single hyphens only.",
            )
        )

    frontmatter, body = extract_frontmatter(path)

    if frontmatter is None:
        issues.append(
            ValidationIssue(
                "ERROR",
                path,
                "Missing, malformed, or invalid YAML frontmatter.",
            )
        )
        return issues

    description = frontmatter.get("description")

    if not isinstance(description, str) or not description.strip():
        issues.append(
            ValidationIssue(
                "ERROR",
                path,
                "Command frontmatter must include a non-empty description.",
            )
        )

    if not body:
        issues.append(
            ValidationIssue(
                "ERROR",
                path,
                "Command body is empty.",
            )
        )
        return issues

    if "$ARGUMENTS" not in body:
        issues.append(
            ValidationIssue(
                "WARNING",
                path,
                "Command does not reference $ARGUMENTS.",
            )
        )

    return issues


def validate_tool_file(path: Path) -> list[ValidationIssue]:
    """Validate one OpenCode custom tool TypeScript wrapper."""
    issues: list[ValidationIssue] = []
    filename = path.name

    if not filename.endswith(".ts"):
        issues.append(ValidationIssue("ERROR", path, "Must be a .ts file."))
        return issues

    tool_name = filename.removesuffix(".ts")

    if not VALID_TOOL_NAME_PATTERN.fullmatch(tool_name):
        issues.append(
            ValidationIssue(
                "ERROR",
                path,
                "Filename must be lowercase with underscores only.",
            )
        )

    if tool_name in BUILTIN_TOOL_NAMES:
        issues.append(
            ValidationIssue(
                "WARNING",
                path,
                f"Filename '{tool_name}' collides with a likely built-in tool name.",
            )
        )

    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        issues.append(ValidationIssue("ERROR", path, "Could not read file."))
        return issues

    if not content.strip():
        issues.append(ValidationIssue("ERROR", path, "File is empty."))
        return issues

    if 'import { tool } from "@opencode-ai/plugin"' not in content:
        issues.append(
            ValidationIssue(
                "ERROR",
                path,
                "Missing required import: import { tool } from \"@opencode-ai/plugin\".",
            )
        )

    if "export default tool(" not in content:
        issues.append(
            ValidationIssue(
                "ERROR",
                path,
                "Missing required export: export default tool(...).",
            )
        )

    if "description" not in content:
        issues.append(
            ValidationIssue(
                "ERROR",
                path,
                "Missing description property.",
            )
        )

    if "args" not in content:
        issues.append(
            ValidationIssue(
                "ERROR",
                path,
                "Missing args property.",
            )
        )

    if "execute" not in content:
        issues.append(
            ValidationIssue(
                "ERROR",
                path,
                "Missing execute property.",
            )
        )

    return issues


PACK_REQUIRED_SECTIONS = [
    "Who This Is For",
    "Included Skills",
    "Recommended Commands",
    "Best Use Cases",
    "Example Prompts",
    "Installation",
    "When Not to Use",
]


def validate_pack_file(path: Path) -> list[ValidationIssue]:
    """Validate one skill pack Markdown file."""
    issues: list[ValidationIssue] = []
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        issues.append(ValidationIssue("ERROR", path, "Could not read pack file."))
        return issues

    if not content.strip():
        issues.append(ValidationIssue("ERROR", path, "Pack file is empty."))
        return issues

    if not content.lstrip().startswith("# "):
        issues.append(ValidationIssue("WARNING", path, "Pack file does not start with a top-level heading."))

    for section in PACK_REQUIRED_SECTIONS:
        if f"## {section}" not in content:
            issues.append(ValidationIssue("WARNING", path, f"Missing required section '## {section}'."))

    return issues


def validate_repository() -> list[ValidationIssue]:
    """Validate repository structure, skills, and commands."""
    issues: list[ValidationIssue] = []

    if not SKILLS_DIR.is_dir():
        issues.append(
            ValidationIssue(
                "ERROR",
                SKILLS_DIR,
                "Skills directory does not exist.",
            )
        )
        return issues

    skill_dirs = sorted(
        path for path in SKILLS_DIR.iterdir() if path.is_dir()
    )

    if not skill_dirs:
        issues.append(
            ValidationIssue(
                "ERROR",
                SKILLS_DIR,
                "No skill directories were found.",
            )
        )
        return issues

    seen_names: set[str] = set()

    for skill_dir in skill_dirs:
        issues.extend(validate_skill_directory(skill_dir, seen_names))

    existing_skill_names = {path.name for path in skill_dirs}
    missing_recommended_skills = _discover_skills() - existing_skill_names

    for missing_skill in sorted(missing_recommended_skills):
        issues.append(
            ValidationIssue(
                "WARNING",
                SKILLS_DIR,
                f"Recommended skill '{missing_skill}' is missing.",
            )
        )

    unexpected_files = sorted(
        path
        for path in SKILLS_DIR.iterdir()
        if path.is_file() and not path.name.startswith(".")
    )

    for unexpected_file in unexpected_files:
        issues.append(
            ValidationIssue(
                "WARNING",
                unexpected_file,
                "Unexpected file directly inside skills directory.",
            )
        )

    if not COMMANDS_DIR.is_dir():
        issues.append(
            ValidationIssue(
                "WARNING",
                COMMANDS_DIR,
                "Commands directory does not exist.",
            )
        )
    else:
        command_files = sorted(COMMANDS_DIR.glob("*.md"))

        if not command_files:
            issues.append(
                ValidationIssue(
                    "WARNING",
                    COMMANDS_DIR,
                    "No command Markdown files were found.",
                )
            )

        for command_file in command_files:
            issues.extend(validate_command_file(command_file))

        existing_commands = {path.stem for path in command_files}
        missing_commands = _discover_commands() - existing_commands

        for missing_command in sorted(missing_commands):
            issues.append(
                ValidationIssue(
                    "WARNING",
                    COMMANDS_DIR,
                    f"Recommended command '{missing_command}.md' is missing.",
                )
            )

        unexpected_command_files = sorted(
            path
            for path in COMMANDS_DIR.iterdir()
            if path.is_file()
            and path.suffix != ".md"
            and not path.name.startswith(".")
        )

        for unexpected_file in unexpected_command_files:
            issues.append(
                ValidationIssue(
                    "WARNING",
                    unexpected_file,
                    "Unexpected non-Markdown file in commands directory.",
                )
            )

    # --------------------------------------------------
    # Validate pack files
    # --------------------------------------------------

    if PACKS_DIR.is_dir():
        pack_files = sorted(PACKS_DIR.glob("*.md"))
        if not pack_files:
            issues.append(ValidationIssue("WARNING", PACKS_DIR, "No pack Markdown files were found."))
        for pack_file in pack_files:
            issues.extend(validate_pack_file(pack_file))
    else:
        issues.append(ValidationIssue("WARNING", PACKS_DIR, "Packs directory does not exist."))

    required_repository_files = [
        ROOT_DIR / "README.md",
        ROOT_DIR / "LICENSE",
        ROOT_DIR / "CHANGELOG.md",
        ROOT_DIR / "pyproject.toml",
        ROOT_DIR / "requirements.txt",
    ]

    for required_file in required_repository_files:
        if not required_file.is_file():
            issues.append(
                ValidationIssue(
                    "WARNING",
                    required_file,
                    f"Recommended repository file '{required_file.name}' "
                    "is missing.",
                )
            )

    install_script = ROOT_DIR / "scripts" / "install-pack.sh"
    if not install_script.is_file():
        issues.append(ValidationIssue("WARNING", install_script, "Pack installer script is missing."))
    elif not os.access(install_script, os.X_OK):
        issues.append(ValidationIssue("WARNING", install_script, "Pack installer script is not executable."))

    issues.extend(_validate_readme_skill_table())
    issues.extend(_validate_readme_command_table())

    # --------------------------------------------------
    # Validate recommended documentation
    # --------------------------------------------------

    if DOCS_DIR.is_dir():
        for doc_name in RECOMMENDED_DOCS:
            doc_path = DOCS_DIR / doc_name
            if not doc_path.is_file():
                issues.append(
                    ValidationIssue(
                        "WARNING",
                        DOCS_DIR,
                        f"Recommended documentation '{doc_name}' is missing.",
                    )
                )
    else:
        issues.append(
            ValidationIssue(
                "WARNING",
                DOCS_DIR,
                "Docs directory does not exist.",
            )
        )

    # --------------------------------------------------
    # Validate TypeScript custom tool wrappers
    # --------------------------------------------------

    if not TOOLS_DIR.is_dir():
        issues.append(
            ValidationIssue(
                "WARNING",
                TOOLS_DIR,
                "opencode-tools directory does not exist.",
            )
        )
    else:
        for required_file in REQUIRED_TOOL_FILES:
            tool_path = TOOLS_DIR / required_file
            if not tool_path.is_file():
                issues.append(
                    ValidationIssue(
                        "ERROR",
                        TOOLS_DIR,
                        f"Required tool file '{required_file}' is missing.",
                    )
                )
            else:
                issues.extend(validate_tool_file(tool_path))

        # Warn about unexpected .ts files beyond the required set
        expected = set(REQUIRED_TOOL_FILES)
        for path in sorted(TOOLS_DIR.glob("*.ts")):
            if path.name not in expected:
                issues.append(
                    ValidationIssue(
                        "WARNING",
                        path,
                        "Unexpected tool file (not in the required set).",
                    )
                )

        # Check for non-TS files in the directory
        for path in sorted(TOOLS_DIR.iterdir()):
            if path.is_file() and path.suffix != ".ts" and not path.name.startswith("."):
                issues.append(
                    ValidationIssue(
                        "WARNING",
                        path,
                        "Unexpected non-TS file in opencode-tools directory.",
                    )
                )

    # --------------------------------------------------
    # Validate Python tool backend scripts
    # --------------------------------------------------

    if PYTHON_TOOLS_DIR.is_dir():
        for required_file in REQUIRED_PYTHON_TOOL_FILES:
            py_path = PYTHON_TOOLS_DIR / required_file
            if not py_path.is_file():
                issues.append(
                    ValidationIssue(
                        "ERROR",
                        PYTHON_TOOLS_DIR,
                        f"Required Python tool script '{required_file}' is missing.",
                    )
                )
            elif py_path.stat().st_size == 0:
                issues.append(
                    ValidationIssue(
                        "ERROR",
                        py_path,
                        "Python tool script is empty.",
                    )
                )
    else:
        issues.append(
            ValidationIssue(
                "WARNING",
                PYTHON_TOOLS_DIR,
                "tools directory does not exist.",
            )
        )

    return issues


def print_summary(issues: list[ValidationIssue]) -> int:
    """Print validation output and return an exit code."""
    errors = [issue for issue in issues if issue.severity == "ERROR"]
    warnings = [issue for issue in issues if issue.severity == "WARNING"]

    if issues:
        for issue in issues:
            print(issue.format())

        print()

    print("Validation summary")
    print(f"Errors:   {len(errors)}")
    print(f"Warnings: {len(warnings)}")

    if errors:
        print("\nSkill validation failed.")
        return 1

    print("\nAll required validations passed.")

    if warnings:
        print("Review the warnings before publishing.")

    return 0


def main() -> int:
    issues = validate_repository()
    return print_summary(issues)


if __name__ == "__main__":
    sys.exit(main())
