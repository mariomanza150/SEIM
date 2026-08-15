"""Tests for shared Celery retry / failure logging helpers."""

import smtplib
from unittest.mock import MagicMock

from core.celery_utils import (
    TRANSIENT_TASK_ERRORS,
    log_celery_failure,
    log_task_exception,
    retryable_task_kwargs,
)


def test_retryable_task_kwargs_include_backoff_and_transient_errors():
    kwargs = retryable_task_kwargs(max_retries=5)

    assert kwargs["bind"] is True
    assert kwargs["retry_backoff"] is True
    assert kwargs["retry_jitter"] is True
    assert kwargs["max_retries"] == 5
    assert ConnectionError in kwargs["autoretry_for"]
    assert smtplib.SMTPException in kwargs["autoretry_for"]
    assert Exception not in kwargs["autoretry_for"]


def test_retryable_task_kwargs_accept_extra_exceptions():
    kwargs = retryable_task_kwargs(extra_exceptions=(ValueError,))

    assert ValueError in kwargs["autoretry_for"]
    for exc in TRANSIENT_TASK_ERRORS:
        assert exc in kwargs["autoretry_for"]


def test_log_task_exception_includes_name_and_id(caplog):
    task = MagicMock()
    task.name = "notifications.tasks.send_notification_email"
    task.request.id = "task-123"

    with caplog.at_level("ERROR"):
        log_task_exception(task, RuntimeError("boom"))

    assert "notifications.tasks.send_notification_email" in caplog.text
    assert "task-123" in caplog.text


def test_shared_tasks_use_retry_helper():
    from analytics.tasks import generate_report
    from documents.tasks import scan_document_virus
    from notifications.tasks import send_notification_email

    for task in (send_notification_email, scan_document_virus, generate_report):
        assert task.max_retries == 3
        assert task.autoretry_for


def test_log_celery_failure_hook_logs_task_identity(caplog):
    task = MagicMock()
    task.name = "documents.tasks.scan_document_virus"

    with caplog.at_level("ERROR"):
        log_celery_failure(
            task,
            RuntimeError("scanner down"),
            "abc-id",
            ("doc-1",),
            {"validator_id": "v1"},
            None,
        )

    assert "documents.tasks.scan_document_virus" in caplog.text
    assert "abc-id" in caplog.text
