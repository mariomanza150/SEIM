"""
Scholarship allocation scoring (transparent default rubric).

Phase 1: deterministic factor logic (``default_v1``) with staff-editable
per-factor max weights via ``ScholarshipScoringRuleset``. Workflow hooks remain backlog.
Staff use exports and full disclaimer; owning students receive the same numeric breakdown
with a student-facing disclaimer on application detail.
"""

from __future__ import annotations

import csv
import io
from collections.abc import Iterable
from dataclasses import dataclass
from io import BytesIO
from typing import Any

from django.http import HttpResponse
from django.utils import timezone

from exchange.readiness import _document_progress, _form_progress

CEFR_RANK: dict[str, int] = {
    "A1": 1,
    "A2": 2,
    "B1": 3,
    "B2": 4,
    "C1": 5,
    "C2": 6,
}

RULESET_ID = "default_v1"
RULESET_LABEL = "Default scholarship rubric (v1)"

STUDENT_SCHOLARSHIP_DISCLAIMER = (
    "This is an informational estimate from the current default rubric. "
    "It is not a guarantee of funding; staff make final decisions."
)

FACTOR_IDS: tuple[str, ...] = (
    "academic",
    "language",
    "program_fit",
    "application_quality",
    "timeliness",
)

# Built-in v1 ceilings (also the migration seed / fallback when no DB row).
DEFAULT_FACTOR_MAX: dict[str, float] = {
    "academic": 25.0,
    "language": 20.0,
    "program_fit": 15.0,
    "application_quality": 25.0,
    "timeliness": 15.0,
}

MAX_ACADEMIC = DEFAULT_FACTOR_MAX["academic"]
MAX_LANGUAGE = DEFAULT_FACTOR_MAX["language"]
MAX_PROGRAM_FIT = DEFAULT_FACTOR_MAX["program_fit"]
MAX_APPLICATION_QUALITY = DEFAULT_FACTOR_MAX["application_quality"]
MAX_TIMELINESS = DEFAULT_FACTOR_MAX["timeliness"]


def _student_profile(student):
    try:
        return student.profile
    except Exception:
        return None


def _safe_gpa_for_scoring(profile) -> tuple[float | None, str | None]:
    """Return (4.0-scale value or raw GPA, note for breakdown)."""
    if not profile or profile.gpa is None:
        return None, None
    try:
        eq = profile.get_gpa_equivalent()
        if eq is not None:
            return float(eq), "GPA (4.0-scale equivalent)"
    except Exception:
        pass
    return float(profile.gpa), "GPA (institutional scale; no translation)"


def get_active_scholarship_ruleset_config() -> dict[str, Any]:
    """
    Resolve active ruleset id/label/weights (DB first, then built-in defaults).

    Ensures a default row exists when the table is empty so the admin editor
    always has something to show after migrate.
    """
    try:
        from exchange.models import (
            ScholarshipScoringRuleset,
            default_scholarship_factor_weights,
        )

        active = (
            ScholarshipScoringRuleset.objects.filter(is_active=True)
            .order_by("-updated_at")
            .first()
        )
        if active is None:
            active = ScholarshipScoringRuleset.objects.order_by("created_at").first()
        if active is None:
            active = ScholarshipScoringRuleset.objects.create(
                slug=RULESET_ID,
                label=RULESET_LABEL,
                description=(
                    "Built-in transparent rubric. Edit factor max weights to "
                    "rebalance academic, language, fit, quality, and timeliness."
                ),
                factor_weights=default_scholarship_factor_weights(),
                is_active=True,
            )
        return {
            "ruleset_id": active.slug,
            "ruleset_label": active.label,
            "factor_max": active.normalized_weights(),
        }
    except Exception:
        return {
            "ruleset_id": RULESET_ID,
            "ruleset_label": RULESET_LABEL,
            "factor_max": dict(DEFAULT_FACTOR_MAX),
        }


