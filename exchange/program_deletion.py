"""Helpers for previewing cascade impact when deleting a Program."""

from __future__ import annotations

from django.contrib.admin.utils import NestedObjects
from django.db import router
from django.utils.text import capfirst

from exchange.models import Program

# Prefer a stable, user-facing order for common cascade targets.
_RELATED_DISPLAY_ORDER = (
    "exchange.application",
    "documents.document",
    "exchange.hostinstitution",
    "exchange.hostschool",
    "exchange.hostacademicprogram",
    "exchange.hostsubject",
    "exchange.nominationcycle",
    "exchange.nominationpartnerallocation",
    "exchange.programdocumentrequirement",
    "exchange.programfieldrequirement",
    "application_forms.formsubmission",
    "exchange.comment",
    "exchange.timelineevent",
    "exchange.applicationsubjectselection",
    "exchange.applicationsubjectplanversion",
    "exchange.scholarshipaward",
    "exchange.scholarshipdisbursement",
)


def _model_sort_key(label: str) -> tuple[int, str]:
    try:
        return (_RELATED_DISPLAY_ORDER.index(label), label)
    except ValueError:
        return (len(_RELATED_DISPLAY_ORDER), label)


def get_program_deletion_impact(program: Program) -> dict:
    """
    Return counts of objects that would be cascade-deleted with ``program``.

    Uses Django's NestedObjects collector (same mechanism as admin delete).
    """
    using = router.db_for_write(program.__class__)
    collector = NestedObjects(using=using)
    collector.collect([program])

    related: list[dict] = []
    total = 0
    for model, objs in collector.model_objs.items():
        count = len(objs)
        if count == 0:
            continue
        label = model._meta.label_lower
        # Always include the program itself as the root object.
        if model is Program:
            continue
        related.append(
            {
                "model": label,
                "label": str(capfirst(model._meta.verbose_name_plural)),
                "count": count,
            }
        )
        total += count

    related.sort(key=lambda row: _model_sort_key(row["model"]))

    protected = [
        {
            "model": obj._meta.label_lower,
            "label": str(capfirst(obj._meta.verbose_name)),
            "repr": str(obj),
        }
        for obj in collector.protected
    ]

    return {
        "program": {
            "id": str(program.pk),
            "name": program.name,
        },
        "can_delete": not protected,
        "related": related,
        "protected": protected,
        "total_related": total,
    }
