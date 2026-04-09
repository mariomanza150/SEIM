from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from exchange.filters import ExchangeAgreementFilter
from exchange.models import ExchangeAgreement, Program


class ExchangeAgreementModelTests(TestCase):
    def test_clean_rejects_end_before_start(self):
        today = timezone.localdate()
        a = ExchangeAgreement(
            title="Test",
            partner_institution_name="Partner U",
            start_date=today,
            end_date=today - timedelta(days=1),
            status=ExchangeAgreement.Status.DRAFT,
        )
        with self.assertRaises(ValidationError):
            a.full_clean()

    def test_str_contains_title_and_partner(self):
        a = ExchangeAgreement.objects.create(
            title="Framework 2025",
            partner_institution_name="Partner U",
            status=ExchangeAgreement.Status.DRAFT,
        )
        self.assertIn("Framework 2025", str(a))
        self.assertIn("Partner U", str(a))


class ExchangeAgreementFilterTests(TestCase):
    def test_expiring_within_days_limits_to_active_with_end_date(self):
        today = timezone.localdate()
        p = Program.objects.create(
            name="P1",
            description="d",
            start_date=today + timedelta(days=30),
            end_date=today + timedelta(days=200),
        )
        soon = ExchangeAgreement.objects.create(
            title="Soon",
            partner_institution_name="A",
            status=ExchangeAgreement.Status.ACTIVE,
            start_date=today - timedelta(days=10),
            end_date=today + timedelta(days=20),
        )
        soon.programs.add(p)
        later = ExchangeAgreement.objects.create(
            title="Later",
            partner_institution_name="B",
            status=ExchangeAgreement.Status.ACTIVE,
            start_date=today,
            end_date=today + timedelta(days=200),
        )
        draft = ExchangeAgreement.objects.create(
            title="Draft soon",
            partner_institution_name="C",
            status=ExchangeAgreement.Status.DRAFT,
            end_date=today + timedelta(days=5),
        )

        f = ExchangeAgreementFilter(
            data={"expiring_within_days": "30"},
            queryset=ExchangeAgreement.objects.all(),
        )
        self.assertTrue(f.is_valid(), f.errors)
        qs = f.qs
        self.assertEqual(list(qs), [soon])
        self.assertNotIn(later, qs)
        self.assertNotIn(draft, qs)
