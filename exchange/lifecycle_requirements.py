"""Schedule when documents and fields become mandatory on the success pipeline.

``ApplicationStatus.order`` is not a pipeline rank. Side statuses never inherit
onward requirements.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

from django.core.exceptions import ValidationError as DjangoValidationError

SUCCESS_PIPELINE: tuple[str, ...] = (
    "draft",
    "submitted",
    "under_review",
    "nominated",
    "approved",
    "completed",
)

SIDE_STATUSES: frozenset[str] = frozenset(
    {"waitlist", "rejected", "cancelled", "withdrawn"}
)

SUBMITTED = "submitted"
DRAFT = "draft"

APPLY_START_PROFILE_FIELDS: tuple[str, ...] = (
    "first_name",
    "last_name",
    "matricula",
    "academic_level",
    "school",
    "unidad",
    "home_academic_program",
    "gender",
    "date_of_birth",
    "birthplace",
    "postal_code",
    "mobile_phone",
    "secondary_email",
    "gpa",
    "grade_scale",
    "language",
    "credits_approved_percent",
    "semester",
)

PROFILE_FIELD_CATALOG: tuple[str, ...] = APPLY_START_PROFILE_FIELDS + (
    "passport_number",
    "rfc",
    "bank_institution",
    "clabe",
)

APPLICATION_FIELD_CATALOG: tuple[str, ...] = (
    "host_institution",
    "host_school",
    "host_academic_program",
    "host_destination",
)

SOURCE_PROFILE = "profile"
SOURCE_APPLICATION = "application"
SOURCE_FORM = "form"

_ELIGIBILITY_APPLY_KEYS = frozenset(
    {
        "gpa",
        "grade_scale",
        "language",
        "credits_approved_percent",
        "semester",
    }
)


@dataclass(frozen=True)
class LifecycleItem:
    kind: str
    key: str
    name: str
    required_from: str | None
    due_now: bool
    satisfied: bool
    status: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LifecycleEvaluation:
    current_status: str
    items: list[LifecycleItem]

    def missing_now(self) -> list[LifecycleItem]:
        return [i for i in self.items if i.due_now and not i.satisfied]

    def missing_later(self) -> list[LifecycleItem]:
        cur = pipeline_index(self.current_status)
        out: list[LifecycleItem] = []
        for item in self.items:
            if item.satisfied or not item.required_from:
                continue
            if item.due_now:
                continue
            req_i = pipeline_index(item.required_from)
            if cur is None:
                if req_i is not None:
                    out.append(item)
                continue
            if req_i is not None and req_i > cur:
                out.append(item)
        return out

    def payload(self) -> dict[str, Any]:
        return {
            "current_status": self.current_status,
            "missing_now": [i.as_dict() for i in self.missing_now()],
            "missing_later": [i.as_dict() for i in self.missing_later()],
            "items": [i.as_dict() for i in self.items],
        }


def pipeline_index(status_name: str | None) -> int | None:
    name = (status_name or "").strip()
    try:
        return SUCCESS_PIPELINE.index(name)
    except ValueError:
        return None


def is_due(required_from: str | None, current_status: str | None) -> bool:
    """True when ``current_status`` is on the success pipeline at or after ``required_from``."""
    if not required_from:
        return False
    current = (current_status or "").strip()
    if current in SIDE_STATUSES:
        return False
    req_i = pipeline_index(required_from)
    cur_i = pipeline_index(current)
    if req_i is None or cur_i is None:
        return False
    return cur_i >= req_i


def document_completeness_gate(status_name: str | None) -> str:
    """Status used to count checklist completeness.

    Documents cannot be due at draft; the student submit gate is ``submitted``.
    Later pipeline statuses use the live status so staff see due-now items.
    """
    name = (status_name or "").strip() or DRAFT
    if name == DRAFT:
        return SUBMITTED
    return name


def effective_document_required_from(requirement) -> str | None:
    """None = optional throughout; otherwise a pipeline status name."""
    if not getattr(requirement, "is_required", True):
        return None
    rel = getattr(requirement, "required_from_status", None)
    name = getattr(rel, "name", None) if rel is not None else None
    if not name:
        return SUBMITTED
    if name == DRAFT:
        return SUBMITTED
    return name


def document_is_due(requirement, current_status: str | None) -> bool:
    return is_due(effective_document_required_from(requirement), current_status)


def form_schema_field_keys(program=None) -> list[str]:
    """JSON Schema property names on the program's ``application_form``."""
    if program is None:
        return []
    ft = getattr(program, "application_form", None)
    if ft is None:
        return []
    schema = getattr(ft, "schema", None) or {}
    properties = schema.get("properties") if isinstance(schema, dict) else None
    if not isinstance(properties, dict):
        return []
    return sorted(str(k) for k in properties.keys() if k)


