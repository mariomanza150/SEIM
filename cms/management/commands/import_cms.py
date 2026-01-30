"""
Import Wagtail CMS content from a fixture file.

Usage:
    python manage.py import_cms [--input PATH] [--clear]
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from wagtail.models import Page


class Command(BaseCommand):
    help = 'Import Wagtail CMS content from fixture file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--input',
            type=str,
            default='cms/fixtures/cms_content.json',
            help='Input file path (default: cms/fixtures/cms_content.json)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing CMS pages before importing (except Root)',
        )

    def handle(self, *args, **options):
        input_path = options['input']
        
        self.stdout.write(self.style.SUCCESS('📥 Importing CMS content...'))
        
        # Optionally clear existing content
        if options['clear']:
            self.stdout.write('🗑️  Clearing existing CMS pages...')
            root = Page.objects.get(depth=1)
            for page in root.get_children():
                self.stdout.write(f'  Deleting: {page.title}')
                page.delete()
            self.stdout.write(self.style.SUCCESS('  ✓ Cleared existing pages'))
        
        try:
            # Import the fixture
            call_command('loaddata', input_path)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ CMS content imported from: {input_path}')
            )
            self.stdout.write('')
            self.stdout.write('🌐 Visit: http://localhost:8000/')
            self.stdout.write('🎨 CMS Admin: http://localhost:8000/cms/')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error importing: {str(e)}'))
            self.stdout.write('')
            self.stdout.write('💡 Tip: Make sure you\'ve run migrations first:')
            self.stdout.write('  python manage.py migrate')
            raise

