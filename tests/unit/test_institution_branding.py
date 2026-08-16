"""Institution branding settings and template context."""

import importlib.util
from pathlib import Path

from django.test import SimpleTestCase, override_settings

from core.context_processors import institution


def _check_python_deps_main():
    path = Path(__file__).resolve().parents[2] / "scripts" / "check_python_deps.py"
    spec = importlib.util.spec_from_file_location("check_python_deps", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.main


class InstitutionBrandingTests(SimpleTestCase):
    def test_defaults_are_uadec_example_theme(self):
        from django.conf import settings

        self.assertEqual(settings.INSTITUTION_SHORT_NAME, "UAdeC")
        self.assertIn("Coahuila", settings.INSTITUTION_NAME)
        self.assertEqual(settings.INSTITUTION_THEME["primary"], "#2E5090")

    @override_settings(
        INSTITUTION_SHORT_NAME="ExampleU",
        INSTITUTION_NAME="Example University",
        INSTITUTION_TAGLINE="Mobility",
        INSTITUTION_NAV_BRAND="",
        INSTITUTION_THEME={"primary": "#111111"},
    )
    def test_context_processor_reads_settings(self):
        ctx = institution(None)
        self.assertEqual(ctx["institution"]["short_name"], "ExampleU")
        self.assertEqual(ctx["institution"]["name"], "Example University")
        self.assertEqual(ctx["institution"]["nav_brand"], "ExampleU Mobility")
        self.assertEqual(ctx["institution"]["theme"]["primary"], "#111111")

    def test_runtime_requirements_are_wired_in_pyproject(self):
        self.assertEqual(_check_python_deps_main()(), 0)
