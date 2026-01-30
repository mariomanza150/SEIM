"""
Management command to remove the old django-dynforms system
after migration to Wagtail is complete and verified.

WARNING: This will remove the application_forms app and django-dynforms.
Make sure migration is complete and tested before running this command.

Usage:
    python manage.py remove_old_form_system --confirm
"""

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Remove old form system after migration to Wagtail (requires --confirm flag)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm removal of old form system',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(self.style.ERROR(
                'This command requires --confirm flag to proceed.\n'
                'This will remove the application_forms app and django-dynforms package.\n'
                'Make sure you have:\n'
                '1. Migrated all forms to Wagtail\n'
                '2. Tested the new form system\n'
                '3. Backed up your database\n'
                '4. Updated all Program.application_form references\n'
            ))
            return

        self.stdout.write(self.style.WARNING(
            '='*60 + '\n'
            'WARNING: This will remove:\n'
            '1. application_forms Django app\n'
            '2. django-dynforms package references\n'
            '3. Related URLs and views\n'
            '\nHistorical form submission data will be preserved in the database\n'
            'but the models will no longer be accessible.\n'
            + '='*60
        ))

        confirm = input('\nAre you sure you want to proceed? Type "yes" to continue: ')

        if confirm.lower() != 'yes':
            self.stdout.write(self.style.ERROR('Operation cancelled'))
            return

        self.stdout.write(self.style.WARNING('\nManual steps required:'))
        self.stdout.write('1. Remove "application_forms" from INSTALLED_APPS in settings/base.py')
        self.stdout.write('2. Remove django-dynforms URLs from seim/urls.py')
        self.stdout.write('3. Remove django-dynforms from requirements.txt:')
        self.stdout.write('   - django-dynforms==2025.9.10')
        self.stdout.write('   - crispy-bootstrap5==2025.6')
        self.stdout.write('   - django-crisp-modals==2025.10.0')
        self.stdout.write('   - django-itemlist==2025.7.7')
        self.stdout.write('4. Update exchange.models.Program.application_form to reference FormPage')
        self.stdout.write('5. Run: pip uninstall django-dynforms crispy-bootstrap5 django-crisp-modals django-itemlist')
        self.stdout.write('6. Run: python manage.py makemigrations')
        self.stdout.write('7. Run: python manage.py migrate')
        self.stdout.write('8. Delete the application_forms/ directory')
        self.stdout.write('\n' + self.style.SUCCESS('Please complete these steps manually.'))

