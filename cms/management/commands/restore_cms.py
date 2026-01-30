"""
Single command to restore CMS to a working state.
Combines setup_wagtail_site, populate_uadec_content, and enhance_homepage.

Usage:
    python manage.py restore_cms [--skip-setup] [--skip-populate] [--skip-enhance]
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Restore CMS to working state with UAdeC content'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-setup',
            action='store_true',
            help='Skip Wagtail site setup (if already done)',
        )
        parser.add_argument(
            '--skip-populate',
            action='store_true',
            help='Skip content population',
        )
        parser.add_argument(
            '--skip-enhance',
            action='store_true',
            help='Skip homepage enhancement',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('🔧 Restoring CMS...'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        try:
            # Step 1: Setup Wagtail site structure
            if not options['skip_setup']:
                self.stdout.write('\n📦 Step 1/3: Setting up Wagtail site structure...')
                call_command('setup_wagtail_site')
            else:
                self.stdout.write('\n⏭️  Skipping Wagtail site setup')
            
            # Step 2: Populate UAdeC content
            if not options['skip_populate']:
                self.stdout.write('\n📝 Step 2/3: Populating UAdeC content...')
                call_command('populate_uadec_content')
            else:
                self.stdout.write('\n⏭️  Skipping content population')
            
            # Step 3: Enhance homepage
            if not options['skip_enhance']:
                self.stdout.write('\n✨ Step 3/3: Enhancing homepage...')
                call_command('enhance_homepage')
            else:
                self.stdout.write('\n⏭️  Skipping homepage enhancement')
            
            # Success summary
            self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
            self.stdout.write(self.style.SUCCESS('✅ CMS RESTORED SUCCESSFULLY!'))
            self.stdout.write(self.style.SUCCESS('=' * 60))
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('🌐 Visit: http://localhost:8000/'))
            self.stdout.write(self.style.SUCCESS('🎨 CMS Admin: http://localhost:8000/cms/'))
            self.stdout.write('')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error: {str(e)}'))
            raise

