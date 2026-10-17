"""Structured JSON logging, request IDs and Sentry/GlitchTip error tracking."""

from __future__ import annotations

import json
import logging
import re
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


# Keys whose values never leave the server (matched case-insensitively as substrings).
_SENSITIVE_KEYS = (
    "password",
    "passwd",
    "secret",
    "token",
    "authorization",
    "cookie",
    "session",
    "csrf",
    "api_key",
    "apikey",
    "dsn",
    "email",
    "username",
    "first_name",
    "last_name",
    "full_name",
    "display_name",
    "phone",
    "birth",
    "curp",
    "student_id",
)
# Exact keys (substring matching would also hide logger/file names).
# Exact keys. Plain "name" is not here: contexts.os.name etc. are harmless (user.name goes with user).
_SENSITIVE_EXACT = frozenset({"user_name", "address", "ip_address"})
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_BEARER_RE = re.compile(r"(?i)\b(bearer|token|basic)\s+[A-Za-z0-9._~+/=-]{8,}")
_JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\b")
_QUERY_SECRET_RE = re.compile(
    r"(?i)([?&](?:token|access|refresh|key|code|password|email|signature|uid)[^=&]*=)[^&#\s]+"
)
_KV_SECRET_RE = re.compile(
    r"(?i)\b((?:password|passwd|secret|token|api_key)\s*[=:]\s*)[^\s&,;]+"
)
FILTERED = "[Filtered]"


def _is_sensitive(key: object) -> bool:
    k = str(key).lower()
    return k in _SENSITIVE_EXACT or any(s in k for s in _SENSITIVE_KEYS)


def scrub_text(value: str) -> str:
    """Mask e-mail addresses, bearer/JWT tokens and secret query parameters inside free text."""
    value = _EMAIL_RE.sub(FILTERED, value)
    value = _JWT_RE.sub(FILTERED, value)
    value = _BEARER_RE.sub(lambda m: f"{m.group(1)} {FILTERED}", value)
    value = _QUERY_SECRET_RE.sub(lambda m: m.group(1) + FILTERED, value)
    return _KV_SECRET_RE.sub(lambda m: m.group(1) + FILTERED, value)


def scrub(value, depth: int = 0):
    """Recursively mask sensitive keys and patterns in dicts, lists and strings."""
    if depth > 12:
        return FILTERED
    if isinstance(value, dict):
        return {
            k: (FILTERED if _is_sensitive(k) else scrub(v, depth + 1))
            for k, v in value.items()
        }
    if isinstance(value, list | tuple):
        return [scrub(v, depth + 1) for v in value]
    if isinstance(value, str):
        return scrub_text(value)
    return value


