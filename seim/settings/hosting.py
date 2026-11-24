"""Helpers for LAN / Tailscale / Cloudflare Tunnel hosts when production settings are used locally."""

from __future__ import annotations

import os
from urllib.parse import urlsplit

from django.core.exceptions import ImproperlyConfigured

TAILSCALE_HOST_SUFFIX = ".ts.net"
TAILSCALE_CSRF_ORIGINS = ("https://*.ts.net", "http://*.ts.net")
TAILSCALE_CORS_ORIGIN_REGEX = r"^https?://[\w.-]+\.ts\.net(?::\d+)?$"

# Quick Tunnels (*.trycloudflare.com) and named tunnels (*.cfargotunnel.com).
CLOUDFLARE_HOST_SUFFIXES = (".trycloudflare.com", ".cfargotunnel.com")
CLOUDFLARE_CSRF_ORIGINS = (
    "https://*.trycloudflare.com",
    "https://*.cfargotunnel.com",
)
CLOUDFLARE_CORS_ORIGIN_REGEX = (
    r"^https://[\w.-]+\.(trycloudflare\.com|cfargotunnel\.com)(?::\d+)?$"
)

# Prefer DJANGO_ALLOWED_HOSTS; ALLOWED_HOSTS remains as a compatibility alias.
_ALLOWED_HOSTS_ENV_KEYS = ("DJANGO_ALLOWED_HOSTS", "ALLOWED_HOSTS")


def merge_unique(existing: list[str], extra: list[str] | tuple[str, ...]) -> list[str]:
    """Preserve order while appending values that are not already present."""
    merged = list(existing)
    seen = set(merged)
    for item in extra:
        if item and item not in seen:
            merged.append(item)
            seen.add(item)
    return merged


def parse_allowed_hosts_csv(raw: str | None) -> list[str]:
    """Split a comma-separated host list and drop empty segments."""
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def resolve_production_allowed_hosts(
    *,
    environ: dict[str, str] | None = None,
    use_tls_proxy: bool = False,
) -> list[str]:
    """Resolve ALLOWED_HOSTS for production-like settings.

    Reads ``DJANGO_ALLOWED_HOSTS`` (preferred) or legacy ``ALLOWED_HOSTS``.
    Fails closed when unset/empty or when ``*`` is present. Never honors
    ``ALLOW_ANY_HOST`` — that footgun is removed for production-like tiers.
    """
    env = environ if environ is not None else os.environ
    raw = ""
    for key in _ALLOWED_HOSTS_ENV_KEYS:
        value = (env.get(key) or "").strip()
        if value:
            raw = value
            break

    hosts = parse_allowed_hosts_csv(raw)
    if not hosts:
        raise ImproperlyConfigured(
            "DJANGO_ALLOWED_HOSTS must be set to a comma-separated host list "
            "when using production settings (legacy ALLOWED_HOSTS is also "
            "accepted). Wildcard '*' is not allowed."
        )
    if "*" in hosts:
        raise ImproperlyConfigured(
            "DJANGO_ALLOWED_HOSTS must not contain '*' on production-like "
            "tiers. List explicit hosts or suffixes (e.g. example.com,.ts.net)."
        )
    if use_tls_proxy:
        return allowed_hosts_with_tailscale(hosts)
    return hosts


def allowed_hosts_with_tailscale(
    hosts: list[str], *, allow_any: bool = False
) -> list[str]:
    # allow_any is retained for unit-test compatibility but must not be used
    # by production settings (see resolve_production_allowed_hosts).
    if allow_any:
        return ["*"]
    return merge_unique(hosts, [TAILSCALE_HOST_SUFFIX, *CLOUDFLARE_HOST_SUFFIXES])


def csrf_origins_with_tailscale(origins: list[str]) -> list[str]:
    return merge_unique(origins, TAILSCALE_CSRF_ORIGINS)


def csrf_origins_with_cloudflare(origins: list[str]) -> list[str]:
    return merge_unique(origins, CLOUDFLARE_CSRF_ORIGINS)


def csrf_origins_with_tls_proxies(origins: list[str]) -> list[str]:
    """CSRF origins for Tailscale Serve/Funnel and Cloudflare Tunnel terminators."""
    return csrf_origins_with_cloudflare(csrf_origins_with_tailscale(origins))


def public_base_url_parts(url: str) -> tuple[str, int | None, bool] | None:
    """Return (hostname, port, is_https) from a public origin, or None if invalid."""
    if not url:
        return None
    parsed = urlsplit(url if "://" in url else f"http://{url}")
    hostname = (parsed.hostname or "").strip()
    if not hostname:
        return None
    is_https = (parsed.scheme or "http").lower() == "https"
    return hostname, parsed.port, is_https
