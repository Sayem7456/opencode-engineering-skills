"""Tests for tools/repo_map.py."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from tools.repo_map import (
    _check_secrets,
    _is_ignored_dir,
    _relative_path,
    build_repo_map,
)


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("# entry point\n")
    (src / "models.py").write_text("class User:\n    pass\n")
    (src / "routes.py").write_text("# routes\n")

    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_main.py").write_text("def test_pass():\n    assert True\n")
    (tests / "__init__.py").write_text("")

    migrations = tmp_path / "migrations"
    migrations.mkdir()
    (migrations / "001_init.py").write_text("def upgrade():\n    pass\n")

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[project]\nname = 'test'\nversion = '0.1'\n")

    readme = tmp_path / "README.md"
    readme.write_text("# Test Project\n")

    (tmp_path / ".git").mkdir()
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / ".next").mkdir()

    return tmp_path


class TestRepoMap:
    def test_valid_path(self, tmp_project: Path) -> None:
        result = build_repo_map(tmp_project, max_files=300)
        assert "## Repo Map:" in result
        assert "Python" in result
        src_path = str(tmp_project / "src")
        assert src_path not in "ERROR"

    def test_invalid_path(self) -> None:
        result = build_repo_map(Path("/nonexistent/path"), max_files=300)
        assert "ERROR" in result
        assert "not found" in result

    def test_file_path(self, tmp_path: Path) -> None:
        f = tmp_path / "file.txt"
        f.write_text("hello")
        result = build_repo_map(f, max_files=300)
        assert "ERROR" in result
        assert "not a directory" in result

    def test_empty_directory(self, tmp_path: Path) -> None:
        result = build_repo_map(tmp_path, max_files=300)
        assert "## Repo Map:" in result

    def test_ignored_dirs_excluded(self, tmp_path: Path) -> None:
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "lib.js").write_text("// lib\n")
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("# main\n")
        (tmp_path / ".gitignore").write_text("node_modules\n")
        result = build_repo_map(tmp_path, max_files=300)
        assert "lib.js" not in result
        assert "config" in result.lower() or "Config" in result

    def test_language_detection(self, tmp_path: Path) -> None:
        (tmp_path / "main.py").write_text("")
        (tmp_path / "component.tsx").write_text("")
        (tmp_path / "style.css").write_text("")
        result = build_repo_map(tmp_path, max_files=300)
        assert "Python" in result
        assert "TypeScript" in result
        assert "CSS" in result

    def test_framework_detection_pytest(self, tmp_path: Path) -> None:
        (tmp_path / "conftest.py").write_text("")
        result = build_repo_map(tmp_path, max_files=300)
        assert "Pytest" in result

    def test_framework_detection_nextjs(self, tmp_path: Path) -> None:
        (tmp_path / "next.config.js").write_text("module.exports = {}")
        result = build_repo_map(tmp_path, max_files=300)
        assert "Next.js" in result

    def test_backend_file_group(self, tmp_path: Path) -> None:
        routes = tmp_path / "routes"
        routes.mkdir()
        (routes / "users.py").write_text("")
        (tmp_path / "main.py").write_text("")
        result = build_repo_map(tmp_path, max_files=300)
        assert "Backend" in result or "routes" in result

    def test_test_group(self, tmp_path: Path) -> None:
        tests = tmp_path / "tests"
        tests.mkdir()
        (tests / "test_auth.py").write_text("")
        result = build_repo_map(tmp_path, max_files=300)
        assert "Tests" in result
        assert "test_auth.py" in result

    def test_migration_group(self, tmp_path: Path) -> None:
        migrations = tmp_path / "migrations"
        migrations.mkdir()
        (migrations / "001_mig.py").write_text("")
        result = build_repo_map(tmp_path, max_files=300)
        assert "Database / Migration" in result

    def test_config_files_detected(self, tmp_path: Path) -> None:
        (tmp_path / "Dockerfile").write_text("FROM python")
        (tmp_path / "Makefile").write_text("all:\n\techo")
        result = build_repo_map(tmp_path, max_files=300)
        assert "Dockerfile" in result
        assert "Makefile" in result
        assert "Config" in result

    def test_suggested_next_reads(self, tmp_path: Path) -> None:
        (tmp_path / "main.py").write_text("")
        result = build_repo_map(tmp_path, max_files=300)
        assert "Suggested Next Reads" in result

    def test_no_crash_on_binary(self, tmp_path: Path) -> None:
        (tmp_path / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        result = build_repo_map(tmp_path, max_files=300)
        assert "## Repo Map:" in result

    def test_max_files_truncates_each_category(self, tmp_path: Path) -> None:
        for i in range(5):
            route_dir = tmp_path / "routes"
            route_dir.mkdir(exist_ok=True)
            (route_dir / f"file_{i}.py").write_text("")
        result_all = build_repo_map(tmp_path, max_files=0)
        result_limited = build_repo_map(tmp_path, max_files=2)
        count_all = result_all.count("file_")
        count_limited = result_limited.count("file_")
        assert count_all > count_limited
        assert count_limited <= 4  # 2 per category * 2 categories (backend may appear too)

    def test_framework_detection_fastapi_via_main_py(self, tmp_path: Path) -> None:
        (tmp_path / "main.py").write_text("from fastapi import FastAPI\n")
        result = build_repo_map(tmp_path, max_files=300)
        assert "FastAPI" in result

    def test_secret_detection(self, tmp_path: Path) -> None:
        (tmp_path / "config.py").write_text('API_KEY = "sk-abc12345def67890ghij"\n')
        result = build_repo_map(tmp_path, max_files=300)
        assert "Possible Secrets" in result
        assert "config.py" in result

    def test_secret_detection_ignored_dir(self, tmp_path: Path) -> None:
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "secret.js").write_text('API_KEY = "sk-abc"\n')
        result = build_repo_map(tmp_path, max_files=300)
        assert "Possible Secrets" not in result

    def test_is_ignored_dir_egg_info(self) -> None:
        assert _is_ignored_dir("my_package.egg-info")
        assert _is_ignored_dir(".git")
        assert not _is_ignored_dir("src")

    def test_relative_path_within_root(self, tmp_path: Path) -> None:
        sub = tmp_path / "a" / "b" / "file.py"
        sub.parent.mkdir(parents=True)
        sub.write_text("")
        assert _relative_path(sub, tmp_path) == "a/b/file.py"

    def test_relative_path_outside_root(self, tmp_path: Path) -> None:
        outside = Path("/tmp/other.py")
        assert _relative_path(outside, tmp_path) == "other.py"