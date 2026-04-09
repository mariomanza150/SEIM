"""
Student-facing application readiness (documents, window, optional dynamic form).
"""

from __future__ import annotations

from typing import Any

from django.utils import timezone

from documents.services import DocumentService

from .services import ApplicationService


def _days_until_deadline(deadline, today) -> int | None:
    if deadline is None:
        return None
    return (deadline - today).days


def _resubmission_requests_for(doc):
    rel = getattr(doc, "documentresubmissionrequest_set", None)
    if rel is None:
        return ()
    return tuple(rel.all())


def _doc_workflow_status(doc) -> str:
    for r in _resubmission_requests_for(doc):
        if not r.resolved:
            return "resubmit_requested"
    if doc.is_valid:
        return "approved"
    return "pending_review"


def _latest_document_per_type(application):
    """Pick newest document per type_id from prefetched or loaded document_set."""
    by_type: dict[Any, Any] = {}
    docs = list(application.document_set.all())
    docs.sort(key=lambda d: d.created_at, reverse=True)
    for doc in docs:
        tid = doc.type_id
        if tid not in by_type:
            by_type[tid] = doc
    return by_type


def _document_progress_from_prefetch(application) -> tuple[float, dict[str, int]]:
    """
    Returns (progress 0..1, counts).
    Uses prefetched program.required_document_types and document_set when possible.
    """
    program = application.program
    required = list(program.required_document_types.all())
    if not required:
        return 1.0, {"required": 0, "approved": 0, "pending_review": 0, "resubmit": 0, "missing": 0}

    latest = _latest_document_per_type(application)
    approved = pending = resubmit = missing = 0
    for dt in required:
        doc = latest.get(dt.id)
        if not doc:
            missing += 1
            continue
        st = _doc_workflow_status(doc)
        if st == "approved":
            approved += 1
        elif st == "pending_review":
            pending += 1
        else:
            resubmit += 1

    # Weight partial progress (aligned with checklist semantics).
    weighted = approved + 0.55 * pending + 0.25 * resubmit
    progress = weighted / len(required)
    return min(1.0, max(0.0, progress)), {
        "required": len(required),
        "approved": approved,
        "pending_review": pending,
        "resubmit": resubmit,
        "missing": missing,
    }


def _document_progress(application) -> tuple[float, dict[str, int]]:
    cache = getattr(application.program, "_prefetched_objects_cache", None)
    app_cache = getattr(application, "_prefetched_objects_cache", None)
    if cache and "required_document_types" in cache and app_cache and "document_set" in app_cache:
        return _document_progress_from_prefetch(application)
    summary = DocumentService.build_application_document_checklist(application)
    req = summary["required_count"]
    if req == 0:
        return 1.0, {
            "required": 0,
            "approved": summary["approved_count"],
            "pending_review": 0,
            "resubmit": 0,
            "missing": 0,
        }
    approved = summary["approved_count"]
    pending = resubmit = missing = 0
    for item in summary["items"]:
        st = item["status"]
        if st == "pending_review":
            pending += 1
        elif st == "resubmit_requested":
            resubmit += 1
        elif st == "missing":
            missing += 1
    weighted = approved + 0.55 * pending + 0.25 * resubmit
    return min(1.0, weighted / req), {
        "required": req,
        "approved": approved,
        "pending_review": pending,
        "resubmit": resubmit,
        "missing": missing,
    }


def _form_progress(application) -> float:
    program = application.program
    if not program.application_form_id:
        return 1.0
    sub = ApplicationService.get_dynamic_form_submission(application)
    if not sub:
        return 0.2
    responses = sub.responses or {}
    if not responses:
        return 0.35
    return 1.0


def _headline_draft(counts: dict[str, int], window_open: bool, days_left: int | None, form_ok: bool) -> str:
    if not window_open:
        return "Application window is closed for this program."
    parts = []
    if counts["missing"]:
        parts.append(f"{counts['missing']} required document(s) missing")
    if counts["resubmit"]:
        parts.append(f"{counts['resubmit']} document(s) need resubmission")
    if counts["pending_review"]:
        parts.append(f"{counts['pending_review']} awaiting review")
    if not form_ok:
        parts.append("Program form incomplete")
    if days_left is not None and days_left >= 0:
        if days_left <= 3:
            parts.append(f"Deadline in {days_left} day(s)")
        elif days_left <= 14:
            parts.append(f"Deadline in {days_left} days")
    if not parts:
        if counts["required"] == 0 and form_ok:
            return "Ready to review and submit when you are satisfied."
        return "Requirements look complete — submit when ready."
    return "; ".join(parts) + "."


def compute_application_readiness(
    application,
    *,
    include_dynamic_form: bool = True,
    today=None,
) -> dict[str, Any]:
    """
    Summarize how close a draft application is to being submittable.

    List endpoints should pass include_dynamic_form=False to avoid N+1 FormSubmission queries.
    """
    today = today or timezone.localdate()
    program = application.program
    status_name = application.status.name if application.status else ""

    deadline = program.application_deadline
    days_left = _days_until_deadline(deadline, today)
    window = program.get_application_window_status(today)

    if status_name != "draft":
        headlines = {
            "submitted": "Application submitted.",
            "under_review": "Under review with coordinators.",
            "approved": "Application approved.",
            "rejected": "Application was not approved.",
            "completed": "Application completed.",
            "withdrawn": "Application withdrawn.",
        }
        return {
            "score": 100,
            "level": "done",
            "headline": headlines.get(
                status_name,
                f"Status: {status_name.replace('_', ' ')}.",
            ),
            "window_open": window["is_open"],
            "deadline_days": days_left,
            "document_counts": None,
        }

    doc_progress, counts = _document_progress(application)
    form_progress = _form_progress(application) if include_dynamic_form else 1.0

    if not window["is_open"]:
        score = max(0, min(30, int(doc_progress * 30)))
        return {
            "score": score,
            "level": "blocked",
            "headline": window["message"],
            "window_open": False,
            "deadline_days": days_left,
            "document_counts": counts,
        }

    # Draft + window open
    score = int(doc_progress * 58 + form_progress * 32 + 10)
    if days_left is not None and 0 <= days_left <= 7:
        score = max(25, score - 12)
    if days_left is not None and days_left < 0:
        score = min(score, 20)
    score = max(0, min(99, score))

    form_ok = form_progress >= 0.99
    headline = _headline_draft(
        counts,
        window_open=True,
        days_left=days_left,
        form_ok=form_ok,
    )

    docs_ok = counts["required"] == 0 or (
        counts["approved"] == counts["required"]
        and counts["resubmit"] == 0
        and counts["pending_review"] == 0
    )
    if docs_ok and form_ok and (days_left is None or days_left >= 0):
        level = "ready"
        score = max(score, 92)
    elif counts["missing"] or counts["resubmit"] or not form_ok or (days_left is not None and days_left <= 7):
        level = "attention"
    else:
        level = "ok"

    return {
        "score": min(99, score) if level != "ready" else min(100, max(score, 92)),
        "level": level,
        "headline": headline,
        "window_open": True,
        "deadline_days": days_left,
        "document_counts": counts,
    }
