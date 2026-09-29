"""Helpers for LAN / Tailscale / Cloudflare Tunnel hosts when production settings are used locally."""

from __future__ import annotations

from urllib.parse import urlsplit

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


def merge_unique(existing: list[str], extra: list[str] | tuple[str, ...]) -> list[str]:
    """Preserve order while appending values that are not already present."""
    merged = list(existing)
    seen = set(merged)
    for item in extra:
        if item and item not in seen:
            merged.append(item)
            seen.add(item)
    return merged


def allowed_hosts_with_tailscale(hosts: list[str], *, allow_any: bool = False) -> list[str]:
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
