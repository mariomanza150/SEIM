"""
Staff workflow: mark agreements for renewal and create draft successor records.

Repository documents on the predecessor can be copied to the new agreement (file rollover).
"""

from __future__ import annotations

import os
from datetime import date

from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from documents.models import ExchangeAgreementDocument
from notifications.services import NotificationService

from .models import ExchangeAgreement


def _notify_staff(title: str, message: str) -> None:
    recipients = User.objects.filter(roles__name__in=["admin", "coordinator"]).distinct()
    if not recipients:
        return
    NotificationService.send_bulk_notifications(
        recipients,
        title,
        message,
        notification_type="in_app",
        transactional_route_key="agreement_renewal_staff_bulk_in_app",
    )


def _rollover_repository_documents(
    source: ExchangeAgreement, target: ExchangeAgreement, uploaded_by: User
) -> int:
    n = 0
    for doc in source.repository_documents.all():
        with doc.file.open("rb") as src:
            content = ContentFile(src.read())
        name = os.path.basename(doc.file.name)
        suffix = f"\n\n[Rolled over from predecessor agreement {source.id}.]"
        nd = ExchangeAgreementDocument(
            agreement=target,
            category=doc.category,
            title=doc.title,
            notes=(doc.notes or "").strip() + suffix,
            uploaded_by=uploaded_by,
        )
        nd.file.save(name, content, save=True)
        n += 1
    return n


class AgreementRenewalService:
    """Renewal stages: ``renewal_pending`` + optional follow-up date; draft successor with rollover."""

    RENEWAL_SOURCE_STATUSES = frozenset(
        {
            ExchangeAgreement.Status.ACTIVE,
            ExchangeAgreement.Status.EXPIRED,
            ExchangeAgreement.Status.SUSPENDED,
            ExchangeAgreement.Status.RENEWAL_PENDING,
        }
    )

    @staticmethod
    @transaction.atomic
    def mark_renewal_pending(
        agreement: ExchangeAgreement,
        *,
        renewal_follow_up_due: date | None = None,
        notify: bool = True,
    ) -> ExchangeAgreement:
        if agreement.status not in AgreementRenewalService.RENEWAL_SOURCE_STATUSES:
            raise ValueError(
                "Only active, expired, suspended, or already renewal-pending agreements "
                "can be marked for renewal."
            )
        agreement.status = ExchangeAgreement.Status.RENEWAL_PENDING
        if renewal_follow_up_due is not None:
            agreement.renewal_follow_up_due = renewal_follow_up_due
        agreement.save(update_fields=["status", "renewal_follow_up_due", "updated_at"])
        if notify:
            _notify_staff(
                "Agreement marked renewal pending",
                f"{agreement.title} ({agreement.partner_institution_name}) is now renewal pending.",
            )
        return agreement

    @staticmethod
    @transaction.atomic
    def create_renewal_successor(
        agreement: ExchangeAgreement,
        user: User,
        *,
        copy_documents: bool = True,
        notify: bool = True,
    ) -> ExchangeAgreement:
        if agreement.status not in AgreementRenewalService.RENEWAL_SOURCE_STATUSES:
            raise ValueError("Cannot create a renewal successor from this agreement status.")
        if agreement.renewal_successors.filter(status=ExchangeAgreement.Status.DRAFT).exists():
            raise ValueError("A draft renewal successor for this agreement already exists.")

        successor = ExchangeAgreement.objects.create(
            title=f"{agreement.title} (Renewal draft)",
            partner_institution_name=agreement.partner_institution_name,
            partner_country=agreement.partner_country,
            partner_reference_id=agreement.partner_reference_id,
            internal_reference="",
            agreement_type=agreement.agreement_type,
            start_date=None,
            end_date=None,
            status=ExchangeAgreement.Status.DRAFT,
            notes=(
                f"Renewal draft created from agreement {agreement.id}. "
                f"Review dates and references before activation.\n\n"
            ),
            renewed_from=agreement,
        )
        successor.programs.set(agreement.programs.all())

        doc_count = 0
        if copy_documents:
            doc_count = _rollover_repository_documents(agreement, successor, user)

        if notify:
            _notify_staff(
                "Renewal draft agreement created",
                f"Draft successor for {agreement.title}: {successor.title}. "
                f"Repository documents copied: {doc_count}.",
            )

        return successor
