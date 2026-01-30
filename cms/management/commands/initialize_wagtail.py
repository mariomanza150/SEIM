"""
Simple management command to initialize Wagtail CMS with basic structure.
"""

from django.core.management.base import BaseCommand
from wagtail.models import Page, Site
from cms.models import HomePage


class Command(BaseCommand):
    help = 'Initialize Wagtail CMS with basic structure'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Initializing Wagtail CMS...'))
        
        # Check if a HomePage already exists
        if HomePage.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    '✓ HomePage already exists - Wagtail is already initialized'
                )
            )
            home_page = HomePage.objects.first()
        else:
            # Get root page
            root_page = Page.objects.get(depth=1)
            
            # Delete any existing non-HomePage children of root
            for page in root_page.get_children():
                if not isinstance(page.specific, HomePage):
                    self.stdout.write(f'  Deleting: {page.title}')
                    page.delete()
            
            # Fix root's numchild if it's inconsistent
            actual_num_children = root_page.get_children().count()
            if root_page.numchild != actual_num_children:
                root_page.numchild = actual_num_children
                root_page.save()
            
            # Create HomePage
            home_page = HomePage(
                title='SEIM - Student Exchange Information Management',
                slug='home',
                hero_title='Welcome to SEIM',
                hero_subtitle='Streamline your student exchange program management',
                hero_cta_text='Get Started'
            )
            
            root_page.add_child(instance=home_page)
            revision = home_page.save_revision()
            revision.publish()
            
            self.stdout.write(self.style.SUCCESS('  ✓ Created HomePage'))
        
        # Configure default site
        try:
            site = Site.objects.get(is_default_site=True)
            if site.root_page != home_page:
                site.root_page = home_page
                site.save()
                self.stdout.write(self.style.SUCCESS('  ✓ Updated default site'))
        except Site.DoesNotExist:
            site = Site.objects.create(
                hostname='localhost',
                port=8000,
                root_page=home_page,
                is_default_site=True,
                site_name='SEIM'
            )
            self.stdout.write(self.style.SUCCESS('  ✓ Created default site'))
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Wagtail initialized successfully!'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Home page: {home_page.title}'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Wagtail admin: http://localhost:8000/cms/'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'\nYou can now log in with your staff account and start adding content!'
            )
        )

