"""Tests for scripts/install-opencode.sh."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
INSTALL_SCRIPT = SCRIPTS_DIR / "install-opencode.sh"


def _run_installer(
    repo_root: Path,
    xdg_config_home: str,
) -> subprocess.CompletedProcess:
    """Run the installer script from within a mock repo.

    Copies the installer into the mock repo's scripts/ directory so
    that BASH_SOURCE resolves inside the mock tree.
    """
    mock_scripts = repo_root / "scripts"
    mock_scripts.mkdir(parents=True, exist_ok=True)
    mock_installer = mock_scripts / "install-opencode.sh"
    shutil.copy2(str(INSTALL_SCRIPT), str(mock_installer))
    mock_installer.chmod(0o755)

    env = os.environ.copy()
    env["XDG_CONFIG_HOME"] = xdg_config_home
    result = subprocess.run(
        [str(mock_installer)],
        capture_output=True,
        text=True,
        env=env,
    )
    return result


def _create_mock_skill(skills_dir: Path, name: str) -> None:
    """Create a mock skill directory with a minimal SKILL.md."""
    skill_dir = skills_dir / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\nname: " + name + "\n---\n# " + name + "\nbody\n")


def _create_mock_command(commands_dir: Path, name: str) -> None:
    """Create a mock command .md file."""
    (commands_dir / (name + ".md")).write_text("---\ndescription: test\n---\n$ARGUMENTS\n")


def _create_mock_doc(docs_dir: Path, name: str) -> None:
    """Create a mock doc .md file."""
    (docs_dir / (name + ".md")).write_text("# " + name + "\ndoc body\n")


def _create_mock_tool(tools_dir: Path, name: str) -> None:
    """Create a mock tool .ts file."""
    (tools_dir / (name + ".ts")).write_text(
        'import { tool } from "@opencode-ai/plugin";\n'
        "export default tool({\n"
        "  description: 'test',\n"
        '  args: {},\n'
        "  execute: async () => 'test',\n"
        "});\n"
    )


# --------------------------------------------------
# Fixtures
# --------------------------------------------------


@pytest.fixture
def mock_repo(tmp_path: Path) -> Path:
    """Create a mock repository structure with skills, commands, docs, tools."""
    skills_dir = tmp_path / "skills"
    commands_dir = tmp_path / "commands"
    docs_dir = tmp_path / "docs"
    tools_dir = tmp_path / "opencode-tools"

    skills_dir.mkdir()
    commands_dir.mkdir()
    docs_dir.mkdir()
    tools_dir.mkdir()

    _create_mock_skill(skills_dir, "python-quality")
    _create_mock_skill(skills_dir, "code-review")
    _create_mock_command(commands_dir, "review")
    _create_mock_command(commands_dir, "fix")
    _create_mock_doc(docs_dir, "design")
    _create_mock_doc(docs_dir, "guide")
    _create_mock_tool(tools_dir, "repo_map")
    _create_mock_tool(tools_dir, "diff_summarizer")

    return tmp_path


@pytest.fixture
def xdg_config(tmp_path: Path) -> str:
    """Return a temporary XDG_CONFIG_HOME path."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return str(config_dir)


@pytest.fixture
def skip_if_no_python() -> None:
    """Skip test if python3 is not available (installer uses it for resolve_path)."""
    if not shutil.which("python3") and not shutil.which("python"):
        pytest.skip("python3/python not available")


# --------------------------------------------------
# Tests
# --------------------------------------------------


