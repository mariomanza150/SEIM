"""Microsoft Graph OAuth2 helpers for personal Microsoft accounts (Hotmail/Outlook).

Uses the consumers authority and delegated Mail.Send + offline_access scopes.
Tokens are never logged. Rotated refresh tokens are persisted via Django cache
(Redis in production via django-redis).

Non-recoverable token refresh failures (e.g. invalid_grant) set a persistent
reconnect-required flag so callers stop retrying until a new refresh token is
configured via ``manage.py ms_graph_device_code`` or an updated env token.
"""

from __future__ import annotations

import hashlib
import logging
import re
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
CACHE_RECONNECT_KEY = "ms_graph:v1:reconnect_required"
CACHE_BOOTSTRAP_FP_KEY = "ms_graph:v1:bootstrap_fp"
# Refresh tokens can live a long time; keep them in cache indefinitely until rotated.
REFRESH_CACHE_TIMEOUT = None
# Safety skew when caching access tokens.
ACCESS_TOKEN_SKEW_SECONDS = 60
HTTP_TIMEOUT = 30

# OAuth error codes are short machine tokens (e.g. invalid_grant). Never log
# error_description — it can contain account identifiers.
_SAFE_OAUTH_ERROR_RE = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")

RECONNECT_MESSAGE = (
    "Microsoft Graph email reconnect required. "
    "Run: python manage.py ms_graph_device_code"
)

GRAPH_BACKEND_PATH = "core.email.backends.MicrosoftGraphEmailBackend"


class MicrosoftGraphAuthError(Exception):
    """Raised when OAuth token acquisition, refresh, or sendMail fails."""

    def __init__(
        self,
        message: str,
        *,
        reconnect_required: bool = False,
        error_code: str | None = None,
        http_status: int | None = None,
    ) -> None:
        super().__init__(message)
        self.reconnect_required = reconnect_required
        self.error_code = error_code
        self.http_status = http_status


def graph_email_selected() -> bool:
    """True when Django is configured to deliver mail via Microsoft Graph."""
    backend = getattr(settings, "EMAIL_BACKEND", "") or ""
    if backend == GRAPH_BACKEND_PATH:
        return True
    if backend == "core.email.backends.RateLimitedEmailBackend":
        delivery = getattr(settings, "EMAIL_DELIVERY_BACKEND", "") or ""
        return delivery == GRAPH_BACKEND_PATH
    return False


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


def _token_fingerprint(token: str) -> str:
    """Short non-reversible fingerprint for detecting env token changes."""
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return digest[:16]


def _parse_oauth_error_fields(response: requests.Response) -> tuple[str | None, str | None]:
    """Extract safe OAuth ``error`` and optional numeric ``error_codes`` only."""
    try:
        payload = response.json()
    except ValueError:
        return None, None
    if not isinstance(payload, dict):
        return None, None

    error = payload.get("error")
    safe_error = (
        error if isinstance(error, str) and _SAFE_OAUTH_ERROR_RE.match(error) else None
    )

    codes = payload.get("error_codes")
    codes_label = None
    if isinstance(codes, list):
        ints = [str(c) for c in codes if isinstance(c, int)]
        if ints:
            codes_label = ",".join(ints[:8])
    return safe_error, codes_label


def _is_nonrecoverable_token_status(status_code: int) -> bool:
    """4xx other than timeout/rate-limit mean the refresh token cannot be reused."""
    if status_code < 400 or status_code >= 500:
        return False
    if status_code in (408, 429):
        return False
    return True


def mark_reconnect_required(
    *,
    error_code: str | None = None,
    http_status: int | None = None,
    refresh_token: str | None = None,
) -> None:
    """Persist reconnect-required until a new refresh token is configured."""
    token = refresh_token or ""
    if not token:
        try:
            token = get_refresh_token(sync_bootstrap=False)
        except ImproperlyConfigured:
            token = _bootstrap_refresh_token()
    state = {
        "error_code": error_code or "",
        "http_status": http_status or 0,
        "token_fp": _token_fingerprint(token) if token else "",
    }
    cache.set(CACHE_RECONNECT_KEY, state, timeout=REFRESH_CACHE_TIMEOUT)
    cache.delete(CACHE_ACCESS_KEY)
    logger.error(
        "Microsoft Graph reconnect required (error=%s http=%s)",
        error_code or "unknown",
        http_status or "unknown",
    )


def clear_reconnect_required() -> None:
    """Clear the reconnect-required flag (successful refresh or new token)."""
    if cache.get(CACHE_RECONNECT_KEY) is not None:
        cache.delete(CACHE_RECONNECT_KEY)
        logger.info("Microsoft Graph reconnect-required flag cleared")


def get_reconnect_state() -> dict[str, Any] | None:
    """Return reconnect state dict, or None when reconnect is not required."""
    state = cache.get(CACHE_RECONNECT_KEY)
    if not isinstance(state, dict):
        return None
    return state


def is_reconnect_required() -> bool:
    """True when Graph mail must not refresh/send until re-authorized."""
    return get_reconnect_state() is not None


def reconnect_status_payload() -> dict[str, Any]:
    """Public-safe status for health / ops notices (no secrets)."""
    state = get_reconnect_state()
    if not state:
        return {
            "reconnect_required": False,
            "message": "",
        }
    return {
        "reconnect_required": True,
        "error_code": state.get("error_code") or "",
        "http_status": state.get("http_status") or 0,
        "message": RECONNECT_MESSAGE,
    }


