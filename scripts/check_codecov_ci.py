#!/usr/bin/env python
"""Fail closed in GitHub Actions when Codecov is not configured.

Local runs always succeed so developers can test without a token.
Same-repo CI must set the GitHub Actions secret CODECOV_TOKEN and produce
the listed coverage files. Fork PRs skip the token requirement because
GitHub does not expose secrets to workflows from forks.

    python scripts/check_codecov_ci.py --coverage-file coverage.xml
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def in_github_actions() -> bool:
    return _truthy(os.environ.get("GITHUB_ACTIONS"))


def skip_token_for_fork() -> bool:
    return _truthy(os.environ.get("CODECOV_SKIP_FORK"))


def check(
    *,
    token: str,
    coverage_files: list[str],
    require_token: bool,
) -> list[str]:
    errors: list[str] = []
    if require_token and not (token or "").strip():
        errors.append(
            "CODECOV_TOKEN is required in CI. Add the GitHub Actions secret "
            "under Settings → Secrets and variables → Actions. "
            "See .github/README.md. Do not commit a real token."
        )
    missing = [name for name in coverage_files if name and not Path(name).is_file()]
    if missing:
        errors.append("Coverage report not generated: " + ", ".join(missing))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--coverage-file",
        action="append",
        default=[],
        dest="coverage_files",
        help="Coverage artifact that must exist (repeatable).",
    )
    parser.add_argument(
        "--require-token",
        action="store_true",
        help="Require CODECOV_TOKEN even outside GitHub Actions (tests).",
    )
    args = parser.parse_args([] if argv is None else argv)

    token = os.environ.get("CODECOV_TOKEN", "")
    running_in_ci = in_github_actions()
    require_token = args.require_token or (running_in_ci and not skip_token_for_fork())

    if not running_in_ci and not args.require_token:
        print("OK: local run; Codecov token/coverage gate skipped.")
        return 0

    errors = check(
        token=token,
        coverage_files=args.coverage_files,
        require_token=require_token,
    )
    if errors:
        print("Codecov CI check failed:")
        for item in errors:
            print(f"  - {item}")
        return 1

    if require_token:
        print("OK: CODECOV_TOKEN is set and coverage artifacts are present.")
    else:
        print("OK: fork PR; token not required. Coverage artifacts checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