def field_requirement_catalog(program=None) -> dict[str, list[str]]:
    return {
        SOURCE_PROFILE: list(PROFILE_FIELD_CATALOG),
        SOURCE_APPLICATION: list(APPLICATION_FIELD_CATALOG),
        SOURCE_FORM: form_schema_field_keys(program),
    }


def allowed_field_keys(source: str) -> frozenset[str] | None:
    if source == SOURCE_PROFILE:
        return frozenset(PROFILE_FIELD_CATALOG)
    if source == SOURCE_APPLICATION:
        return frozenset(APPLICATION_FIELD_CATALOG)
    if source == SOURCE_FORM:
        return None
    return frozenset()


def _blank(value: Any) -> bool:
    return value is None or not str(value).strip()


def profile_field_satisfied(profile, field_key: str) -> bool:
    if profile is None:
        return False
    user = getattr(profile, "user", None)
    if field_key == "first_name":
        return user is not None and not _blank(user.first_name)
    if field_key == "last_name":
        return user is not None and not _blank(user.last_name)
    if field_key == "matricula":
        return not _blank(getattr(profile, "matricula", None))
    if field_key == "academic_level":
        return bool(getattr(profile, "academic_level_id", None))
    if field_key == "school":
        return bool(getattr(profile, "school_id", None))
    if field_key == "unidad":
        return bool(getattr(profile, "unidad_id", None))
    if field_key == "home_academic_program":
        return bool(getattr(profile, "home_academic_program_id", None))
    if field_key == "gender":
        return not _blank(getattr(profile, "gender", None))
    if field_key == "date_of_birth":
        return bool(getattr(profile, "date_of_birth", None))
    if field_key == "birthplace":
        return not _blank(getattr(profile, "birthplace", None))
    if field_key == "postal_code":
        return not _blank(getattr(profile, "postal_code", None))
    if field_key == "mobile_phone":
        return not _blank(getattr(profile, "mobile_phone", None))
    if field_key == "secondary_email":
        return not _blank(getattr(profile, "secondary_email", None))
    if field_key == "gpa":
        return getattr(profile, "gpa", None) is not None
    if field_key == "grade_scale":
        return bool(getattr(profile, "grade_scale_id", None))
    if field_key == "language":
        return not _blank(getattr(profile, "language", None))
    if field_key == "credits_approved_percent":
        return getattr(profile, "credits_approved_percent", None) is not None
    if field_key == "semester":
        getter = getattr(profile, "get_effective_semester", None)
        if callable(getter):
            return getter() is not None
        return bool(getattr(profile, "ingress_date", None)) or (
            getattr(profile, "current_semester", None) is not None
        )
    if field_key == "passport_number":
        return not _blank(getattr(profile, "passport_number", None))
    if field_key == "rfc":
        return not _blank(getattr(profile, "rfc", None))
    if field_key == "bank_institution":
        return bool(getattr(profile, "bank_institution_id", None))
    if field_key == "clabe":
        digits = "".join(
            ch for ch in str(getattr(profile, "clabe", None) or "") if ch.isdigit()
        )
        return len(digits) == 18
    return not _blank(getattr(profile, field_key, None))


def application_field_satisfied(application, field_key: str) -> bool:
    if field_key == "host_destination":
        from exchange.models import validate_application_host_destination

        errors = validate_application_host_destination(
            application, require_complete=True
        )
        return not bool(errors)
    if field_key == "host_institution":
        return bool(getattr(application, "host_institution_id", None))
    if field_key == "host_school":
        return bool(getattr(application, "host_school_id", None))
    if field_key == "host_academic_program":
        return bool(getattr(application, "host_academic_program_id", None))
    return False