class TestInstallOpenCode:
    """Tests for the install-opencode.sh symlink installer."""

    def test_installs_all_items(self, mock_repo: Path, xdg_config: str) -> None:
        result = _run_installer(mock_repo, xdg_config)
        assert result.returncode == 0, f"Installer failed:\n{result.stderr}"

        config_dir = Path(xdg_config) / "opencode"
        skills_target = config_dir / "skills"
        commands_target = config_dir / "commands"
        docs_target = config_dir / "docs"
        tools_target = config_dir / "tools"

        # Verify symlinks exist for all items
        assert (skills_target / "python-quality").is_symlink()
        assert (skills_target / "code-review").is_symlink()
        assert (commands_target / "review.md").is_symlink()
        assert (commands_target / "fix.md").is_symlink()
        assert (docs_target / "design.md").is_symlink()
        assert (docs_target / "guide.md").is_symlink()
        assert (tools_target / "repo_map.ts").is_symlink()
        assert (tools_target / "diff_summarizer.ts").is_symlink()

        # Verify symlinks resolve to the correct source
        expected_skill_source = str(mock_repo / "skills" / "python-quality")
        assert os.path.realpath(skills_target / "python-quality") == os.path.realpath(expected_skill_source)

        expected_command_source = str(mock_repo / "commands" / "review.md")
        assert os.path.realpath(commands_target / "review.md") == os.path.realpath(expected_command_source)

        expected_doc_source = str(mock_repo / "docs" / "design.md")
        assert os.path.realpath(docs_target / "design.md") == os.path.realpath(expected_doc_source)

        expected_tool_source = str(mock_repo / "opencode-tools" / "repo_map.ts")
        assert os.path.realpath(tools_target / "repo_map.ts") == os.path.realpath(expected_tool_source)

        # Verify stdout contains installation messages
        assert "Installed skill: python-quality" in result.stdout
        assert "Installed skill: code-review" in result.stdout
        assert "Installed command: /review" in result.stdout
        assert "Installed command: /fix" in result.stdout
        assert "Installed doc: design.md" in result.stdout
        assert "Installed doc: guide.md" in result.stdout
        assert "Installed tool: repo_map" in result.stdout
        assert "Installed tool: diff_summarizer" in result.stdout

        # Verify summary counts
        assert "Skills installed:   2" in result.stdout
        assert "Commands installed: 2" in result.stdout
        assert "Docs installed:     2" in result.stdout
        assert "Tools installed:    2" in result.stdout

    def test_rerun_is_idempotent(self, mock_repo: Path, xdg_config: str) -> None:
        result1 = _run_installer(mock_repo, xdg_config)
        assert result1.returncode == 0

        result2 = _run_installer(mock_repo, xdg_config)
        assert result2.returncode == 0

        # Second run should show "Replacing existing symlink" messages
        assert "Replacing existing symlink: python-quality" in result2.stdout
        assert "Replacing existing symlink: /review" in result2.stdout

        config_dir = Path(xdg_config) / "opencode"
        assert (config_dir / "skills" / "python-quality").is_symlink()
        assert (config_dir / "skills" / "code-review").is_symlink()

    def test_foreign_symlink_is_preserved(
        self, mock_repo: Path, xdg_config: str
    ) -> None:
        config_dir = Path(xdg_config) / "opencode"
        skills_target = config_dir / "skills"
        skills_target.mkdir(parents=True)

        # Create a foreign symlink (points to /tmp, not the mock repo)
        foreign_link = skills_target / "python-quality"
        foreign_target = Path("/tmp/foreign-skill")
        foreign_target.write_text("foreign")
        foreign_link.symlink_to(foreign_target)

        result = _run_installer(mock_repo, xdg_config)
        assert result.returncode == 0

        # Foreign symlink should still be preserved
        assert foreign_link.is_symlink()
        assert os.path.realpath(foreign_link) == os.path.realpath(foreign_target)

        # The warning should mention the foreign symlink
        assert "symlink from another source" in result.stderr

        # Other items should still be installed
        assert (config_dir / "skills" / "code-review").is_symlink()

    def test_existing_non_symlink_is_skipped(
        self, mock_repo: Path, xdg_config: str
    ) -> None:
        config_dir = Path(xdg_config) / "opencode"
        skills_target = config_dir / "skills"
        skills_target.mkdir(parents=True)

        # Create a regular file (not a symlink) at the target path
        regular_file = skills_target / "python-quality"
        regular_file.write_text("not a symlink")

        result = _run_installer(mock_repo, xdg_config)
        assert result.returncode == 0

        # The regular file should be preserved
        assert regular_file.is_file()
        assert not regular_file.is_symlink()
        assert regular_file.read_text() == "not a symlink"

        # Warning should be in stderr
        assert "already exists and is not a symlink" in result.stderr

    def test_empty_skills_directory(self, tmp_path: Path) -> None:
        """Empty skills/ dir should produce a notice on stderr."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        # No subdirectories in skills/

        xdg_config = str(tmp_path / "config")
        result = _run_installer(tmp_path, xdg_config)
        assert result.returncode == 0
        assert "No skill directories found" in result.stderr

    def test_missing_skills_directory(self, tmp_path: Path) -> None:
        """Missing skills/ dir should produce an error on stderr and exit non-zero."""
        xdg_config = str(tmp_path / "config")
        result = _run_installer(tmp_path, xdg_config)
        assert result.returncode != 0
        assert "skills directory not found" in result.stderr

    def test_empty_commands_directory(self, tmp_path: Path) -> None:
        """Empty commands/ dir (no .md files) should produce a notice on stderr."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        # Create at least one skill so we don't hit the missing-skills error
        _create_mock_skill(skills_dir, "test-skill")

        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()  # exists but empty

        xdg_config = str(tmp_path / "config")
        result = _run_installer(tmp_path, xdg_config)
        assert result.returncode == 0
        assert "No command files found" in result.stderr

    def test_warnings_go_to_stderr(self, mock_repo: Path, xdg_config: str) -> None:
        """Warnings for non-symlink targets should appear on stderr."""
        config_dir = Path(xdg_config) / "opencode"
        skills_target = config_dir / "skills"
        skills_target.mkdir(parents=True)

        # Place a regular file blocking a skill
        regular_file = skills_target / "python-quality"
        regular_file.write_text("blocker")

        result = _run_installer(mock_repo, xdg_config)
        assert result.returncode == 0
        assert "already exists and is not a symlink" in result.stderr
        # Normal install messages should still be on stdout
        assert "Installed skill: code-review" in result.stdout

    def test_missing_commands_directory(self, tmp_path: Path) -> None:
        """Missing commands/ dir should print info and continue."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        _create_mock_skill(skills_dir, "test-skill")

        xdg_config = str(tmp_path / "config")
        result = _run_installer(tmp_path, xdg_config)
        assert result.returncode == 0
        assert "Commands directory not found" in result.stdout

    def test_missing_tools_directory(self, mock_repo: Path, xdg_config: str) -> None:
        """Missing opencode-tools/ dir should print info and continue."""
        # Remove the tools dir from the mock repo
        shutil.rmtree(str(mock_repo / "opencode-tools"))

        result = _run_installer(mock_repo, xdg_config)
        assert result.returncode == 0
        assert "Tools directory not found" in result.stdout
        # Skills should still be installed
        assert "Installed skill: python-quality" in result.stdout