def _academic_factor(profile, program, max_points: float) -> dict[str, Any]:
    gpa_val, gpa_note = _safe_gpa_for_scoring(profile)
    if gpa_val is None:
        return {
            "id": "academic",
            "label": "Academic record",
            "points": 0.0,
            "max_points": max_points,
            "detail": "No GPA on student profile.",
        }
    # Map roughly to 0–max on a 0–4.0 style scale (saturating above 4).
    ratio = max(0.0, min(1.0, gpa_val / 4.0))
    pts = round(ratio * max_points, 2)
    detail = f"{gpa_note}: {gpa_val:.2f}"
    if program.min_gpa is not None and gpa_val < float(program.min_gpa):
        detail += f" (below program minimum {program.min_gpa}; points still reflect raw strength)"
    return {
        "id": "academic",
        "label": "Academic record",
        "points": pts,
        "max_points": max_points,
        "detail": detail,
    }


def _student_best_cefr_rank(profile) -> tuple[int | None, str]:
    if not profile:
        return None, "No profile"
    best = 0
    parts = []
    if profile.language_level and profile.language_level in CEFR_RANK:
        r = CEFR_RANK[profile.language_level]
        best = max(best, r)
        parts.append(f"primary {profile.language_level}")
    for row in profile.additional_languages or []:
        if not isinstance(row, dict):
            continue
        lvl = row.get("level") or row.get("cefr")
        if lvl in CEFR_RANK:
            r = CEFR_RANK[str(lvl)]
            best = max(best, r)
            nm = row.get("name") or "language"
            parts.append(f"{nm} {lvl}")
    if not parts:
        return None, "No CEFR levels recorded"
    return best, "; ".join(parts)


def _language_factor(profile, program, max_points: float) -> dict[str, Any]:
    student_rank, student_desc = _student_best_cefr_rank(profile)
    # Relative bands from default_v1 (max 20): partial 5, one-below 6.
    partial = round(max_points * (5.0 / MAX_LANGUAGE), 2) if MAX_LANGUAGE else 0.0
    one_below = round(max_points * (6.0 / MAX_LANGUAGE), 2) if MAX_LANGUAGE else 0.0
    min_lvl = program.min_language_level
    if not min_lvl or min_lvl not in CEFR_RANK:
        if student_rank is None:
            pts = partial
            detail = "Program does not require a CEFR minimum; no language level on file (partial credit)."
        else:
            pts = max_points
            detail = f"No CEFR minimum on program; documented levels: {student_desc}"
        return {
            "id": "language",
            "label": "Language proficiency",
            "points": pts,
            "max_points": max_points,
            "detail": detail,
        }

    need = CEFR_RANK[min_lvl]
    if student_rank is None:
        return {
            "id": "language",
            "label": "Language proficiency",
            "points": 0.0,
            "max_points": max_points,
            "detail": f"Program requires {min_lvl}; no comparable CEFR level on profile.",
        }
    if student_rank >= need:
        pts = max_points
        detail = f"Meets or exceeds program minimum ({min_lvl}); best documented: {student_desc}"
    elif student_rank == need - 1:
        pts = one_below
        detail = f"One CEFR band below minimum ({min_lvl}); {student_desc}"
    else:
        pts = 0.0
        detail = f"Below program minimum ({min_lvl}); {student_desc}"
    return {
        "id": "language",
        "label": "Language proficiency",
        "points": round(pts, 2),
        "max_points": max_points,
        "detail": detail,
    }


