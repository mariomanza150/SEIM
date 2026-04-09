from django.core.management.base import BaseCommand

from exchange.agreement_expiration import process_agreement_expiration_reminders


class Command(BaseCommand):
    help = (
        "Send staff notifications for exchange agreements approaching end_date "
        "(same logic as notifications.tasks.send_agreement_expiration_reminders)."
    )

    def handle(self, *args, **options):
        result = process_agreement_expiration_reminders()
        self.stdout.write(
            self.style.SUCCESS(
                f"date={result['date']} notifications_sent={result['notifications_sent']} "
                f"milestones_logged={result['milestones_logged']}"
            )
        )
