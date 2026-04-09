from django.core.management import call_command
from django.test import TestCase

from accounts.models import User
from documents.models import Document
from exchange.demo_seed import (
    DEMO_AGREEMENT_SPECS,
    DEMO_APPLICATION_SPECS,
    DEMO_PROGRAM_SPECS,
    DEMO_USER_SPECS,
)
from exchange.models import Application, Comment, ExchangeAgreement, Program, TimelineEvent
from notifications.models import Notification


class TestSeedDemoReadinessCommand(TestCase):
    def test_seed_demo_readiness_creates_full_demo_dataset(self):
        call_command("seed_demo_readiness")

        self.assertEqual(
            User.objects.filter(
                username__in=[spec["username"] for spec in DEMO_USER_SPECS]
            ).count(),
            len(DEMO_USER_SPECS),
        )
        self.assertEqual(
            Program.objects.filter(
                name__in=[spec["name"] for spec in DEMO_PROGRAM_SPECS]
            ).count(),
            len(DEMO_PROGRAM_SPECS),
        )
        self.assertEqual(
            Application.objects.filter(
                student__username__in=[spec["username"] for spec in DEMO_USER_SPECS]
            ).count(),
            len(DEMO_APPLICATION_SPECS),
        )

        statuses = set(
            Application.objects.filter(
                student__username__in=[spec["username"] for spec in DEMO_USER_SPECS]
            ).values_list("status__name", flat=True)
        )
        self.assertEqual(
            statuses,
            {spec["status"] for spec in DEMO_APPLICATION_SPECS},
        )

        self.assertGreaterEqual(Document.objects.count(), len(DEMO_APPLICATION_SPECS))
        self.assertEqual(
            ExchangeAgreement.objects.filter(
                internal_reference__in=[
                    s["internal_reference"] for s in DEMO_AGREEMENT_SPECS
                ]
            ).count(),
            len(DEMO_AGREEMENT_SPECS),
        )
        active_demo = ExchangeAgreement.objects.filter(
            internal_reference="DEMO-SEED-AGR-001",
            status=ExchangeAgreement.Status.ACTIVE,
        ).first()
        self.assertIsNotNone(active_demo)
        self.assertEqual(active_demo.programs.count(), 1)
        self.assertGreater(Comment.objects.count(), 0)
        self.assertGreater(TimelineEvent.objects.count(), 0)
        self.assertGreater(Notification.objects.filter(is_read=False).count(), 0)

    def test_seed_demo_readiness_is_idempotent_for_core_records(self):
        call_command("seed_demo_readiness")
        call_command("seed_demo_readiness")

        self.assertEqual(
            User.objects.filter(
                username__in=[spec["username"] for spec in DEMO_USER_SPECS]
            ).count(),
            len(DEMO_USER_SPECS),
        )
        self.assertEqual(
            Application.objects.filter(
                student__username__in=[spec["username"] for spec in DEMO_USER_SPECS]
            ).count(),
            len(DEMO_APPLICATION_SPECS),
        )
        self.assertEqual(
            ExchangeAgreement.objects.filter(
                internal_reference__in=[
                    s["internal_reference"] for s in DEMO_AGREEMENT_SPECS
                ]
            ).count(),
            len(DEMO_AGREEMENT_SPECS),
        )
