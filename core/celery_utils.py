"""Shared Celery retry and failure-logging helpers."""

from __future__ import annotations

import logging
import smtplib
from collections.abc import Iterable
from typing import Any

logger = logging.getLogger(__name__)

TRANSIENT_TASK_ERRORS: tuple[type[BaseException], ...] = (
    ConnectionError,
    TimeoutError,
    OSError,
    smtplib.SMTPException,
)

DEFAULT_MAX_RETRIES = 3


def retryable_task_kwargs(
    *,
    extra_exceptions: Iterable[type[BaseException]] = (),
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> dict[str, Any]:
    """Keyword arguments for ``@shared_task`` with backoff retries."""
    return {
        "bind": True,
        "autoretry_for": TRANSIENT_TASK_ERRORS + tuple(extra_exceptions),
        "retry_backoff": True,
        "retry_jitter": True,
        "max_retries": max_retries,
    }


def log_task_exception(task: Any, exc: BaseException | None = None) -> None:
    """Log a task failure with name and request id when available."""
    request = getattr(task, "request", None)
    task_name = getattr(task, "name", None) or task.__class__.__name__
    task_id = getattr(request, "id", None)
    logger.exception(
        "Celery task failed: name=%s id=%s",
        task_name,
        task_id,
        exc_info=exc if exc is not None else True,
    )


def log_celery_failure(
    self: Any,
    exc: BaseException,
    task_id: str,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    einfo: Any,
) -> None:
    """Celery ``on_failure`` hook: log name, id, and exception."""
    logger.error(
        "Celery task failed: name=%s id=%s args=%s kwargs=%s error=%s",
        getattr(self, "name", self.__class__.__name__),
        task_id,
        args,
        kwargs,
        exc,
        exc_info=einfo,
    )