def _program_fit_factor(profile, program, max_points: float) -> dict[str, Any]:
    # Relative bands from default_v1 (max 15): neutral 12, weak match 6.
    neutral = round(max_points * (12.0 / MAX_PROGRAM_FIT), 2) if MAX_PROGRAM_FIT else 0.0
    weak = round(max_points * (6.0 / MAX_PROGRAM_FIT), 2) if MAX_PROGRAM_FIT else 0.0
    req_lang = (program.required_language or "").strip()
    if not req_lang:
        return {
            "id": "program_fit",
            "label": "Program / language fit",
            "points": neutral,
            "max_points": max_points,
            "detail": "No specific host-language requirement on program (neutral fit score).",
        }
    req_lower = req_lang.lower()
    primary = (profile.language or "").strip().lower() if profile else ""
    if primary and primary == req_lower:
        return {
            "id": "program_fit",
            "label": "Program / language fit",
            "points": max_points,
            "max_points": max_points,
            "detail": f"Primary language matches program requirement ({req_lang}).",
        }
    if profile and profile.additional_languages:
        for row in profile.additional_languages:
            if not isinstance(row, dict):
                continue
            name = (row.get("name") or "").strip().lower()
            if name and name == req_lower:
                return {
                    "id": "program_fit",
                    "label": "Program / language fit",
                    "points": neutral,
                    "max_points": max_points,
                    "detail": f"Additional language matches program requirement ({req_lang}).",
                }
    return {
        "id": "program_fit",
        "label": "Program / language fit",
        "points": weak,
        "max_points": max_points,
        "detail": f"Program lists {req_lang}; no explicit match on profile languages.",
    }


def _application_quality_factor(application, max_points: float) -> dict[str, Any]:
    doc_progress, counts = _document_progress(application)
    form_progress = _form_progress(application)
    # Default split was 15 docs + 10 form of 25.
    doc_share = 15.0 / MAX_APPLICATION_QUALITY if MAX_APPLICATION_QUALITY else 0.6
    form_share = 10.0 / MAX_APPLICATION_QUALITY if MAX_APPLICATION_QUALITY else 0.4
    doc_pts = round(doc_progress * doc_share * max_points, 2)
    form_pts = round(form_progress * form_share * max_points, 2)
    pts = min(max_points, doc_pts + form_pts)
    detail_parts = [
        f"Documents weighted progress {doc_progress:.0%} ({counts['approved']}/{counts['required'] or 0} approved"
        f", pending {counts['pending_review']}, resubmit {counts['resubmit']}, "
        f"invalid {counts.get('invalid', 0)}, missing {counts['missing']})",
        f"dynamic form completeness {form_progress:.0%}",
    ]
    return {
        "id": "application_quality",
        "label": "Application quality (documents & form)",
        "points": pts,
        "max_points": max_points,
        "detail": "; ".join(detail_parts) + ".",
    }


def _reference_date_for_timeliness(application):
    dt = application.submitted_at or application.created_at
    if dt is None:
        return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_default_timezone())
    return timezone.localtime(dt).date()


def _timeliness_factor(application, program, max_points: float) -> dict[str, Any]:
    open_d = program.application_open_date
    close_d = program.application_deadline
    ref = _reference_date_for_timeliness(application)
    mid = round(max_points * (10.0 / MAX_TIMELINESS), 2) if MAX_TIMELINESS else 0.0
    late = round(max_points * (5.0 / MAX_TIMELINESS), 2) if MAX_TIMELINESS else 0.0
    outside = round(max_points * (4.0 / MAX_TIMELINESS), 2) if MAX_TIMELINESS else 0.0
    if not ref or not open_d or not close_d:
        neutral = round(max_points / 2, 2)
        return {
            "id": "timeliness",
            "label": "Timeliness (within apply window)",
            "points": neutral,
            "max_points": max_points,
            "detail": "Open/close dates incomplete — neutral timeliness score.",
        }
    span = (close_d - open_d).days
    if span <= 0:
        on_time = open_d <= ref <= close_d
        pts = max_points if on_time else outside
        return {
            "id": "timeliness",
            "label": "Timeliness (within apply window)",
            "points": pts,
            "max_points": max_points,
            "detail": "Single-day or same open/close window; scored as on-time if within bounds."
            if on_time
            else "Outside stated window.",
        }
    pos = (ref - open_d).days / span
    pos = max(0.0, min(1.0, pos))
    if pos <= 0.33:
        pts, msg = max_points, "Submitted/started early in the window."
    elif pos <= 0.66:
        pts, msg = mid, "Submitted/started mid-window."
    else:
        pts, msg = late, "Submitted/started toward the end of the window."
    return {
        "id": "timeliness",
        "label": "Timeliness (within apply window)",
        "points": pts,
        "max_points": max_points,
        "detail": msg,
    }


