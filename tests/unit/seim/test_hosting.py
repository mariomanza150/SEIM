"""Tests for production host / Tailscale / Cloudflare origin helpers."""

from seim.settings.hosting import (
    CLOUDFLARE_CSRF_ORIGINS,
    CLOUDFLARE_HOST_SUFFIXES,
    TAILSCALE_CSRF_ORIGINS,
    TAILSCALE_HOST_SUFFIX,
    allowed_hosts_with_tailscale,
    csrf_origins_with_cloudflare,
    csrf_origins_with_tailscale,
    csrf_origins_with_tls_proxies,
    merge_unique,
    public_base_url_parts,
)


def test_merge_unique_preserves_order_and_skips_duplicates():
    assert merge_unique(["a", "b"], ["b", "c"]) == ["a", "b", "c"]


def test_allowed_hosts_with_tailscale_appends_suffix():
    hosts = allowed_hosts_with_tailscale(["localhost"])
    assert hosts[0] == "localhost"
    assert TAILSCALE_HOST_SUFFIX in hosts
    for suffix in CLOUDFLARE_HOST_SUFFIXES:
        assert suffix in hosts


def test_allowed_hosts_allow_any_replaces_list():
    assert allowed_hosts_with_tailscale(["localhost"], allow_any=True) == ["*"]


def test_csrf_origins_with_tailscale_includes_https_wildcard():
    origins = csrf_origins_with_tailscale(["http://localhost:8020"])
    assert "http://localhost:8020" in origins
    for extra in TAILSCALE_CSRF_ORIGINS:
        assert extra in origins


def test_csrf_origins_with_cloudflare_includes_trycloudflare():
    origins = csrf_origins_with_cloudflare(["http://localhost:8020"])
    for extra in CLOUDFLARE_CSRF_ORIGINS:
        assert extra in origins


def test_csrf_origins_with_tls_proxies_includes_tailscale_and_cloudflare():
    origins = csrf_origins_with_tls_proxies(["http://localhost:8020"])
    for extra in (*TAILSCALE_CSRF_ORIGINS, *CLOUDFLARE_CSRF_ORIGINS):
        assert extra in origins


def test_public_base_url_parts_parses_https_origin():
    assert public_base_url_parts("https://oem.tailnet.ts.net") == (
        "oem.tailnet.ts.net",
        None,
        True,
    )


def test_public_base_url_parts_rejects_empty():
    assert public_base_url_parts("") is None
