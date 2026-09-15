from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from accounts.models import User
from analytics.models import Report
from application_forms.models import FormStepTemplate, FormType
from data_management.models import DataOperationLog, DemoDataSet
from documents.models import Document
from exchange.demo_seed import (
    DEMO_AGREEMENT_SPECS,
    DEMO_DATASET_NAME,
    DEMO_ELIGIBILITY_RULESET_NAME,
    DEMO_FORM_NAME,
    DEMO_FORM_STEP_TEMPLATE_SLUG,
    DEMO_NOMINATION_CYCLE_NAME,
    DEMO_TOEFL_SESSION_PREFIX,
    DEMO_WORKFLOW_SLUG,
    demo_emails,
    demo_program_names,
    demo_usernames,
)
from exchange.models import (
    Application,
    Comment,
    EligibilityRuleSet,
    ExchangeAgreement,
    NominationCycle,
    Program,
    TimelineEvent,
)
from grades.models import GradeTranslation
from notifications.models import Notification, NotificationRoutingOverride
from toefl.models import PracticeAttempt
from workflows.models import WorkflowDefinition


class Command(BaseCommand):
    help = (
        "Cleanup all demo data created for SEIM system demonstration. "
        "This will NOT remove initial system data, real users, or CMS pages "
        "(re-run restore_cms / seed_spa_help separately if needed)."
    )

    def handle(self, *args, **options):
        self.stdout.write("Cleaning up demo data for SEIM...")
        demo_user_filter = self._demo_user_filter()
        demo_users = User.objects.filter(demo_user_filter)

        with transaction.atomic():
            attempt_count = PracticeAttempt.objects.filter(
                Q(user__in=demo_users)
                | Q(external_session_id__startswith=DEMO_TOEFL_SESSION_PREFIX)
            ).delete()[0]
            self.stdout.write(f"  Deleted {attempt_count} TOEFL practice attempts.")

            notif_count = Notification.objects.filter(
                Q(recipient__in=demo_users)
            ).delete()[0]
            self.stdout.write(f"  Deleted {notif_count} notifications.")

            timeline_count = TimelineEvent.objects.filter(
                application__student__in=demo_users
            ).delete()[0]
            comment_count = Comment.objects.filter(
                application__student__in=demo_users
            ).delete()[0]
            self.stdout.write(f"  Deleted {timeline_count} timeline events.")
            self.stdout.write(f"  Deleted {comment_count} comments.")

            doc_count = Document.objects.filter(Q(uploaded_by__in=demo_users)).delete()[
                0
            ]
            self.stdout.write(f"  Deleted {doc_count} documents.")

            app_count = Application.objects.filter(student__in=demo_users).delete()[0]
            self.stdout.write(f"  Deleted {app_count} applications.")

            demo_agreement_refs = [
                s["internal_reference"] for s in DEMO_AGREEMENT_SPECS
            ]
            agr_count = ExchangeAgreement.objects.filter(
                internal_reference__in=demo_agreement_refs
            ).delete()[0]
            self.stdout.write(f"  Deleted {agr_count} demo exchange agreements.")

            cycle_count = NominationCycle.objects.filter(
                name=DEMO_NOMINATION_CYCLE_NAME
            ).delete()[0]
            self.stdout.write(f"  Deleted {cycle_count} nomination cycles.")

            prog_count = Program.objects.filter(name__in=demo_program_names()).delete()[
                0
            ]
            self.stdout.write(f"  Deleted {prog_count} programs.")

            EligibilityRuleSet.objects.filter(
                name=DEMO_ELIGIBILITY_RULESET_NAME
            ).delete()
            FormType.objects.filter(name=DEMO_FORM_NAME).delete()
            FormStepTemplate.objects.filter(slug=DEMO_FORM_STEP_TEMPLATE_SLUG).delete()
            WorkflowDefinition.objects.filter(slug=DEMO_WORKFLOW_SLUG).delete()
            Report.objects.filter(name="Demo applications by status").delete()

            DemoDataSet.objects.filter(name=DEMO_DATASET_NAME).delete()
            DataOperationLog.objects.filter(
                operation_details__source="seed_demo_readiness"
            ).delete()

            NotificationRoutingOverride.objects.filter(
                key__in=["application_deadline", "document_validated"]
            ).delete()

            GradeTranslation.objects.filter(
                notes="Demo US GPA → ECTS mapping."
            ).delete()

            user_count = User.objects.filter(demo_user_filter).delete()[0]
            self.stdout.write(
                f"  Deleted {user_count} demo users (and their profiles)."
            )

        self.stdout.write(self.style.SUCCESS("Demo data cleanup completed!"))
        self.stdout.write(
            "Note: CMS / SPA help pages are left in place; "
            "use restore_cms / seed_spa_help to refresh them."
        )

    def _demo_user_filter(self):
        canonical_users = Q(username__in=demo_usernames()) | Q(email__in=demo_emails())
        legacy_admins = Q(username__startswith="admin", email__endswith="@seim.edu")
        legacy_coordinators = Q(
            username__startswith="coordinator",
            email__endswith="@seim.edu",
        )
        legacy_students = Q(
            username__startswith="student",
            email__endswith="@university.edu",
        )
        return (
            canonical_users | legacy_admins | legacy_coordinators | legacy_students
        )