def compute_scholarship_allocation_score(application) -> dict[str, Any]:
    """
    Compute total score and per-factor breakdown for one application.

    Intended for coordinator/admin review; not a guarantee of funding.
    """
    cfg = get_active_scholarship_ruleset_config()
    factor_max = cfg["factor_max"]
    program = application.program
    profile = _student_profile(application.student)
    factors: list[dict[str, Any]] = [
        _academic_factor(profile, program, factor_max["academic"]),
        _language_factor(profile, program, factor_max["language"]),
        _program_fit_factor(profile, program, factor_max["program_fit"]),
        _application_quality_factor(application, factor_max["application_quality"]),
        _timeliness_factor(application, program, factor_max["timeliness"]),
    ]
    total = round(sum(f["points"] for f in factors), 2)
    max_total = round(sum(f["max_points"] for f in factors), 2)
    gpa_sort, _ = _safe_gpa_for_scoring(profile)
    return {
        "ruleset_id": cfg["ruleset_id"],
        "ruleset_label": cfg["ruleset_label"],
        "total_points": total,
        "max_points": max_total,
        "factors": factors,
        "tie_breakers": [
            "total_points_desc",
            "gpa_equivalent_desc",
            "submitted_at_asc",
            "created_at_asc",
        ],
        "sort_keys": {
            "gpa_for_rank": gpa_sort,
            "submitted_at": (
                application.submitted_at.isoformat()
                if application.submitted_at
                else None
            ),
            "created_at": application.created_at.isoformat()
            if application.created_at
            else None,
        },
        "flags": {
            "withdrawn": application.withdrawn,
        },
        "disclaimer": (
            "Staff comparison tool only — not a commitment of aid. "
            "Factor max weights are editable by staff; award workflow hooks are separate."
        ),
    }


def _sort_key_for_ranking(score_payload: dict[str, Any]) -> tuple:
    sk = score_payload.get("sort_keys") or {}
    gpa = sk.get("gpa_for_rank")
    gpa_typed = float(gpa) if gpa is not None else -1.0
    sub = sk.get("submitted_at") or ""
    cre = sk.get("created_at") or ""
    return (-score_payload["total_points"], -gpa_typed, sub, cre)


@dataclass
class RankedApplication:
    application: Any
    score: dict[str, Any]
    rank: int


def rank_applications_for_scholarship(
    applications: Iterable,
) -> list[RankedApplication]:
    """Attach scores and stable ranks (1 = highest points)."""
    items: list[RankedApplication] = []
    for app in applications:
        payload = compute_scholarship_allocation_score(app)
        items.append(RankedApplication(application=app, score=payload, rank=0))
    items.sort(key=lambda x: _sort_key_for_ranking(x.score))
    for i, row in enumerate(items, start=1):
        row.rank = i
    return items