def scrub_event(event: dict, hint: dict | None = None) -> dict:
    """``before_send`` / ``before_send_transaction``: drop request bodies, cookies, auth headers and
    user identity; mask transaction names, spans, URLs and everything else."""
    if isinstance(event.get("transaction"), str):
        event["transaction"] = scrub_text(event["transaction"])
    for span in event.get("spans") or []:
        if isinstance(span.get("description"), str):
            span["description"] = scrub_text(span["description"])
        if "data" in span:
            span["data"] = scrub(span["data"])
        if "tags" in span:
            span["tags"] = scrub(span["tags"])
    request = event.get("request")
    if isinstance(request, dict):
        request.pop("data", None)
        request.pop("cookies", None)
        if isinstance(request.get("headers"), dict):
            request["headers"] = {
                k: (
                    FILTERED
                    if _is_sensitive(k) or k.lower() in ("x-csrftoken",)
                    else scrub_text(v)
                    if isinstance(v, str)
                    else v
                )
                for k, v in request["headers"].items()
            }
        if isinstance(request.get("query_string"), str):
            request["query_string"] = scrub_text("?" + request["query_string"])[1:]
        if isinstance(request.get("url"), str):
            request["url"] = scrub_text(request["url"])
    user = event.get("user")
    if isinstance(user, dict):
        event["user"] = {"id": user["id"]} if user.get("id") is not None else {}
    for key in ("extra", "contexts", "tags"):
        if key in event:
            event[key] = scrub(event[key])
    if "message" in event and isinstance(event["message"], str):
        event["message"] = scrub_text(event["message"])
    logentry = event.get("logentry")
    if isinstance(logentry, dict):
        for k in ("message", "formatted"):
            if isinstance(logentry.get(k), str):
                logentry[k] = scrub_text(logentry[k])
        # Params can carry names verbatim; the formatted text is enough (and is scrubbed).
        logentry.pop("params", None)
    for exc in (event.get("exception") or {}).get("values") or []:
        if isinstance(exc.get("value"), str):
            exc["value"] = scrub_text(exc["value"])
        for frame in (exc.get("stacktrace") or {}).get("frames") or []:
            if "vars" in frame:
                frame["vars"] = scrub(frame["vars"])
    crumbs = event.get("breadcrumbs")
    values = crumbs.get("values") if isinstance(crumbs, dict) else crumbs
    for crumb in values or []:
        if isinstance(crumb.get("message"), str):
            crumb["message"] = scrub_text(crumb["message"])
        if "data" in crumb:
            crumb["data"] = scrub(crumb["data"])
    return event


def scrub_log(log: dict, hint: dict | None = None) -> dict | None:
    """``before_send_log``: mask the body and attributes of a structured log record.

    django.request warnings (4xx responses) are dropped; 5xx are errors and still sent."""
    attrs = log.get("attributes") if isinstance(log.get("attributes"), dict) else {}
    level = str(log.get("level") or log.get("severity_text") or "").lower()
    if attrs.get("logger.name") == "django.request" and level.startswith("warn"):
        return None
    if isinstance(log.get("body"), str):
        log["body"] = scrub_text(log["body"])
    if isinstance(log.get("attributes"), dict):
        # Drop message parameters entirely (names etc.); the body already holds the scrubbed text.
        log["attributes"] = scrub(
            {
                k: v
                for k, v in log["attributes"].items()
                if not str(k).startswith("sentry.message.parameter")
            }
        )
    return log


def _log_level(name: str) -> int | None:
    name = (name or "").strip().upper()
    if name in ("", "OFF", "NONE", "FALSE", "0"):
        return None
    return (
        logging.getLevelName(name)
        if isinstance(logging.getLevelName(name), int)
        else logging.WARNING
    )


def init_sentry(
    dsn: str,
    environment: str,
    release: str,
    *,
    traces_sample_rate: float = 0.05,
    sample_rate: float = 1.0,
    logs_level: str = "WARNING",
    trace_propagation_targets: list[str] | None = None,
) -> bool:
    """Initialise sentry-sdk for GlitchTip/Sentry. No-op without a DSN.

    Errors go through :func:`scrub_event`; with ``logs_level`` set (default WARNING, ``off`` disables),
    log records at that level and above are also sent as structured logs through :func:`scrub_log`.
    """
    if not dsn:
        return False
    try:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration
    except ImportError:
        logging.getLogger(__name__).warning(
            "SENTRY_DSN is set but sentry-sdk is not installed"
        )
        return False
    level = _log_level(logs_level)
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=release or None,
        sample_rate=sample_rate,
        traces_sample_rate=traces_sample_rate,
        send_default_pii=False,
        max_request_body_size="never",
        include_local_variables=False,
        before_send=scrub_event,
        before_send_transaction=scrub_event,
        before_send_log=scrub_log,
        # Trace headers only to our own hosts, never to third parties.
        trace_propagation_targets=trace_propagation_targets or [],
        enable_logs=level is not None,
        integrations=[
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR,
                sentry_logs_level=level if level is not None else logging.CRITICAL + 10,
            )
        ],
    )
    return True
