#!/usr/bin/env python3
"""Validate OpenCode skill and command files in this repository."""

from __future__ import annotations

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

VALID_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

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


def _parse_readme_table(pattern: re.Pattern[str]) -> set[str]:
    """Extract names from a Markdown table in README.md matching the given regex."""
    if not README_PATH.is_file():
        return set()
    try:
        content = README_PATH.read_text(encoding="utf-8")
    except OSError:
        return set()
    return set(pattern.findall(content))


def _validate_readme_skill_table() -> list[ValidationIssue]:
    """Check README skills table matches skills on disk."""
    issues: list[ValidationIssue] = []
    readme_skills = _parse_readme_table(
        re.compile(r"^\|\s+`([a-z0-9]+(?:-[a-z0-9]+)*)`\s+\|", re.MULTILINE)
    )
    disk_skills = _discover_skills()
    if not readme_skills:
        return issues
    extra = readme_skills - disk_skills
    missing = disk_skills - readme_skills
    for name in sorted(extra):
        issues.append(ValidationIssue("WARNING", README_PATH, f"Skill '{name}' listed in README but missing on disk."))
    for name in sorted(missing):
        issues.append(ValidationIssue("WARNING", README_PATH, f"Skill '{name}' on disk but missing from README table."))
    return issues


def _validate_readme_command_table() -> list[ValidationIssue]:
    """Check README commands table matches commands on disk."""
    issues: list[ValidationIssue] = []
    readme_commands = _parse_readme_table(
        re.compile(r"^\|\s+`/([a-z0-9]+(?:-[a-z0-9]+)*)`\s+\|", re.MULTILINE)
    )
    disk_commands = _discover_commands()
    if not readme_commands:
        return issues
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

    required_repository_files = [
        ROOT_DIR / "README.md",
        ROOT_DIR / "LICENSE",
        ROOT_DIR / "CHANGELOG.md",
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

    issues.extend(_validate_readme_skill_table())
    issues.extend(_validate_readme_command_table())

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
