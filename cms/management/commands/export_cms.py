"""
Export Wagtail CMS content to a fixture file.

Usage:
    python manage.py export_cms [--output PATH]
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
import os


class Command(BaseCommand):
    help = 'Export Wagtail CMS content to fixture file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='cms/fixtures/cms_content.json',
            help='Output file path (default: cms/fixtures/cms_content.json)',
        )

    def handle(self, *args, **options):
        output_path = options['output']
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        self.stdout.write(self.style.SUCCESS('📦 Exporting CMS content...'))
        
        # Export all CMS-related models
        models_to_export = [
            # Wagtail core
            'wagtailcore.Page',
            'wagtailcore.Site',
            'wagtailcore.Revision',
            # CMS models
            'cms.HomePage',
            'cms.StandardPage',
            'cms.BlogIndexPage',
            'cms.BlogPostPage',
            'cms.BlogCategory',
            'cms.ProgramIndexPage',
            'cms.ProgramPage',
            'cms.FAQIndexPage',
            'cms.FAQPage',
            'cms.InternationalHomePage',
            'cms.CGRIPage',
            'cms.MovilidadLandingPage',
            'cms.ConvenioPage',
            'cms.ConvenioIndexPage',
            'cms.TestimonialPage',
            'cms.TestimonialIndexPage',
            # Images (if you want to include them)
            # 'wagtailimages.Image',
        ]
        
        try:
            with open(output_path, 'w') as f:
                call_command(
                    'dumpdata',
                    *models_to_export,
                    indent=2,
                    natural_foreign=True,
                    natural_primary=True,
                    stdout=f
                )
            
            file_size = os.path.getsize(output_path)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ CMS content exported to: {output_path} ({file_size:,} bytes)'
                )
            )
            self.stdout.write('')
            self.stdout.write('To import this content later, run:')
            self.stdout.write(f'  python manage.py import_cms --input {output_path}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error exporting: {str(e)}'))
            raise

