"""Unit tests for Microsoft Graph email backend (mocked HTTP)."""

from __future__ import annotations

import base64
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.cache import cache
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from core.email.backends import (
    MicrosoftGraphEmailBackend,
    email_message_to_graph_payload,
)
from core.email.ms_graph import (
    CACHE_ACCESS_KEY,
    CACHE_REFRESH_KEY,
    MicrosoftGraphAuthError,
    get_access_token,
    is_reconnect_required,
    mark_reconnect_required,
    persist_refresh_token,
    refresh_access_token,
    send_mail_payload,
)

# test.py uses DummyCache; LocMem is required to assert token persistence.
LOCMEM_CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "ms-graph-email-tests",
    }
}

GRAPH_SETTINGS = {
    "MS_GRAPH_CLIENT_ID": "test-client-id",
    "MS_GRAPH_CLIENT_SECRET": "",
    "MS_GRAPH_TENANT": "consumers",
    "MS_GRAPH_REFRESH_TOKEN": "bootstrap-refresh-token",
    "CACHES": LOCMEM_CACHES,
}


@pytest.fixture(autouse=True)
def _clear_cache():
    # LocMem LOCATION is shared across Graph tests; clear it under that backend
    # so reconnect flags cannot leak (test settings default to DummyCache).
    with override_settings(CACHES=LOCMEM_CACHES):
        cache.clear()
    yield
    with override_settings(CACHES=LOCMEM_CACHES):
        cache.clear()


@override_settings(**GRAPH_SETTINGS)
def test_email_message_to_graph_payload_text_to_cc_bcc():
    msg = EmailMessage(
        subject="Hello",
        body="Plain text",
        from_email="sender@example.com",
        to=["a@example.com", "b@example.com"],
        cc=["c@example.com"],
        bcc=["d@example.com"],
    )
    payload = email_message_to_graph_payload(msg)
    assert payload["saveToSentItems"] is True
    message = payload["message"]
    assert message["subject"] == "Hello"
    assert message["body"] == {"contentType": "Text", "content": "Plain text"}
    assert message["toRecipients"] == [
        {"emailAddress": {"address": "a@example.com"}},
        {"emailAddress": {"address": "b@example.com"}},
    ]
    assert message["ccRecipients"] == [{"emailAddress": {"address": "c@example.com"}}]
    assert message["bccRecipients"] == [{"emailAddress": {"address": "d@example.com"}}]


@override_settings(**GRAPH_SETTINGS)
def test_email_message_to_graph_payload_html_and_attachments():
    msg = EmailMultiAlternatives(
        subject="HTML mail",
        body="fallback text",
        from_email="sender@example.com",
        to=["to@example.com"],
    )
    msg.attach_alternative("<p>Hi</p>", "text/html")
    msg.attach("note.txt", b"hello bytes", "text/plain")

    payload = email_message_to_graph_payload(msg)
    message = payload["message"]
    assert message["body"] == {"contentType": "HTML", "content": "<p>Hi</p>"}
    assert len(message["attachments"]) == 1
    att = message["attachments"][0]
    assert att["@odata.type"] == "#microsoft.graph.fileAttachment"
    assert att["name"] == "note.txt"
    assert att["contentType"] == "text/plain"
    assert att["contentBytes"] == base64.b64encode(b"hello bytes").decode("ascii")


@override_settings(**GRAPH_SETTINGS)
@patch("core.email.ms_graph.requests.post")
def test_send_messages_success(mock_post):
    token_resp = MagicMock()
    token_resp.status_code = 200
    token_resp.json.return_value = {
        "access_token": "access-abc",
        "expires_in": 3600,
        "refresh_token": "bootstrap-refresh-token",
    }
    send_resp = MagicMock()
    send_resp.status_code = 202
    mock_post.side_effect = [token_resp, send_resp]

    backend = MicrosoftGraphEmailBackend()
    msg = EmailMessage("Subj", "Body", "from@example.com", ["to@example.com"])
    assert backend.send_messages([msg]) == 1

    assert mock_post.call_count == 2
    send_call = mock_post.call_args_list[1]
    assert send_call.args[0] == "https://graph.microsoft.com/v1.0/me/sendMail"
    assert send_call.kwargs["headers"]["Authorization"] == "Bearer access-abc"
    assert send_call.kwargs["json"]["message"]["subject"] == "Subj"


