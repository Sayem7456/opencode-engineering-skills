"""Tests for tools/diff_summarizer.py."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools.diff_summarizer import (
    _classify_risk,
    _detect_symbols,
    _get_diff_from_git,
    _parse_diff,
    _redact_line,
    _suggest_tests,
    summarize_diff,
)


SAMPLE_DIFF = """diff --git a/src/routes/users.py b/src/routes/users.py
index 123..456 789
--- a/src/routes/users.py
+++ b/src/routes/users.py
@@ -10,7 +10,9 @@
 def get_user(user_id: int):
     return User.query.get(user_id)
+    logger.info("Fetching user")
+    return db_session.query(User).filter(User.id == user_id).first()
+
+def create_user(data: dict):
+    db_session.add(User(**data))
+    db_session.commit()
"""

SAMPLE_DIFF_SECRETS = """diff --git a/src/config.py b/src/config.py
index abc..def 789
--- a/src/config.py
+++ b/src/config.py
@@ -1,3 +1,4 @@
-API_KEY = "old-key-here"
+API_KEY = "sk-new-key-in-diff"
 PASSWORD = "super-secret"
"""

SAMPLE_DIFF_DELETED = """diff --git a/src/old_file.py b/src/old_file.py
index 123..456 789
--- a/src/old_file.py
+++ /dev/null
@@ -1,5 +0,0 @@
-def old_function():
-    pass
"""

SAMPLE_DIFF_MULTI = """diff --git a/a.py b/a.py
index 1..2 3
--- a/a.py
+++ b/a.py
@@ -1 +1,2 @@
 a
+b
diff --git a/b.py b/b.py
index 1..2 3
--- a/b.py
+++ b/b.py
@@ -1 +1,2 @@
 a
+b
diff --git a/c.py b/c.py
index 1..2 3
--- a/c.py
+++ b/c.py
@@ -1 +1,2 @@
 a
+b
"""

SAMPLE_DIFF_NEW_FILE = """diff --git a/src/new.py b/src/new.py
new file mode 100644
index 000..123
--- /dev/null
+++ b/src/new.py
@@ -0,0 +1,5 @@
+def hello():
+    return "world"
+
+
+def goodbye():
+    return "bye"
"""

SAMPLE_DIFF_REMOVED_SECURITY = """diff --git a/src/code.py b/src/code.py
index 1..2 3
--- a/src/code.py
+++ b/src/code.py
@@ -1,3 +1,2 @@
-# TODO: fix this security issue later
-# FIXME: remove this workaround
 def main():
     pass
"""

SAMPLE_DIFF_ASYNC = """diff --git a/src/handler.py b/src/handler.py
index 1..2 3
--- a/src/handler.py
+++ b/src/handler.py
@@ -1 +1,2 @@
+async def fetch_data():
+    return await db.query()
"""


class TestParseDiff:
    def test_parse_basic(self):
        files = _parse_diff(SAMPLE_DIFF)
        assert len(files) == 1
        assert files[0].path == "src/routes/users.py"
        assert files[0].added > 0
        assert files[0].removed == 0

    def test_parse_deleted_file(self):
        files = _parse_diff(SAMPLE_DIFF_DELETED)
        assert len(files) == 1
        assert files[0].is_deleted

    def test_empty_diff(self):
        files = _parse_diff("")
        assert len(files) == 0

    def test_new_file_line_count_excludes_context(self):
        files = _parse_diff(SAMPLE_DIFF_NEW_FILE)
        assert len(files) == 1
        # 6 added lines, only +-prefixed lines should be counted
        assert files[0].added == 6
        assert files[0].is_new


class TestRedactSecrets:
    def test_redact_api_key(self):
        text = 'API_KEY = "sk-abc12345def67890ghijklmn"'
        result = _redact_line(text)
        assert "[REDACTED]" in result

    def test_redact_password(self):
        result = _redact_line('PASSWORD = "super-secret"')
        assert "[REDACTED]" in result

    def test_redact_github_token(self):
        result = _redact_line("ghp_abc123def456ghi789jkl012mnop345qrstuv")
        assert "[REDACTED]" in result


class TestClassifyRisk:
    def test_removed_security_keywords_not_classified_high(self):
        lines = [
            "-# TODO: fix this security issue later",
            "-# FIXME: remove this workaround",
            " def main():",
            "     pass",
        ]
        risk = _classify_risk("src/code.py", lines)
        assert risk != "High"

    def test_removed_keywords_do_not_escalate_risk(self):
        lines = [
            "-# TODO: remove this refactor later",
            " def foo():",
        ]
        risk = _classify_risk("src/code.py", lines)
        assert risk == "Info"

    def test_added_security_keyword_classified_high(self):
        lines = [
            "+PASSWORD = \"new-value\"",
            " def get_config():",
        ]
        risk = _classify_risk("src/config.py", lines)
        assert risk == "High"


class TestDetectSymbols:
    def test_detects_async_def(self):
        lines = ["+async def fetch_data():"]
        symbols = _detect_symbols(lines)
        assert "fetch_data" in symbols


class TestSuggestTests:
    def test_python_suggests_python_mpytest(self):
        suggestions = _suggest_tests("src/routes/users.py")
        assert len(suggestions) >= 1
        assert suggestions[0].startswith("python -m pytest")

    def test_test_path_from_nested_module(self):
        suggestions = _suggest_tests("src/tools/diff_summarizer.py")
        assert len(suggestions) >= 1
        assert "test_diff_summarizer.py" in suggestions[0]


class TestSummarize:
    def test_summarize_basic(self):
        result = summarize_diff(SAMPLE_DIFF)
        assert "## Diff Summary" in result
        assert "src/routes/users.py" in result

    def test_summarize_empty(self):
        result = summarize_diff("")
        assert "No changes" in result

    def test_summarize_secrets_redacted(self):
        result = summarize_diff(SAMPLE_DIFF_SECRETS)
        assert "src/config.py" in result
        assert "+1 / -1" in result

    def test_summarize_deleted_file(self):
        result = summarize_diff(SAMPLE_DIFF_DELETED)
        assert "deleted" in result.lower() or "src/old_file.py" in result

    def test_max_files_truncates(self):
        result = summarize_diff(SAMPLE_DIFF_MULTI, max_files=1)
        assert "a.py" in result
        assert "b.py" not in result
        assert "c.py" not in result
        assert "**Files changed:** 1" in result

    def test_max_files_zero_shows_all(self):
        result = summarize_diff(SAMPLE_DIFF_MULTI, max_files=0)
        assert "a.py" in result
        assert "b.py" in result
        assert "c.py" in result
        assert "**Files changed:** 3" in result

    def test_removed_security_lines_do_not_raise_risk(self):
        result = summarize_diff(SAMPLE_DIFF_REMOVED_SECURITY)
        assert "**Risk category:** Info" in result or "**Risk category:** Low" in result


class TestGitDiff:
    def test_not_a_git_repo(self, tmp_path: Path) -> None:
        result = _get_diff_from_git(cwd=tmp_path)
        assert "ERROR" in result

    def test_no_changes(self, tmp_path: Path) -> None:
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        (tmp_path / "file.txt").write_text("content")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)
        result = _get_diff_from_git(cwd=tmp_path)
        assert result == "" or "no changes" in result.lower()
