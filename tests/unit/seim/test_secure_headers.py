"""Guardrails for clickjacking / referrer / MIME sniffing headers."""

from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, override_settings

REPO_ROOT = Path(__file__).resolve().parents[3]
NGINX_CONF = REPO_ROOT / "nginx" / "nginx.conf"


class TestSecureHeaderSettings(SimpleTestCase):
    def test_base_frame_and_nosniff_defaults(self):
        self.assertEqual(settings.X_FRAME_OPTIONS, "DENY")
        self.assertTrue(settings.SECURE_CONTENT_TYPE_NOSNIFF)
        self.assertEqual(
            settings.SECURE_REFERRER_POLICY, "strict-origin-when-cross-origin"
        )

    @override_settings(
        SECURE_HSTS_SECONDS=31536000,
        SECURE_HSTS_INCLUDE_SUBDOMAINS=True,
        SECURE_HSTS_PRELOAD=True,
        SECURE_SSL_REDIRECT=True,
    )
    def test_production_style_hsts_flags(self):
        self.assertGreaterEqual(settings.SECURE_HSTS_SECONDS, 31536000)
        self.assertTrue(settings.SECURE_HSTS_INCLUDE_SUBDOMAINS)
        self.assertTrue(settings.SECURE_HSTS_PRELOAD)
        self.assertTrue(settings.SECURE_SSL_REDIRECT)


class TestNginxSecurityHeaders(SimpleTestCase):
    def test_nginx_conf_aligns_with_django_frame_options(self):
        text = NGINX_CONF.read_text(encoding="utf-8")
        self.assertIn('add_header X-Frame-Options "DENY" always;', text)
        self.assertNotIn('add_header X-Frame-Options "SAMEORIGIN"', text)
        self.assertIn(
            'add_header Referrer-Policy "strict-origin-when-cross-origin" always;',
            text,
        )
        self.assertIn('add_header X-Content-Type-Options "nosniff" always;', text)
