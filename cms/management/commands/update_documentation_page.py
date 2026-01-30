"""
Management command to add PDF download blocks to Documentation page.
"""

from django.core.management.base import BaseCommand
from cms.models import StandardPage
from wagtail.documents.models import Document


class Command(BaseCommand):
    help = 'Add PDF download blocks to the Documentación page'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("UPDATING DOCUMENTATION PAGE"))
        self.stdout.write("=" * 60)
        
        # Find the Documentation page
        try:
            doc_page = StandardPage.objects.filter(
                slug='documentacion',
                title__icontains='Documentación'
            ).first()
            
            if not doc_page:
                self.stdout.write(self.style.ERROR("✗ Documentation page not found!"))
                return
            
            self.stdout.write(f"✓ Found page: {doc_page.title}")
            self.stdout.write(f"  URL: {doc_page.url}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Error finding page: {e}"))
            return
        
        # Get all mobility forms
        forms = Document.objects.filter(
            tags__name='mobility-form'
        ).order_by('title')
        
        if not forms.exists():
            self.stdout.write(self.style.ERROR("✗ No forms found! Run: populate_pdf_forms"))
            return
        
        self.stdout.write(f"\n✓ Found {forms.count()} forms")
        
        # Organize forms by category
        categories = {
            'general': {
                'title': 'Formularios Generales',
                'forms': []
            },
            'academic': {
                'title': 'Formularios Académicos',
                'forms': []
            },
            'administrative': {
                'title': 'Formularios Administrativos',
                'forms': []
            }
        }
        
        # Categorize forms
        for form in forms:
            if 'Solicitud' in form.title or 'Compromiso' in form.title:
                categories['general']['forms'].append(form)
            elif 'Equivalencias' in form.title or 'Retorno' in form.title:
                categories['academic']['forms'].append(form)
            else:
                categories['administrative']['forms'].append(form)
        
        # Build new body content
        from wagtail import blocks
        from wagtail.blocks import StreamValue
        
        new_body = []
        
        # Add introduction
        new_body.append(('rich_text', {
            'content': '<h2>Documentación Requerida</h2><p>A continuación encontrarás todos los formularios necesarios para tu solicitud de movilidad internacional. Descarga, completa y entrega según las instrucciones de cada documento.</p>'
        }))
        
        # Add forms by category
        for category_key, category_data in categories.items():
            if category_data['forms']:
                # Category heading
                new_body.append(('rich_text', {
                    'content': f'<h3>{category_data["title"]}</h3>'
                }))
                
                # Add each form
                for form in category_data['forms']:
                    # Get description from form metadata
                    if 'Solicitud' in form.title:
                        description = 'Formulario oficial para aplicar al programa de movilidad internacional'
                    elif 'Compromiso' in form.title:
                        description = 'Carta de compromiso del estudiante con el programa de movilidad'
                    elif 'Postulación' in form.title:
                        description = 'Formato para que el director de facultad/escuela postule al estudiante'
                    elif 'Equivalencias' in form.title:
                        description = 'Para establecer las equivalencias de materias entre UAdeC y universidad destino'
                    elif 'Lineamientos' in form.title:
                        description = 'Reglas y disposiciones del programa de movilidad internacional'
                    elif 'Retorno' in form.title:
                        description = 'Informe final y revalidación de créditos al regresar del intercambio'
                    else:
                        description = 'Documento requerido para el programa de movilidad'
                    
                    new_body.append(('document', {
                        'document': form,
                        'title': form.title,
                        'description': description
                    }))
        
        # Add additional information
        new_body.append(('rich_text', {
            'content': '<h3>Información Adicional</h3><p><strong>Entrega de Documentos:</strong></p><ul><li><strong>Ubicación:</strong> Oficinas de la CGRI, Lic. Salvador González Lobo s/n, Col. República Ote., Saltillo, Coah. C.P. 25280</li><li><strong>Horario:</strong> Lunes a Viernes, 9:00 AM - 5:00 PM</li><li><strong>Contacto:</strong> 844 415 3077 | 844 416 9995</li><li><strong>Email:</strong> relaciones.internacionales@uadec.edu.mx</li></ul><p><strong>Recomendaciones:</strong></p><ul><li>Descarga todos los formularios con anticipación</li><li>Lee cuidadosamente las instrucciones de cada documento</li><li>Completa los formularios con letra legible o a máquina</li><li>Verifica que toda la información sea correcta</li><li>Solicita las cartas de recomendación con al menos 2 semanas de anticipación</li><li>Mantén copias de todos los documentos que entregues</li></ul>'
        }))
        
        # Update the page
        try:
            # Convert to StreamValue
            doc_page.body = new_body
            
            # Save revision and publish
            revision = doc_page.save_revision()
            revision.publish()
            
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(self.style.SUCCESS("✓ DOCUMENTATION PAGE UPDATED!"))
            self.stdout.write("=" * 60)
            self.stdout.write(f"Added {forms.count()} document download blocks")
            self.stdout.write(f"\nView at: http://localhost:8000{doc_page.url}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Error updating page: {e}"))
            import traceback
            self.stdout.write(traceback.format_exc())