def _reseed_from_bootstrap(bootstrap: str, fp: str) -> None:
    cache.set(CACHE_REFRESH_KEY, bootstrap, timeout=REFRESH_CACHE_TIMEOUT)
    cache.set(CACHE_BOOTSTRAP_FP_KEY, fp, timeout=REFRESH_CACHE_TIMEOUT)
    cache.delete(CACHE_ACCESS_KEY)
    clear_reconnect_required()
    logger.info("Microsoft Graph bootstrap refresh token changed; cache reseeding")


def _sync_bootstrap_token() -> None:
    """If env bootstrap refresh token changed, prefer it and clear reconnect.

    On first observation of the env fingerprint (e.g. after deploy), record it
    without clobbering a rotated refresh token already stored in cache — unless
    reconnect is required for a different token fingerprint (env was replaced).
    """
    bootstrap = _bootstrap_refresh_token()
    if not bootstrap:
        return
    fp = _token_fingerprint(bootstrap)
    prev = cache.get(CACHE_BOOTSTRAP_FP_KEY)
    if prev is None:
        cache.set(CACHE_BOOTSTRAP_FP_KEY, fp, timeout=REFRESH_CACHE_TIMEOUT)
        state = get_reconnect_state()
        failed_fp = (state or {}).get("token_fp") or ""
        if state and failed_fp and failed_fp != fp:
            _reseed_from_bootstrap(bootstrap, fp)
        return
    if prev == fp:
        return
    _reseed_from_bootstrap(bootstrap, fp)


def get_refresh_token(*, sync_bootstrap: bool = True) -> str:
    """Return the active refresh token (cache preferred, then env bootstrap)."""
    if sync_bootstrap:
        _sync_bootstrap_token()
    cached = cache.get(CACHE_REFRESH_KEY)
    if cached:
        return str(cached)
    bootstrap = _bootstrap_refresh_token()
    if bootstrap:
        # Seed cache so subsequent rotations have a place to land.
        cache.set(CACHE_REFRESH_KEY, bootstrap, timeout=REFRESH_CACHE_TIMEOUT)
        cache.set(
            CACHE_BOOTSTRAP_FP_KEY,
            _token_fingerprint(bootstrap),
            timeout=REFRESH_CACHE_TIMEOUT,
        )
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
    cache.delete(CACHE_ACCESS_KEY)
    clear_reconnect_required()
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


def _raise_if_reconnect_required() -> None:
    _sync_bootstrap_token()
    if not is_reconnect_required():
        return
    state = get_reconnect_state() or {}
    raise MicrosoftGraphAuthError(
        RECONNECT_MESSAGE,
        reconnect_required=True,
        error_code=state.get("error_code") or None,
        http_status=int(state.get("http_status") or 0) or None,
    )


def refresh_access_token() -> str:
    """Exchange the refresh token for a new access token; persist rotation."""
    _raise_if_reconnect_required()
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
        error_code, error_codes = _parse_oauth_error_fields(response)
        # Log only safe machine codes — never the response body or tokens.
        logger.error(
            "Microsoft Graph token refresh failed (HTTP %s, error=%s, error_codes=%s)",
            response.status_code,
            error_code or "unknown",
            error_codes or "none",
        )
        if _is_nonrecoverable_token_status(response.status_code):
            mark_reconnect_required(
                error_code=error_code,
                http_status=response.status_code,
                refresh_token=refresh,
            )
            raise MicrosoftGraphAuthError(
                RECONNECT_MESSAGE,
                reconnect_required=True,
                error_code=error_code,
                http_status=response.status_code,
            )
        raise MicrosoftGraphAuthError(
            f"Microsoft Graph token refresh failed (HTTP {response.status_code})",
            error_code=error_code,
            http_status=response.status_code,
        )

    payload = response.json()
    access_token = payload.get("access_token") or ""
    if not access_token:
        raise MicrosoftGraphAuthError(
            "Microsoft Graph token refresh returned no access_token"
        )

    expires_in = int(payload.get("expires_in") or 3600)

    new_refresh = payload.get("refresh_token") or ""
    if new_refresh and new_refresh != refresh:
        persist_refresh_token(new_refresh)
        logger.info("Microsoft Graph refresh token rotated and persisted")
    else:
        clear_reconnect_required()

    # Cache access after persist so a rotated refresh does not wipe it.
    _cache_access_token(access_token, expires_in)
    return access_token


def get_access_token() -> str:
    """Return a valid access token, refreshing when the cache miss/expires."""
    _raise_if_reconnect_required()
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
        safe_error = (
            error
            if isinstance(error, str) and _SAFE_OAUTH_ERROR_RE.match(error)
            else None
        )
        logger.error(
            "Device code poll failed (HTTP %s, error=%s)",
            response.status_code,
            safe_error or "unknown",
        )
        raise MicrosoftGraphAuthError(
            f"Device code authorization failed (error={safe_error or response.status_code})"
        )

    raise MicrosoftGraphAuthError("Device code authorization timed out")


def send_mail_payload(payload: dict[str, Any], access_token: str | None = None) -> None:
    """POST a Graph sendMail JSON payload using a bearer access token."""
    if access_token is None:
        _raise_if_reconnect_required()
        token = get_access_token()
    else:
        token = access_token
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
            f"Microsoft Graph sendMail failed (HTTP {response.status_code})",
            http_status=response.status_code,
        )
