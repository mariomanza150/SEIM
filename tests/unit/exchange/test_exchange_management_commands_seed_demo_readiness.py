from django.core.management import call_command
from django.test import TestCase

from accounts.models import AllowedEmailDomain, User
from application_forms.models import FormType
from documents.models import Document, DocumentResubmissionRequest, ExchangeAgreementDocument
from exchange.demo_seed import (
    DEMO_AGREEMENT_SPECS,
    DEMO_APPLICATION_SPECS,
    DEMO_CLOSED_WINDOW_PROGRAM,
    DEMO_ELIGIBILITY_RULESET_NAME,
    DEMO_FORM_NAME,
    DEMO_HOST_SPECS,
    DEMO_LIFECYCLE_PROGRAM,
    DEMO_PROGRAM_SPECS,
    DEMO_RESUBMIT_PROGRAM,
    DEMO_SUBMIT_GATE_PROGRAM,
    DEMO_USER_SPECS,
    DEMO_WORKFLOW_SLUG,
)
from exchange.models import (
    Application,
    Comment,
    EligibilityRuleSet,
    ExchangeAgreement,
    HostInstitution,
    PartnerContact,
    Program,
    SavedSearch,
    ScholarshipAward,
    TimelineEvent,
)
from grades.models import GradeTranslation
from notifications.models import Notification, Reminder
from workflows.models import WorkflowDefinition, WorkflowInstance


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
        student = User.objects.get(email="student@test.com")
        self.assertTrue(student.profile.is_ready_to_apply)
        self.assertTrue(student.is_email_verified)

        partner = User.objects.get(username="partner", email="partner@test.com")
        self.assertTrue(partner.is_email_verified)
        self.assertTrue(partner.has_role("partner"))
        self.assertFalse(partner.has_role("admin"))

        coordinator = User.objects.get(email="coordinator@test.com")
        self.assertTrue(coordinator.is_email_verified)
        self.assertTrue(coordinator.has_role("coordinator"))
        self.assertFalse(coordinator.has_role("admin"))
        self.assertFalse(coordinator.has_role("partner"))
        self.assertFalse(coordinator.is_admin)
        self.assertTrue(
            Application.objects.filter(
                student__username="student_waitlist", status__name="waitlist"
            ).exists()
        )
        self.assertGreaterEqual(
            HostInstitution.objects.filter(program__name__in=DEMO_HOST_SPECS).count(),
            6,
        )
        hosted_apps = Application.objects.filter(
            student__username__in=[spec["username"] for spec in DEMO_USER_SPECS]
        ).exclude(host_institution=None)
        self.assertEqual(hosted_apps.count(), len(DEMO_APPLICATION_SPECS))
        self.assertTrue(
            EligibilityRuleSet.objects.filter(
                name=DEMO_ELIGIBILITY_RULESET_NAME
            ).exists()
        )
        self.assertTrue(FormType.objects.filter(name=DEMO_FORM_NAME).exists())
        self.assertTrue(
            WorkflowDefinition.objects.filter(slug=DEMO_WORKFLOW_SLUG).exists()
        )
        self.assertGreater(WorkflowInstance.objects.count(), 0)
        self.assertGreater(ScholarshipAward.objects.count(), 0)
        self.assertTrue(
            PartnerContact.objects.filter(user__username="partner").exists()
        )
        self.assertGreater(ExchangeAgreementDocument.objects.count(), 0)
        self.assertGreater(SavedSearch.objects.count(), 0)
        self.assertGreater(Reminder.objects.count(), 0)
        self.assertGreater(GradeTranslation.objects.count(), 0)
        self.assertTrue(
            AllowedEmailDomain.objects.filter(name="test.com", is_active=True).exists()
        )
        daad = Program.objects.get(
            name="DAAD Exchange - Technical University of Munich, Germany"
        )
        self.assertEqual(daad.enrollment_capacity, 1)
        self.assertTrue(daad.coordinators.filter(username="coordinator").exists())

        closed = Program.objects.get(name=DEMO_CLOSED_WINDOW_PROGRAM)
        self.assertTrue(closed.is_active)
        self.assertFalse(closed.is_application_open())
        self.assertFalse(
            Application.objects.filter(program__name=DEMO_LIFECYCLE_PROGRAM).exists()
        )

        gate_app = Application.objects.get(
            student__username="student", program__name=DEMO_SUBMIT_GATE_PROGRAM
        )
        self.assertEqual(gate_app.status.name, "draft")
        gate_docs = Document.objects.filter(application=gate_app)
        self.assertGreaterEqual(gate_docs.count(), 2)
        self.assertFalse(gate_docs.filter(is_valid=True).exists())

        self.assertTrue(
            DocumentResubmissionRequest.objects.filter(
                resolved=False,
                document__application__student__username="student",
                document__application__program__name=DEMO_RESUBMIT_PROGRAM,
            ).exists()
        )

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
