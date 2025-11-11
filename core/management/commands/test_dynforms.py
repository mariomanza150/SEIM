"""Management command to test dynforms setup"""

import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.urls import reverse


class Command(BaseCommand):
    help = 'Test dynforms setup and configuration'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("DYNFORMS SETUP TEST"))
        self.stdout.write("=" * 60)
        self.stdout.write("")

        User = get_user_model()

        # Check for superuser
        superuser = User.objects.filter(is_superuser=True).first()
        if superuser:
            self.stdout.write(self.style.SUCCESS(f"✅ Superuser found: {superuser.username}"))

            # Check admin role
            try:
                from accounts.models import Role
                admin_role = Role.objects.get(name='admin')
                if admin_role in superuser.roles.all():
                    self.stdout.write(self.style.SUCCESS("✅ Superuser has admin role"))
                else:
                    self.stdout.write(self.style.WARNING("⚠️  Adding admin role to superuser..."))
                    superuser.roles.add(admin_role)
                    self.stdout.write(self.style.SUCCESS("✅ Admin role added"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️  Admin role check: {e}"))
        else:
            self.stdout.write(self.style.ERROR("❌ No superuser found"))

        self.stdout.write("")

        # Check dynforms package
        try:
            import dynforms
            version = getattr(dynforms, '__version__', 'unknown')
            self.stdout.write(self.style.SUCCESS(f"✅ django-dynforms installed: v{version}"))
        except ImportError:
            self.stdout.write(self.style.ERROR("❌ django-dynforms not installed"))
            return

        self.stdout.write("")

        # Check dynforms models
        try:
            from dynforms.models import FormType as DynFormType
            form_types = DynFormType.objects.all()
            self.stdout.write(self.style.SUCCESS("✅ Dynforms FormType model accessible"))
            self.stdout.write(f"   Total form types: {form_types.count()}")

            if form_types.exists():
                self.stdout.write("\n   Existing forms:")
                for ft in form_types[:5]:
                    self.stdout.write(f"   - {ft.name} (ID: {ft.id})")
            else:
                self.stdout.write(self.style.WARNING("   ℹ️  No forms created yet"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))

        self.stdout.write("")

        # Check static files
        staticfiles_dir = os.path.join(settings.BASE_DIR, 'staticfiles', 'dynforms')
        if os.path.exists(staticfiles_dir):
            files = os.listdir(staticfiles_dir)
            self.stdout.write(self.style.SUCCESS(f"✅ Static files: {len(files)} files"))

            required = ['dynforms.min.css', 'builder.min.css', 'dynforms.min.js', 'df-toasts.min.js']
            missing = [f for f in required if f not in files]

            if missing:
                self.stdout.write(self.style.WARNING(f"   ⚠️  Missing: {', '.join(missing)}"))
            else:
                self.stdout.write(self.style.SUCCESS("   ✅ All required files present"))
        else:
            self.stdout.write(self.style.ERROR("❌ Static files not found"))

        self.stdout.write("")

        # Check templates
        templates_dir = os.path.join(settings.BASE_DIR, 'templates', 'dynforms')
        if os.path.exists(templates_dir):
            template_files = os.listdir(templates_dir)
            self.stdout.write(self.style.SUCCESS(f"✅ Custom templates: {', '.join(template_files)}"))
        else:
            self.stdout.write(self.style.WARNING("⚠️  No custom templates"))

        self.stdout.write("")

        # Check URLs
        try:
            url = reverse('dynforms-list')
            self.stdout.write(self.style.SUCCESS(f"✅ Form list URL: {url}"))

            builder_url = reverse('dynforms-builder')
            self.stdout.write(self.style.SUCCESS(f"✅ Builder URL: {builder_url}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ URL error: {e}"))

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("NEXT STEPS:"))
        self.stdout.write("=" * 60)
        self.stdout.write("1. Visit http://localhost:8000/dynforms/")
        self.stdout.write("2. Visit http://localhost:8000/dynforms/builder/")
        self.stdout.write("3. Check browser console for errors")
        self.stdout.write("")