def _form_keys_satisfied(application, keys: Iterable[str]) -> dict[str, bool]:
    keys = [k for k in keys if k]
    result = {k: False for k in keys}
    if not keys:
        return result
    program = application.program
    if not getattr(program, "application_form_id", None):
        return result
    try:
        from application_forms.models import FormSubmission
        from application_forms.services import FormSubmissionService
        from exchange.services import ApplicationService
    except ImportError:
        return result

    ft = program.application_form
    sub = FormSubmission.objects.filter(application=application, form_type=ft).first()
    responses = (sub.responses or {}) if sub else {}
    properties = (ft.schema or {}).get("properties", {}) if ft.schema else {}
    vctx = ApplicationService._visibility_context_for_application(
        application, application.student
    )
    for key in keys:
        if key not in properties:
            result[key] = False
            continue
        try:
            FormSubmissionService.validate_responses(
                ft,
                responses,
                visibility_context=vctx,
                only_keys=[key],
            )
            result[key] = True
        except DjangoValidationError:
            result[key] = False
    return result


def draft_required_profile_keys(program=None) -> list[str]:
    """Profile keys required at apply-start (pipeline status ``draft``)."""
    required = list(APPLY_START_PROFILE_FIELDS)
    if program is None:
        return required
    from exchange.models import ProgramFieldRequirement

    rows = list(
        ProgramFieldRequirement.objects.filter(
            program=program, source=SOURCE_PROFILE
        ).select_related("required_from_status")
    )
    by_key = {row.field_key: row for row in rows}
    kept: list[str] = []
    for key in required:
        row = by_key.get(key)
        if row is None:
            kept.append(key)
            continue
        name = (
            row.required_from_status.name
            if row.required_from_status_id
            else None
        )
        if name == DRAFT:
            kept.append(key)
    extras = []
    for row in rows:
        if row.field_key in kept or row.field_key in required:
            continue
        name = (
            row.required_from_status.name
            if row.required_from_status_id
            else None
        )
        if name == DRAFT and row.field_key in PROFILE_FIELD_CATALOG:
            extras.append(row.field_key)
    return kept + extras


def due_profile_field_keys_for_user(user) -> list[str]:
    """Profile keys already due on any of the student's applications."""
    if user is None or not getattr(user, "pk", None):
        return []
    from exchange.models import Application, ProgramFieldRequirement

    apps = list(
        Application.objects.filter(student_id=user.pk).select_related(
            "status", "program"
        )
    )
    if not apps:
        return []
    program_ids = {a.program_id for a in apps}
    rows = list(
        ProgramFieldRequirement.objects.filter(
            program_id__in=program_ids, source=SOURCE_PROFILE
        ).select_related("required_from_status", "program")
    )
    by_program: dict[Any, list] = {}
    for row in rows:
        by_program.setdefault(row.program_id, []).append(row)
    due: list[str] = []
    seen: set[str] = set()
    for app in apps:
        status_name = app.status.name if app.status else ""
        for row in by_program.get(app.program_id, []):
            req_from = (
                row.required_from_status.name
                if row.required_from_status_id
                else None
            )
            if is_due(req_from, status_name) and row.field_key not in seen:
                seen.add(row.field_key)
                due.append(row.field_key)
    return due


def _is_student_only_actor(user) -> bool:
    if user is None or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return False
    has_any = getattr(user, "has_any_role", None)
    if callable(has_any) and has_any(["coordinator", "admin"]):
        return False
    has_role = getattr(user, "has_role", None)
    return bool(callable(has_role) and has_role("student"))


