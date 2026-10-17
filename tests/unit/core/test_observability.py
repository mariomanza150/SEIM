"""Structured logging, request ID and Sentry helpers (core.observability)."""

import io
import json
import logging
import logging.config
import sys

import pytest
from django.conf import settings

from core.observability import (
    JsonFormatter,
    RequestIdFilter,
    init_sentry,
    logging_config,
    request_id_var,
)


def _record(msg="hello %s", args=("world",)):
    return logging.LogRecord("seim.test", logging.INFO, __file__, 1, msg, args, None)


def test_json_formatter_emits_standard_fields_and_extras():
    record = _record()
    record.application_id = 7
    token = request_id_var.set("req-1")
    try:
        RequestIdFilter().filter(record)
    finally:
        request_id_var.reset(token)

    payload = json.loads(JsonFormatter().format(record))

    assert payload["level"] == "info"
    assert payload["logger"] == "seim.test"
    assert payload["msg"] == "hello world"
    assert payload["request_id"] == "req-1"
    assert payload["application_id"] == 7
    assert payload["ts"].endswith("+00:00")


def test_json_formatter_includes_exception():
    try:
        raise ValueError("boom")
    except ValueError:
        record = logging.LogRecord(
            "seim.test", logging.ERROR, __file__, 1, "failed", (), sys.exc_info()
        )

    payload = json.loads(JsonFormatter().format(record))

    assert "ValueError: boom" in payload["exc_info"]


@pytest.mark.parametrize("fmt", ["json", "text"])
def test_logging_config_is_valid_dictconfig(fmt, monkeypatch):
    stream = io.StringIO()
    monkeypatch.setattr("sys.stdout", stream)
    try:
        logging.config.dictConfig(logging_config(fmt=fmt, level="info"))
        logging.getLogger("seim.test").info("configured")
    finally:
        logging.config.dictConfig(settings.LOGGING)

    line = stream.getvalue().strip()
    if fmt == "json":
        assert json.loads(line)["msg"] == "configured"
    else:
        assert line.endswith("configured")


def test_init_sentry_is_noop_without_dsn():
    assert init_sentry(dsn="", environment="test", release="x") is False


# --- scrubbing and envelope relay -------------------------------------------------------------
from core.observability import (  # noqa: E402
    FILTERED,
    scrub,
    scrub_event,
    scrub_log,
    scrub_text,
)


def test_scrub_text_masks_emails_tokens_and_query_secrets():
    out = scrub_text("ana@uni.mx Bearer abcdefghijk /reset?token=s3cr3t&page=2")
    assert "ana@uni.mx" not in out and "abcdefghijk" not in out and "s3cr3t" not in out
    assert "page=2" in out


def test_scrub_masks_sensitive_keys_only():
    assert scrub(
        {"password": "x", "logger": "a", "inner": {"email": "a@b.co", "n": 1}}
    ) == {
        "password": FILTERED,
        "logger": "a",
        "inner": {"email": FILTERED, "n": 1},
    }


def test_scrub_event_drops_bodies_cookies_auth_and_identity():
    event = scrub_event(
        {
            "request": {
                "url": "https://x/api?token=abc",
                "data": {"password": "p"},
                "cookies": {"sessionid": "s"},
                "headers": {
                    "Authorization": "Bearer t",
                    "Cookie": "c",
                    "Accept": "json",
                },
            },
            "user": {"id": 3, "email": "a@b.co", "username": "ana"},
            "logentry": {"message": "login a@b.co", "params": [{"token": "t"}]},
            "exception": {"values": [{"value": "bad a@b.co"}]},
            "breadcrumbs": {
                "values": [{"message": "a@b.co", "data": {"password": "x"}}]
            },
        }
    )
    req = event["request"]
    assert "data" not in req and "cookies" not in req
    assert req["headers"] == {
        "Authorization": FILTERED,
        "Cookie": FILTERED,
        "Accept": "json",
    }
    assert "abc" not in req["url"]
    assert event["user"] == {"id": 3}
    assert "a@b.co" not in event["logentry"]["message"]
    assert event["logentry"]["params"] == [{"token": FILTERED}]
    assert "a@b.co" not in event["exception"]["values"][0]["value"]
    assert event["breadcrumbs"]["values"][0]["data"] == {"password": FILTERED}


def test_scrub_log_masks_body_and_attributes():
    log = scrub_log(
        {"body": "user a@b.co failed", "attributes": {"email": "a@b.co", "x": 1}}
    )
    assert log == {
        "body": f"user {FILTERED} failed",
        "attributes": {"email": FILTERED, "x": 1},
    }


def test_init_sentry_enables_scrubbing_and_logs(monkeypatch):
    import sentry_sdk

    captured = {}
    monkeypatch.setattr(sentry_sdk, "init", lambda **kw: captured.update(kw))
    assert init_sentry(
        dsn="http://k@h/1", environment="t", release="r", logs_level="warning"
    )
    assert captured["send_default_pii"] is False
    assert captured["traces_sample_rate"] == 0.05
    assert captured["enable_logs"] is True
    assert captured["before_send"] is scrub_event
    assert captured["before_send_log"] is scrub_log
    captured.clear()
    init_sentry(dsn="http://k@h/1", environment="t", release="r", logs_level="off")
    assert captured["enable_logs"] is False
