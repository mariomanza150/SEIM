from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from accounts.models import User
from documents.models import Document
from exchange.models import Application, Comment, Program, TimelineEvent
from notifications.models import Notification


class Command(BaseCommand):
    help = "Cleanup all demo data created for SEIM system demonstration. This will NOT remove initial system data or real users."

    def handle(self, *args, **options):
        self.stdout.write("Cleaning up demo data for SEIM...")
        with transaction.atomic():
            notif_count = Notification.objects.filter(
                Q(recipient__username__startswith="admin") |
                Q(recipient__username__startswith="coordinator") |
                Q(recipient__username__startswith="student")
            ).delete()[0]
            self.stdout.write(f"  Deleted {notif_count} notifications.")

            timeline_count = TimelineEvent.objects.filter(
                application__student__username__startswith="student"
            ).delete()[0]
            comment_count = Comment.objects.filter(
                application__student__username__startswith="student"
            ).delete()[0]
            self.stdout.write(f"  Deleted {timeline_count} timeline events.")
            self.stdout.write(f"  Deleted {comment_count} comments.")

            doc_count = Document.objects.filter(
                uploaded_by__username__startswith="student"
            ).delete()[0]
            self.stdout.write(f"  Deleted {doc_count} documents.")

            app_count = Application.objects.filter(
                student__username__startswith="student"
            ).delete()[0]
            self.stdout.write(f"  Deleted {app_count} applications.")

            program_names = [
                "Erasmus+ Computer Science Exchange",
                "Business Administration in Spain",
                "Engineering Exchange in Germany",
                "Arts and Culture in France",
            ]
            prog_count = Program.objects.filter(name__in=program_names).delete()[0]
            self.stdout.write(f"  Deleted {prog_count} programs.")

            user_count = User.objects.filter(
                Q(username__startswith="admin") |
                Q(username__startswith="coordinator") |
                Q(username__startswith="student")
            ).delete()[0]
            self.stdout.write(f"  Deleted {user_count} demo users (and their profiles).")

        self.stdout.write(self.style.SUCCESS("Demo data cleanup completed!"))
