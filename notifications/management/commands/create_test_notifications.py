"""
Management command to create test notifications for Vue.js testing.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()


class Command(BaseCommand):
    help = "Create test notifications for development and testing"

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            default='student@test.com',
            help='Email of user to create notifications for',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of notifications to create',
        )

    def handle(self, *args, **options):
        email = options['user']
        count = options['count']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User with email '{email}' not found."))
            self.stdout.write("Create test users first: python manage.py create_vue_test_users")
            return

        self.stdout.write(f"Creating {count} test notifications for {email}...")

        notifications_data = [
            {
                "title": "Application Submitted",
                "message": "Your application for Erasmus+ Exchange - University of Barcelona has been submitted successfully.",
                "category": "success",
                "action_url": "/applications",
                "action_text": "View Applications",
            },
            {
                "title": "Document Received",
                "message": "Your transcript has been received and is under review.",
                "category": "info",
                "action_url": "/documents",
                "action_text": "View Documents",
            },
            {
                "title": "Reminder: Deadline Approaching",
                "message": "Your application deadline is in 7 days. Please ensure all documents are uploaded.",
                "category": "warning",
                "action_url": "/applications",
                "action_text": "Complete Application",
            },
            {
                "title": "Status Update",
                "message": "Your application status has been updated to Under Review.",
                "category": "info",
                "action_url": "/applications",
                "action_text": "View Details",
            },
            {
                "title": "Welcome to SEIM",
                "message": "Welcome to the Student Exchange Information Management system. Start by creating an application.",
                "category": "info",
                "action_url": "/applications/new",
                "action_text": "Create Application",
            },
        ]

        created = 0
        for i in range(min(count, len(notifications_data))):
            data = notifications_data[i].copy()
            notification, was_created = Notification.objects.get_or_create(
                recipient=user,
                title=data["title"],
                defaults={
                    "message": data["message"],
                    "category": data["category"],
                    "action_url": data.get("action_url", ""),
                    "action_text": data.get("action_text", "View"),
                    "is_read": i % 2 == 1,
                },
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"  ✓ Created: {data['title']}"))

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS(f"✓ Created {created} new notifications"))
        self.stdout.write("=" * 60)
        self.stdout.write("\nView notifications at: http://localhost:5173/notifications")
        self.stdout.write("\n")
