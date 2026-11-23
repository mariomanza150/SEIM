"""Settings / observability tests for optional LOG_FILE rotating handler."""

from __future__ import annotations

import logging.config
from pathlib import Path

from django.conf import settings

from core.observability import (
    attach_rotating_file_handler,
    logging_config,
    resolve_log_file_path,
)


def test_resolve_log_file_path_prefers_explicit_file():
    assert (
        resolve_log_file_path("/tmp/custom.log", "/tmp/logs") == "/tmp/custom.log"
    )


def test_resolve_log_file_path_uses_dir_when_file_empty(tmp_path):
    path = resolve_log_file_path("", str(tmp_path))
    assert path == str(tmp_path / "seim.log")


def test_resolve_log_file_path_none_when_unset():
    assert resolve_log_file_path("", "") is None
    assert resolve_log_file_path(None, None) is None


def test_attach_rotating_file_handler_adds_handler(tmp_path, monkeypatch):
    log_path = tmp_path / "web.log"
    config = logging_config(fmt="text", level="INFO")
    attach_rotating_file_handler(
        config,
        filename=str(log_path),
        max_bytes=1024,
        backup_count=2,
    )
    assert "file" in config["handlers"]
    handler = config["handlers"]["file"]
    assert handler["class"] == "logging.handlers.RotatingFileHandler"
    assert handler["filename"] == str(log_path)
    assert handler["maxBytes"] == 1024
    assert handler["backupCount"] == 2
    assert "file" in config["root"]["handlers"]
    assert "file" in config["loggers"]["seim.audit"]["handlers"]

    logging.config.dictConfig(config)
    try:
        logging.getLogger("seim.audit").info("audit_probe")
        logging.getLogger("seim.test").info("root_probe")
    finally:
        logging.config.dictConfig(settings.LOGGING)

    text = log_path.read_text(encoding="utf-8")
    assert "audit_probe" in text
    assert "root_probe" in text


def test_production_style_log_file_handler_config(tmp_path):
    """Mirrors production/development attach when LOG_FILE is set."""
    log_file = tmp_path / "prod.log"
    resolved = resolve_log_file_path(str(log_file), "")
    assert resolved == str(log_file)
    config = logging_config(fmt="json", level="INFO")
    attach_rotating_file_handler(config, filename=resolved, backup_count=3)
    assert Path(config["handlers"]["file"]["filename"]) == log_file
    assert config["handlers"]["file"]["backupCount"] == 3
    assert config["handlers"]["file"]["class"] == "logging.handlers.RotatingFileHandler"
