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
