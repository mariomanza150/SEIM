"""
Management command to scan documents for malware.
"""

import sys

from django.core.management.base import BaseCommand
from django.db import models
from django.utils import timezone

from exchange.models import Document
from exchange.validators import MalwareScanner


class Command(BaseCommand):
    help = "Scan documents for malware using configured scanner"

    def add_arguments(self, parser):
        parser.add_argument(
            "--unscanned-only",
            action="store_true",
            help="Only scan documents that haven't been scanned yet",
        )
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Rescan documents older than this many days (default: 30)",
        )
        parser.add_argument(
            "--exchange-id", type=int, help="Scan documents for a specific exchange ID"
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed output for each document",
        )

    def handle(self, *args, **options):
        scanner = MalwareScanner()

        # Check if scanner is available
        if not scanner.scanner:
            self.stdout.write(
                self.style.WARNING(
                    "Warning: Malware scanner not available. Please install and configure ClamAV."
                )
            )
            return

        # Build query
        queryset = Document.objects.all()

        if options["unscanned_only"]:
            queryset = queryset.filter(virus_scanned=False)
        else:
            # Rescan documents older than specified days
            cutoff_date = timezone.now() - timezone.timedelta(days=options["days"])
            queryset = queryset.filter(
                models.Q(virus_scanned=False)
                | models.Q(virus_scan_date__lt=cutoff_date)
            )

        if options["exchange_id"]:
            queryset = queryset.filter(exchange_id=options["exchange_id"])

        total_documents = queryset.count()
        infected_documents = []
        errors = []
        scanned = 0

        self.stdout.write(f"Scanning {total_documents} documents for malware...")

        for document in queryset.iterator(chunk_size=50):
            scanned += 1

            if options["verbose"]:
                self.stdout.write(
                    f"Scanning: {document.original_filename} (ID: {document.id})"
                )

            # Show progress
            if scanned % 50 == 0:
                self.stdout.write(f"Progress: {scanned}/{total_documents}")

            try:
                # Scan the document
                if document.file:
                    is_clean = scanner.scan(document.file)

                    # Update scan results
                    document.virus_scanned = True
                    document.virus_scan_date = timezone.now()

                    if is_clean:
                        document.virus_scan_result = "Clean"
                    else:
                        document.virus_scan_result = "Infected - Quarantined"
                        infected_documents.append(document)

                        # Optionally quarantine the file
                        document.is_public = False
                        document.verification_notes = f"File quarantined due to malware detection on {timezone.now()}"

                    document.save()
                else:
                    errors.append((document, "File missing"))

            except Exception as e:
                errors.append((document, str(e)))
                if options["verbose"]:
                    self.stdout.write(
                        self.style.ERROR(f"Error scanning {document.id}: {e}")
                    )

        # Report results
        self.stdout.write(
            self.style.SUCCESS(f"\nScan complete. Scanned {scanned} documents.")
        )

        if infected_documents:
            self.stdout.write(
                self.style.ERROR(
                    f"ALERT: Found {len(infected_documents)} infected documents:"
                )
            )

            for doc in infected_documents:
                self.stdout.write(
                    self.style.ERROR(
                        f"  - {doc.original_filename} (ID: {doc.id}) - QUARANTINED"
                    )
                )

        if errors:
            self.stdout.write(
                self.style.WARNING(f"Encountered {len(errors)} errors during scanning:")
            )

            for doc, error in errors:
                self.stdout.write(
                    self.style.WARNING(
                        f"  - {doc.original_filename} (ID: {doc.id}): {error}"
                    )
                )

        if not infected_documents and not errors:
            self.stdout.write(self.style.SUCCESS("All documents are clean!"))

        # Return exit code based on results
        sys.exit(1 if infected_documents else 0)
