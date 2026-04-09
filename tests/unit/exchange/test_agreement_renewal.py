"""Tests for exchange agreement renewal workflow."""

from datetime import date, timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from accounts.models import Role
from documents.models import ExchangeAgreementDocument
from exchange.agreement_renewal import AgreementRenewalService
from exchange.models import ExchangeAgreement, Program

User = get_user_model()


@pytest.fixture
def coordinator_user(db):
    u = User.objects.create_user(
        username="coord_ren", email="cr@example.com", password="pass12345"
    )
    role, _ = Role.objects.get_or_create(name="coordinator")
    u.roles.add(role)
    return u


@pytest.fixture
def active_agreement(db):
    today = date.today()
    return ExchangeAgreement.objects.create(
        title="Accord X",
        partner_institution_name="Partner U",
        status=ExchangeAgreement.Status.ACTIVE,
        start_date=today - timedelta(days=30),
        end_date=today + timedelta(days=200),
    )


@pytest.mark.django_db
def test_mark_renewal_pending_sets_status_and_date(active_agreement):
    due = date.today() + timedelta(days=14)
    with patch("exchange.agreement_renewal._notify_staff"):
        AgreementRenewalService.mark_renewal_pending(
            active_agreement, renewal_follow_up_due=due
        )
    active_agreement.refresh_from_db()
    assert active_agreement.status == ExchangeAgreement.Status.RENEWAL_PENDING
    assert active_agreement.renewal_follow_up_due == due


@pytest.mark.django_db
def test_mark_renewal_pending_rejects_draft(active_agreement):
    active_agreement.status = ExchangeAgreement.Status.DRAFT
    active_agreement.save()
    with pytest.raises(ValueError, match="renewal"):
        AgreementRenewalService.mark_renewal_pending(active_agreement, notify=False)


@pytest.mark.django_db
def test_create_successor_links_programs_and_rollover(coordinator_user, active_agreement):
    today = date.today()
    prog = Program.objects.create(
        name="P1",
        description="d",
        start_date=today + timedelta(days=10),
        end_date=today + timedelta(days=300),
    )
    active_agreement.programs.add(prog)
    f = SimpleUploadedFile("sig.pdf", b"%PDF-1.4 renewal test", content_type="application/pdf")
    ExchangeAgreementDocument.objects.create(
        agreement=active_agreement,
        category=ExchangeAgreementDocument.Category.SIGNED_COPY,
        title="Signed",
        file=f,
        uploaded_by=coordinator_user,
    )

    with patch("exchange.agreement_renewal._notify_staff"):
        successor = AgreementRenewalService.create_renewal_successor(
            active_agreement, coordinator_user, copy_documents=True, notify=False
        )

    assert successor.status == ExchangeAgreement.Status.DRAFT
    assert successor.renewed_from_id == active_agreement.id
    assert list(successor.programs.all()) == [prog]
    rolled = successor.repository_documents.all()
    assert rolled.count() == 1
    assert "Rolled over from predecessor" in rolled[0].notes


@pytest.mark.django_db
def test_create_successor_blocks_second_draft(coordinator_user, active_agreement):
    with patch("exchange.agreement_renewal._notify_staff"):
        AgreementRenewalService.create_renewal_successor(
            active_agreement, coordinator_user, copy_documents=False, notify=False
        )
    with pytest.raises(ValueError, match="draft renewal successor"):
        AgreementRenewalService.create_renewal_successor(
            active_agreement, coordinator_user, copy_documents=False, notify=False
        )