def build_scholarship_scores_table(
    applications_queryset,
) -> tuple[list[str], list[list[Any]]]:
    """Headers and row values for CSV / Excel / PDF exports."""
    ranked = rank_applications_for_scholarship(applications_queryset)
    headers = (
        [
            "rank",
            "application_id",
            "student_email",
            "student_name",
            "status",
            "withdrawn",
            "total_points",
            "max_points",
            "ruleset_id",
        ]
        + [f"factor_{fid}" for fid in FACTOR_IDS]
        + ["factor_details_json"]
    )
    rows: list[list[Any]] = []
    for row in ranked:
        app = row.application
        sc = row.score
        by_id = {f["id"]: f for f in sc["factors"]}
        student = app.student
        name = student.get_full_name().strip() or student.username
        status_name = app.status.name if app.status else ""
        rows.append(
            [
                row.rank,
                str(app.id),
                student.email,
                name,
                status_name,
                "yes" if app.withdrawn else "no",
                sc["total_points"],
                sc["max_points"],
                sc["ruleset_id"],
            ]
            + [round(by_id[fid]["points"], 2) for fid in FACTOR_IDS]
            + [str({fid: by_id[fid]["detail"] for fid in FACTOR_IDS})],
        )
    return headers, rows


def build_scholarship_scores_csv(applications_queryset) -> str:
    """CSV text for a program cohort (includes rank and factor columns)."""
    headers, rows = build_scholarship_scores_table(applications_queryset)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    for r in rows:
        writer.writerow(r)
    return buffer.getvalue()


def render_scholarship_scores_xlsx(applications_queryset) -> bytes:
    from openpyxl import Workbook

    headers, rows = build_scholarship_scores_table(applications_queryset)
    wb = Workbook()
    ws = wb.active
    ws.title = "Scores"
    ws.append(headers)
    for r in rows:
        ws.append(list(r))
    bio = BytesIO()
    wb.save(bio)
    return bio.getvalue()


def render_scholarship_scores_pdf(
    applications_queryset,
    *,
    program_name: str = "",
) -> bytes:
    """Landscape PDF with scores table (omits long JSON column; use CSV/XLSX for full text)."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    headers, rows = build_scholarship_scores_table(applications_queryset)
    pdf_headers = headers[:-1]
    pdf_rows = [r[:-1] for r in rows]
    data = [pdf_headers] + [[str(c) for c in r] for r in pdf_rows]

    buffer = BytesIO()
    page = landscape(letter)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=page,
        rightMargin=28,
        leftMargin=28,
        topMargin=36,
        bottomMargin=32,
    )
    styles = getSampleStyleSheet()
    story = []
    title = "Scholarship allocation scores"
    if program_name:
        title += f" — {program_name}"
    story.append(Paragraph(title, styles["Title"]))
    cfg = get_active_scholarship_ruleset_config()
    story.append(
        Paragraph(
            f"Ruleset <b>{cfg['ruleset_id']}</b>. Per-factor narrative text: export CSV or Excel "
            "(column <i>factor_details_json</i>).",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 8))

    tw = page[0] - 56
    nc = len(pdf_headers)
    col_w = tw / nc
    col_widths = [col_w] * nc

    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 6),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f8f9fa")],
                ),
            ]
        )
    )
    story.append(tbl)
    doc.build(story)
    return buffer.getvalue()


def scholarship_scores_export_response(
    program_id,
    applications_queryset,
    *,
    export_format: str = "csv",
    program_name: str = "",
) -> HttpResponse:
    """Attachment response: ``csv`` (default), ``xlsx``, or ``pdf``."""
    fmt = (export_format or "csv").lower().strip()
    base = f"scholarship-scores-{program_id}"
    if fmt == "csv":
        csv_text = build_scholarship_scores_csv(applications_queryset)
        resp = HttpResponse(csv_text, content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="{base}.csv"'
        return resp
    if fmt == "xlsx":
        body = render_scholarship_scores_xlsx(applications_queryset)
        resp = HttpResponse(
            body,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        resp["Content-Disposition"] = f'attachment; filename="{base}.xlsx"'
        return resp
    if fmt == "pdf":
        body = render_scholarship_scores_pdf(
            applications_queryset, program_name=program_name or ""
        )
        resp = HttpResponse(body, content_type="application/pdf")
        resp["Content-Disposition"] = f'attachment; filename="{base}.pdf"'
        return resp
    raise ValueError(
        f"Unsupported export_format: {export_format!r} (use csv, xlsx, or pdf)."
    )
