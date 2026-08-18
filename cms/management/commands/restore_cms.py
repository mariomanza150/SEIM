"""
Single command to restore CMS to a working state.
Combines setup_wagtail_site, populate_institution_content, enhance_homepage,
and the internacional (CGRI / Movilidad) section.

Usage:
    python manage.py restore_cms [--skip-setup] [--skip-populate] [--skip-enhance] [--skip-internacional]
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Restore CMS with configured institution example content "
        "(UAdeC defaults unless INSTITUTION_* is set)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-setup",
            action="store_true",
            help="Skip Wagtail site setup (if already done)",
        )
        parser.add_argument(
            "--skip-populate",
            action="store_true",
            help="Skip content population",
        )
        parser.add_argument(
            "--skip-enhance",
            action="store_true",
            help="Skip homepage enhancement",
        )
        parser.add_argument(
            "--skip-internacional",
            action="store_true",
            help="Skip CGRI / Movilidad internacional section",
        )
        parser.add_argument(
            "--replace-internacional",
            action="store_true",
            help="Delete and recreate the internacional tree before populating",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("🔧 Restoring CMS..."))
        self.stdout.write(self.style.SUCCESS("=" * 60))

        try:
            # Step 1: Setup Wagtail site structure
            if not options["skip_setup"]:
                self.stdout.write("\n📦 Step 1/4: Setting up Wagtail site structure...")
                call_command("setup_wagtail_site")
            else:
                self.stdout.write("\n⏭️  Skipping Wagtail site setup")

            # Step 2: Populate example institution content (UAdeC tokens unless overridden)
            if not options["skip_populate"]:
                self.stdout.write(
                    "\n📝 Step 2/4: Populating institution example content..."
                )
                call_command("populate_institution_content")
            else:
                self.stdout.write("\n⏭️  Skipping content population")

            # Step 3: Enhance homepage
            if not options["skip_enhance"]:
                self.stdout.write("\n✨ Step 3/4: Enhancing homepage...")
                call_command("enhance_homepage")
            else:
                self.stdout.write("\n⏭️  Skipping homepage enhancement")

            self.stdout.write("\n📋 Step 4/4: Creating How to Apply page...")
            call_command("create_application_page")

            if not options["skip_internacional"]:
                self.stdout.write(
                    "\n🌍 Setting up Internacional (CGRI & Movilidad)..."
                )
                if options["replace_internacional"]:
                    call_command("setup_internacional", replace=True)
                else:
                    call_command("setup_internacional")
                call_command("populate_internacional_content")
            else:
                self.stdout.write("\n⏭️  Skipping internacional section")

            # Success summary
            self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
            self.stdout.write(self.style.SUCCESS("✅ CMS RESTORED SUCCESSFULLY!"))
            self.stdout.write(self.style.SUCCESS("=" * 60))
            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS("🌐 Visit: http://localhost:8000/"))
            self.stdout.write(
                self.style.SUCCESS("🎨 CMS Admin: http://localhost:8000/cms/")
            )
            self.stdout.write("")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Error: {str(e)}"))
            raise
