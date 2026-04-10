"""
Structured eligibility evaluation for programs (rules engine).

Rules are evaluated in fixed order; each produces a ``rules`` row for APIs and audits.
``ApplicationService.check_eligibility`` raises ``ValueError`` with the same aggregate
message as before when any rule fails.

Program fields remain the source of truth; rules are code-defined. Future phases may
load rule configuration from the database or admin UI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

from accounts.models import Profile, User
from exchange.models import Application, Program


def _norm(s: str | None) -> str:
    return (s or "").strip().casefold()


CEFR_ORDER = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}


@dataclass
class RuleOutcome:
    """Single rule evaluation result."""

    rule_id: str
    passed: bool
    skipped: bool = False
    message: str | None = None


@dataclass
class EligibilityEvaluation:
    eligible: bool
    failures: list[str] = field(default_factory=list)
    rules: list[RuleOutcome] = field(default_factory=list)

    def rules_as_dicts(self) -> list[dict[str, Any]]:
        return [
            {
                "id": r.rule_id,
                "passed": r.passed,
                "skipped": r.skipped,
                **({"message": r.message} if r.message else {}),
            }
            for r in self.rules
        ]


def _student_speaks_required_language(profile, required: str) -> bool:
    if not (required or "").strip():
        return True
    req = _norm(required)
    if profile.language and _norm(profile.language) == req:
        return True
    for row in profile.additional_languages or []:
        if not isinstance(row, dict):
            continue
        name = (row.get("name") or "").strip()
        if name and _norm(name) == req:
            return True
    return False


def _effective_language_level_for_program(profile, program: Program) -> str | None:
    """
    CEFR level used when comparing to ``program.min_language_level``.

    If a required language is set, prefer the level from the matching primary or
    additional-language row; otherwise fall back to the profile's primary level
    (legacy behaviour when only ``min_language_level`` is set).
    """
    req = (program.required_language or "").strip()
    if req:
        if profile.language and _norm(profile.language) == _norm(req):
            return (profile.language_level or "").strip() or None
        for row in profile.additional_languages or []:
            if not isinstance(row, dict):
                continue
            name = (row.get("name") or "").strip()
            if not name or _norm(name) != _norm(req):
                continue
            lv = row.get("level")
            if lv is None or lv == "":
                return None
            return str(lv).strip()
    return (profile.language_level or "").strip() or None


def _rule_application_window(_profile, program: Program, application=None) -> RuleOutcome:
    """Gate on ``Program.application_open_date`` / ``application_deadline`` when either is set."""
    if not program.application_open_date and not program.application_deadline:
        return RuleOutcome("application_window", passed=True, skipped=True)
    status = program.get_application_window_status()
    if status["is_open"]:
        return RuleOutcome("application_window", passed=True)
    return RuleOutcome(
        "application_window",
        passed=False,
        message=status["message"],
    )


def _rule_gpa(profile, program: Program, application=None) -> RuleOutcome:
    if not (hasattr(program, "min_gpa") and program.min_gpa):
        return RuleOutcome("gpa", passed=True, skipped=True)
    # Legacy parity: if student has no GPA value, the minimum-GPA rule is not applied.
    if profile.gpa is None:
        return RuleOutcome("gpa", passed=True, skipped=True)
    if profile.grade_scale:
        student_gpa_equivalent = profile.get_gpa_equivalent()
        if student_gpa_equivalent < program.min_gpa:
            return RuleOutcome(
                "gpa",
                passed=False,
                message=(
                    f"GPA below program minimum. Your GPA equivalent: {student_gpa_equivalent:.2f}, "
                    f"Required: {program.min_gpa:.2f}"
                ),
            )
    elif profile.gpa < program.min_gpa:
        return RuleOutcome(
            "gpa",
            passed=False,
            message=(
                f"GPA below program minimum. Your GPA: {profile.gpa:.2f}, "
                f"Required: {program.min_gpa:.2f}"
            ),
        )
    return RuleOutcome("gpa", passed=True)


def _rule_required_language(profile, program: Program, application=None) -> RuleOutcome:
    if not (program.required_language or "").strip():
        return RuleOutcome("required_language", passed=True, skipped=True)
    if _student_speaks_required_language(profile, program.required_language):
        return RuleOutcome("required_language", passed=True)
    return RuleOutcome(
        "required_language",
        passed=False,
        message=(
            f"Language requirement not met. Required: {program.required_language}, "
            f"Your language: {profile.language or 'Not specified'}"
        ),
    )


def _rule_language_proficiency(profile, program: Program, application=None) -> RuleOutcome:
    if not (program.min_language_level or "").strip():
        return RuleOutcome("language_proficiency", passed=True, skipped=True)
    level = _effective_language_level_for_program(profile, program)
    required = program.min_language_level
    student_rank = CEFR_ORDER.get(level or "", 0)
    required_rank = CEFR_ORDER.get(required, 0)
    if not level:
        return RuleOutcome(
            "language_proficiency",
            passed=False,
            message=f"Language proficiency not specified. Required: {required}",
        )
    if student_rank < required_rank:
        return RuleOutcome(
            "language_proficiency",
            passed=False,
            message=(
                f"Language proficiency below requirement. "
                f"Required: {required}, "
                f"Your level: {level}"
            ),
        )
    return RuleOutcome("language_proficiency", passed=True)


def _rule_age(profile, program: Program, application=None) -> RuleOutcome:
    if not (program.min_age or program.max_age):
        return RuleOutcome("age", passed=True, skipped=True)
    # Legacy parity: age rules only run when date_of_birth is set (otherwise silently ignored).
    if not profile.date_of_birth:
        return RuleOutcome("age", passed=True, skipped=True)
    today = date.today()
    dob = profile.date_of_birth
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    if program.min_age and age < program.min_age:
        return RuleOutcome(
            "age",
            passed=False,
            message=f"Age below minimum requirement. Your age: {age}, Required: {program.min_age}+",
        )
    if program.max_age and age > program.max_age:
        return RuleOutcome(
            "age",
            passed=False,
            message=f"Age above maximum requirement. Your age: {age}, Maximum: {program.max_age}",
        )
    return RuleOutcome("age", passed=True)


def _rule_required_documents(
    _profile, program: Program, application: Application | None
) -> RuleOutcome:
    """Program required document types must be approved on the given application (submit parity)."""
    if not program.required_document_types.exists():
        return RuleOutcome("required_documents", passed=True, skipped=True)
    if application is None:
        return RuleOutcome("required_documents", passed=True, skipped=True)
    if application.program_id != program.pk:
        return RuleOutcome("required_documents", passed=True, skipped=True)

    from documents.services import DocumentService

    summary = DocumentService.build_application_document_checklist(application)
    if summary["complete"]:
        return RuleOutcome("required_documents", passed=True)
    problems = [
        f"{item['name']} ({item['status']})"
        for item in summary["items"]
        if item["status"] != "approved"
    ]
    return RuleOutcome(
        "required_documents",
        passed=False,
        message="Required documents are not all approved yet: " + "; ".join(problems),
    )


def evaluate_eligibility(
    student: User,
    program: Program,
    application: Application | None = None,
) -> EligibilityEvaluation:
    """
    Run all eligibility rules; return structured outcome (no exceptions for failures).

    Profile is loaded with a queryset read so results are not stale when the ``User``
    instance still holds a cached ``profile`` from an earlier access (e.g. signals on
    user create followed by ``Profile.objects.update_or_create``).
    """
    profile = Profile.objects.filter(user_id=student.pk).first()
    if not profile:
        return EligibilityEvaluation(
            eligible=False,
            failures=["Student profile is missing."],
            rules=[
                RuleOutcome("profile", passed=False, message="Student profile is missing."),
            ],
        )

    runners: list = [
        _rule_application_window,
        _rule_gpa,
        _rule_required_language,
        _rule_language_proficiency,
        _rule_age,
    ]
    if program.required_document_types.exists():
        runners.append(_rule_required_documents)

    rules: list[RuleOutcome] = []
    failures: list[str] = []
    for fn in runners:
        out = fn(profile, program, application)
        rules.append(out)
        if not out.skipped and not out.passed and out.message:
            failures.append(out.message)

    return EligibilityEvaluation(eligible=len(failures) == 0, failures=failures, rules=rules)


def checks_passed_labels(program: Program) -> list[str | None]:
    """Legacy ``checks_passed`` shape: which requirement dimensions apply to the program."""
    labels: list[str | None] = [
        "Application window"
        if (program.application_open_date or program.application_deadline)
        else None,
        "GPA requirement" if program.min_gpa else None,
        "Language requirement" if program.required_language else None,
        "Language proficiency" if program.min_language_level else None,
        "Age requirements" if (program.min_age or program.max_age) else None,
    ]
    if getattr(program, "pk", None) and program.required_document_types.exists():
        labels.append("Required documents")
    return labels
