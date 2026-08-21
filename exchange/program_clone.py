"""Shared helpers for cloning a program's requirement schedule."""

from __future__ import annotations

from exchange.models import ProgramDocumentRequirement, ProgramFieldRequirement


def copy_program_requirement_schedule(original, cloned) -> None:
    """Copy document and field requirement rows onto ``cloned``."""
    for req in original.program_document_requirements.all():
        ProgramDocumentRequirement.objects.create(
            program=cloned,
            document_type=req.document_type,
            is_required=req.is_required,
            required_from_status=req.required_from_status,
            deadline=req.deadline,
            deadline_days_before_program_deadline=req.deadline_days_before_program_deadline,
            deadline_days_after_program_start=req.deadline_days_after_program_start,
            instructions_override=req.instructions_override,
            sort_order=req.sort_order,
        )
    for row in original.field_requirements.all():
        ProgramFieldRequirement.objects.create(
            program=cloned,
            source=row.source,
            field_key=row.field_key,
            required_from_status=row.required_from_status,
        )
