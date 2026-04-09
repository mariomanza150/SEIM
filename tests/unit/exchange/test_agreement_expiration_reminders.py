from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from accounts.models import Role
from exchange.agreement_expiration import process_agreement_expiration_reminders, recipients_for_agreement
from exchange.models import AgreementExpirationReminderLog, ExchangeAgreement, Program
from notifications.models import Notification

User = get_user_model()


class AgreementExpirationReminderTests(TestCase):
    def setUp(self):
        self.role_admin, _ = Role.objects.get_or_create(name="admin")
        self.role_coord, _ = Role.objects.get_or_create(name="coordinator")
        self.role_student, _ = Role.objects.get_or_create(name="student")

        self.admin = User.objects.create_user(
            username="adm_exp", email="adm_exp@example.com", password="x"
        )
        self.admin.roles.add(self.role_admin)

        self.student = User.objects.create_user(
            username="stu_exp", email="stu_exp@example.com", password="x"
        )
        self.student.roles.add(self.role_student)

    @override_settings(AGREEMENT_EXPIRATION_REMINDER_DAYS=[90])
    def test_sends_on_exact_milestone_and_idempotent(self):
        today = date(2026, 1, 1)
        end = date(2026, 4, 1)
        agr = ExchangeAgreement.objects.create(
            title="Test Agr",
            partner_institution_name="Partner",
            status=ExchangeAgreement.Status.ACTIVE,
            end_date=end,
        )

        with patch(
            "exchange.agreement_expiration.NotificationService.is_enabled",
            return_value=True,
        ):
            r1 = process_agreement_expiration_reminders(today=today)
        self.assertEqual(r1["notifications_sent"], 1)
        self.assertEqual(r1["milestones_logged"], 1)
        self.assertEqual(Notification.objects.count(), 1)
        n = Notification.objects.get()
        self.assertEqual(n.recipient_id, self.admin.id)
        self.assertEqual((n.data or {}).get("kind"), "agreement_expiration")

        with patch(
            "exchange.agreement_expiration.NotificationService.is_enabled",
            return_value=True,
        ):
            r2 = process_agreement_expiration_reminders(today=today)
        self.assertEqual(r2["notifications_sent"], 0)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(AgreementExpirationReminderLog.objects.count(), 1)

    @override_settings(AGREEMENT_EXPIRATION_REMINDER_DAYS=[90])
    def test_coordinator_on_linked_program_gets_notified(self):
        coord = User.objects.create_user(
            username="coord_exp", email="coord_exp@example.com", password="x"
        )
        coord.roles.add(self.role_coord)

        today = date(2026, 1, 1)
        end = date(2026, 4, 1)
        prog = Program.objects.create(
            name="Linked",
            description="d",
            start_date=today,
            end_date=date(2027, 1, 1),
        )
        prog.coordinators.add(coord)

        agr = ExchangeAgreement.objects.create(
            title="With program",
            partner_institution_name="P",
            status=ExchangeAgreement.Status.ACTIVE,
            end_date=end,
        )
        agr.programs.add(prog)

        with patch(
            "exchange.agreement_expiration.NotificationService.is_enabled",
            return_value=True,
        ):
            process_agreement_expiration_reminders(today=today)

        recipients = {n.recipient_id for n in Notification.objects.all()}
        self.assertIn(self.admin.id, recipients)
        self.assertIn(coord.id, recipients)

    def test_recipients_for_agreement_excludes_student(self):
        coord = User.objects.create_user(
            username="coord_exp2", email="coord_exp2@example.com", password="x"
        )
        coord.roles.add(self.role_coord)

        agr = ExchangeAgreement.objects.create(
            title="A",
            partner_institution_name="P",
            status=ExchangeAgreement.Status.ACTIVE,
            end_date=date(2027, 1, 1),
        )
        ids = {u.id for u in recipients_for_agreement(agr)}
        self.assertIn(self.admin.id, ids)
        self.assertIn(coord.id, ids)
        self.assertNotIn(self.student.id, ids)
