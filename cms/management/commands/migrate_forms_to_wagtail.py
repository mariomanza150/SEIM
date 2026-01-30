"""
Management command to migrate FormType and FormSubmission data
from application_forms app to Wagtail CMS FormPage.

Usage:
    python manage.py migrate_forms_to_wagtail [--dry-run]
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from wagtail.models import Page, Site

from application_forms.models import FormType, FormSubmission
from cms.models import FormPage, FormField


class Command(BaseCommand):
    help = 'Migrate FormType and FormSubmission data to Wagtail FormPage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run migration without committing changes to database',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('Running in DRY RUN mode - no changes will be saved'))

        # Get or create a Forms parent page
        try:
            site = Site.objects.get(is_default_site=True)
            root_page = site.root_page
        except Site.DoesNotExist:
            self.stdout.write(self.style.ERROR('No default site found. Please set up Wagtail first.'))
            return

        # Count existing data
        form_types = FormType.objects.all()
        form_submissions = FormSubmission.objects.all()

        self.stdout.write(f'Found {form_types.count()} FormTypes to migrate')
        self.stdout.write(f'Found {form_submissions.count()} FormSubmissions to migrate')

        if form_types.count() == 0:
            self.stdout.write(self.style.SUCCESS('No forms to migrate'))
            return

        migrated_forms = 0
        migrated_submissions = 0
        errors = []

        with transaction.atomic():
            # Migrate FormTypes to FormPages
            for form_type in form_types:
                try:
                    self.stdout.write(f'Migrating FormType: {form_type.name}')

                    # Check if already migrated (by name)
                    existing = FormPage.objects.filter(title=form_type.name).first()
                    if existing:
                        self.stdout.write(self.style.WARNING(f'  FormPage already exists: {form_type.name}'))
                        continue

                    # Create FormPage
                    form_page = FormPage(
                        title=form_type.name,
                        slug=form_type.name.lower().replace(' ', '-')[:50],
                        introduction=form_type.description or '',
                        to_address=form_type.created_by.email if form_type.created_by else 'admin@seim.local',
                        from_address='noreply@seim.local',
                        subject=f'New submission for {form_type.name}',
                        thank_you_text='<p>Thank you for your submission!</p>',
                        live=form_type.is_active,
                        linked_program=None,  # Will need to be set manually if needed
                    )

                    # Add as child of root page
                    root_page.add_child(instance=form_page)

                    # Migrate form fields from schema
                    if form_type.schema and 'properties' in form_type.schema:
                        properties = form_type.schema['properties']
                        required_fields = form_type.schema.get('required', [])

                        sort_order = 0
                        for field_name, field_config in properties.items():
                            field_type = field_config.get('type', 'string')
                            field_title = field_config.get('title', field_name)
                            field_help = field_config.get('description', '')

                            # Map JSON schema types to Wagtail form field types
                            wagtail_field_type = self._map_field_type(field_type, field_config)

                            # Create FormField
                            FormField.objects.create(
                                page=form_page,
                                sort_order=sort_order,
                                label=field_title,
                                field_type=wagtail_field_type,
                                required=field_name in required_fields,
                                help_text=field_help,
                            )
                            sort_order += 1

                    self.stdout.write(self.style.SUCCESS(f'  ✓ Created FormPage: {form_page.title}'))
                    migrated_forms += 1

                    # Note: FormSubmissions are stored by Wagtail differently
                    # Historical submissions from FormSubmission model will remain
                    # for reference but new submissions will use Wagtail's system

                except Exception as e:
                    error_msg = f'Error migrating FormType {form_type.name}: {str(e)}'
                    errors.append(error_msg)
                    self.stdout.write(self.style.ERROR(f'  ✗ {error_msg}'))

            if dry_run:
                self.stdout.write(self.style.WARNING('DRY RUN - Rolling back transaction'))
                transaction.set_rollback(True)
            else:
                self.stdout.write(self.style.SUCCESS('Migration committed to database'))

        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'Migration Summary:'))
        self.stdout.write(f'  FormPages created: {migrated_forms}')
        self.stdout.write(f'  Errors encountered: {len(errors)}')

        if errors:
            self.stdout.write('\nErrors:')
            for error in errors:
                self.stdout.write(f'  - {error}')

        if dry_run:
            self.stdout.write(self.style.WARNING('\nThis was a DRY RUN - no changes were saved'))
        else:
            self.stdout.write('\n' + self.style.SUCCESS('Migration complete!'))
            self.stdout.write('\nNext steps:')
            self.stdout.write('1. Review the migrated forms in Wagtail admin at /cms/')
            self.stdout.write('2. Update Program.application_form references to use new FormPages')
            self.stdout.write('3. Test form submissions')
            self.stdout.write('4. Once verified, run: python manage.py remove_old_form_system')

    def _map_field_type(self, json_type, field_config):
        """Map JSON schema field type to Wagtail form field type."""
        field_format = field_config.get('format')

        # Map based on type and format
        if json_type == 'string':
            if field_format == 'email':
                return 'email'
            elif field_format == 'url':
                return 'url'
            elif field_format == 'date':
                return 'date'
            elif field_format == 'datetime':
                return 'datetime'
            elif field_config.get('enum'):
                return 'dropdown'
            elif field_config.get('maxLength', 200) > 200:
                return 'multiline'
            else:
                return 'singleline'
        elif json_type == 'number' or json_type == 'integer':
            return 'number'
        elif json_type == 'boolean':
            return 'checkbox'
        elif json_type == 'array':
            return 'checkboxes'
        else:
            return 'singleline'

