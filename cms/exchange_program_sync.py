"""Sync exchange.Program operational fields with Wagtail ProgramPage (admin workflow)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional, Tuple

from django.db import transaction
from django.utils.text import slugify
from wagtail.actions.unpublish_page import UnpublishPageAction

if TYPE_CHECKING:
    from django.contrib.auth import get_user_model

    User = get_user_model()
    from exchange.models import Program


def _duration_label(program: "Program") -> str:
    return f"{program.start_date:%b %d, %Y} – {program.end_date:%b %d, %Y}"


def get_program_index_page():
    """First ProgramIndexPage in the tree (prefers a live page)."""
    from cms.models import ProgramIndexPage

    qs = ProgramIndexPage.objects.order_by("path")
    live = qs.live().first()
    if live:
        return live
    return qs.first()


def _unique_slug_under(parent, base: str) -> str:
    from cms.models import ProgramPage

    slug_base = (slugify(base) or "program")[:180]
    candidate = slug_base
    n = 2
    while ProgramPage.objects.child_of(parent).filter(slug=candidate).exists():
        suffix = f"-{n}"
        candidate = f"{slug_base[: 200 - len(suffix)]}{suffix}"
        n += 1
    return candidate


def _apply_operational_fields(program: "Program", page) -> None:
    page.title = program.name
    desc = (program.description or "").strip()
    page.introduction = desc[:500]
    page.language = (program.required_language or "")[:100]
    page.application_deadline = program.application_deadline
    page.duration = _duration_label(program)[:100]


def create_draft_program_page_for_program(program: "Program", user: Optional["User"] = None):
    """
    Add a draft ProgramPage under the primary ProgramIndexPage and link this program.
    Raises ValueError if no index exists or a page is already linked.
    """
    from cms.models import ProgramPage

    if ProgramPage.objects.filter(program=program).exists():
        raise ValueError("This program already has a linked CMS program page.")

    index = get_program_index_page()
    if not index:
        raise ValueError(
            "No ProgramIndexPage found. Create one in Wagtail before linking programs."
        )

    slug = _unique_slug_under(index, program.name)

    with transaction.atomic():
        page = ProgramPage(
            title=program.name,
            slug=slug,
            introduction=(program.description or "")[:500],
            body=[],
            language=(program.required_language or "")[:100],
            application_deadline=program.application_deadline,
            duration=_duration_label(program)[:100],
            program=program,
        )
        index.add_child(instance=page)
        page = page.specific
        _apply_operational_fields(program, page)
        page.save()
        page.save_revision(user=user)
        page.refresh_from_db()
        page = page.specific
        # Workflow/moderation can mark new pages live; keep these as drafts for editor review.
        if page.live:
            UnpublishPageAction(page, user=user).execute(skip_permission_checks=True)

    return page.specific


def sync_program_page_operational_fields_and_publish(
    program: "Program", user: Optional["User"] = None
) -> Tuple[Literal["updated", "missing"], Optional[object]]:
    """
    Push Program name, summary, language, dates to the linked ProgramPage.
    If the page is live, publish a new revision so the public site updates.
    """
    from cms.models import ProgramPage

    page = ProgramPage.objects.filter(program=program).first()
    if not page:
        return "missing", None

    was_live = page.live
    page = page.specific
    _apply_operational_fields(program, page)
    page.save()
    revision = page.save_revision(user=user)
    if was_live:
        revision.publish(user=user, skip_permission_checks=True)
    return "updated", page
