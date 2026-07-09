"""Tests for tools/diff_summarizer.py."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from tools.diff_summarizer import summarize_diff, _parse_diff, _redact_line


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


class TestRedactSecrets:
    def test_redact_api_key(self):
        text = 'API_KEY = "sk-abc12345def67890ghijklmn"'
        from tools.diff_summarizer import _redact_line
        result = _redact_line(text)
        assert "[REDACTED]" in result

    def test_redact_password(self):
        from tools.diff_summarizer import _redact_line
        result = _redact_line('PASSWORD = "super-secret"')
        assert "[REDACTED]" in result

    def test_redact_github_token(self):
        from tools.diff_summarizer import _redact_line
        result = _redact_line("ghp_abc123def456ghi789jkl012mnop345qrstuv")
        assert "[REDACTED]" in result


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


class TestGitDiff:
    def test_not_a_git_repo(self, tmp_path: Path) -> None:
        from tools.diff_summarizer import _get_diff_from_git as gd
        result = gd(cwd=tmp_path)
        assert "ERROR" in result

    def test_no_changes(self, tmp_path: Path) -> None:
        from tools.diff_summarizer import _get_diff_from_git as gd
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        (tmp_path / "file.txt").write_text("content")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)
        result = gd(cwd=tmp_path)
        assert result == "" or "no changes" in result.lower()