from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from accounts.models import User
from documents.models import Document
from exchange.demo_seed import (
    DEMO_AGREEMENT_SPECS,
    demo_emails,
    demo_program_names,
    demo_usernames,
)
from exchange.models import Application, Comment, ExchangeAgreement, Program, TimelineEvent
from notifications.models import Notification


class Command(BaseCommand):
    help = "Cleanup all demo data created for SEIM system demonstration. This will NOT remove initial system data or real users."

    def handle(self, *args, **options):
        self.stdout.write("Cleaning up demo data for SEIM...")
        demo_user_filter = self._demo_user_filter()
        demo_users = User.objects.filter(demo_user_filter)

        with transaction.atomic():
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

            doc_count = Document.objects.filter(
                Q(uploaded_by__in=demo_users)
            ).delete()[0]
            self.stdout.write(f"  Deleted {doc_count} documents.")

            app_count = Application.objects.filter(
                student__in=demo_users
            ).delete()[0]
            self.stdout.write(f"  Deleted {app_count} applications.")

            demo_agreement_refs = [
                s["internal_reference"] for s in DEMO_AGREEMENT_SPECS
            ]
            agr_count = ExchangeAgreement.objects.filter(
                internal_reference__in=demo_agreement_refs
            ).delete()[0]
            self.stdout.write(f"  Deleted {agr_count} demo exchange agreements.")

            prog_count = Program.objects.filter(name__in=demo_program_names()).delete()[0]
            self.stdout.write(f"  Deleted {prog_count} programs.")

            user_count = User.objects.filter(demo_user_filter).delete()[0]
            self.stdout.write(f"  Deleted {user_count} demo users (and their profiles).")

        self.stdout.write(self.style.SUCCESS("Demo data cleanup completed!"))

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
        return canonical_users | legacy_admins | legacy_coordinators | legacy_students
