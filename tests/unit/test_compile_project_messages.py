"""Regression tests for pytest gettext catalog bootstrap."""

from pathlib import Path
from unittest.mock import patch

from tests.conftest import compile_project_messages


def test_compile_project_messages_succeeds_when_msgfmt_available():
    ok, detail = compile_project_messages()
    assert ok is True, detail
    root = Path(__file__).resolve().parents[2]
    for lang in ("de", "es", "fr"):
        assert (root / "locale" / lang / "LC_MESSAGES" / "django.mo").is_file()


def test_compile_project_messages_reports_missing_msgfmt():
    with patch("shutil.which", return_value=None):
        ok, detail = compile_project_messages()
    assert ok is False
    assert "msgfmt" in detail
