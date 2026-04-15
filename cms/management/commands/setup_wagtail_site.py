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
from django.db import transaction
from wagtail.models import Page, Site, Locale
from cms.models import (
    HomePage, BlogIndexPage, ProgramIndexPage, 
    FAQIndexPage, StandardPage
)


class Command(BaseCommand):
    help = 'Set up initial Wagtail site structure'

    def _add_first_child_compat(self, parent: Page, child: Page) -> Page:
        """
        Compatibility path for older treebeard versions that crash when adding the
        first child under a node (get_last_child() returns None).
        """
        steplen = getattr(parent, "steplen", 4)
        child.depth = parent.depth + 1
        child.path = f"{parent.path}{'1'.zfill(steplen)}"
        child.numchild = 0
        child.url_path = f"{parent.url_path}{child.slug}/"
        child.save()
        parent.numchild = (parent.numchild or 0) + 1
        parent.save(update_fields=["numchild"])
        return child

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
        
        # Get the Wagtail root page
        root_page = Page.get_first_root_node()
        if root_page is None:
            raise RuntimeError("Wagtail root page not found (Page.get_first_root_node() returned None).")
        
        # Identify the default Wagtail welcome page (non-HomePage with slug 'home').
        # IMPORTANT: On some treebeard versions, deleting the only child of root causes
        # add_child() to crash when adding the next (first) child. We avoid that by
        # renaming first, then deleting after our structure is created.
        from cms.models import HomePage as HomePageModel
        default_welcome_pages = list(Page.objects.filter(slug='home', depth=2))
        renamed_welcome_pages = []
        for page in default_welcome_pages:
            if page.specific_class != HomePageModel:
                page.slug = "wagtail-welcome"
                page.title = page.title or "Welcome"
                page.save()
                renamed_welcome_pages.append(page)
                self.stdout.write(self.style.WARNING('  ⚠ Renamed default Wagtail welcome page (will delete later)'))
        
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
        with transaction.atomic():
            home_page = HomePage(
                title='SEIM - Student Exchange Information Management',
                slug='home',
                hero_title='Welcome to SEIM',
                hero_subtitle='Streamline your student exchange program management with our comprehensive platform',
                hero_cta_text='Get Started',
                show_in_menus=True,
                locale=locale
            )
            if root_page.get_children().exists():
                root_page.add_child(instance=home_page)
            else:
                # Root has zero children (often after manual cleanup). Use a safe fallback.
                self._add_first_child_compat(root_page, home_page)
            home_page.save_revision().publish()
        self.stdout.write(self.style.SUCCESS('  ✓ Created HomePage'))

        # Now it is safe to delete the default Wagtail welcome page(s) we renamed earlier.
        for page in renamed_welcome_pages:
            try:
                page.delete()
                self.stdout.write(self.style.WARNING('  ⚠ Deleted default Wagtail welcome page'))
            except Exception:
                # Non-fatal: welcome page cleanup should not block CMS restore.
                self.stdout.write(self.style.WARNING('  ⚠ Could not delete default Wagtail welcome page; continuing'))
        
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

