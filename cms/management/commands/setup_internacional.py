"""
Management command to set up the International section (CGRI & Movilidad)
Drop-in replacement for /cgri/ and /movilidad/ pages.

Idempotent: creates missing pages under an existing internacional tree unless
--replace is passed.
"""

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.models import Site

from cms.models import (
    CGRIPage,
    ConvenioIndexPage,
    FAQIndexPage,
    InternationalHomePage,
    MovilidadLandingPage,
    ProgramIndexPage,
    StandardPage,
    TestimonialIndexPage,
)
from core.branding import apply_institution_tokens, brand_from_settings


class Command(BaseCommand):
    help = "Set up International Relations section (CGRI & Movilidad) pages"

    def add_arguments(self, parser):
        parser.add_argument(
            "--replace",
            action="store_true",
            help="Replace existing internacional page if it exists",
        )

    def _ensure_child(self, parent, model, slug, **fields):
        existing = parent.get_children().filter(slug=slug).first()
        if existing:
            self.stdout.write(self.style.WARNING(f"  ⚠ {slug} already exists"))
            return existing.specific
        page = model(slug=slug, **fields)
        parent.add_child(instance=page)
        page.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"  ✓ {page.url}"))
        return page

    @transaction.atomic
    def handle(self, *args, **options):
        site = Site.objects.get(is_default_site=True)
        root_page = site.root_page

        brand = brand_from_settings(settings)

        def t(text):
            return apply_institution_tokens(text, brand)

        self.stdout.write("\n=== Setting up International Relations Section ===\n")

        internacional = InternationalHomePage.objects.filter(slug="internacional").first()
        if internacional and options["replace"]:
            self.stdout.write(
                self.style.WARNING("Deleting existing 'internacional' page...")
            )
            internacional.delete()
            internacional = None

        if internacional is None:
            self.stdout.write("Creating International Home Page...")
            internacional = InternationalHomePage(
                title="Relaciones Internacionales",
                slug="internacional",
                hero_title=t("Relaciones Internacionales UAdeC"),
                hero_subtitle=(
                    "Tu puerta al mundo académico - Intercambio, movilidad y "
                    "convenios internacionales"
                ),
                introduction=t(
                    "<p>La Coordinación General de Relaciones Internacionales (CGRI) "
                    "de la Universidad Autónoma de Coahuila promueve la "
                    "internacionalización de la universidad a través de programas de "
                    "movilidad estudiantil, convenios de colaboración académica y "
                    "oportunidades de intercambio cultural.</p>"
                ),
                show_stats=True,
                stat_programs_count=25,
                stat_countries_count=15,
                stat_students_count=150,
                stat_institutions_count=40,
                seo_title=t("Relaciones Internacionales - UAdeC"),
                search_description=t(
                    "Coordinación General de Relaciones Internacionales de la "
                    "Universidad Autónoma de Coahuila. Programas de intercambio y "
                    "movilidad estudiantil."
                ),
                show_in_menus=True,
            )
            root_page.add_child(instance=internacional)
            internacional.save_revision().publish()
            self.stdout.write(self.style.SUCCESS(f"✓ Created: {internacional.url}"))
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Page 'internacional' already exists; adding any missing children."
                )
            )

        # 2. CGRI Institutional section
        self.stdout.write("\nCreating CGRI Institutional Section...")
        cgri_home = self._ensure_child(
            internacional,
            CGRIPage,
            "institucional",
            title="Información Institucional",
            subtitle="Coordinación General de Relaciones Internacionales",
            introduction=t(
                "La CGRI es responsable de promover y coordinar las actividades de "
                "internacionalización de la Universidad Autónoma de Coahuila."
            ),
            show_contact=True,
            contact_name="Coordinación General de Relaciones Internacionales",
            contact_email=t("cgri@uadec.mx"),
            contact_phone="+52 (844) 000-0000",
            contact_office="Rectoría, Edificio Central",
            seo_title="CGRI - Información Institucional",
            show_in_menus=True,
        )

        cgri_pages = [
            {
                "title": "Misión y Visión",
                "slug": "mision-vision",
                "introduction": "Conoce la misión, visión y objetivos de la CGRI.",
            },
            {
                "title": "Equipo",
                "slug": "equipo",
                "introduction": t(
                    "Conoce al equipo que hace posible la internacionalización de la UAdeC."
                ),
            },
            {
                "title": "Organigrama",
                "slug": "organigrama",
                "introduction": (
                    "Consulta el organigrama de la Coordinación General de "
                    "Relaciones Internacionales."
                ),
            },
            {
                "title": "Acreditaciones",
                "slug": "acreditaciones",
                "introduction": "Acreditaciones internacionales de nuestros programas académicos.",
            },
            {
                "title": "Centros de Idiomas",
                "slug": "centros-de-idiomas",
                "introduction": t(
                    "La CGRI coadyuva en la enseñanza de lenguas extranjeras a través "
                    "de los centros de idiomas de la UAdeC."
                ),
            },
            {
                "title": "Asesoría Consular",
                "slug": "asesoria-consular",
                "introduction": (
                    "Servicios de asesoría consular e internacionalización de la lengua "
                    "para trámites de movilidad."
                ),
            },
            {
                "title": "Asociaciones",
                "slug": "asociaciones",
                "introduction": (
                    "Redes y asociaciones internacionales de las que forma parte la CGRI."
                ),
            },
            {
                "title": "Contacto",
                "slug": "contacto",
                "introduction": "Ponte en contacto con la Coordinación de Relaciones Internacionales.",
                "show_contact": True,
                "contact_name": t("CGRI UAdeC"),
                "contact_email": t("cgri@uadec.mx"),
            },
        ]

        for page_data in cgri_pages:
            self._ensure_child(
                cgri_home,
                CGRIPage,
                page_data["slug"],
                title=page_data["title"],
                introduction=page_data["introduction"],
                show_contact=page_data.get("show_contact", False),
                contact_name=page_data.get("contact_name", ""),
                contact_email=page_data.get("contact_email", ""),
                show_in_menus=True,
            )

        self.stdout.write("\nCreating Convenios Section...")
        convenios_index = self._ensure_child(
            cgri_home,
            ConvenioIndexPage,
            "convenios",
            title="Convenios Internacionales",
            introduction=t(
                "<p>La UAdeC mantiene convenios de colaboración con instituciones "
                "educativas de todo el mundo, facilitando el intercambio académico y "
                "la movilidad estudiantil.</p>"
            ),
            seo_title=t("Convenios Internacionales - UAdeC"),
            show_in_menus=True,
        )

        # 4. Movilidad Estudiantil
        self.stdout.write("\nCreating Movilidad Estudiantil Section...")
        movilidad = self._ensure_child(
            internacional,
            MovilidadLandingPage,
            "movilidad-estudiantil",
            title="Movilidad Estudiantil",
            hero_title="Movilidad Estudiantil Internacional",
            hero_subtitle="Vive una experiencia académica única en el extranjero",
            introduction=t(
                "<p>El programa de movilidad estudiantil de la UAdeC te permite "
                "realizar parte de tus estudios en universidades extranjeras con las "
                "que tenemos convenios de colaboración. Amplía tus horizontes "
                "académicos, culturales y profesionales.</p>"
            ),
            show_quick_links=True,
            show_application_cta=True,
            application_cta_text="Aplicar Ahora",
            seo_title=t("Movilidad Estudiantil - UAdeC"),
            show_in_menus=True,
        )

        self.stdout.write("\nCreating Movilidad Subpages...")

        programas = self._ensure_child(
            movilidad,
            ProgramIndexPage,
            "programas",
            title="Programas Disponibles",
            introduction=(
                "<p>Explora los programas de intercambio disponibles en universidades "
                "de todo el mundo.</p>"
            ),
            seo_title="Programas de Intercambio",
            show_in_menus=True,
        )

        como_aplicar = self._ensure_child(
            movilidad,
            StandardPage,
            "como-aplicar",
            title="¿Cómo Aplicar?",
            introduction=(
                "Guía paso a paso para aplicar a programas de intercambio internacional."
            ),
            show_in_menus=True,
        )

        requisitos = self._ensure_child(
            movilidad,
            StandardPage,
            "requisitos",
            title="Requisitos",
            introduction=(
                "Requisitos académicos, idiomáticos y administrativos para participar "
                "en programas de movilidad."
            ),
            show_in_menus=True,
        )

        documentacion = self._ensure_child(
            movilidad,
            StandardPage,
            "documentacion",
            title="Documentación",
            introduction="Lista de documentos necesarios para tu aplicación de intercambio.",
            show_in_menus=True,
        )

        entrante = self._ensure_child(
            movilidad,
            StandardPage,
            "entrante",
            title="Movilidad Internacional Entrante",
            introduction=(
                "Convocatoria, formularios y formatos para estudiantes internacionales "
                "que desean realizar movilidad en la UAdeC."
            ),
            show_in_menus=True,
        )

        saliente = self._ensure_child(
            movilidad,
            StandardPage,
            "saliente",
            title="Movilidad Internacional Saliente",
            introduction=t(
                "Convocatoria, formularios y formatos para estudiantes UAdeC que "
                "desean realizar movilidad en el extranjero."
            ),
            show_in_menus=True,
        )

        beneficios = self._ensure_child(
            movilidad,
            StandardPage,
            "beneficios",
            title="Beneficios y Apoyos",
            introduction=(
                "Conoce los beneficios académicos, becas y apoyos disponibles para "
                "estudiantes en movilidad."
            ),
            show_in_menus=True,
        )

        calendario = self._ensure_child(
            movilidad,
            StandardPage,
            "calendario",
            title="Calendario y Fechas Importantes",
            introduction=(
                "Fechas límite para aplicaciones, convocatorias y periodos de intercambio."
            ),
            show_in_menus=True,
        )

        faq = self._ensure_child(
            movilidad,
            FAQIndexPage,
            "preguntas-frecuentes",
            title="Preguntas Frecuentes",
            introduction=(
                "<p>Encuentra respuestas a las preguntas más comunes sobre movilidad "
                "estudiantil.</p>"
            ),
            show_in_menus=True,
        )

        testimonials = self._ensure_child(
            movilidad,
            TestimonialIndexPage,
            "testimonios",
            title="Testimonios",
            introduction=t(
                "<p>Lee las experiencias de estudiantes UAdeC que han vivido un "
                "intercambio internacional.</p>"
            ),
            seo_title="Testimonios de Estudiantes",
            show_in_menus=True,
        )

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("✓ International section setup complete!"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write("\nPage Structure:\n")
        self.stdout.write(f"  • {internacional.url} (Main landing)")
        self.stdout.write(f"    ├── {cgri_home.url} (CGRI - Institutional)")
        self.stdout.write(f"    │   ├── {cgri_home.url}mision-vision/")
        self.stdout.write(f"    │   ├── {cgri_home.url}equipo/")
        self.stdout.write(f"    │   ├── {cgri_home.url}organigrama/")
        self.stdout.write(f"    │   ├── {cgri_home.url}acreditaciones/")
        self.stdout.write(f"    │   ├── {cgri_home.url}centros-de-idiomas/")
        self.stdout.write(f"    │   ├── {cgri_home.url}asesoria-consular/")
        self.stdout.write(f"    │   ├── {cgri_home.url}asociaciones/")
        self.stdout.write(f"    │   ├── {cgri_home.url}contacto/")
        self.stdout.write(f"    │   └── {convenios_index.url}")
        self.stdout.write(f"    └── {movilidad.url} (Student-facing)")
        self.stdout.write(f"        ├── {programas.url}")
        self.stdout.write(f"        ├── {como_aplicar.url}")
        self.stdout.write(f"        ├── {requisitos.url}")
        self.stdout.write(f"        ├── {documentacion.url}")
        self.stdout.write(f"        ├── {entrante.url}")
        self.stdout.write(f"        ├── {saliente.url}")
        self.stdout.write(f"        ├── {beneficios.url}")
        self.stdout.write(f"        ├── {calendario.url}")
        self.stdout.write(f"        ├── {faq.url}")
        self.stdout.write(f"        └── {testimonials.url}")

        self.stdout.write("\n" + self.style.SUCCESS("Next Steps:"))
        self.stdout.write("  1. python manage.py populate_internacional_content")
        self.stdout.write("  2. Add convenio pages under /convenios/")
        self.stdout.write("  3. Configure menu in Wagtail admin")
        self.stdout.write(
            "\n"
            + self.style.WARNING(
                "To replace existing pages, run: python manage.py setup_internacional --replace"
            )
        )
