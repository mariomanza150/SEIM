"""Management command to enhance the homepage with content blocks."""

from django.core.management.base import BaseCommand

from cms.models import HomePage
from cms.utils.official_assets import (
    download_official_assets,
    get_or_create_wagtail_image,
)

CONVOCATORIA_ENTRANTE = "https://www2.uadec.mx/pub/CGRI/ConvocatoriaMIEntrante.pdf"
CONVOCATORIA_SALIENTE = "https://www2.uadec.mx/pub/CGRI/ConvocatoriaMISaliente.pdf"
UNIVERSIDADES_CONVENIO = "https://www2.uadec.mx/pub/CGRI/UniversidadesPorConvenio.pdf"
UNIVERSIDADES_CONAHEC = "https://www2.uadec.mx/pub/CGRI/UniversidadesPorCONAHEC.pdf"
YOUTUBE_PLAYLIST = (
    "https://www.youtube.com/playlist?list=PLdq68rAvMCQyPeE5QyjLBwlvDkDr-derl"
)


class Command(BaseCommand):
    help = "Enhance homepage with content blocks for students and teachers"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Enhancing CMS homepage..."))

        try:
            home = HomePage.objects.get(slug="home")
        except HomePage.DoesNotExist:
            self.stdout.write(self.style.ERROR("  ✗ HomePage not found"))
            return

        try:
            saved = download_official_assets()
            hero_path = saved.get("mi2026.jpg")
            if hero_path:
                hero_image = get_or_create_wagtail_image("mi2026.jpg", hero_path)
                home.hero_image = hero_image
            self.stdout.write(self.style.SUCCESS("  ✓ Official assets downloaded"))
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f"  ⚠ Could not attach hero image: {exc}"))
            self.stdout.write(
                self.style.WARNING("  Run: python manage.py sync_uadec_cms_assets")
            )

        enhanced_content = [
            {
                "type": "hero",
                "value": {
                    "title": "Vive una Experiencia Internacional",
                    "subtitle": "Amplía tus horizontes académicos y culturales con los programas de movilidad de la CGRI",
                    "background_color": "primary",
                    "button_text": "Ver Programas",
                    "button_link": "/programas/",
                },
            },
            {
                "type": "paragraph",
                "value": (
                    "<p>La UAdeC, a través de la Coordinación General de Relaciones "
                    "Internacionales, promueve la movilidad internacional de "
                    "estudiantes y académicos, gestiona convenios de colaboración y "
                    "asesora a quienes desean una estancia en el extranjero o en "
                    "nuestra universidad.</p>"
                ),
            },
            {
                "type": "card_grid",
                "value": {
                    "heading": "¿Por qué elegir un intercambio académico?",
                    "subheading": "Beneficios de la movilidad internacional UAdeC",
                    "columns": "3",
                    "cards": [
                        {
                            "icon": "bi-award",
                            "title": "Valor curricular",
                            "text": "Las materias cursadas se homologan con tu plan de estudios mediante el formato oficial de la CGRI.",
                            "link": "/preguntas-frecuentes/",
                            "link_text": "Ver requisitos",
                        },
                        {
                            "icon": "bi-globe2",
                            "title": "Experiencia intercultural",
                            "text": "Estudia en universidades con convenio en América, Europa y Asia, y construye una red académica internacional.",
                            "link": "/sobre-nosotros/",
                            "link_text": "Conoce la CGRI",
                        },
                        {
                            "icon": "bi-people",
                            "title": "Relaciones y contactos",
                            "text": "Genera vínculos con docentes y estudiantes de instituciones socias y de redes como CONAHEC.",
                            "link": "/contacto/",
                            "link_text": "Contacto",
                        },
                        {
                            "icon": "bi-briefcase",
                            "title": "Visión profesional global",
                            "text": "Abre oportunidades laborales y académicas con una perspectiva internacional en tu disciplina.",
                            "link": "/programas/",
                            "link_text": "Ver destinos",
                        },
                        {
                            "icon": "bi-translate",
                            "title": "Segunda lengua",
                            "text": "La CGRI promueve el estudio de una segunda lengua como herramienta de crecimiento profesional.",
                            "link": "/programas/",
                            "link_text": "Ver programas",
                        },
                        {
                            "icon": "bi-person-check",
                            "title": "Desarrollo personal",
                            "text": "Autonomía, resiliencia y competencias interculturales que complementan tu formación en la UAdeC.",
                            "link": "/blog/",
                            "link_text": "Experiencias",
                        },
                    ],
                },
            },
            {
                "type": "call_to_action",
                "value": {
                    "title": "Convocatoria de Movilidad Internacional 2026-2",
                    "text": "Consulta las convocatorias oficiales de movilidad entrante y saliente, y las universidades con convenio o CONAHEC para el periodo 2026-2.",
                    "button_text": "Convocatoria saliente (PDF)",
                    "button_link": CONVOCATORIA_SALIENTE,
                    "style": "primary",
                },
            },
            {
                "type": "card_grid",
                "value": {
                    "heading": "Documentos oficiales CGRI",
                    "subheading": "Convocatorias y listados publicados por Relaciones Internacionales",
                    "columns": "2",
                    "cards": [
                        {
                            "icon": "bi-file-earmark-arrow-down",
                            "title": "Movilidad entrante",
                            "text": "Convocatoria oficial para estudiantes internacionales que desean una estancia en la UAdeC.",
                            "link": CONVOCATORIA_ENTRANTE,
                            "link_text": "Descargar PDF",
                        },
                        {
                            "icon": "bi-file-earmark-arrow-down",
                            "title": "Movilidad saliente",
                            "text": "Convocatoria para estudiantes UAdeC que aplican a una estancia en el extranjero.",
                            "link": CONVOCATORIA_SALIENTE,
                            "link_text": "Descargar PDF",
                        },
                        {
                            "icon": "bi-building",
                            "title": "Universidades por convenio 2026-2",
                            "text": "Listado de instituciones con convenio vigente para movilidad internacional.",
                            "link": UNIVERSIDADES_CONVENIO,
                            "link_text": "Ver listado",
                        },
                        {
                            "icon": "bi-diagram-3",
                            "title": "Universidades CONAHEC 2026-2",
                            "text": "Opciones de movilidad a través del consorcio CONAHEC.",
                            "link": UNIVERSIDADES_CONAHEC,
                            "link_text": "Ver listado",
                        },
                    ],
                },
            },
            {
                "type": "video",
                "value": {
                    "video": YOUTUBE_PLAYLIST,
                    "caption": "CGRI UAdeC — Movilidad Internacional",
                },
            },
            {
                "type": "process_steps",
                "value": {
                    "heading": "¿Cómo aplicar?",
                    "subheading": "Sigue estos pasos para iniciar tu movilidad a través de SEIM y la CGRI",
                    "steps": [
                        {
                            "number": "1",
                            "title": "Infórmate",
                            "description": "Revisa convocatorias, requisitos y universidades con convenio o CONAHEC.",
                            "icon": "bi-info-circle",
                        },
                        {
                            "number": "2",
                            "title": "Prepara documentos",
                            "description": "Kárdex, carta de motivos, CV, pasaporte, credencial UAdeC y tres cartas de recomendación.",
                            "icon": "bi-file-earmark-text",
                        },
                        {
                            "number": "3",
                            "title": "Aplica en línea",
                            "description": "Crea tu cuenta en SEIM y envía tu solicitud de movilidad.",
                            "icon": "bi-laptop",
                        },
                        {
                            "number": "4",
                            "title": "Evaluación",
                            "description": "La CGRI y tu unidad académica revisan expediente, idioma y postulación.",
                            "icon": "bi-clipboard-check",
                        },
                        {
                            "number": "5",
                            "title": "Preparativos",
                            "description": "Visa, seguro médico, trámites migratorios y homologación de materias.",
                            "icon": "bi-airplane",
                        },
                        {
                            "number": "6",
                            "title": "¡Viaja!",
                            "description": "Inicia tu estancia. La CGRI te acompaña durante el proceso.",
                            "icon": "bi-star",
                        },
                    ],
                },
            },
            {
                "type": "testimonial",
                "value": {
                    "quote": "Mi experiencia en la Universidad de Salamanca cambió mi vida. No solo mejoré mi nivel académico, sino que hice amigos de todo el mundo y descubrí una nueva perspectiva de mi carrera. Fue la mejor decisión que pude tomar.",
                    "author": "María Rodríguez",
                    "author_title": "Estudiante de Relaciones Internacionales - Intercambio en España 2024",
                },
            },
            {
                "type": "faq",
                "value": {
                    "heading": "Preguntas Frecuentes",
                    "items": [
                        {
                            "question": "¿Cuál es el promedio mínimo requerido?",
                            "answer": (
                                "<p>Según la convocatoria oficial: promedio mínimo general de "
                                "<strong>90</strong> para universidades de habla hispana y "
                                "<strong>85</strong> para universidades de lengua extranjera, "
                                "respaldado por Kárdex al momento de aplicar. Debes ser "
                                "estudiante regular y no estar en el último semestre.</p>"
                            ),
                        },
                        {
                            "question": "¿Necesito saber el idioma del país?",
                            "answer": (
                                "<p>Sí. Para universidades de lengua extranjera se requiere "
                                "inglés nivel B2 o equivalente a 550 puntos TOEFL. Para "
                                "universidades de habla hispana, mínimo B1 o equivalente a "
                                "450 TOEFL, más el idioma que pida la institución destino.</p>"
                            ),
                        },
                        {
                            "question": "¿Cuánto tiempo dura un intercambio?",
                            "answer": (
                                "<p>La convocatoria es semestral. La mayoría de las estancias "
                                "son de un semestre (4–6 meses), con opciones de movilidad "
                                "presencial o virtual según créditos cursados.</p>"
                            ),
                        },
                        {
                            "question": "¿Puedo elegir mis materias en el extranjero?",
                            "answer": (
                                "<p>Sí, previa homologación con tu coordinador de carrera "
                                "usando el formato oficial de Homologación de Materias "
                                "(FS-HM) publicado por la CGRI.</p>"
                            ),
                        },
                    ],
                },
            },
            {
                "type": "call_to_action",
                "value": {
                    "title": "¿Listo para tu aventura internacional?",
                    "text": "Crea tu cuenta en SEIM y envía tu solicitud. Te guiamos paso a paso en el proceso.",
                    "button_text": "¿Cómo Aplicar?",
                    "button_link": "/como-aplicar/",
                    "style": "primary",
                },
            },
        ]

        home.body = enhanced_content
        try:
            home.save_revision().publish()
        except Exception as exc:
            self.stdout.write(
                self.style.WARNING(f"  ⚠ Full homepage save failed ({exc}); retrying without video")
            )
            enhanced_content = [
                block for block in enhanced_content if block.get("type") != "video"
            ]
            home.body = enhanced_content
            home.save_revision().publish()

        self.stdout.write(self.style.SUCCESS("\n✅ Homepage enhanced successfully!"))
        self.stdout.write(
            self.style.SUCCESS(f"   Added {len(enhanced_content)} content blocks")
        )
