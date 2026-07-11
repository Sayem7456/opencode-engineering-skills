"""Tests for scripts/validate-skills.sh edge-case handling."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
VALIDATE_SCRIPT = SCRIPTS_DIR / "validate-skills.sh"

SKILL_TEMPLATE = """\
---
name: {name}
description: {name} skill for testing validate-skills.sh edge cases.
license: {license}
compatibility: opencode
metadata:
  category: test
  stack: test
  version: "1.0.0"
orchestration:
  {orchestration}
---
# {name}

Body content for {name}.
"""

SKILL_COMMAND_TEMPLATE = """\
---
description: test command
---
$ARGUMENTS
"""


def _run_validator(repo_root: Path) -> subprocess.CompletedProcess:
    """Copy the validator into the mock repo and run it there.

    The script resolves ROOT from BASH_SOURCE, so it must live inside the
    mock repo tree for validation to target the temp directory.
    """
    mock_scripts = repo_root / "scripts"
    mock_scripts.mkdir(parents=True, exist_ok=True)
    mock_validator = mock_scripts / "validate-skills.sh"
    shutil.copy2(str(VALIDATE_SCRIPT), str(mock_validator))
    mock_validator.chmod(0o755)
    result = subprocess.run(
        [str(mock_validator)],
        capture_output=True,
        text=True,
        cwd=str(repo_root),
    )
    return result


def _create_minimal_repo_structure(repo_root: Path) -> None:
    """Create the minimal set of directories and files the validator expects."""
    skills_dir = repo_root / "skills"
    commands_dir = repo_root / "commands"
    docs_dir = repo_root / "docs"
    tools_dir = repo_root / "opencode-tools"
    py_tools_dir = repo_root / "tools"

    skills_dir.mkdir(parents=True)
    commands_dir.mkdir()
    docs_dir.mkdir()
    tools_dir.mkdir()
    py_tools_dir.mkdir()

    # Minimal command
    (commands_dir / "review.md").write_text(SKILL_COMMAND_TEMPLATE)
    # Minimal docs
    (docs_dir / "skill-orchestration-design.md").write_text("# design\n")
    (docs_dir / "skill-routing-matrix.md").write_text("# routing\n")
    # Minimal TS tool (must have all required properties)
    tool_ts = (
        'import { tool } from "@opencode-ai/plugin";\n'
        "export default tool({\n"
        "  description: 'test',\n"
        "  args: {},\n"
        "  execute: async () => 'test',\n"
        "});\n"
    )
    for tool_file in ("repo_map.ts", "diff_summarizer.ts",
                      "context_compressor.ts", "prompt_budget.ts"):
        (tools_dir / tool_file).write_text(tool_ts)
    # Minimal Python tools
    for py_file in ("repo_map.py", "diff_summarizer.py",
                    "context_compressor.py", "prompt_budget.py"):
        (py_tools_dir / py_file).write_text("# placeholder\n")


def _create_skill(skills_dir: Path, name: str, **overrides: str) -> None:
    """Create a skill directory with SKILL.md using overrides.

    Override keys: name, license, compatibility, orchestration.
    """
    skill_dir = skills_dir / name
    skill_dir.mkdir(parents=True)
    content = SKILL_TEMPLATE.format(
        name=overrides.get("name", name),
        license=overrides.get("license", "MIT"),
        orchestration=overrides.get(
            "orchestration",
            'lead_for:\n    - test\n  support_for: []\n'
            '  conflicts_with:\n    - other\n',
        ),
    )
    (skill_dir / "SKILL.md").write_text(content)


# --------------------------------------------------
# Fixtures
# --------------------------------------------------


@pytest.fixture
def repo_with_skill(tmp_path: Path) -> Path:
    """Create a mock repo with one minimal valid skill."""
    _create_minimal_repo_structure(tmp_path)
    _create_skill(tmp_path / "skills", "test-skill")
    return tmp_path


# --------------------------------------------------
# Tests
# --------------------------------------------------


class TestShellValidation:
    """Tests for validate-skills.sh handling of edge cases."""

    def test_normal_skill_passes(self, repo_with_skill: Path) -> None:
        result = _run_validator(repo_with_skill)
        assert result.returncode == 0, (
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
        assert "All validations passed" in result.stdout

    def test_quoted_license_passes(self, repo_with_skill: Path) -> None:
        skill_dir = repo_with_skill / "skills" / "test-skill"
        content = (skill_dir / "SKILL.md").read_text()
        content = content.replace("license: MIT", 'license: "MIT"')
        (skill_dir / "SKILL.md").write_text(content)

        result = _run_validator(repo_with_skill)
        assert result.returncode == 0, (
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )

    def test_quoted_compatibility_passes(self, repo_with_skill: Path) -> None:
        skill_dir = repo_with_skill / "skills" / "test-skill"
        content = (skill_dir / "SKILL.md").read_text()
        content = content.replace("compatibility: opencode",
                                  'compatibility: "opencode"')
        (skill_dir / "SKILL.md").write_text(content)

        result = _run_validator(repo_with_skill)
        assert result.returncode == 0, (
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )

    def test_space_before_colon_in_name_passes(self, repo_with_skill: Path) -> None:
        skill_dir = repo_with_skill / "skills" / "test-skill"
        content = (skill_dir / "SKILL.md").read_text()
        content = content.replace("name: test-skill", "name : test-skill")
        (skill_dir / "SKILL.md").write_text(content)

        result = _run_validator(repo_with_skill)
        assert result.returncode == 0, (
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )

    def test_non_list_lead_for_fails(self, repo_with_skill: Path) -> None:
        skill_dir = repo_with_skill / "skills" / "test-skill"
        content = (skill_dir / "SKILL.md").read_text()
        content = content.replace(
            "  lead_for:\n    - test\n  support_for: []\n"
            "  conflicts_with:\n    - other\n",
            "  lead_for: not-a-list\n  support_for: []\n"
            "  conflicts_with: []\n",
        )
        (skill_dir / "SKILL.md").write_text(content)

        result = _run_validator(repo_with_skill)
        assert result.returncode != 0
        assert "lead_for must be a YAML list" in result.stdout

    def test_non_list_support_for_fails(self, repo_with_skill: Path) -> None:
        skill_dir = repo_with_skill / "skills" / "test-skill"
        content = (skill_dir / "SKILL.md").read_text()
        content = content.replace(
            "  lead_for:\n    - test\n  support_for: []\n"
            "  conflicts_with:\n    - other\n",
            "  lead_for:\n    - test\n  support_for: false\n"
            "  conflicts_with:\n    - other\n",
        )
        (skill_dir / "SKILL.md").write_text(content)

        result = _run_validator(repo_with_skill)
        assert result.returncode != 0
        assert "support_for must be a YAML list" in result.stdout

    def test_non_list_conflicts_with_fails(self, repo_with_skill: Path) -> None:
        skill_dir = repo_with_skill / "skills" / "test-skill"
        content = (skill_dir / "SKILL.md").read_text()
        content = content.replace(
            "  lead_for:\n    - test\n  support_for: []\n"
            "  conflicts_with:\n    - other\n",
            "  lead_for:\n    - test\n  support_for: []\n"
            "  conflicts_with:\n    key: value\n",
        )
        (skill_dir / "SKILL.md").write_text(content)

        result = _run_validator(repo_with_skill)
        assert result.returncode != 0
        assert "conflicts_with must be a YAML list" in result.stdout
