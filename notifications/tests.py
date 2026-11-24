"""Notification app tests collected by pytest (see pytest.ini testpaths)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework_simplejwt.tokens import RefreshToken

from notifications.jwt_middleware import (
    WS_JWT_SUBPROTOCOL,
    JWTAuthMiddleware,
    extract_token_from_query_string,
    extract_token_from_subprotocols,
    get_user_from_token,
)
from notifications.models import Notification, NotificationType

User = get_user_model()


def _run_middleware(scope: dict) -> tuple[dict, AsyncMock]:
    inner = AsyncMock(return_value="ok")
    middleware = JWTAuthMiddleware(inner)
    result = async_to_sync(middleware)(scope, AsyncMock(), AsyncMock())
    return result, inner


@pytest.mark.django_db
class TestGetUserFromToken:
    def test_valid_access_token_returns_user(self):
        user = User.objects.create_user(
            username="jwtuser", email="jwt@example.com", password="testpass123"
        )
        token = str(RefreshToken.for_user(user).access_token)

        assert get_user_from_token(token) == user

    def test_invalid_token_returns_none(self):
        assert get_user_from_token("not-a-jwt") is None

    def test_unknown_user_id_returns_none(self):
        user = User.objects.create_user(
            username="goneuser", email="gone@example.com", password="testpass123"
        )
        token = str(RefreshToken.for_user(user).access_token)
        user.delete()

        assert get_user_from_token(token) is None


class TestSubprotocolExtraction:
    def test_extracts_token_after_seim_jwt(self):
        token, negotiated = extract_token_from_subprotocols(
            [WS_JWT_SUBPROTOCOL, "abc.def.ghi"]
        )
        assert token == "abc.def.ghi"
        assert negotiated == WS_JWT_SUBPROTOCOL

    def test_missing_token_returns_none(self):
        assert extract_token_from_subprotocols([WS_JWT_SUBPROTOCOL]) == (None, None)
        assert extract_token_from_subprotocols([]) == (None, None)


class TestQueryTokenExtraction:
    def test_extracts_query_token(self):
        assert extract_token_from_query_string(b"token=abc") == "abc"

    def test_missing_query_token(self):
        assert extract_token_from_query_string(b"") is None


@pytest.mark.django_db
class TestJWTAuthMiddleware:
    def test_valid_subprotocol_token_sets_scope_user(self):
        user = MagicMock()
        scope = {
            "type": "websocket",
            "query_string": b"",
            "subprotocols": [WS_JWT_SUBPROTOCOL, "valid-jwt"],
        }

        with patch(
            "notifications.jwt_middleware.get_user_from_token", return_value=user
        ):
            result, inner = _run_middleware(scope)

        assert scope["user"] is user
        assert scope["seim_ws_subprotocol"] == WS_JWT_SUBPROTOCOL
        assert scope["seim_ws_auth_via"] == "sec_websocket_protocol"
        assert result == "ok"
        inner.assert_awaited_once()

    def test_valid_query_token_sets_scope_user_when_allowed(self):
        user = MagicMock()
        scope = {"type": "websocket", "query_string": b"token=valid-jwt"}

        with (
            override_settings(WEBSOCKET_ALLOW_QUERY_JWT=True),
            patch(
                "notifications.jwt_middleware.get_user_from_token", return_value=user
            ),
        ):
            result, inner = _run_middleware(scope)

        assert scope["user"] is user
        assert scope["seim_ws_auth_via"] == "query_string_deprecated"
        assert result == "ok"
        inner.assert_awaited_once()

    def test_query_token_ignored_when_disabled(self):
        scope = {"type": "websocket", "query_string": b"token=valid-jwt"}

        with (
            override_settings(WEBSOCKET_ALLOW_QUERY_JWT=False),
            patch(
                "notifications.jwt_middleware.get_user_from_token"
            ) as get_user,
        ):
            _run_middleware(scope)

        assert "user" not in scope
        get_user.assert_not_called()

    def test_subprotocol_preferred_over_query_token(self):
        user = MagicMock()
        scope = {
            "type": "websocket",
            "query_string": b"token=query-jwt",
            "subprotocols": [WS_JWT_SUBPROTOCOL, "proto-jwt"],
        }

        with patch(
            "notifications.jwt_middleware.get_user_from_token", return_value=user
        ) as get_user:
            _run_middleware(scope)

        get_user.assert_called_once_with("proto-jwt")
        assert scope["seim_ws_auth_via"] == "sec_websocket_protocol"

    def test_invalid_query_token_does_not_set_user(self):
        scope = {"type": "websocket", "query_string": b"token=invalid"}

        with override_settings(WEBSOCKET_ALLOW_QUERY_JWT=True):
            _run_middleware(scope)

        assert "user" not in scope

    def test_missing_token_leaves_scope_unchanged(self):
        scope = {"type": "websocket", "query_string": b"", "subprotocols": []}

        _run_middleware(scope)

        assert "user" not in scope

    def test_http_scope_is_ignored(self):
        scope = {"type": "http", "query_string": b"token=abc"}

        result, inner = _run_middleware(scope)

        assert "user" not in scope
        assert result == "ok"
        inner.assert_awaited_once()


@pytest.mark.django_db
class TestNotificationModel:
    def test_str_includes_title_and_recipient(self):
        user = User.objects.create_user(
            username="notifuser", email="notif@example.com", password="testpass123"
        )
        notification = Notification.objects.create(
            recipient=user,
            title="Deadline soon",
            message="Submit your application",
            category="warning",
        )

        assert str(notification) == "Deadline soon - notifuser"
        assert notification.is_read is False
        assert notification.notification_type == "in_app"

    def test_str_without_recipient(self):
        notification = Notification.objects.create(
            title="Broadcast",
            message="System notice",
        )

        assert str(notification) == "Broadcast - None"

    def test_notification_type_str(self):
        ntype = NotificationType.objects.create(name="status_change")
        assert str(ntype) == "status_change"


@pytest.mark.django_db
def test_empty_token_returns_none():
    assert get_user_from_token("") is None
