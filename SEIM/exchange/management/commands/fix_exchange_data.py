"""
Management command to fix existing exchange data inconsistencies
"""

import datetime

from django.core.management.base import BaseCommand
from django.db import models, transaction
from django.utils import timezone
from exchange.models import Exchange


class Command(BaseCommand):
    help = "Fix existing exchange data inconsistencies"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be fixed without making changes",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))

        self.stdout.write("Analyzing exchange data for inconsistencies...")

        fixes_made = 0

        try:
            with transaction.atomic():
                # Fix 1: Exchanges with invalid status transitions (approved/rejected without submission date)
                invalid_exchanges = Exchange.objects.filter(
                    status__in=["APPROVED", "REJECTED", "COMPLETED"],
                    submission_date__isnull=True,
                )

                if invalid_exchanges.exists():
                    self.stdout.write(f"Found {invalid_exchanges.count()} exchanges with missing submission dates")

                    if not dry_run:
                        for exchange in invalid_exchanges:
                            if exchange.created_at:
                                exchange.submission_date = exchange.created_at
                                exchange.save()
                                fixes_made += 1
                                self.stdout.write(f"  Fixed submission date for exchange {exchange.id}")

                # Fix 2: Exchanges missing required personal data
                exchanges_missing_data = Exchange.objects.filter(
                    models.Q(first_name__isnull=True)
                    | models.Q(first_name="")
                    | models.Q(last_name__isnull=True)
                    | models.Q(last_name="")
                    | models.Q(email__isnull=True)
                    | models.Q(email="")
                )

                if exchanges_missing_data.exists():
                    self.stdout.write(f"Found {exchanges_missing_data.count()} exchanges with missing personal data")

                    if not dry_run:
                        for exchange in exchanges_missing_data:
                            if exchange.student:
                                updated = False
                                if not exchange.first_name:
                                    exchange.first_name = exchange.student.first_name or "Unknown"
                                    updated = True
                                if not exchange.last_name:
                                    exchange.last_name = exchange.student.last_name or "Unknown"
                                    updated = True
                                if not exchange.email:
                                    exchange.email = exchange.student.email or "unknown@example.com"
                                    updated = True

                                if updated:
                                    exchange.save()
                                    fixes_made += 1
                                    self.stdout.write(f"  Fixed basic data for exchange {exchange.id}")

                # Fix 3: Invalid date ranges
                invalid_date_exchanges = Exchange.objects.exclude(
                    models.Q(start_date__isnull=True) | models.Q(end_date__isnull=True)
                ).filter(end_date__lte=models.F("start_date"))

                if invalid_date_exchanges.exists():
                    self.stdout.write(f"Found {invalid_date_exchanges.count()} exchanges with invalid date ranges")

                    if not dry_run:
                        for exchange in invalid_date_exchanges:
                            # Set end date to 6 months after start date as default
                            if exchange.start_date:
                                exchange.end_date = exchange.start_date + datetime.timedelta(days=180)
                                exchange.save()
                                fixes_made += 1
                                self.stdout.write(f"  Fixed date range for exchange {exchange.id}")

                # Fix 4: Missing student numbers
                exchanges_missing_student_number = Exchange.objects.filter(
                    models.Q(student_number__isnull=True) | models.Q(student_number="")
                )

                if exchanges_missing_student_number.exists():
                    self.stdout.write(
                        f"Found {exchanges_missing_student_number.count()} exchanges with missing student numbers"
                    )

                    if not dry_run:
                        for exchange in exchanges_missing_student_number:
                            if exchange.student and hasattr(exchange.student, "profile"):
                                if exchange.student.profile.student_id:
                                    exchange.student_number = exchange.student.profile.student_id
                                    exchange.save()
                                    fixes_made += 1
                                    self.stdout.write(f"  Fixed student number for exchange {exchange.id}")
                            else:
                                # Generate a placeholder student number
                                exchange.student_number = f"STU{exchange.id:06d}"
                                exchange.save()
                                fixes_made += 1
                                self.stdout.write(f"  Generated student number for exchange {exchange.id}")

                # Fix 5: Exchanges in draft status but with submission dates
                draft_with_submission = Exchange.objects.filter(status="DRAFT", submission_date__isnull=False)

                if draft_with_submission.exists():
                    self.stdout.write(f"Found {draft_with_submission.count()} draft exchanges with submission dates")

                    if not dry_run:
                        for exchange in draft_with_submission:
                            exchange.submission_date = None
                            exchange.save()
                            fixes_made += 1
                            self.stdout.write(f"  Cleared submission date for draft exchange {exchange.id}")

                if dry_run:
                    self.stdout.write(self.style.WARNING("DRY RUN COMPLETE - No changes were made"))
                    # Rollback transaction in dry run mode
                    transaction.set_rollback(True)
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f"Exchange data cleanup completed - {fixes_made} fixes applied")
                    )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during data cleanup: {str(e)}"))
            raise

        # Summary report
        self.stdout.write("\n=== DATA CLEANUP SUMMARY ===")
        total_exchanges = Exchange.objects.count()
        self.stdout.write(f"Total exchanges in database: {total_exchanges}")

        if not dry_run:
            self.stdout.write(f"Fixes applied: {fixes_made}")
        else:
            self.stdout.write("Run without --dry-run to apply fixes")

        self.stdout.write("\n=== RECOMMENDATIONS ===")
        self.stdout.write("1. Review exchange applications for completeness")
        self.stdout.write("2. Ensure all users have proper profiles set up")
        self.stdout.write("3. Consider running this command periodically for maintenance")
