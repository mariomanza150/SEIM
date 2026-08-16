"""Fill a student profile so application create/E2E flows can run."""

from datetime import date
from decimal import Decimal

from accounts.models import AcademicLevel, HomeAcademicProgram, SchoolFaculty, Unidad
from grades.models import GradeScale


def complete_apply_profile(user) -> None:
    """Fill personal, academic, and eligibility fields required to start an application."""
    updates = {}
    if not (user.first_name or "").strip():
        updates["first_name"] = "Test"
    if not (user.middle_name or "").strip():
        updates["middle_name"] = "Q"
    if not (user.last_name or "").strip():
        updates["last_name"] = "User"
    if not (user.mothers_last_name or "").strip():
        updates["mothers_last_name"] = "Garcia"
    if updates:
        for field, value in updates.items():
            setattr(user, field, value)
        user.save(update_fields=list(updates))

    school, _ = SchoolFaculty.objects.get_or_create(name="Engineering")
    home_program, _ = HomeAcademicProgram.objects.get_or_create(
        name="Computer Science",
        defaults={"school": school},
    )
    if home_program.school_id != school.id:
        home_program.school = school
        home_program.save(update_fields=["school"])
    level, _ = AcademicLevel.objects.get_or_create(name="Undergraduate")
    unidad, _ = Unidad.objects.get_or_create(name="Ciudad Universitaria")
    scale, _ = GradeScale.objects.get_or_create(
        code="US_GPA_4",
        defaults={
            "name": "US GPA 4.0 Scale",
            "min_value": 0.0,
            "max_value": 4.0,
            "passing_value": 2.0,
        },
    )

    profile = user.profile
    digits = "".join(ch for ch in str(user.pk) if ch.isdigit())
    if len(digits) < 7:
        digits = f"{abs(hash(str(user.pk))) % 10_000_000:07d}"
    profile.matricula = digits[:12]
    profile.academic_level = level
    profile.school = school
    profile.unidad = unidad
    profile.home_academic_program = home_program
    profile.gender = profile.gender or "prefer_not_to_say"
    profile.gpa = 3.5 if profile.gpa is None else profile.gpa
    profile.language = (profile.language or "").strip() or "English"
    profile.language_level = (profile.language_level or "").strip() or "B2"
    profile.date_of_birth = profile.date_of_birth or date(2000, 1, 1)
    profile.birthplace = (profile.birthplace or "").strip() or "Monterrey"
    profile.postal_code = (profile.postal_code or "").strip() or "64000"
    profile.passport_number = (profile.passport_number or "").strip() or "P1234567"
    profile.mobile_phone = (profile.mobile_phone or "").strip() or "8112345678"
    profile.secondary_email = (profile.secondary_email or "").strip() or (
        f"alt-{user.username}@example.net"
    )
    profile.rfc = (profile.rfc or "").strip() or "XAXX010101000"
    profile.grade_scale = profile.grade_scale or scale
    if profile.credits_approved_percent is None:
        profile.credits_approved_percent = Decimal("70.00")
    profile.ingress_date = profile.ingress_date or date(2022, 8, 1)
    profile.save()
