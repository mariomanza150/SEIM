"""
Management command to create partner logos and Convenio pages.
"""

from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
from django.utils.text import slugify
from wagtail.images.models import Image
from wagtail.models import Page, Collection
from cms.models import ConvenioPage, ConvenioIndexPage
from cms.utils.logo_generator import create_placeholder_logo, PARTNER_INSTITUTIONS


class Command(BaseCommand):
    help = 'Create partner institution logos and Convenio pages'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("CREATING PARTNER LOGOS & CONVENIO PAGES"))
        self.stdout.write("=" * 60)
        
        # Get or create collection for logos
        try:
            root_collection = Collection.get_first_root_node()
            logo_collection, created = Collection.objects.get_or_create(
                name='Partner Logos',
                defaults={'depth': root_collection.depth + 1}
            )
            if created:
                root_collection.add_child(instance=logo_collection)
                self.stdout.write(self.style.SUCCESS("✓ Created 'Partner Logos' collection"))
        except Exception as e:
            logo_collection = None
            self.stdout.write(self.style.WARNING(f"⚠ Could not create collection: {e}"))
        
        # Find ConvenioIndexPage
        try:
            convenio_index = ConvenioIndexPage.objects.live().first()
            if not convenio_index:
                self.stdout.write(self.style.ERROR("✗ ConvenioIndexPage not found!"))
                self.stdout.write("  Run: docker-compose exec web python manage.py populate_internacional_content")
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Error finding ConvenioIndexPage: {e}"))
            return
        
        logos_created = 0
        logos_updated = 0
        pages_created = 0
        pages_updated = 0
        
        for slug, info in PARTNER_INSTITUTIONS.items():
            self.stdout.write(f"\n🏛️  Processing: {info['name']}")
            
            try:
                # Generate logo
                logo_buffer = create_placeholder_logo(info['name'], return_buffer=True)
                
                # Check if image already exists
                existing_image = Image.objects.filter(title=info['name']).first()
                
                if existing_image:
                    # Update existing image
                    existing_image.file.delete(save=False)
                    existing_image.file.save(
                        f"{slug}.png",
                        ImageFile(logo_buffer),
                        save=True
                    )
                    logo_image = existing_image
                    logos_updated += 1
                    self.stdout.write(self.style.WARNING("  ↻ Updated existing logo"))
                else:
                    # Create new image - save file first, then save model
                    logo_image = Image(
                        title=info['name'],
                        collection=logo_collection
                    )
                    
                    # Save the file - this will automatically extract dimensions
                    logo_image.file.save(
                        f"{slug}.png",
                        ImageFile(logo_buffer),
                        save=True  # Save immediately to process the image
                    )
                    
                    # Add tags
                    logo_image.tags.add('partner-logo', 'institution', info['country'].lower())
                    
                    logos_created += 1
                    self.stdout.write(self.style.SUCCESS("  ✓ Created logo"))
                
                # Check if ConvenioPage already exists
                existing_page = ConvenioPage.objects.filter(
                    institution_name=info['name']
                ).first()
                
                if existing_page:
                    # Update existing page
                    existing_page.institution_logo = logo_image
                    existing_page.country = info['country']
                    existing_page.city = info.get('city', '')
                    existing_page.agreement_type = info.get('agreement_type', 'bilateral')
                    existing_page.save_revision().publish()
                    pages_updated += 1
                    self.stdout.write(self.style.WARNING("  ↻ Updated existing Convenio page"))
                else:
                    # Create new ConvenioPage
                    convenio_page = ConvenioPage(
                        title=info['name'],
                        slug=slug,
                        institution_name=info['name'],
                        institution_logo=logo_image,
                        country=info['country'],
                        city=info.get('city', ''),
                        agreement_type=info.get('agreement_type', 'bilateral'),
                        introduction=f"Convenio de cooperación académica con {info['name']}.",
                        available_for_students=True,
                        show_in_menus=True
                    )
                    
                    # Add as child of ConvenioIndexPage
                    convenio_index.add_child(instance=convenio_page)
                    convenio_page.save_revision().publish()
                    
                    pages_created += 1
                    self.stdout.write(self.style.SUCCESS("  ✓ Created Convenio page"))
                
                self.stdout.write(f"     Country: {info['country']}")
                self.stdout.write(f"     Type: {info.get('agreement_type', 'bilateral')}")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ✗ Error: {str(e)}"))
                import traceback
                self.stdout.write(traceback.format_exc())
        
        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("SUMMARY"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"🖼️  Logos:")
        self.stdout.write(f"   ✓ Created: {logos_created}")
        self.stdout.write(f"   ↻ Updated: {logos_updated}")
        self.stdout.write(f"   📁 Total: {logos_created + logos_updated}")
        self.stdout.write(f"\n📄 Convenio Pages:")
        self.stdout.write(f"   ✓ Created: {pages_created}")
        self.stdout.write(f"   ↻ Updated: {pages_updated}")
        self.stdout.write(f"   📁 Total: {pages_created + pages_updated}")
        
        # Instructions
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("VERIFICATION"))
        self.stdout.write("=" * 60)
        self.stdout.write("View Convenios at:")
        self.stdout.write("  http://localhost:8000/internacional/institucional/convenios/")
        self.stdout.write("\nView logos in Wagtail admin:")
        self.stdout.write("  http://localhost:8000/cms/ → Images → Partner Logos collection")
        self.stdout.write("=" * 60)

