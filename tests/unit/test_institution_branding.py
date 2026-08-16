"""Institution branding settings, tokens, and template context."""

import importlib.util
import json
from pathlib import Path

from django.test import SimpleTestCase, override_settings

from core.branding import (
    DEFAULT_INSTITUTION,
    apply_institution_tokens,
    brand_from_config,
    load_json_object,
    merge_institution_config,
    resolve_institution_slug,
)
from core.context_processors import institution


def _load_script(name: str):
    path = Path(__file__).resolve().parents[2] / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _check_python_deps_main():
    return _load_script("check_python_deps.py").main


class InstitutionBrandingTests(SimpleTestCase):
    def test_defaults_are_uadec_example_theme(self):
        from django.conf import settings

        self.assertEqual(settings.INSTITUTION_SHORT_NAME, "UAdeC")
        self.assertIn("Coahuila", settings.INSTITUTION_NAME)
        self.assertEqual(settings.INSTITUTION_THEME["primary"], "#2E5090")
        self.assertEqual(settings.INSTITUTION_THEME_CSS, "uadec/theme.css")

    @override_settings(
        INSTITUTION_SHORT_NAME="ExampleU",
        INSTITUTION_NAME="Example University",
        INSTITUTION_TAGLINE="Mobility",
        INSTITUTION_NAV_BRAND="",
        INSTITUTION_THEME={"primary": "#111111"},
        INSTITUTION_THEME_CSS="exampleu/theme.css",
    )
    def test_context_processor_reads_settings(self):
        ctx = institution(None)
        self.assertEqual(ctx["institution"]["short_name"], "ExampleU")
        self.assertEqual(ctx["institution"]["name"], "Example University")
        self.assertEqual(ctx["institution"]["nav_brand"], "ExampleU Mobility")
        self.assertEqual(ctx["institution"]["theme"]["primary"], "#111111")
        self.assertEqual(ctx["institution"]["theme_css"], "exampleu/theme.css")

    def test_apply_institution_tokens_replaces_uadec_copy(self):
        brand = brand_from_config(
            {
                **DEFAULT_INSTITUTION,
                "INSTITUTION_NAME": "Example University",
                "INSTITUTION_SHORT_NAME": "ExampleU",
                "INSTITUTION_EMAIL": "exchange@example.edu",
            }
        )
        text = apply_institution_tokens(
            "Estudiante de la Universidad Autónoma de Coahuila (UAdeC) "
            "contacte intercambio@uadec.edu.mx",
            brand,
        )
        self.assertIn("Example University", text)
        self.assertIn("ExampleU", text)
        self.assertIn("exchange@example.edu", text)
        self.assertNotIn("UAdeC", text)
        self.assertNotIn("uadec.edu.mx", text)

        letterhead = apply_institution_tokens(
            "UNIVERSIDAD AUTÓNOMA DE COAHUILA",
            brand,
        )
        self.assertEqual(letterhead, "EXAMPLE UNIVERSITY")

    def test_merge_institution_config_reads_override_file(self, tmp_path=None):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw:
            base = Path(raw)
            override = base / "institution.json"
            override.write_text(
                json.dumps({"INSTITUTION_SHORT_NAME": "OverrideU"}),
                encoding="utf-8",
            )
            merged = merge_institution_config(base, override)
            self.assertEqual(merged["INSTITUTION_SHORT_NAME"], "OverrideU")
            self.assertEqual(
                merged["INSTITUTION_NAME"], DEFAULT_INSTITUTION["INSTITUTION_NAME"]
            )

    def test_load_json_object_missing_or_invalid(self):
        self.assertEqual(load_json_object(None), {})
        self.assertEqual(load_json_object(Path("definitely-missing.json")), {})

    def test_runtime_requirements_are_wired_in_pyproject(self):
        self.assertEqual(_check_python_deps_main()(), 0)

    def test_resolve_slug_reads_override_file(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw:
            base = Path(raw)
            override = base / "institution.json"
            override.write_text(
                '{"INSTITUTION_SLUG": "exampleu"}',
                encoding="utf-8",
            )
            self.assertEqual(resolve_institution_slug(base, override), "exampleu")

    def test_merge_loads_pack_for_slug(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw:
            base = Path(raw)
            pack = base / "branding" / "exampleu"
            pack.mkdir(parents=True)
            (pack / "config.json").write_text(
                '{"INSTITUTION_SLUG": "exampleu", "INSTITUTION_SHORT_NAME": "ExampleU"}',
                encoding="utf-8",
            )
            override = base / "institution.json"
            override.write_text(
                '{"INSTITUTION_SLUG": "exampleu"}',
                encoding="utf-8",
            )
            merged = merge_institution_config(base, override)
            self.assertEqual(merged["INSTITUTION_SLUG"], "exampleu")
            self.assertEqual(merged["INSTITUTION_SHORT_NAME"], "ExampleU")

    def test_tenant_config_json_overrides_institution_overlay(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw:
            base = Path(raw)
            (base / "branding").mkdir()
            (base / "institution.json").write_text(
                '{"INSTITUTION_SHORT_NAME": "OverlayU"}',
                encoding="utf-8",
            )
            (base / "tenant_config.json").write_text(
                '{"INSTITUTION_SLUG": "exampleu", "INSTITUTION_SHORT_NAME": "TenantU",'
                ' "INSTITUTION_WEBSITE": "https://www.example.edu/"}',
                encoding="utf-8",
            )
            merged = merge_institution_config(base, base / "institution.json")
            self.assertEqual(merged["INSTITUTION_SLUG"], "exampleu")
            self.assertEqual(merged["INSTITUTION_SHORT_NAME"], "TenantU")
            self.assertEqual(merged["INSTITUTION_WEBSITE"], "https://www.example.edu/")
            self.assertEqual(
                merged["INSTITUTION_NAME"], DEFAULT_INSTITUTION["INSTITUTION_NAME"]
            )

    def test_download_config_uses_branding_slug(self):
        module = _load_script("download_institution_assets.py")
        config = module.load_asset_config(Path(__file__).resolve().parents[2])
        self.assertEqual(config["slug"], "uadec")
        self.assertIn("branding/uadec/logos", config["asset_dir"].replace("\\", "/"))
        self.assertTrue(config["website"].startswith("http"))
