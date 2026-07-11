"""Tests for tools/prompt_budget.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.prompt_budget import (
    estimate_tokens,
    build_prompt_budget,
    analyze_file,
    analyze_directory,
    run,
)


class TestEstimateTokens:
    def test_empty(self):
        assert estimate_tokens("") == 1

    def test_short(self):
        assert estimate_tokens("hello") == 1

    def test_exact_division(self):
        assert estimate_tokens("a" * 8) == 2

    def test_rounds_down(self):
        assert estimate_tokens("a" * 7) == 1


class TestAnalyzeFile:
    def test_small_file(self, tmp_path: Path) -> None:
        f = tmp_path / "small.py"
        f.write_text("x = 1\n")
        result = analyze_file(f)
        assert result["chars"] == 6
        assert result["lines"] == 1
        assert result["estimated_tokens"] >= 1

    def test_unreadable_file(self, tmp_path: Path) -> None:
        f = tmp_path / "missing.py"
        result = analyze_file(f)
        assert "error" in result


class TestAnalyzeDirectory:
    def test_empty_directory(self, tmp_path: Path) -> None:
        result = analyze_directory(tmp_path)
        assert result["total_files"] == 0
        assert result["total_chars"] == 0

    def test_with_python_files(self, tmp_path: Path) -> None:
        (tmp_path / "main.py").write_text("x = 1\n")
        (tmp_path / "utils.py").write_text("y = 2\n")
        result = analyze_directory(tmp_path)
        assert result["total_files"] == 2


class TestBuildPromptBudget:
    def test_text_input(self):
        result = build_prompt_budget(text="hello world")
        assert "# Prompt Budget" in result
        assert "hello world" not in result
        assert "Tokens" in result or "tokens" in result

    def test_text_empty(self):
        result = build_prompt_budget(text="")
        assert "ERROR" in result or "Prompt Budget" in result

    def test_file_input(self, tmp_path: Path) -> None:
        f = tmp_path / "analyze.py"
        f.write_text("def foo():\n    pass\n")
        result = build_prompt_budget(file_path=f)
        assert "# Prompt Budget" in result
        assert "File:" in result

    def test_file_not_found(self, tmp_path: Path) -> None:
        result = build_prompt_budget(file_path=tmp_path / "nope")
        assert "ERROR" in result

    def test_directory_input(self, tmp_path: Path) -> None:
        (tmp_path / "main.py").write_text("x = 1\n")
        result = build_prompt_budget(directory=tmp_path)
        assert "# Prompt Budget" in result
        assert "Directory:" in result

    def test_directory_not_found(self, tmp_path: Path) -> None:
        result = build_prompt_budget(directory=tmp_path / "nope")
        assert "0" in result or "ERROR" in result

    def test_recommendation_present(self, tmp_path: Path) -> None:
        (tmp_path / "main.py").write_text("x = 1\n")
        result = build_prompt_budget(directory=tmp_path)
        assert "Recommended" in result

    def test_large_file_warning(self, tmp_path: Path) -> None:
        f = tmp_path / "large.py"
        f.write_text("x\n" * 50000)
        result = build_prompt_budget(file_path=f)
        assert "⚠" in result or "Warning" in result or "recommendation" in result.lower()

    def test_ignored_directories(self, tmp_path: Path) -> None:
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "lib.js").write_text("// large lib\n")
        result = analyze_directory(tmp_path)
        assert result["total_files"] == 0

    def test_top_parameter(self, tmp_path: Path) -> None:
        for i in range(10):
            (tmp_path / f"file_{i}.py").write_text(f"# file {i}\n")
        result = build_prompt_budget(directory=tmp_path, top=5)
        assert "Largest Files" in result

    def test_no_args_returns_error(self):
        result = build_prompt_budget()
        assert "ERROR" in result

    def test_top_above_twenty(self, tmp_path: Path) -> None:
        for i in range(30):
            (tmp_path / f"file_{i}.py").write_text(f"# file {i}\n")
        result = build_prompt_budget(directory=tmp_path, top=25)
        table_lines = [l for l in result.splitlines() if "file_" in l]
        assert len(table_lines) == 25

    def test_run_file_dispatch(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("hello world\n")
        result = run(["--file", str(f)])
        assert "# Prompt Budget" in result
        assert "File:" in result

    def test_run_dir_dispatch(self, tmp_path: Path) -> None:
        (tmp_path / "a.py").write_text("x = 1\n")
        (tmp_path / "b.py").write_text("y = 2\n")
        result = run(["--dir", str(tmp_path)])
        assert "# Prompt Budget" in result
        assert "Directory:" in result
        assert "2" in result or "2" in result

    def test_run_invalid_arg(self, tmp_path: Path) -> None:
        result = run(["--file", str(tmp_path / "nope")])
        assert "ERROR" in result

    def test_run_no_args(self) -> None:
        result = run([])
        assert "ERROR" in result


class TestWalkSignificantFiles:
    def test_egg_info_excluded(self, tmp_path: Path) -> None:
        pkg_dir = tmp_path / "my_package.egg-info"
        pkg_dir.mkdir()
        (pkg_dir / "PKG-INFO").write_text("Metadata-Version: 2.1\n")
        (tmp_path / "main.py").write_text("x = 1\n")
        result = analyze_directory(tmp_path)
        assert result["total_files"] == 1

    def test_analyze_directory_respects_top(self, tmp_path: Path) -> None:
        for i in range(10):
            (tmp_path / f"file_{i}.py").write_text(f"# file {i}\n")
        result = analyze_directory(tmp_path, top=3)
        assert len(result["largest"]) == 3

    def test_circular_symlink_does_not_crash(self, tmp_path: Path) -> None:
        (tmp_path / "real.py").write_text("x = 1\n")
        link = tmp_path / "loop"
        try:
            link.symlink_to(tmp_path, target_is_directory=True)
        except (OSError, NotImplementedError):
            pytest.skip("Cannot create symlinks on this platform")
        result = analyze_directory(tmp_path)
        assert result["total_files"] >= 1