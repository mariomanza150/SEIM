"""Codecov CI fail-closed helper."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from django.test import SimpleTestCase

from tests.unit.test_institution_branding import _load_script


class CheckCodecovCiTests(SimpleTestCase):
    def setUp(self):
        self.mod = _load_script("check_codecov_ci.py")

    def test_local_run_skips_gate(self):
        env = {"CODECOV_TOKEN": "", "GITHUB_ACTIONS": ""}
        with mock.patch.dict(os.environ, env, clear=False):
            os.environ.pop("GITHUB_ACTIONS", None)
            os.environ.pop("CODECOV_TOKEN", None)
            self.assertEqual(self.mod.main([]), 0)

    def test_ci_missing_token_fails(self):
        env = {
            "GITHUB_ACTIONS": "true",
            "CODECOV_TOKEN": "",
            "CODECOV_SKIP_FORK": "",
        }
        with mock.patch.dict(os.environ, env, clear=False):
            self.assertEqual(self.mod.main(["--coverage-file", "missing.xml"]), 1)

    def test_ci_with_token_and_coverage_passes(self):
        with TemporaryDirectory() as raw:
            report = Path(raw) / "coverage.xml"
            report.write_text("<coverage/>", encoding="utf-8")
            env = {
                "GITHUB_ACTIONS": "true",
                "CODECOV_TOKEN": "not-a-real-token",
                "CODECOV_SKIP_FORK": "",
            }
            with mock.patch.dict(os.environ, env, clear=False):
                self.assertEqual(
                    self.mod.main(["--coverage-file", str(report)]),
                    0,
                )

    def test_fork_pr_skips_token_but_requires_coverage(self):
        env = {
            "GITHUB_ACTIONS": "true",
            "CODECOV_TOKEN": "",
            "CODECOV_SKIP_FORK": "true",
        }
        with mock.patch.dict(os.environ, env, clear=False):
            self.assertEqual(self.mod.main(["--coverage-file", "missing.xml"]), 1)
            self.assertEqual(self.mod.main([]), 0)
