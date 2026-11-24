"""
Read-only audit: count documents whose is_valid=True likely came from the
legacy clean virus-scan path (pre-#227) rather than staff review.

Does not modify any data. Safe to run against a replica / staging dump.
Do not run against production unless Mario explicitly asks.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db.models import Exists, OuterRef, Q

from documents.models import Document, DocumentValidation

SCAN_DETAILS_PREFIX = "Scanned by async task"

# Equivalent SQL for ops / replica use (PostgreSQL). Keep in sync with the ORM.
EQUIVALENT_SQL = """
-- Read-only. Counts Document rows still marked staff-approved (is_valid=True)
-- whose only "valid" DocumentValidation rows look like virus-scan outcomes,
-- not coordinator/admin validate_document() reviews.
SELECT COUNT(*) AS likely_clean_scan_approvals
FROM documents_document d
WHERE d.is_valid = TRUE
  AND EXISTS (
    SELECT 1
    FROM documents_documentvalidation v
    WHERE v.document_id = d.id
      AND v.result = 'valid'
      AND v.details LIKE 'Scanned by async task%'
  )
  AND NOT EXISTS (
    SELECT 1
    FROM documents_documentvalidation v
    WHERE v.document_id = d.id
      AND v.result = 'valid'
      AND (v.details IS NULL OR v.details NOT LIKE 'Scanned by async task%')
  );
"""


def _scan_valid_q() -> Q:
    return Q(result="valid", details__startswith=SCAN_DETAILS_PREFIX)


def _staff_valid_q() -> Q:
    """Staff/manual approval: result=valid and details are not the scan template."""
    return Q(result="valid") & ~Q(details__startswith=SCAN_DETAILS_PREFIX)


def queryset_likely_clean_scan_approvals():
    """Documents with is_valid=True explained only by clean-scan validation rows."""
    scan_valid = DocumentValidation.objects.filter(document_id=OuterRef("pk")).filter(
        _scan_valid_q()
    )
    staff_valid = DocumentValidation.objects.filter(document_id=OuterRef("pk")).filter(
        _staff_valid_q()
    )
    return (
        Document.objects.filter(is_valid=True)
        .annotate(
            has_scan_valid=Exists(scan_valid),
            has_staff_valid=Exists(staff_valid),
        )
        .filter(has_scan_valid=True, has_staff_valid=False)
        .order_by("created_at", "id")
    )


class Command(BaseCommand):
    help = (
        "Read-only: count documents where is_valid=True appears to come from the "
        "legacy clean virus-scan path (no staff DocumentValidation), so Mario can "
        "decide whether a repair is needed. Prints equivalent SQL. Never writes."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--sample",
            type=int,
            default=20,
            help="Max sample document IDs to print (0 = none). Default: 20.",
        )
        parser.add_argument(
            "--sql-only",
            action="store_true",
            help="Print the equivalent SQL and exit (no DB query).",
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.NOTICE("READ-ONLY audit — no rows will be updated.")
        )
        self.stdout.write("")
        self.stdout.write("Equivalent SQL:")
        self.stdout.write(EQUIVALENT_SQL.strip())
        self.stdout.write("")

        if options["sql_only"]:
            return

        total_valid = Document.objects.filter(is_valid=True).count()
        with_staff = (
            Document.objects.filter(is_valid=True)
            .filter(
                Exists(
                    DocumentValidation.objects.filter(
                        document_id=OuterRef("pk")
                    ).filter(_staff_valid_q())
                )
            )
            .count()
        )
        likely = queryset_likely_clean_scan_approvals()
        likely_count = likely.count()
        no_validation = (
            Document.objects.filter(is_valid=True)
            .exclude(
                Exists(DocumentValidation.objects.filter(document_id=OuterRef("pk")))
            )
            .count()
        )

        self.stdout.write(f"is_valid=True total:                    {total_valid}")
        self.stdout.write(f"  with staff/manual valid Validation:   {with_staff}")
        self.stdout.write(f"  likely clean-scan auto-approvals:      {likely_count}")
        self.stdout.write(f"  is_valid=True with no Validation rows: {no_validation}")
        self.stdout.write("")
        self.stdout.write(
            "Heuristic: is_valid=True AND has DocumentValidation "
            f"(result=valid, details startswith '{SCAN_DETAILS_PREFIX}') "
            "AND has no non-scan result=valid Validation (staff path)."
        )

        sample_n = max(0, int(options["sample"]))
        if sample_n and likely_count:
            self.stdout.write("")
            self.stdout.write(f"Sample IDs (up to {sample_n}):")
            for doc in likely[:sample_n]:
                self.stdout.write(
                    f"  {doc.id}  app={doc.application_id}  "
                    f"validated_at={doc.validated_at}  uploaded_by={doc.uploaded_by_id}"
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Audit complete. No data was modified. "
                "Mario decides whether a repair migration is warranted."
            )
        )
