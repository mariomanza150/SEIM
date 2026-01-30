"""
List all published CMS page URLs.

Usage:
    python manage.py list_cms_urls
"""

from django.core.management.base import BaseCommand
from wagtail.models import Page


class Command(BaseCommand):
    help = 'List all published CMS page URLs'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📄 Published CMS Pages and URLs:\n'))
        
        # Get all published pages except root
        pages = Page.objects.live().public().filter(depth__gt=1).order_by('path')
        
        # Group by parent
        grouped = {}
        for page in pages:
            specific = page.specific
            parent_title = page.get_parent().title if page.get_parent() else "Root"
            if parent_title not in grouped:
                grouped[parent_title] = []
            grouped[parent_title].append(specific)
        
        for parent, children in grouped.items():
            self.stdout.write(f'\n{parent}:')
            for page in children:
                page_type = page.__class__.__name__
                self.stdout.write(f'  • {page.title}')
                self.stdout.write(f'    URL: http://localhost:8000{page.url}')
                self.stdout.write(f'    Type: {page_type}')
        
        self.stdout.write(f'\n\n✅ Total: {pages.count()} published pages')

