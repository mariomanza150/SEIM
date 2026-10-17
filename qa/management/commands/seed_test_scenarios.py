from django.core.management.base import BaseCommand

from qa.models import TestScenario
from qa.scenarios import SCENARIOS


class Command(BaseCommand):
    help = "Create/update the manual test checklist from qa/scenarios.py (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite text edited in Django admin (default: only create missing).",
        )

    def handle(self, *args, **options):
        created = updated = 0
        for order, spec in enumerate(SCENARIOS, start=1):
            defaults = {**spec, "order": order * 10}
            code = defaults.pop("code")
            obj = TestScenario.objects.filter(code=code).first()
            if obj is None:
                TestScenario.objects.create(code=code, **defaults)
                created += 1
            elif options["overwrite"]:
                for k, v in defaults.items():
                    setattr(obj, k, v)
                obj.save()
                updated += 1
        self.stdout.write(
            self.style.SUCCESS(f"Test scenarios: {created} created, {updated} updated.")
        )
