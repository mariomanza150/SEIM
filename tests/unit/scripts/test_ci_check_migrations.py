"""Unit tests for scripts/ci_check_migrations.py (no DB)."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "scripts" / "ci_check_migrations.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("ci_check_migrations", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mig():
    return _load_module()


def test_pr_labels_from_event_reads_names(tmp_path, mig):
    event = tmp_path / "event.json"
    event.write_text(
        json.dumps(
            {
                "pull_request": {
                    "labels": [
                        {"name": "enhancement"},
                        {"name": "contract-migration"},
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    labels = mig.pr_labels_from_event(str(event))
    assert "contract-migration" in labels
    assert "enhancement" in labels


def test_pr_labels_missing_file(mig):
    assert mig.pr_labels_from_event("/nonexistent/event.json") == set()
    assert mig.pr_labels_from_event(None) == set()


def test_has_contract_label_case_insensitive(tmp_path, mig):
    event = tmp_path / "event.json"
    event.write_text(
        json.dumps({"pull_request": {"labels": [{"name": "Contract-Migration"}]}}),
        encoding="utf-8",
    )
    assert mig.has_contract_label(event_path=str(event)) is True


def test_has_contract_label_absent(tmp_path, mig):
    event = tmp_path / "event.json"
    event.write_text(
        json.dumps({"pull_request": {"labels": [{"name": "bug"}]}}),
        encoding="utf-8",
    )
    assert mig.has_contract_label(event_path=str(event)) is False


def test_allow_contract_flag(mig):
    assert mig.has_contract_label(allow_contract=True) is True


def test_resolve_git_commit_id_explicit(mig, monkeypatch):
    monkeypatch.delenv("SEIM_MIGRATION_LINTER_BASE", raising=False)
    monkeypatch.delenv("GITHUB_BASE_SHA", raising=False)
    monkeypatch.delenv("GITHUB_EVENT_BEFORE", raising=False)
    assert mig.resolve_git_commit_id("abc123") == "abc123"
    assert mig._is_null_sha("0000000000000000000000000000000000000000") is True
    # Null SHA is ignored; fallthrough may return a merge-base or None (shallow CI).
    _ = mig.resolve_git_commit_id("0000000000000000000000000000000000000000")


def test_resolve_git_commit_id_from_env(mig, monkeypatch):
    monkeypatch.setenv("SEIM_MIGRATION_LINTER_BASE", "deadbeef")
    assert mig.resolve_git_commit_id(None) == "deadbeef"
