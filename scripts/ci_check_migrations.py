#!/usr/bin/env python
"""CI gate: model state matches migrations, and *new* schema changes stay safe.

Runs:

1. ``manage.py makemigrations --check --dry-run`` — fails if model changes lack a migration.
2. ``django-migration-linter`` on first-party apps for migrations introduced since
   the comparison commit (PR base / push ``before`` / ``origin/main``). Historical
   migrations are not re-litigated; new ones must follow expand/contract.

Escape hatch: a pull request labeled ``contract-migration`` may land a deliberate
contract (breaking) step. Process: ``docs/migrations.md``.

    python scripts/ci_check_migrations.py
    python scripts/ci_check_migrations.py --allow-contract
    python scripts/ci_check_migrations.py --git-commit-id abc1234
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

CONTRACT_LABEL = "contract-migration"
REPO_ROOT = Path(__file__).resolve().parents[1]

# First-party apps we own. Third-party package migrations (taggit, JWT blacklist,
# Wagtail, …) are excluded — we cannot rewrite their history.
INCLUDE_APPS = (
    "accounts",
    "analytics",
    "application_forms",
    "cms",
    "core",
    "data_management",
    "documents",
    "exchange",
    "grades",
    "internacional",
    "notifications",
    "qa",
    "toefl",
    "workflows",
)


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def pr_labels_from_event(event_path: str | None) -> set[str]:
    """Return lowercase label names from a GitHub Actions event payload."""
    if not event_path:
        return set()
    path = Path(event_path)
    if not path.is_file():
        return set()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    pr = payload.get("pull_request") or {}
    labels = pr.get("labels") or []
    names: set[str] = set()
    for label in labels:
        if isinstance(label, dict):
            name = label.get("name")
            if isinstance(name, str) and name.strip():
                names.add(name.strip().lower())
        elif isinstance(label, str) and label.strip():
            names.add(label.strip().lower())
    return names


def has_contract_label(
    *,
    event_path: str | None = None,
    allow_contract: bool = False,
) -> bool:
    if allow_contract:
        return True
    labels = pr_labels_from_event(event_path)
    return CONTRACT_LABEL.lower() in labels


def _git_rev_parse(*args: str) -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", *args],
            cwd=REPO_ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    sha = out.strip()
    return sha or None


def _is_null_sha(sha: str | None) -> bool:
    return not sha or set(sha) <= {"0"}


def resolve_git_commit_id(explicit: str | None) -> str | None:
    """Commit to pass as ``--git-commit-id`` (lint migrations after this point).

    Preference order:
    1. Explicit CLI / ``SEIM_MIGRATION_LINTER_BASE``
    2. ``GITHUB_BASE_SHA`` (set by workflow for PRs)
    3. ``github.event.before`` via ``GITHUB_EVENT_BEFORE`` (push)
    4. Merge-base with ``origin/main`` or ``main``
    """
    if explicit and not _is_null_sha(explicit):
        return explicit.strip()
    env_base = os.environ.get("SEIM_MIGRATION_LINTER_BASE", "").strip()
    if env_base and not _is_null_sha(env_base):
        return env_base
    for key in ("GITHUB_BASE_SHA", "GITHUB_EVENT_BEFORE"):
        val = (os.environ.get(key) or "").strip()
        if val and not _is_null_sha(val):
            return val
    for ref in ("origin/main", "main", "origin/master", "master"):
        base = _git_rev_parse(ref)
        if not base:
            continue
        # Prefer merge-base so PR branches only lint their delta.
        head = _git_rev_parse("HEAD")
        if head:
            try:
                mb = subprocess.check_output(
                    ["git", "merge-base", base, head],
                    cwd=REPO_ROOT,
                    stderr=subprocess.DEVNULL,
                    text=True,
                ).strip()
                if mb:
                    return mb
            except (OSError, subprocess.CalledProcessError):
                return base
        return base
    return None


def run_makemigrations_check() -> int:
    cmd = [
        sys.executable,
        "manage.py",
        "makemigrations",
        "--check",
        "--dry-run",
    ]
    print("+", " ".join(cmd), flush=True)
    return subprocess.call(cmd, cwd=REPO_ROOT)


def run_migration_linter(*, git_commit_id: str | None) -> int:
    cmd = [
        sys.executable,
        "manage.py",
        "lintmigrations",
        "--no-cache",
        "--quiet",
        "ok",
        "ignore",
        "--include-apps",
        *INCLUDE_APPS,
    ]
    if git_commit_id:
        cmd.extend(["--git-commit-id", git_commit_id])
        print(f"# linting first-party migrations since {git_commit_id}", flush=True)
    else:
        print(
            "::warning::No comparison commit found; linting all first-party "
            "migrations (may fail on historical contract ops).",
            flush=True,
        )
    print("+", " ".join(cmd), flush=True)
    return subprocess.call(cmd, cwd=REPO_ROOT)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-contract",
        action="store_true",
        help="Treat this run as if the PR had the contract-migration label.",
    )
    parser.add_argument(
        "--git-commit-id",
        default=None,
        help="Only lint migrations introduced after this commit.",
    )
    parser.add_argument(
        "--skip-makemigrations",
        action="store_true",
        help="Only run the linter (tests).",
    )
    parser.add_argument(
        "--skip-linter",
        action="store_true",
        help="Only run makemigrations --check (tests).",
    )
    args = parser.parse_args([] if argv is None else argv)

    if not args.skip_makemigrations:
        code = run_makemigrations_check()
        if code != 0:
            print(
                "::error::makemigrations --check failed. "
                "Generate migrations with `python manage.py makemigrations` "
                "and commit them.",
                flush=True,
            )
            return code

    if args.skip_linter:
        print("OK: makemigrations --check passed (linter skipped).")
        return 0

    git_commit_id = resolve_git_commit_id(args.git_commit_id)
    if git_commit_id and not _git_rev_parse("--verify", f"{git_commit_id}^{{commit}}"):
        # Shallow checkouts often lack the PR base; fetch it for git-diff linting.
        print(f"# fetching comparison commit {git_commit_id}", flush=True)
        subprocess.call(
            ["git", "fetch", "--no-tags", "--depth=1", "origin", git_commit_id],
            cwd=REPO_ROOT,
        )

    linter_code = run_migration_linter(git_commit_id=git_commit_id)
    if linter_code == 0:
        print("OK: migration linter passed.")
        return 0

    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if has_contract_label(
        event_path=event_path,
        allow_contract=args.allow_contract
        or _truthy(os.environ.get("SEIM_ALLOW_CONTRACT_MIGRATION")),
    ):
        print(
            f"::warning::django-migration-linter reported "
            f"backward-incompatible operations, but the "
            f"`{CONTRACT_LABEL}` label (or --allow-contract) is present. "
            f"Ensure this is an intentional contract phase "
            f"(see docs/migrations.md).",
            flush=True,
        )
        return 0

    print(
        "::error::django-migration-linter found backward-incompatible "
        "migration operations in new first-party migrations (or could not "
        "git-diff against the comparison commit). Prefer expand/contract "
        "(docs/migrations.md). Ensure CI checks out with fetch-depth: 0. "
        f"Only add the `{CONTRACT_LABEL}` label for a deliberate contract step "
        "that will break old app code after deploy.",
        flush=True,
    )
    return linter_code


if __name__ == "__main__":
    raise SystemExit(main())
