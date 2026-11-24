"""
JWT authentication middleware for Django Channels WebSocket.

Preferred: pass the access token via Sec-WebSocket-Protocol as
``seim.jwt`` + ``<access_token>`` (never in the URL).

Deprecated fallback: ``?token=<access_token>`` when
``WEBSOCKET_ALLOW_QUERY_JWT`` is true (logs a warning).
"""

from __future__ import annotations

import logging
import urllib.parse

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.conf import settings
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

logger = logging.getLogger(__name__)

# Negotiated subprotocol name; the JWT itself is the next subprotocol value.
WS_JWT_SUBPROTOCOL = "seim.jwt"


def get_user_from_token(token_string):
    """Validate JWT and return User or None. Runs in sync context."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    try:
        access = AccessToken(token_string)
        user_id_claim = getattr(settings, "SIMPLE_JWT", {}).get(
            "USER_ID_CLAIM", "user_id"
        )
        user_id = access.get(user_id_claim)
        if user_id is None:
            return None
        return User.objects.get(pk=user_id)
    except (TokenError, InvalidToken, User.DoesNotExist):
        return None


def extract_token_from_subprotocols(subprotocols) -> tuple[str | None, str | None]:
    """Return (token, negotiated_subprotocol) from Sec-WebSocket-Protocol values."""
    subs = [str(s) for s in (subprotocols or []) if s]
    if WS_JWT_SUBPROTOCOL not in subs:
        return None, None
    idx = subs.index(WS_JWT_SUBPROTOCOL)
    if idx + 1 >= len(subs):
        return None, None
    token = subs[idx + 1]
    if not token or token == WS_JWT_SUBPROTOCOL:
        return None, None
    return token, WS_JWT_SUBPROTOCOL


def extract_token_from_query_string(query_string: bytes | str) -> str | None:
    """Deprecated: read JWT from ``?token=`` query string."""
    raw = (
        query_string.decode()
        if isinstance(query_string, bytes)
        else (query_string or "")
    )
    query = urllib.parse.parse_qs(raw)
    token_list = query.get("token")
    return token_list[0] if token_list else None


class JWTAuthMiddleware(BaseMiddleware):
    """
    Set scope['user'] from JWT for WebSocket connections.

    Order: Sec-WebSocket-Protocol (preferred), then deprecated query token
    when ``WEBSOCKET_ALLOW_QUERY_JWT`` is enabled.
    """

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "websocket":
            token = None
            subprotocol = None

            token, subprotocol = extract_token_from_subprotocols(
                scope.get("subprotocols")
            )
            if token:
                scope["seim_ws_subprotocol"] = subprotocol
            else:
                allow_query = getattr(settings, "WEBSOCKET_ALLOW_QUERY_JWT", True)
                if allow_query:
                    query_token = extract_token_from_query_string(
                        scope.get("query_string") or b""
                    )
                    if query_token:
                        logger.warning(
                            "DEPRECATED: WebSocket JWT passed in query string "
                            "(?token=). Prefer Sec-WebSocket-Protocol "
                            "('%s', '<access_token>'). "
                            "Set WEBSOCKET_ALLOW_QUERY_JWT=0 to disable.",
                            WS_JWT_SUBPROTOCOL,
                        )
                        token = query_token
                        scope["seim_ws_auth_via"] = "query_string_deprecated"
                elif extract_token_from_query_string(scope.get("query_string") or b""):
                    logger.warning(
                        "Ignoring WebSocket ?token= query JWT "
                        "(WEBSOCKET_ALLOW_QUERY_JWT is disabled)"
                    )

            if token:
                user = await database_sync_to_async(get_user_from_token)(token)
                if user:
                    scope["user"] = user
                    if subprotocol:
                        scope["seim_ws_auth_via"] = "sec_websocket_protocol"
        return await super().__call__(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    """Wrap inner application with JWT auth then Channels auth (session)."""
    from channels.auth import AuthMiddlewareStack

    return JWTAuthMiddleware(AuthMiddlewareStack(inner))
