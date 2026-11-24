"""Tests for production host / Tailscale / Cloudflare origin helpers."""

import pytest
from django.core.exceptions import ImproperlyConfigured

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
    parse_allowed_hosts_csv,
    public_base_url_parts,
    resolve_production_allowed_hosts,
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
    # Helper still supports allow_any for tests; production settings never call it.
    assert allowed_hosts_with_tailscale(["localhost"], allow_any=True) == ["*"]


def test_parse_allowed_hosts_csv_strips_and_skips_empty():
    assert parse_allowed_hosts_csv(" example.com , ,www.example.com ") == [
        "example.com",
        "www.example.com",
    ]
    assert parse_allowed_hosts_csv("") == []
    assert parse_allowed_hosts_csv(None) == []


def test_resolve_production_allowed_hosts_prefers_django_allowed_hosts():
    hosts = resolve_production_allowed_hosts(
        environ={
            "DJANGO_ALLOWED_HOSTS": "example.com,api.example.com",
            "ALLOWED_HOSTS": "legacy.example.com",
        }
    )
    assert hosts == ["example.com", "api.example.com"]


def test_resolve_production_allowed_hosts_falls_back_to_legacy_allowed_hosts():
    hosts = resolve_production_allowed_hosts(
        environ={"ALLOWED_HOSTS": "legacy.example.com,.ts.net"}
    )
    assert hosts == ["legacy.example.com", ".ts.net"]


def test_resolve_production_allowed_hosts_merges_tls_proxy_suffixes():
    hosts = resolve_production_allowed_hosts(
        environ={"DJANGO_ALLOWED_HOSTS": "example.com"},
        use_tls_proxy=True,
    )
    assert "example.com" in hosts
    assert TAILSCALE_HOST_SUFFIX in hosts
    for suffix in CLOUDFLARE_HOST_SUFFIXES:
        assert suffix in hosts


def test_resolve_production_allowed_hosts_fails_closed_when_unset():
    with pytest.raises(ImproperlyConfigured, match="DJANGO_ALLOWED_HOSTS"):
        resolve_production_allowed_hosts(environ={})


def test_resolve_production_allowed_hosts_rejects_wildcard():
    with pytest.raises(ImproperlyConfigured, match="must not contain"):
        resolve_production_allowed_hosts(environ={"DJANGO_ALLOWED_HOSTS": "*"})
    with pytest.raises(ImproperlyConfigured, match="must not contain"):
        resolve_production_allowed_hosts(
            environ={"DJANGO_ALLOWED_HOSTS": "example.com,*"}
        )


def test_resolve_production_allowed_hosts_ignores_allow_any_host_env():
    # ALLOW_ANY_HOST must not widen the list or unlock "*".
    hosts = resolve_production_allowed_hosts(
        environ={
            "DJANGO_ALLOWED_HOSTS": "example.com",
            "ALLOW_ANY_HOST": "1",
        }
    )
    assert hosts == ["example.com"]
    with pytest.raises(ImproperlyConfigured):
        resolve_production_allowed_hosts(
            environ={"ALLOW_ANY_HOST": "1", "DJANGO_ALLOWED_HOSTS": "*"}
        )


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
