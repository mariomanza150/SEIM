"""WhiteNoise Cache-Control overrides for HTML entry documents."""

from core.static_headers import whitenoise_add_headers


class _Headers(dict):
    """Minimal stand-in for wsgiref.headers.Headers (dict-like)."""


def test_html_path_gets_no_cache():
    headers = _Headers({"Cache-Control": "max-age=60, public"})
    whitenoise_add_headers(headers, "/app/staticfiles/index.html", "/static/index.html")
    assert headers["Cache-Control"] == "no-cache, no-store, must-revalidate"


def test_html_url_alone_gets_no_cache():
    headers = _Headers({"Cache-Control": "max-age=60, public"})
    whitenoise_add_headers(headers, "/tmp/something", "/static/offline.html")
    assert headers["Cache-Control"] == "no-cache, no-store, must-revalidate"


def test_hashed_js_keeps_existing_cache_control():
    headers = _Headers({"Cache-Control": "max-age=315360000, public, immutable"})
    whitenoise_add_headers(
        headers,
        "/app/staticfiles/assets/AppShell-abc123.js",
        "/static/assets/AppShell-abc123.js",
    )
    assert headers["Cache-Control"] == "max-age=315360000, public, immutable"


def test_css_and_other_assets_unchanged():
    headers = _Headers({"Cache-Control": "max-age=60, public"})
    whitenoise_add_headers(headers, "/app/staticfiles/css/app.css", "/static/css/app.css")
    assert headers["Cache-Control"] == "max-age=60, public"


def test_whitenoise_setting_points_at_helper():
    from django.conf import settings

    assert settings.WHITENOISE_ADD_HEADERS_FUNCTION is whitenoise_add_headers