def evaluate(application, *, target_status: str | None = None) -> LifecycleEvaluation:
    """Missing/due items for the live status, or a proposed student transition."""
    from documents.models import DocumentType
    from documents.services import DocumentService
    from exchange.models import ProgramDocumentRequirement, ProgramFieldRequirement

    status_name = (target_status or "").strip() or (
        application.status.name if application.status else DRAFT
    )
    items: list[LifecycleItem] = []
    summary = DocumentService.build_application_document_checklist(application)
    by_type = {item["document_type_id"]: item for item in summary.get("items") or []}
    requirements = ProgramDocumentRequirement.objects.filter(
        program=application.program
    ).select_related("document_type", "required_from_status")
    for req in requirements:
        dt = req.document_type
        req_from = effective_document_required_from(req)
        due = is_due(req_from, status_name)
        entry = by_type.get(dt.id, {})
        st = entry.get("status") or "missing"
        satisfied = st in {"approved", "n_a"}
        if dt.submission_mode == DocumentType.SubmissionMode.INSTRUCTIONS_ONLY:
            satisfied = True
            st = "n_a"
        items.append(
            LifecycleItem(
                kind="document",
                key=dt.slug or str(dt.id),
                name=dt.name,
                required_from=req_from,
                due_now=due,
                satisfied=satisfied,
                status=st,
            )
        )

    field_rows = list(
        ProgramFieldRequirement.objects.filter(program=application.program)
        .select_related("required_from_status")
        .order_by("source", "field_key", "id")
    )
    profile = None
    if getattr(application, "student_id", None):
        from accounts.models import Profile

        profile = Profile.objects.filter(user_id=application.student_id).first()
    form_keys = [r.field_key for r in field_rows if r.source == SOURCE_FORM]
    form_ok = _form_keys_satisfied(application, form_keys)
    for row in field_rows:
        req_from = (
            row.required_from_status.name if row.required_from_status_id else None
        )
        due = is_due(req_from, status_name)
        if row.source == SOURCE_PROFILE:
            satisfied = profile_field_satisfied(profile, row.field_key)
            name = row.field_key
        elif row.source == SOURCE_APPLICATION:
            satisfied = application_field_satisfied(application, row.field_key)
            name = row.field_key
        else:
            satisfied = form_ok.get(row.field_key, False)
            name = row.field_key
        items.append(
            LifecycleItem(
                kind=row.source,
                key=row.field_key,
                name=name,
                required_from=req_from,
                due_now=due,
                satisfied=satisfied,
            )
        )
    return LifecycleEvaluation(current_status=status_name, items=items)


def missing_submit_documents(application) -> list[LifecycleItem]:
    return [
        item
        for item in evaluate(application, target_status=SUBMITTED).items
        if item.kind == "document" and item.due_now and not item.satisfied
    ]


def missing_submit_fields(application) -> list[LifecycleItem]:
    return [
        item
        for item in evaluate(application, target_status=SUBMITTED).items
        if item.kind != "document" and item.due_now and not item.satisfied
    ]


def student_submit_field_errors(application) -> list[str]:
    missing = missing_submit_fields(application)
    if not missing:
        return []
    labels = [f"{item.kind}:{item.key}" for item in missing]
    return [
        "Required fields are not complete for submit: " + "; ".join(labels)
    ]


def eligibility_apply_keys() -> frozenset[str]:
    return _ELIGIBILITY_APPLY_KEYS


def is_student_only_actor(user) -> bool:
    return _is_student_only_actor(user)


DUE_NOW_REMINDER_KIND = "lifecycle_due_now"
DUE_NOW_ROUTE_KEY = "lifecycle_requirements_due"


def _humanize_status_name(name: str) -> str:
    slug = (name or "").replace("_", " ").replace("-", " ").strip()
    return slug.title() if slug else name or ""


def notify_due_now_after_status_change(application) -> object | None:
    """Remind the student if the new status has due-now missing items.

    Deduplicates on application + status + missing item set so the same
    gate does not spam. Staff transitions are not blocked if this returns None.
    """
    from notifications.models import Notification
    from notifications.services import NotificationService

    student = getattr(application, "student", None)
    if student is None:
        return None
    evaluation = evaluate(application)
    missing = evaluation.missing_now()
    if not missing:
        return None
    status_name = evaluation.current_status
    item_keys = sorted(f"{item.kind}:{item.key}" for item in missing)
    fingerprint = "|".join(item_keys)
    already = Notification.objects.filter(
        recipient_id=student.id,
        data__kind=DUE_NOW_REMINDER_KIND,
        data__application_id=str(application.id),
        data__status=status_name,
        data__item_fingerprint=fingerprint,
    ).exists()
    if already:
        return None
    labels = [item.name or item.key for item in missing]
    program = getattr(application, "program", None)
    program_name = getattr(program, "name", "") or "your program"
    message = (
        f"Your application for {program_name} is now "
        f"{_humanize_status_name(status_name)}. Still required: "
        + ", ".join(labels)
        + "."
    )
    return NotificationService.send_notification(
        student,
        "Requirements due",
        message,
        notification_type="both",
        action_url=f"/applications/{application.id}/",
        action_text="View Application",
        category="warning",
        settings_category="applications",
        transactional_route_key=DUE_NOW_ROUTE_KEY,
        data={
            "kind": DUE_NOW_REMINDER_KIND,
            "application_id": str(application.id),
            "status": status_name,
            "items": item_keys,
            "item_fingerprint": fingerprint,
        },
    )
