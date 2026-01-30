"""Management command to display CMS content overview."""

from django.core.management.base import BaseCommand
from cms.models import (
    HomePage, BlogPostPage, ProgramPage, FAQPage,
    StandardPage, BlogIndexPage, ProgramIndexPage, FAQIndexPage
)
from wagtail.models import Page


class Command(BaseCommand):
    help = 'Display overview of CMS content'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("CMS CONTENT OVERVIEW - UAdeC Exchange Department"))
        self.stdout.write("=" * 60)

        # Get all live pages
        pages = Page.objects.live().order_by('path')

        self.stdout.write("\n📄 ALL PUBLISHED PAGES:")
        self.stdout.write("-" * 60)

        for p in pages:
            page_type = p.specific.__class__.__name__
            indent = "  " * (p.depth - 1)
            in_menu = "📌" if p.show_in_menus else "  "
            self.stdout.write(f"{in_menu} {indent}{p.title}")
            self.stdout.write(f"   {indent}Type: {page_type} | URL: /{p.slug}/")

        # Homepage details
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("🏠 HOMEPAGE DETAILS"))
        self.stdout.write("=" * 60)

        try:
            home = HomePage.objects.live().first()
            if home:
                self.stdout.write(f"Title: {home.title}")
                self.stdout.write(f"Hero Title: {home.hero_title}")
                self.stdout.write(f"Hero Subtitle: {home.hero_subtitle}")
                self.stdout.write(f"Hero CTA: {home.hero_cta_text}")
                self.stdout.write(f"Body blocks: {len(home.body) if home.body else 0}")
            else:
                self.stdout.write(self.style.ERROR("❌ No homepage found"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))

        # Blog posts
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("📝 BLOG POSTS"))
        self.stdout.write("=" * 60)

        blog_posts = BlogPostPage.objects.live()
        self.stdout.write(f"Total: {blog_posts.count()}")
        for post in blog_posts:
            self.stdout.write(f"  • {post.title}")
            categories = post.categories.all()
            if categories:
                self.stdout.write(f"    Categories: {', '.join(c.name for c in categories)}")

        # Programs
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("🌍 EXCHANGE PROGRAMS"))
        self.stdout.write("=" * 60)

        programs = ProgramPage.objects.live()
        self.stdout.write(f"Total: {programs.count()}")
        for prog in programs:
            self.stdout.write(f"  • {prog.title}")
            if hasattr(prog, 'location'):
                self.stdout.write(f"    Location: {prog.location}")
            if hasattr(prog, 'duration'):
                self.stdout.write(f"    Duration: {prog.duration}")

        # FAQs
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("❓ FREQUENTLY ASKED QUESTIONS"))
        self.stdout.write("=" * 60)

        faqs = FAQPage.objects.live()
        self.stdout.write(f"Total: {faqs.count()}")
        for faq in faqs:
            self.stdout.write(f"  • {faq.title}")

        # Standard pages
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("📋 STANDARD PAGES"))
        self.stdout.write("=" * 60)

        standard_pages = StandardPage.objects.live()
        self.stdout.write(f"Total: {standard_pages.count()}")
        for page in standard_pages:
            self.stdout.write(f"  • {page.title} (/{page.slug}/)")

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS(f"✅ CMS is serving content at: http://localhost:8000/"))
        self.stdout.write(self.style.SUCCESS(f"🔧 Admin interface at: http://localhost:8000/cms/"))
        self.stdout.write("=" * 60)

