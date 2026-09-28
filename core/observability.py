"""Structured JSON logging, request IDs and Sentry/GlitchTip error tracking."""

from __future__ import annotations

import json
import logging
import uuid
from contextvars import ContextVar
from datetime import UTC, datetime

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

_RESERVED_ATTRS = frozenset(
    vars(logging.LogRecord("", 0, "", 0, "", None, None)).keys()
    | {"message", "asctime", "request"}
)


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(
                timespec="milliseconds"
            ),
            "level": record.levelname.lower(),
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
        }
        for key, value in vars(record).items():
            if key not in _RESERVED_ATTRS and key not in payload:
                payload[key] = value
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, ensure_ascii=False)


class RequestIdMiddleware:
    """Bind ``X-Request-ID`` (or a new id) to the request, its log records and the response."""

    header = "X-Request-ID"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = (
            request.headers.get(self.header, "").strip()[:128] or uuid.uuid4().hex
        )
        request.request_id = request_id
        token = request_id_var.set(request_id)
        try:
            response = self.get_response(request)
        finally:
            request_id_var.reset(token)
        response[self.header] = request_id
        return response


def logging_config(fmt: str = "json", level: str = "INFO") -> dict:
    """``LOGGING`` dict that writes every record to stdout as JSON (or text when ``fmt="text"``)."""
    formatter = (
        {"()": "core.observability.JsonFormatter"}
        if fmt.lower() == "json"
        else {
            "format": "%(asctime)s [%(levelname)s] %(name)s [%(request_id)s]: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    )
    level = level.upper()
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {"request_id": {"()": "core.observability.RequestIdFilter"}},
        "formatters": {"default": formatter},
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
                "filters": ["request_id"],
            },
        },
        "root": {"handlers": ["console"], "level": level},
        "loggers": {
            "django": {"handlers": ["console"], "level": level, "propagate": False},
            "django.request": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
            "django.security": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
            "django.server": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }


def init_sentry(dsn: str, environment: str, release: str) -> bool:
    """Initialise sentry-sdk (Django, Celery and logging integrations auto-enable). No-op without a DSN."""
    if not dsn:
        return False
    try:
        import sentry_sdk
    except ImportError:
        logging.getLogger(__name__).warning(
            "SENTRY_DSN is set but sentry-sdk is not installed"
        )
        return False
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=release or None,
        traces_sample_rate=0.0,
        send_default_pii=False,
    )
    return True
