"""Microsoft Graph OAuth2 helpers for personal Microsoft accounts (Hotmail/Outlook).

Uses the consumers authority and delegated Mail.Send + offline_access scopes.
Tokens are never logged. Rotated refresh tokens are persisted via Django cache
(Redis in production via django-redis).
"""

from __future__ import annotations

import logging
import time
from typing import Any

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

GRAPH_SEND_MAIL_URL = "https://graph.microsoft.com/v1.0/me/sendMail"
DEFAULT_TENANT = "consumers"
SCOPES = "offline_access Mail.Send"

CACHE_REFRESH_KEY = "ms_graph:v1:refresh_token"
CACHE_ACCESS_KEY = "ms_graph:v1:access_token"
# Refresh tokens can live a long time; keep them in cache indefinitely until rotated.
REFRESH_CACHE_TIMEOUT = None
# Safety skew when caching access tokens.
ACCESS_TOKEN_SKEW_SECONDS = 60
HTTP_TIMEOUT = 30


class MicrosoftGraphAuthError(Exception):
    """Raised when OAuth token acquisition or refresh fails."""


def _tenant() -> str:
    return getattr(settings, "MS_GRAPH_TENANT", None) or DEFAULT_TENANT


def authority_base() -> str:
    return f"https://login.microsoftonline.com/{_tenant()}"


def token_url() -> str:
    return f"{authority_base()}/oauth2/v2.0/token"


def device_code_url() -> str:
    return f"{authority_base()}/oauth2/v2.0/devicecode"


def _client_id() -> str:
    client_id = getattr(settings, "MS_GRAPH_CLIENT_ID", "") or ""
    if not client_id:
        raise ImproperlyConfigured(
            "MS_GRAPH_CLIENT_ID is required for Microsoft Graph email."
        )
    return client_id


def _optional_client_secret() -> str:
    return getattr(settings, "MS_GRAPH_CLIENT_SECRET", "") or ""


def _bootstrap_refresh_token() -> str:
    return getattr(settings, "MS_GRAPH_REFRESH_TOKEN", "") or ""


def get_refresh_token() -> str:
    """Return the active refresh token (cache preferred, then env bootstrap)."""
    cached = cache.get(CACHE_REFRESH_KEY)
    if cached:
        return str(cached)
    bootstrap = _bootstrap_refresh_token()
    if bootstrap:
        # Seed cache so subsequent rotations have a place to land.
        cache.set(CACHE_REFRESH_KEY, bootstrap, timeout=REFRESH_CACHE_TIMEOUT)
        return bootstrap
    raise ImproperlyConfigured(
        "MS_GRAPH_REFRESH_TOKEN is required (or a rotated token in cache) "
        "for Microsoft Graph email."
    )


def persist_refresh_token(refresh_token: str) -> None:
    """Persist a (possibly rotated) refresh token in Django cache. Never log it."""
    if not refresh_token:
        return
    cache.set(CACHE_REFRESH_KEY, refresh_token, timeout=REFRESH_CACHE_TIMEOUT)
    logger.info("Microsoft Graph refresh token persisted to cache")


def _cache_access_token(access_token: str, expires_in: int) -> None:
    ttl = max(int(expires_in) - ACCESS_TOKEN_SKEW_SECONDS, 60)
    cache.set(CACHE_ACCESS_KEY, access_token, timeout=ttl)


def _client_form(
    extra: dict[str, str], *, include_scope: bool = False
) -> dict[str, str]:
    data = {"client_id": _client_id(), **extra}
    if include_scope:
        data["scope"] = SCOPES
    secret = _optional_client_secret()
    if secret:
        data["client_secret"] = secret
    return data


