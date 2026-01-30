"""
Management command to set up the International section (CGRI & Movilidad)
Drop-in replacement for /cgri/ and /movilidad/ pages.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.models import Site, Page
from cms.models import (
    InternationalHomePage,
    CGRIPage,
    MovilidadLandingPage,
    ConvenioIndexPage,
    TestimonialIndexPage,
    StandardPage,
    ProgramIndexPage,
    FAQIndexPage,
)


class Command(BaseCommand):
    help = 'Set up International Relations section (CGRI & Movilidad) pages'

    def add_arguments(self, parser):
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Replace existing internacional page if it exists',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        site = Site.objects.get(is_default_site=True)
        root_page = site.root_page
        
        self.stdout.write("\n=== Setting up International Relations Section ===\n")
        
        # Check if internacional already exists
        try:
            internacional = InternationalHomePage.objects.get(slug='internacional')
            if options['replace']:
                self.stdout.write(self.style.WARNING("Deleting existing 'internacional' page..."))
                internacional.delete()
            else:
                self.stdout.write(self.style.WARNING(
                    "Page 'internacional' already exists. Use --replace to recreate it."
                ))
                return
        except InternationalHomePage.DoesNotExist:
            pass
        
        # 1. Create main International home page
        self.stdout.write("Creating International Home Page...")
        internacional = InternationalHomePage(
            title="Relaciones Internacionales",
            slug="internacional",
            hero_title="Relaciones Internacionales UAdeC",
            hero_subtitle="Tu puerta al mundo académico - Intercambio, movilidad y convenios internacionales",
            introduction="<p>La Coordinación General de Relaciones Internacionales (CGRI) de la Universidad Autónoma de Coahuila promueve la internacionalización de la universidad a través de programas de movilidad estudiantil, convenios de colaboración académica y oportunidades de intercambio cultural.</p>",
            show_stats=True,
            stat_programs_count=25,
            stat_countries_count=15,
            stat_students_count=150,
            stat_institutions_count=40,
            seo_title="Relaciones Internacionales - UAdeC",
            search_description="Coordinación General de Relaciones Internacionales de la Universidad Autónoma de Coahuila. Programas de intercambio y movilidad estudiantil.",
            show_in_menus=True,
        )
        root_page.add_child(instance=internacional)
        internacional.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"✓ Created: {internacional.url}"))
        
        # 2. Create Institutional (CGRI) section
        self.stdout.write("\nCreating CGRI Institutional Section...")
        cgri_home = CGRIPage(
            title="Información Institucional",
            slug="institucional",
            subtitle="Coordinación General de Relaciones Internacionales",
            introduction="La CGRI es responsable de promover y coordinar las actividades de internacionalización de la Universidad Autónoma de Coahuila.",
            show_contact=True,
            contact_name="Coordinación General de Relaciones Internacionales",
            contact_email="cgri@uadec.mx",
            contact_phone="+52 (844) 000-0000",
            contact_office="Rectoría, Edificio Central",
            seo_title="CGRI - Información Institucional",
            show_in_menus=True,
        )
        internacional.add_child(instance=cgri_home)
        cgri_home.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"  ✓ {cgri_home.url}"))
        
        # 2.1 CGRI subpages
        cgri_pages = [
            {
                'title': 'Misión y Visión',
                'slug': 'mision-vision',
                'introduction': 'Conoce la misión, visión y objetivos de la CGRI.',
            },
            {
                'title': 'Equipo',
                'slug': 'equipo',
                'introduction': 'Conoce al equipo que hace posible la internacionalización de la UAdeC.',
            },
            {
                'title': 'Acreditaciones',
                'slug': 'acreditaciones',
                'introduction': 'Acreditaciones internacionales de nuestros programas académicos.',
            },
            {
                'title': 'Contacto',
                'slug': 'contacto',
                'introduction': 'Ponte en contacto con la Coordinación de Relaciones Internacionales.',
                'show_contact': True,
                'contact_name': 'CGRI UAdeC',
                'contact_email': 'cgri@uadec.mx',
            },
        ]
        
        for page_data in cgri_pages:
            page = CGRIPage(
                title=page_data['title'],
                slug=page_data['slug'],
                introduction=page_data['introduction'],
                show_contact=page_data.get('show_contact', False),
                contact_name=page_data.get('contact_name', ''),
                contact_email=page_data.get('contact_email', ''),
                show_in_menus=True,
            )
            cgri_home.add_child(instance=page)
            page.save_revision().publish()
            self.stdout.write(self.style.SUCCESS(f"  ✓ {page.url}"))
        
        # 3. Create Convenios (Agreements) section
        self.stdout.write("\nCreating Convenios Section...")
        convenios_index = ConvenioIndexPage(
            title="Convenios Internacionales",
            slug="convenios",
            introduction="<p>La UAdeC mantiene convenios de colaboración con instituciones educativas de todo el mundo, facilitando el intercambio académico y la movilidad estudiantil.</p>",
            seo_title="Convenios Internacionales - UAdeC",
            show_in_menus=True,
        )
        cgri_home.add_child(instance=convenios_index)
        convenios_index.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"  ✓ {convenios_index.url}"))
        
        # 4. Create Movilidad Estudiantil section
        self.stdout.write("\nCreating Movilidad Estudiantil Section...")
        movilidad = MovilidadLandingPage(
            title="Movilidad Estudiantil",
            slug="movilidad-estudiantil",
            hero_title="Movilidad Estudiantil Internacional",
            hero_subtitle="Vive una experiencia académica única en el extranjero",
            introduction="<p>El programa de movilidad estudiantil de la UAdeC te permite realizar parte de tus estudios en universidades extranjeras con las que tenemos convenios de colaboración. Amplía tus horizontes académicos, culturales y profesionales.</p>",
            show_quick_links=True,
            show_application_cta=True,
            application_cta_text="Aplicar Ahora",
            seo_title="Movilidad Estudiantil - UAdeC",
            show_in_menus=True,
        )
        internacional.add_child(instance=movilidad)
        movilidad.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"  ✓ {movilidad.url}"))
        
        # 4.1 Movilidad subpages
        self.stdout.write("\nCreating Movilidad Subpages...")
        
        # Programs Index
        programas = ProgramIndexPage(
            title="Programas Disponibles",
            slug="programas",
            introduction="<p>Explora los programas de intercambio disponibles en universidades de todo el mundo.</p>",
            seo_title="Programas de Intercambio",
            show_in_menus=True,
        )
        movilidad.add_child(instance=programas)
        programas.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"  ✓ {programas.url}"))
        
        # How to Apply
        como_aplicar = StandardPage(
            title="¿Cómo Aplicar?",
            slug="como-aplicar",
            introduction="Guía paso a paso para aplicar a programas de intercambio internacional.",
            show_in_menus=True,
        )
        movilidad.add_child(instance=como_aplicar)
        como_aplicar.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"  ✓ {como_aplicar.url}"))
        
        # Requirements
        requisitos = StandardPage(
            title="Requisitos",
            slug="requisitos",
            introduction="Requisitos académicos, idiomáticos y administrativos para participar en programas de movilidad.",
            show_in_menus=True,
        )
        movilidad.add_child(instance=requisitos)
        requisitos.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"  ✓ {requisitos.url}"))
        
        # Documentation
        documentacion = StandardPage(
            title="Documentación",
            slug="documentacion",
            introduction="Lista de documentos necesarios para tu aplicación de intercambio.",
            show_in_menus=True,
        )
        movilidad.add_child(instance=documentacion)
        documentacion.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"  ✓ {documentacion.url}"))
        
        # Benefits
        beneficios = StandardPage(
            title="Beneficios y Apoyos",
            slug="beneficios",
            introduction="Conoce los beneficios académicos, becas y apoyos disponibles para estudiantes en movilidad.",
            show_in_menus=True,
        )
        movilidad.add_child(instance=beneficios)
        beneficios.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"  ✓ {beneficios.url}"))
        
        # Calendar
        calendario = StandardPage(
            title="Calendario y Fechas Importantes",
            slug="calendario",
            introduction="Fechas límite para aplicaciones, convocatorias y periodos de intercambio.",
            show_in_menus=True,
        )
        movilidad.add_child(instance=calendario)
        calendario.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"  ✓ {calendario.url}"))
        
        # FAQ
        faq = FAQIndexPage(
            title="Preguntas Frecuentes",
            slug="preguntas-frecuentes",
            introduction="<p>Encuentra respuestas a las preguntas más comunes sobre movilidad estudiantil.</p>",
            show_in_menus=True,
        )
        movilidad.add_child(instance=faq)
        faq.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"  ✓ {faq.url}"))
        
        # 5. Create Testimonials section
        self.stdout.write("\nCreating Testimonials Section...")
        testimonials = TestimonialIndexPage(
            title="Testimonios",
            slug="testimonios",
            introduction="<p>Lee las experiencias de estudiantes UAdeC que han vivido un intercambio internacional.</p>",
            seo_title="Testimonios de Estudiantes",
            show_in_menus=True,
        )
        movilidad.add_child(instance=testimonials)
        testimonials.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"  ✓ {testimonials.url}"))
        
        # Summary
        self.stdout.write(self.style.SUCCESS("\n" + "="*60))
        self.stdout.write(self.style.SUCCESS("✓ International section setup complete!"))
        self.stdout.write(self.style.SUCCESS("="*60))
        self.stdout.write("\nPage Structure Created:\n")
        self.stdout.write(f"  • {internacional.url} (Main landing)")
        self.stdout.write(f"    ├── {cgri_home.url} (CGRI - Institutional)")
        self.stdout.write(f"    │   ├── {cgri_home.url}mision-vision/")
        self.stdout.write(f"    │   ├── {cgri_home.url}equipo/")
        self.stdout.write(f"    │   ├── {cgri_home.url}acreditaciones/")
        self.stdout.write(f"    │   ├── {cgri_home.url}contacto/")
        self.stdout.write(f"    │   └── {convenios_index.url}")
        self.stdout.write(f"    └── {movilidad.url} (Student-facing)")
        self.stdout.write(f"        ├── {programas.url}")
        self.stdout.write(f"        ├── {como_aplicar.url}")
        self.stdout.write(f"        ├── {requisitos.url}")
        self.stdout.write(f"        ├── {documentacion.url}")
        self.stdout.write(f"        ├── {beneficios.url}")
        self.stdout.write(f"        ├── {calendario.url}")
        self.stdout.write(f"        ├── {faq.url}")
        self.stdout.write(f"        └── {testimonials.url}")
        
        self.stdout.write("\n" + self.style.SUCCESS("Next Steps:"))
        self.stdout.write("  1. Visit /admin/ to add content to pages")
        self.stdout.write("  2. Add program pages under /programas/")
        self.stdout.write("  3. Add convenio pages under /convenios/")
        self.stdout.write("  4. Add testimonial pages under /testimonios/")
        self.stdout.write("  5. Configure menu in Wagtail admin")
        self.stdout.write("\n" + self.style.WARNING("To replace existing pages, run: python manage.py setup_internacional --replace"))

