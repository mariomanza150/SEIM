"""
Ingest official CGRI binaries from SAMPLES/ into Wagtail Documents and DocumentType templates.
Also seeds HostInstitution rows from curated university JSON lists.
"""

from django.core.management.base import BaseCommand

from documents.cgri_ingest import ingest_cgri_samples


class Command(BaseCommand):
    help = (
        "Upload SAMPLES CGRI files to Wagtail + DocumentType templates, "
        "and seed official university lists"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-universities",
            action="store_true",
            help="Skip HostInstitution / ExchangeAgreement seeding from JSON lists",
        )
        parser.add_argument(
            "--skip-wagtail",
            action="store_true",
            help="Skip Wagtail Document uploads",
        )
        parser.add_argument(
            "--skip-templates",
            action="store_true",
            help="Skip DocumentType.template_file attachment",
        )

    def handle(self, *args, **options):
        ingest_cgri_samples(
            skip_universities=options["skip_universities"],
            skip_wagtail=options["skip_wagtail"],
            skip_templates=options["skip_templates"],
            stdout=self.stdout,
        )