@override_settings(**GRAPH_SETTINGS)
@patch("core.email.ms_graph.requests.post")
def test_refresh_invalid_grant_sets_reconnect_and_stops_retries(mock_post):
    fail_resp = MagicMock()
    fail_resp.status_code = 400
    fail_resp.json.return_value = {
        "error": "invalid_grant",
        "error_codes": [70000],
        "error_description": "should-not-appear-in-logs",
    }
    mock_post.return_value = fail_resp

    with pytest.raises(MicrosoftGraphAuthError, match="reconnect required") as excinfo:
        refresh_access_token()
    assert excinfo.value.reconnect_required is True
    assert excinfo.value.error_code == "invalid_grant"
    assert is_reconnect_required()

    mock_post.reset_mock()
    with pytest.raises(MicrosoftGraphAuthError, match="reconnect required"):
        refresh_access_token()
    mock_post.assert_not_called()

    with pytest.raises(MicrosoftGraphAuthError, match="reconnect required"):
        send_mail_payload(
            {
                "message": {
                    "subject": "x",
                    "body": {"contentType": "Text", "content": "y"},
                }
            }
        )
    mock_post.assert_not_called()


@override_settings(**GRAPH_SETTINGS)
@patch("core.email.ms_graph.requests.post")
def test_refresh_5xx_does_not_set_reconnect(mock_post):
    fail_resp = MagicMock()
    fail_resp.status_code = 503
    fail_resp.json.return_value = {"error": "temporarily_unavailable"}
    mock_post.return_value = fail_resp

    with pytest.raises(MicrosoftGraphAuthError, match="token refresh failed"):
        refresh_access_token()
    assert not is_reconnect_required()


@override_settings(**GRAPH_SETTINGS)
@patch("core.email.ms_graph.requests.post")
def test_refresh_network_error_does_not_set_reconnect(mock_post):
    import requests as req

    mock_post.side_effect = req.ConnectionError("boom")
    with pytest.raises(MicrosoftGraphAuthError, match="request failed"):
        refresh_access_token()
    assert not is_reconnect_required()


@override_settings(**GRAPH_SETTINGS)
@patch("core.email.ms_graph.requests.post")
def test_env_token_change_clears_reconnect_then_refresh_succeeds(mock_post):
    mark_reconnect_required(
        error_code="invalid_grant",
        http_status=400,
        refresh_token="bootstrap-refresh-token",
    )
    assert is_reconnect_required()

    with override_settings(
        **{**GRAPH_SETTINGS, "MS_GRAPH_REFRESH_TOKEN": "replacement-refresh-token"}
    ):
        token_resp = MagicMock()
        token_resp.status_code = 200
        token_resp.json.return_value = {
            "access_token": "access-ok",
            "expires_in": 3600,
            "refresh_token": "replacement-refresh-token",
        }
        mock_post.return_value = token_resp
        assert refresh_access_token() == "access-ok"
        assert not is_reconnect_required()


@override_settings(**GRAPH_SETTINGS)
def test_persist_refresh_token_clears_reconnect():
    mark_reconnect_required(error_code="invalid_grant", http_status=400)
    persist_refresh_token("device-code-refresh-token")
    assert not is_reconnect_required()
    assert cache.get(CACHE_REFRESH_KEY) == "device-code-refresh-token"


@override_settings(**GRAPH_SETTINGS)
@patch("core.email.ms_graph.requests.post")
def test_bootstrap_token_change_after_fp_recorded_reseeds(mock_post):
    from core.email.ms_graph import get_refresh_token

    get_refresh_token()
    mark_reconnect_required(
        error_code="invalid_grant",
        http_status=400,
        refresh_token="bootstrap-refresh-token",
    )
    assert is_reconnect_required()

    with override_settings(
        **{**GRAPH_SETTINGS, "MS_GRAPH_REFRESH_TOKEN": "brand-new-bootstrap"}
    ):
        token_resp = MagicMock()
        token_resp.status_code = 200
        token_resp.json.return_value = {
            "access_token": "access-after-reseed",
            "expires_in": 3600,
        }
        mock_post.return_value = token_resp
        assert refresh_access_token() == "access-after-reseed"
        assert cache.get(CACHE_REFRESH_KEY) == "brand-new-bootstrap"
        assert not is_reconnect_required()