def refresh_access_token() -> str:
    """Exchange the refresh token for a new access token; persist rotation."""
    refresh = get_refresh_token()
    try:
        response = requests.post(
            token_url(),
            data=_client_form(
                {
                    "grant_type": "refresh_token",
                    "refresh_token": refresh,
                },
                include_scope=True,
            ),
            timeout=HTTP_TIMEOUT,
        )
    except requests.RequestException as exc:
        logger.error(
            "Microsoft Graph token refresh request failed: %s", type(exc).__name__
        )
        raise MicrosoftGraphAuthError(
            "Microsoft Graph token refresh request failed"
        ) from exc

    if response.status_code != 200:
        # Never log response body — it may contain tokens or sensitive error details.
        logger.error(
            "Microsoft Graph token refresh failed (HTTP %s)",
            response.status_code,
        )
        raise MicrosoftGraphAuthError(
            f"Microsoft Graph token refresh failed (HTTP {response.status_code})"
        )

    payload = response.json()
    access_token = payload.get("access_token") or ""
    if not access_token:
        raise MicrosoftGraphAuthError(
            "Microsoft Graph token refresh returned no access_token"
        )

    expires_in = int(payload.get("expires_in") or 3600)
    _cache_access_token(access_token, expires_in)

    new_refresh = payload.get("refresh_token") or ""
    if new_refresh and new_refresh != refresh:
        persist_refresh_token(new_refresh)
        logger.info("Microsoft Graph refresh token rotated and persisted")

    return access_token


def get_access_token() -> str:
    """Return a valid access token, refreshing when the cache miss/expires."""
    cached = cache.get(CACHE_ACCESS_KEY)
    if cached:
        return str(cached)
    return refresh_access_token()


def request_device_code() -> dict[str, Any]:
    """Start the OAuth2 device code flow. Returns the device-code payload."""
    try:
        response = requests.post(
            device_code_url(),
            data=_client_form({}, include_scope=True),
            timeout=HTTP_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise MicrosoftGraphAuthError("Device code request failed") from exc

    if response.status_code != 200:
        logger.error("Device code request failed (HTTP %s)", response.status_code)
        raise MicrosoftGraphAuthError(
            f"Device code request failed (HTTP {response.status_code})"
        )
    return response.json()


def poll_device_code(
    device_code: str, interval: int = 5, expires_in: int = 900
) -> dict[str, Any]:
    """Poll the token endpoint until the user completes device-code sign-in."""
    deadline = time.time() + max(int(expires_in), 60)
    sleep_for = max(int(interval), 1)
    while time.time() < deadline:
        try:
            response = requests.post(
                token_url(),
                data=_client_form(
                    {
                        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                        "device_code": device_code,
                    }
                ),
                timeout=HTTP_TIMEOUT,
            )
        except requests.RequestException as exc:
            raise MicrosoftGraphAuthError("Device code poll failed") from exc

        payload = {}
        try:
            payload = response.json()
        except ValueError:
            payload = {}

        if response.status_code == 200 and payload.get("access_token"):
            return payload

        error = payload.get("error")
        if error in ("authorization_pending", "slow_down"):
            if error == "slow_down":
                sleep_for += 5
            time.sleep(sleep_for)
            continue

        # Do not log payload — may include sensitive fields.
        logger.error(
            "Device code poll failed (HTTP %s, error=%s)", response.status_code, error
        )
        raise MicrosoftGraphAuthError(
            f"Device code authorization failed (error={error or response.status_code})"
        )

    raise MicrosoftGraphAuthError("Device code authorization timed out")


def send_mail_payload(payload: dict[str, Any], access_token: str | None = None) -> None:
    """POST a Graph sendMail JSON payload using a bearer access token."""
    token = access_token or get_access_token()
    try:
        response = requests.post(
            GRAPH_SEND_MAIL_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            timeout=HTTP_TIMEOUT,
        )
    except requests.RequestException as exc:
        logger.error("Microsoft Graph sendMail request failed: %s", type(exc).__name__)
        raise MicrosoftGraphAuthError(
            "Microsoft Graph sendMail request failed"
        ) from exc

    # Graph returns 202 Accepted on success with empty body.
    if response.status_code not in (200, 202):
        logger.error("Microsoft Graph sendMail failed (HTTP %s)", response.status_code)
        raise MicrosoftGraphAuthError(
            f"Microsoft Graph sendMail failed (HTTP {response.status_code})"
        )
