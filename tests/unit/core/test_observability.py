"""Structured logging, request ID and Sentry helpers (core.observability)."""

import io
import json
import logging
import logging.config
import re
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


# --- scrubbing (errors, transactions, logs) -------------------------------------------------------------
from core.observability import (  # noqa: E402
    FILTERED,
    own_origin_targets,
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
    assert "params" not in event["logentry"]
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
    assert captured["before_send_transaction"] is scrub_event
    assert captured["trace_propagation_targets"] == []
    assert captured["before_send_log"] is scrub_log
    captured.clear()
    init_sentry(dsn="http://k@h/1", environment="t", release="r", logs_level="off")
    assert captured["enable_logs"] is False


def test_scrub_text_masks_key_value_secrets_and_uid():
    out = scrub_text("password=hunter2 api_key: abc123 /verify?uid=MTIz&page=1")
    assert "hunter2" not in out and "abc123" not in out and "MTIz" not in out
    assert "page=1" in out


def test_scrub_event_scrubs_transactions():
    tx = scrub_event(
        {
            "type": "transaction",
            "transaction": "/api/reset/?token=t0k3n&email=a@b.co",
            "request": {
                "url": "https://s/api/verify/?uid=MTIz",
                "headers": {
                    "Referer": "https://s/seim/reset?token=r3f",
                    "Accept": "json",
                },
            },
            "spans": [
                {
                    "description": "GET /x?token=sp4n",
                    "data": {"url": "/y?email=a@b.co", "db.statement": "password=pw1"},
                }
            ],
            "contexts": {"os": {"name": "Linux"}, "runtime": {"name": "CPython"}},
            "user": {"id": 4, "name": "Ana", "email": "a@b.co"},
        }
    )
    blob = json.dumps(tx)
    for leaked in ("t0k3n", "a@b.co", "MTIz", "r3f", "sp4n", "pw1", "Ana"):
        assert leaked not in blob
    assert tx["user"] == {"id": 4}
    assert tx["contexts"]["os"]["name"] == "Linux"
    assert tx["request"]["headers"]["Accept"] == "json"


def test_scrub_log_drops_django_request_4xx_but_keeps_errors():
    warn = {
        "level": "warn",
        "body": "Not Found: /x",
        "attributes": {"logger.name": "django.request"},
    }
    assert scrub_log(warn) is None
    err = {
        "level": "error",
        "body": "Internal Server Error: /x",
        "attributes": {"logger.name": "django.request"},
    }
    assert scrub_log(err) is not None


def test_message_parameters_are_dropped_from_events_and_logs():
    event = scrub_event({"logentry": {"message": "hi %s", "params": ["Ana Perez"]}})
    assert "Ana Perez" not in json.dumps(event)
    log = scrub_log(
        {
            "level": "warn",
            "body": "hi",
            "attributes": {
                "sentry.message.template": "hi %s",
                "sentry.message.parameter.0": "Ana Perez",
                "sentry.message.parameter.name": "Ana Perez",
            },
        }
    )
    assert log["attributes"] == {"sentry.message.template": "hi %s"}


def test_scrub_log_stringifies_and_scrubs_non_string_attributes():
    class FakeRequest:
        def __repr__(self):
            return "<WSGIRequest: GET '/boom/?email=ana@uni.mx&token=t0k3n'>"

    log = scrub_log(
        {
            "level": "error",
            "body": "Internal Server Error: /boom/",
            "attributes": {
                "logger.name": "django.request",
                "request": FakeRequest(),
                "status_code": 500,
                "ok": False,
            },
        }
    )
    blob = json.dumps(log)
    assert "ana@uni.mx" not in blob and "t0k3n" not in blob
    assert log["attributes"]["status_code"] == 500 and log["attributes"]["ok"] is False


def test_kv_regex_catches_compound_secret_and_name_keys():
    text = (
        "access_token=a1 client_secret=b2 secret_key: c3 apiKey=d4 X-Api-Key=e5 "
        "name=Ana nombre=Ana full_name=Ana Perez filename=report.pdf"
    )
    out = scrub_text(text)
    for leaked in ("a1", "b2", "c3", "d4", "e5", "Ana"):
        assert leaked not in out
    assert "filename=report.pdf" in out


def test_own_origin_targets_are_anchored():
    (pattern,) = own_origin_targets("https://seim.incognitoslw.com/")
    assert re.match(pattern, "https://seim.incognitoslw.com/api/x")
    assert re.match(pattern, "https://seim.incognitoslw.com")
    assert not re.match(
        pattern, "https://evil.example/?next=https://seim.incognitoslw.com/"
    )
    assert not re.match(pattern, "https://seim.incognitoslw.com.evil.example/")
    assert own_origin_targets("") == []
