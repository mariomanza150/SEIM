"""
JWT authentication middleware for Django Channels WebSocket.

Allows Vue SPA (and other JWT-only clients) to connect to WebSocket by passing
?token=<access_token> in the connection URL. If token is valid, scope['user'] is set;
otherwise the next middleware (e.g. AuthMiddlewareStack) can still use session auth.
"""
import urllib.parse
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


def get_user_from_token(token_string):
    """Validate JWT and return User or None. Runs in sync context."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        access = AccessToken(token_string)
        user_id_claim = getattr(settings, 'SIMPLE_JWT', {}).get('USER_ID_CLAIM', 'user_id')
        user_id = access.get(user_id_claim)
        if user_id is None:
            return None
        return User.objects.get(pk=user_id)
    except (TokenError, InvalidToken, User.DoesNotExist):
        return None


class JWTAuthMiddleware(BaseMiddleware):
    """
    Set scope['user'] from JWT in query string (?token=...) for WebSocket connections.
    Does not override user if already set (e.g. by session).
    """
    async def __call__(self, scope, receive, send):
        if scope.get('type') == 'websocket':
            query_string = scope.get('query_string') or b''
            query = urllib.parse.parse_qs(query_string.decode())
            token_list = query.get('token')
            token = token_list[0] if token_list else None
            if token:
                user = await database_sync_to_async(get_user_from_token)(token)
                if user:
                    scope['user'] = user
        return await super().__call__(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    """Wrap inner application with JWT auth (query token) then Channels auth (session)."""
    from channels.auth import AuthMiddlewareStack
    return JWTAuthMiddleware(AuthMiddlewareStack(inner))
