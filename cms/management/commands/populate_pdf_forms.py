"""
Management command to generate and upload PDF forms for mobility program.
"""

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from wagtail.documents.models import Document
from accounts.models import User
from cms.utils.pdf_generator import FORMS
from wagtail.models import Collection


class Command(BaseCommand):
    help = 'Generate and upload standard PDF forms for mobility program'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("GENERATING PDF FORMS"))
        self.stdout.write("=" * 60)
        
        # Get or create collection for forms
        try:
            root_collection = Collection.get_first_root_node()
            forms_collection, created = Collection.objects.get_or_create(
                name='Mobility Forms',
                defaults={'depth': root_collection.depth + 1}
            )
            if created:
                root_collection.add_child(instance=forms_collection)
                self.stdout.write(self.style.SUCCESS("✓ Created 'Mobility Forms' collection"))
        except:
            forms_collection = None
            self.stdout.write(self.style.WARNING("⚠ Could not create collection, using default"))
        
        # Get admin user for uploaded_by_user field
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
        except:
            admin_user = None
        
        created_count = 0
        updated_count = 0
        
        for form_key, form_info in FORMS.items():
            self.stdout.write(f"\n📄 Processing: {form_info['title']}")
            
            try:
                # Generate PDF
                pdf_buffer = form_info['generator']()
                
                # Check if document already exists
                existing_doc = Document.objects.filter(
                    title=form_info['title']
                ).first()
                
                if existing_doc:
                    # Update existing document
                    existing_doc.file.delete(save=False)
                    existing_doc.file.save(
                        form_info['filename'],
                        ContentFile(pdf_buffer.read()),
                        save=True
                    )
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f"  ↻ Updated existing document"))
                else:
                    # Create new document
                    doc = Document(
                        title=form_info['title'],
                        collection=forms_collection
                    )
                    
                    # Add the file
                    doc.file.save(
                        form_info['filename'],
                        ContentFile(pdf_buffer.read()),
                        save=False
                    )
                    
                    # Set uploaded_by_user if available
                    if admin_user:
                        doc.uploaded_by_user = admin_user
                    
                    doc.save()
                    
                    # Add tags
                    doc.tags.add('mobility-form', 'uadec', 'internacional')
                    
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"  ✓ Created new document"))
                
                self.stdout.write(f"     File: {form_info['filename']}")
                self.stdout.write(f"     Description: {form_info['description']}")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ✗ Error: {str(e)}"))
        
        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("SUMMARY"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"✓ Created: {created_count} forms")
        self.stdout.write(f"↻ Updated: {updated_count} forms")
        self.stdout.write(f"📁 Total: {created_count + updated_count} forms available")
        
        # Instructions
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("NEXT STEPS"))
        self.stdout.write("=" * 60)
        self.stdout.write("1. Go to Wagtail admin: /cms/")
        self.stdout.write("2. Navigate to Documents")
        self.stdout.write("3. Find forms in 'Mobility Forms' collection")
        self.stdout.write("4. Add DocumentDownloadBlock to Documentation page:")
        self.stdout.write("   /internacional/movilidad-estudiantil/documentacion/")
        self.stdout.write("\nOR run: docker-compose exec web python manage.py update_documentation_page")
        self.stdout.write("=" * 60)

