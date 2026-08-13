"""Shared host-destination tree helpers for mobility apply-flow tests."""

from __future__ import annotations

from decimal import Decimal

from exchange.models import (
    HostAcademicProgram,
    HostInstitution,
    HostSchool,
    HostSubject,
    Program,
)


def attach_host_destination(
    program: Program,
    *,
    institution_name: str = "Host University",
    school_name: str = "Faculty of Engineering",
    academic_name: str = "Computer Science",
    academic_code: str = "CS",
    with_subject: bool = False,
) -> dict:
    """
    Create a consistent HostInstitution → HostSchool → HostAcademicProgram tree
    under ``program``. Optionally add one HostSubject.
    """
    institution = HostInstitution.objects.create(
        program=program,
        name=institution_name,
        country="MX",
        is_active=True,
    )
    school = HostSchool.objects.create(
        institution=institution,
        name=school_name,
        is_active=True,
    )
    academic = HostAcademicProgram.objects.create(
        school=school,
        name=academic_name,
        code=academic_code,
        is_active=True,
    )
    subject = None
    if with_subject:
        subject = HostSubject.objects.create(
            academic_program=academic,
            code="CS101",
            name="Algorithms",
            credits=Decimal("6.00"),
            is_active=True,
        )
    return {
        "institution": institution,
        "school": school,
        "academic": academic,
        "subject": subject,
    }


def apply_host_destination(application, host_tree: dict) -> None:
    """Assign host FKs from ``attach_host_destination`` onto an Application."""
    application.host_institution = host_tree["institution"]
    application.host_school = host_tree["school"]
    application.host_academic_program = host_tree["academic"]
    application.save(
        update_fields=[
            "host_institution",
            "host_school",
            "host_academic_program",
        ]
    )
