"""
Management command to set up initial Wagtail site structure.

This command creates the initial site structure including:
- HomePage as root
- Blog index page
- Program index page
- FAQ index page
- Standard pages (About, Contact)
"""

from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from wagtail.models import Page, Site, Locale
from cms.models import (
    HomePage, BlogIndexPage, ProgramIndexPage, 
    FAQIndexPage, StandardPage
)


class Command(BaseCommand):
    help = 'Set up initial Wagtail site structure'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-existing',
            action='store_true',
            help='Delete existing pages before creating new structure',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up Wagtail site structure...'))
        
        # Get the default locale
        try:
            locale = Locale.objects.get(language_code='en')
        except Locale.DoesNotExist:
            locale = Locale.objects.create(language_code='en')
            self.stdout.write(self.style.SUCCESS('  ✓ Created default locale (en)'))
        
        # Get the root page
        root_page = Page.objects.get(depth=1)
        
        # Delete the default Wagtail welcome page if it exists (non-HomePage with slug 'home')
        from cms.models import HomePage as HomePageModel
        default_welcome_pages = Page.objects.filter(slug='home', depth=2)
        for page in default_welcome_pages:
            if page.specific_class != HomePageModel:
                page.delete()
                self.stdout.write(self.style.WARNING('  ⚠ Deleted default Wagtail welcome page'))
        
        # Check if our HomePage already exists
        if HomePage.objects.filter(slug='home').exists():
            if options['delete_existing']:
                HomePage.objects.filter(slug='home').delete()
                self.stdout.write(self.style.WARNING('  ⚠ Deleted existing HomePage'))
            else:
                self.stdout.write(
                    self.style.WARNING(
                        '  ⚠ HomePage already exists. Use --delete-existing to recreate.'
                    )
                )
                home_page = HomePage.objects.get(slug='home')
                # Still need to configure the site
                try:
                    site = Site.objects.get(is_default_site=True)
                    if site.root_page != home_page:
                        site.root_page = home_page
                        site.save()
                        self.stdout.write(self.style.SUCCESS('  ✓ Updated default site'))
                except Site.DoesNotExist:
                    pass
                return
        
        # Create HomePage
        home_page = HomePage(
            title='SEIM - Student Exchange Information Management',
            slug='home',
            hero_title='Welcome to SEIM',
            hero_subtitle='Streamline your student exchange program management with our comprehensive platform',
            hero_cta_text='Get Started',
            show_in_menus=True,
            locale=locale
        )
        root_page.add_child(instance=home_page)
        home_page.save_revision().publish()
        self.stdout.write(self.style.SUCCESS('  ✓ Created HomePage'))
        
        # Create or update default site
        try:
            site = Site.objects.get(is_default_site=True)
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
        
        # Create Blog Index Page
        if not BlogIndexPage.objects.filter(slug='blog').exists():
            blog_index = BlogIndexPage(
                title='Blog',
                slug='blog',
                show_in_menus=True,
                locale=locale
            )
            home_page.add_child(instance=blog_index)
            blog_index.save_revision().publish()
            self.stdout.write(self.style.SUCCESS('  ✓ Created Blog Index Page'))
        
        # Create Program Index Page
        if not ProgramIndexPage.objects.filter(slug='programs').exists():
            program_index = ProgramIndexPage(
                title='Exchange Programs',
                slug='programs',
                show_in_menus=True,
                locale=locale
            )
            home_page.add_child(instance=program_index)
            program_index.save_revision().publish()
            self.stdout.write(self.style.SUCCESS('  ✓ Created Program Index Page'))
        
        # Create FAQ Index Page
        if not FAQIndexPage.objects.filter(slug='faq').exists():
            faq_index = FAQIndexPage(
                title='Frequently Asked Questions',
                slug='faq',
                show_in_menus=True,
                locale=locale
            )
            home_page.add_child(instance=faq_index)
            faq_index.save_revision().publish()
            self.stdout.write(self.style.SUCCESS('  ✓ Created FAQ Index Page'))
        
        # Create About Page
        if not StandardPage.objects.filter(slug='about').exists():
            about_page = StandardPage(
                title='About SEIM',
                slug='about',
                show_in_menus=True,
                locale=locale
            )
            home_page.add_child(instance=about_page)
            about_page.save_revision().publish()
            self.stdout.write(self.style.SUCCESS('  ✓ Created About Page'))
        
        # Create Contact Page
        if not StandardPage.objects.filter(slug='contact').exists():
            contact_page = StandardPage(
                title='Contact Us',
                slug='contact',
                show_in_menus=True,
                locale=locale
            )
            home_page.add_child(instance=contact_page)
            contact_page.save_revision().publish()
            self.stdout.write(self.style.SUCCESS('  ✓ Created Contact Page'))
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n✅ Wagtail site structure setup complete!'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Site root: {home_page.title} (/{home_page.slug}/)'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Site URL: http://{site.hostname}:{site.port}/'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Wagtail admin: http://{site.hostname}:{site.port}/cms/'
            )
        )

