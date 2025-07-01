"""
Management command to check file integrity for all documents.
"""

import sys

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from exchange.models import Document


class Command(BaseCommand):
    help = "Check file integrity for all documents in the system"

    def add_arguments(self, parser):
        parser.add_argument(
            "--exchange-id", type=int, help="Check documents for a specific exchange ID"
        )
        parser.add_argument(
            "--category", type=str, help="Check documents of a specific category"
        )
        parser.add_argument(
            "--fix",
            action="store_true",
            help="Attempt to fix integrity issues (mark corrupted files)",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed output for each document",
        )

    def handle(self, *args, **options):
        # Build query based on filters
        queryset = Document.objects.all()

        if options["exchange_id"]:
            queryset = queryset.filter(exchange_id=options["exchange_id"])

        if options["category"]:
            queryset = queryset.filter(category=options["category"])

        total_documents = queryset.count()
        corrupt_documents = []
        checked = 0

        self.stdout.write(f"Checking integrity of {total_documents} documents...")

        for document in queryset.iterator(chunk_size=100):
            checked += 1

            if options["verbose"]:
                self.stdout.write(
                    f"Checking: {document.original_filename} (ID: {document.id})"
                )

            # Show progress
            if checked % 100 == 0:
                self.stdout.write(f"Progress: {checked}/{total_documents}")

            try:
                # Check if file exists
                if not document.file:
                    corrupt_documents.append((document, "File missing"))
                    continue

                # Check integrity
                if not document.check_integrity():
                    corrupt_documents.append((document, "Checksum mismatch"))

                    if options["fix"]:
                        # Mark document as having integrity issues
                        document.verification_notes = f"Integrity check failed on {timezone.now()}: Checksum mismatch"
                        document.is_verified = False
                        document.save()

            except Exception as e:
                corrupt_documents.append((document, f"Error: {str(e)}"))

                if options["fix"]:
                    document.verification_notes = (
                        f"Integrity check failed on {timezone.now()}: {str(e)}"
                    )
                    document.is_verified = False
                    document.save()

        # Report results
        self.stdout.write(
            self.style.SUCCESS(
                f"\nIntegrity check complete. Checked {checked} documents."
            )
        )

        if corrupt_documents:
            self.stdout.write(
                self.style.WARNING(
                    f"Found {len(corrupt_documents)} documents with integrity issues:"
                )
            )

            for doc, issue in corrupt_documents:
                self.stdout.write(
                    self.style.ERROR(
                        f"  - {doc.original_filename} (ID: {doc.id}): {issue}"
                    )
                )

            if options["fix"]:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Marked {len(corrupt_documents)} documents as having integrity issues."
                    )
                )
        else:
            self.stdout.write(
                self.style.SUCCESS("All documents passed integrity check!")
            )

        # Return exit code based on results
        sys.exit(1 if corrupt_documents else 0)
