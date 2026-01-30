"""Display all Wagtail documents."""
from django.core.management.base import BaseCommand
from wagtail.documents.models import Document


class Command(BaseCommand):
    help = 'Display all Wagtail documents'

    def handle(self, *args, **options):
        docs = Document.objects.all().order_by('title')
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("📄 WAGTAIL DOCUMENTS")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Total Documents: {docs.count()}\n")
        
        for i, doc in enumerate(docs, 1):
            self.stdout.write(f"  {i}. {doc.title}")
            self.stdout.write(f"     File: {doc.file.name}")
            self.stdout.write(f"     Size: {doc.file.size} bytes")
            self.stdout.write(f"     Created: {doc.created_at.strftime('%Y-%m-%d %H:%M')}")
            self.stdout.write(f"     URL: /media/{doc.file.name}")
            self.stdout.write("")
        
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("✓ All documents listed"))
        self.stdout.write("=" * 60)

