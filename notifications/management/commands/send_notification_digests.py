from django.core.management.base import BaseCommand

from notifications.digest import process_notification_digests


class Command(BaseCommand):
    help = "Send notification digests (same logic as notifications.tasks.send_notification_digests)."

    def handle(self, *args, **options):
        result = process_notification_digests()
        self.stdout.write(self.style.SUCCESS(str(result)))
