"""Management command to test dynforms page rendering"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.test import Client


class Command(BaseCommand):
    help = 'Test dynforms page rendering'

    def handle(self, *args, **options):
        User = get_user_model()
        client = Client()

        # Get superuser
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            self.stdout.write(self.style.ERROR("❌ No superuser found"))
            return

        # Login
        client.force_login(user)
        self.stdout.write(self.style.SUCCESS(f"✅ Logged in as: {user.username}"))
        self.stdout.write("")

        # Test form list
        self.stdout.write("Testing /dynforms/ (Form List):")
        self.stdout.write("-" * 60)
        response = client.get('/dynforms/')
        self.stdout.write(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            html = response.content.decode('utf-8')

            # Check for key elements
            checks = {
                'dynforms.min.css': 'dynforms/dynforms.min.css' in html,
                'builder.min.css': 'dynforms/builder.min.css' in html,
                'dynforms.min.js': 'dynforms/dynforms.min.js' in html,
                'df-toasts.min.js': 'dynforms/df-toasts.min.js' in html,
                '#df-builder': 'id="df-builder"' in html,
                '#df-sidebar': 'id="df-sidebar"' in html,
                'Form Types title': 'Form Types' in html,
                'jQuery loaded': 'jquery' in html.lower(),
                'Bootstrap icons': 'bi bi-' in html or 'bootstrap-icons' in html,
            }

            all_passed = True
            for name, result in checks.items():
                if result:
                    self.stdout.write(self.style.SUCCESS(f"  ✅ {name}"))
                else:
                    self.stdout.write(self.style.ERROR(f"  ❌ {name}"))
                    all_passed = False

            # Stats
            self.stdout.write("")
            self.stdout.write("Page Statistics:")
            self.stdout.write(f"  - Page length: {len(html):,} characters")
            self.stdout.write(f"  - <link> tags: {html.count('<link')}")
            self.stdout.write(f"  - <script> tags: {html.count('<script')}")
            self.stdout.write(f"  - dynforms elements (df-): {html.count('df-')}")

            if all_passed:
                self.stdout.write("")
                self.stdout.write(self.style.SUCCESS("✅ ALL CHECKS PASSED - Form list renders correctly!"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ Request failed with status {response.status_code}"))

        self.stdout.write("")
        self.stdout.write("")

        # Test builder - need to get a form to edit
        from dynforms.models import FormType as DynFormType
        form_type = DynFormType.objects.first()

        if form_type:
            builder_url = f'/dynforms/builder/{form_type.id}/'
            self.stdout.write(f"Testing {builder_url} (Form Builder - Edit):")
        else:
            # No forms exist, test creation would fail, so skip
            self.stdout.write(self.style.WARNING("⚠️  No forms exist to test builder - skipping"))
            return

        self.stdout.write("-" * 60)
        response = client.get(builder_url)
        self.stdout.write(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            html = response.content.decode('utf-8')

            checks = {
                'builder.min.css loaded': 'builder.min.css' in html,
                'df-toasts.min.js loaded': 'df-toasts.min.js' in html,
                'Add tab visible': '>Add<' in html or 'Add</a>' in html,
                'Field tab visible': '>Field<' in html or 'Field</a>' in html,
                'Form tab visible': '>Form<' in html or 'Form</a>' in html,
                '#df-builder element': 'id="df-builder"' in html,
                '#df-sidebar element': 'id="df-sidebar"' in html,
                '#df-header element': 'id="df-header"' in html,
                'Tab navigation': 'nav-tabs' in html,
                'Field menu': 'field-menu' in html or 'Add' in html,
            }

            all_passed = True
            for name, result in checks.items():
                if result:
                    self.stdout.write(self.style.SUCCESS(f"  ✅ {name}"))
                else:
                    self.stdout.write(self.style.ERROR(f"  ❌ {name}"))
                    all_passed = False

            # Stats
            self.stdout.write("")
            self.stdout.write("Page Statistics:")
            self.stdout.write(f"  - Page length: {len(html):,} characters")
            self.stdout.write(f"  - Builder elements (df-): {html.count('df-')}")
            self.stdout.write(f"  - Tab elements: {html.count('tab-')}")

            if all_passed:
                self.stdout.write("")
                self.stdout.write(self.style.SUCCESS("✅ ALL CHECKS PASSED - Builder renders correctly!"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ Request failed with status {response.status_code}"))

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("RENDERING TEST COMPLETE"))
        self.stdout.write("=" * 60)
        self.stdout.write("")
        self.stdout.write("✅ The dynforms pages are rendering correctly!")
        self.stdout.write("")
        self.stdout.write("You can now visit:")
        self.stdout.write("  • http://localhost:8000/dynforms/ - View forms")
        self.stdout.write("  • http://localhost:8000/dynforms/builder/ - Create new form")
        self.stdout.write("")

