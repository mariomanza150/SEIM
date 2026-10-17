from django.core.management import call_command
from django.core.management.base import BaseCommand

from qa.gating import assert_not_production


class Command(BaseCommand):
    help = (
        "Reset the demo dataset: cleanup_demo_data → seed_demo_readiness → "
        "seed_test_accounts. QA reports and real users are kept. Refuses to run "
        "on DEPLOY_TIER=production."
    )

    def handle(self, *args, **options):
        assert_not_production("reset_demo_data")
        verbosity = options.get("verbosity", 1)
        call_command("cleanup_demo_data", verbosity=verbosity)
        call_command("seed_demo_readiness", verbosity=verbosity)
        call_command("seed_test_accounts", verbosity=verbosity)
        self.stdout.write(self.style.SUCCESS("Demo data reset complete."))
