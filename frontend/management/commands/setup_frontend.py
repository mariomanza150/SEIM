import os

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Setup the SEIM frontend with static files and initial configuration"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force recreation of static files",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🚀 Setting up SEIM Frontend..."))

        # Create static directories if they don't exist
        static_dirs = [
            "static/css",
            "static/js",
            "static/img",
            "templates/frontend",
            "templates/frontend/auth",
            "templates/frontend/programs",
            "templates/frontend/applications",
            "templates/frontend/documents",
            "templates/frontend/admin",
        ]

        for directory in static_dirs:
            os.makedirs(directory, exist_ok=True)
            self.stdout.write(f"✅ Created directory: {directory}")

        # Collect static files
        self.stdout.write("📦 Collecting static files...")
        call_command("collectstatic", "--noinput", verbosity=0)

        # Run migrations
        self.stdout.write("🗄️ Running migrations...")
        call_command("migrate", verbosity=0)

        # Create initial data if it doesn't exist
        self.stdout.write("📊 Creating initial data...")
        try:
            call_command("create_initial_data", verbosity=0)
        except:
            self.stdout.write(
                self.style.WARNING("⚠️ Initial data already exists or failed to create")
            )

        self.stdout.write(self.style.SUCCESS("🎉 Frontend setup complete!"))
        self.stdout.write("")
        self.stdout.write("📋 Next steps:")
        self.stdout.write("1. Start the development server: python manage.py runserver")
        self.stdout.write("2. Visit http://localhost:8000/")
        self.stdout.write("3. Login with admin/admin123 or register a new account")
        self.stdout.write("")
        self.stdout.write("📚 Documentation: documentation/developer_guide.md")
