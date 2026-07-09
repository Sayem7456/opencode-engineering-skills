"""Tests for tools/context_compressor.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.context_compressor import compress_text


LONG_LOG = """INFO 2024-01-15 Starting service
INFO 2024-01-15 Starting service
INFO 2024-01-15 Starting service
INFO 2024-01-15 Starting service
INFO 2024-01-15 Starting service
INFO 2024-01-15 Loading config
INFO 2024-01-15 Loading config
INFO 2024-01-15 Connecting to database
ERROR 2024-01-15 Connection refused: DB_HOST=localhost DB_PORT=5432
  File "src/services/db.py", line 42, in connect
    return psycopg2.connect(**config)
ValueError: timeout expired
INFO 2024-01-15 Retrying in 5s
INFO 2024-01-15 Retrying in 5s
INFO 2024-01-15 Retrying in 5s
"""


MIXED_TEXT = """The assignment scoring endpoint returned a ServerError.

File "/app/src/routes/assignments.py", line 88, in grade_assignment
    result = scoring.calculate(points)
RuntimeError: score must be between 0 and 100

I ran:
pytest tests/test_assignments.py -q

And got:
FAILED test_grade_assignment_invalid_score

The db table "assignments" has a "score" column that allows NULL values.
The score migration 002_add_score_column was applied last week.
Uncertain about why NULL is not handled.

Maybe the scoring.calculate function doesn't handle None.
"""


STANDARD_ERROR = """Traceback (most recent call last):
  File "src/main.py", line 25, in <module>
    app.run()
  File "src/services/app.py", line 88, in run
    result = process(data)
  File "src/services/app.py", line 55, in process
    raise ValueError("invalid input")
ValueError: invalid input
"""

STANDARD_LINE = STANDARD_ERROR


class TestCompressor:
    def test_empty_input(self):
        result = compress_text("")
        assert result == ""

    def test_short_text_unchanged(self):
        text = "Hello world"
        result = compress_text(text, max_lines=60)
        assert result == text

    def test_exact_max_lines(self):
        lines = [f"line {i}" for i in range(5)]
        text = "\n".join(lines)
        result = compress_text(text, max_lines=5)
        assert result == text

    def test_errors_preserved(self):
        result = compress_text(STANDARD_ERROR)
        assert "ValueError" in result
        assert "invalid input" in result

    def test_paths_preserved(self):
        result = compress_text(MIXED_TEXT)
        assert "src/routes/assignments.py" in result
        assert "88" in result

    def test_commands_preserved(self):
        result = compress_text(MIXED_TEXT)
        assert "pytest tests/test_assignments.py -q" in result

    def test_test_results_preserved(self):
        result = compress_text(MIXED_TEXT)
        assert "FAILED" in result or "FAILURES" in result

    def test_http_routes(self):
        text = "POST /api/v1/assignments returned 500"
        result = compress_text(text)
        assert "POST" in result

    def test_schema_migration(self):
        text = "The migration 002_add_score_column was created."
        result = compress_text(text)
        assert "migration" in result.lower()

    def test_log_repeated_lines(self):
        result = compress_text(LONG_LOG)
        assert "Starting service" in result

    def test_uncertainty_preserved(self):
        text = "I am not sure why this fails. Maybe the query is wrong."
        result = compress_text(text)
        assert "not sure" in result

    def test_env_vars_redacted(self):
        text = "DB_HOST=localhost DB_PORT=5432"
        result = compress_text(text)
        assert "DB_HOST" in result
        assert "DB_PORT" in result

    def test_output_format(self):
        result = compress_text(MIXED_TEXT, max_lines=10)
        assert "# Compressed Context" in result or "Original" in result

    def test_max_lines_truncation(self):
        many_lines = "\n".join(f"line {i}" for i in range(100))
        result = compress_text(many_lines, max_lines=20)
        assert len(result.splitlines()) <= 25

    def test_only_errors_returns_full(self):
        error_text = "RuntimeError: critical failure"
        result = compress_text(error_text)
        assert "RuntimeError" in result