@override_settings(**GRAPH_SETTINGS)
@patch("core.email.ms_graph.requests.post")
def test_refresh_token_rotation_persisted_in_cache(mock_post):
    token_resp = MagicMock()
    token_resp.status_code = 200
    token_resp.json.return_value = {
        "access_token": "access-new",
        "expires_in": 3600,
        "refresh_token": "rotated-refresh-token",
    }
    mock_post.return_value = token_resp

    access = refresh_access_token()
    assert access == "access-new"
    assert cache.get(CACHE_REFRESH_KEY) == "rotated-refresh-token"
    assert cache.get(CACHE_ACCESS_KEY) == "access-new"

    # Second call should use cached access token (no HTTP).
    mock_post.reset_mock()
    assert get_access_token() == "access-new"
    mock_post.assert_not_called()


@override_settings(**GRAPH_SETTINGS)
@patch("core.email.ms_graph.requests.post")
def test_send_mail_uses_cached_access_token(mock_post):
    persist_refresh_token("bootstrap-refresh-token")
    cache.set(CACHE_ACCESS_KEY, "cached-access", timeout=600)

    send_resp = MagicMock()
    send_resp.status_code = 202
    mock_post.return_value = send_resp

    send_mail_payload(
        {"message": {"subject": "x", "body": {"contentType": "Text", "content": "y"}}}
    )
    mock_post.assert_called_once()
    assert (
        mock_post.call_args.kwargs["headers"]["Authorization"] == "Bearer cached-access"
    )


@override_settings(**GRAPH_SETTINGS)
@patch("core.email.ms_graph.requests.post")
def test_backend_fail_silently(mock_post):
    fail_resp = MagicMock()
    fail_resp.status_code = 401
    mock_post.return_value = fail_resp

    backend = MicrosoftGraphEmailBackend(fail_silently=True)
    msg = EmailMessage("S", "B", "f@e.com", ["t@e.com"])
    assert backend.send_messages([msg]) == 0


@override_settings(**GRAPH_SETTINGS)
@patch("core.management.commands.ms_graph_device_code.poll_device_code")
@patch("core.management.commands.ms_graph_device_code.request_device_code")
def test_ms_graph_device_code_command_writes_file(mock_request, mock_poll, tmp_path):
    mock_request.return_value = {
        "user_code": "ABCD-EFGH",
        "device_code": "device-xyz",
        "verification_uri": "https://microsoft.com/devicelogin",
        "interval": 1,
        "expires_in": 60,
    }
    mock_poll.return_value = {
        "access_token": "a",
        "refresh_token": "device-refresh-token",
        "expires_in": 3600,
    }
    out = StringIO()
    err = StringIO()
    token_file = tmp_path / "token.out"
    call_command(
        "ms_graph_device_code",
        output=str(token_file),
        stdout=out,
        stderr=err,
    )
    output = out.getvalue()
    assert "https://microsoft.com/devicelogin" in output
    assert "ABCD-EFGH" in output
    assert "device-refresh-token" not in output
    assert token_file.read_text(encoding="utf-8").strip() == "device-refresh-token"
    assert cache.get(CACHE_REFRESH_KEY) == "device-refresh-token"


@override_settings(MS_GRAPH_CLIENT_ID="", CACHES=LOCMEM_CACHES)
def test_ms_graph_device_code_requires_client_id(monkeypatch):
    monkeypatch.delenv("MS_GRAPH_CLIENT_ID", raising=False)
    with pytest.raises(CommandError, match="MS_GRAPH_CLIENT_ID"):
        call_command("ms_graph_device_code")
