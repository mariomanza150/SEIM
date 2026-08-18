"""
Populate International section with UAdeC CGRI / Movilidad content.

Sources: https://www.uadec.mx/cgri/ and https://www.uadec.mx/movilidad/
Official files are linked (not copied) from www2.uadec.mx/pub/CGRI/.
"""

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.blocks import StreamValue

from cms.blocks import BaseStreamBlock
from cms.models import (
    CGRIPage,
    ConvenioIndexPage,
    InternationalHomePage,
    MovilidadLandingPage,
    StandardPage,
)
from cms.uadec_resources import (
    ACHIEVEMENTS,
    ASSOCIATIONS,
    BENEFITS,
    CALL_REQUIREMENTS,
    CONTACT,
    DIRECTORIO_URL,
    FILES,
    FORMS,
    IDIOMAS_URL,
    ILE_URL,
    MISSION,
    OBJECTIVES,
    ORGANIGRAMA_PDF,
    REGIONS,
    REQUIRED_DOCUMENTS,
    RESPONSIBILITIES,
    VIRTUAL_COOPERATION,
    VISION,
)
from core.branding import apply_institution_tokens_deep, brand_from_settings


def _rich(html: str) -> dict:
    return {"type": "rich_text", "value": {"content": html}}


def _cta(title, text, button_text, button_link, style="primary") -> dict:
    return {
        "type": "call_to_action",
        "value": {
            "title": title,
            "text": text,
            "button_text": button_text,
            "button_link": button_link,
            "style": style,
        },
    }


def _cards(heading, items, columns="3", subheading="") -> dict:
    return {
        "type": "card_grid",
        "value": {
            "heading": heading,
            "subheading": subheading,
            "columns": str(columns),
            "cards": items,
        },
    }


def _ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


def _file_link(label: str, url: str) -> str:
    return f'<li><a href="{url}" target="_blank" rel="noopener">{label}</a></li>'


class Command(BaseCommand):
    help = "Populate International section with real UAdeC content"

    def _child(self, parent, model, slug):
        child = parent.get_children().filter(slug=slug).first()
        if child is None:
            return None
        return child.specific

    def _publish_body(self, page, blocks):
        page.body = StreamValue(
            BaseStreamBlock(),
            apply_institution_tokens_deep(blocks, self.brand),
            is_lazy=True,
        )
        page.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"✓ Updated: {page.url}"))

    def _publish_fields(self, page, **fields):
        for key, value in fields.items():
            setattr(page, key, apply_institution_tokens_deep(value, self.brand))
        page.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"✓ Updated: {page.url}"))

    @transaction.atomic
    def handle(self, *args, **options):
        self.brand = brand_from_settings(settings)
        short = self.brand["short_name"]
        name = self.brand["name"]

        self.stdout.write(
            f"\n=== Populating Internacional ({short} example content) ===\n"
        )

        internacional = InternationalHomePage.objects.filter(slug="internacional").first()
        if internacional is None:
            self.stdout.write(
                self.style.ERROR(
                    "International home page not found. Run setup_internacional first."
                )
            )
            return

        cgri_home = self._child(internacional, CGRIPage, "institucional")
        movilidad = self._child(internacional, MovilidadLandingPage, "movilidad-estudiantil")
        if cgri_home is None or movilidad is None:
            self.stdout.write(
                self.style.ERROR(
                    "CGRI or Movilidad pages missing. Run setup_internacional first."
                )
            )
            return

        self._update_internacional(internacional, short, name)
        self._update_cgri(cgri_home, name)
        self._update_movilidad(movilidad)

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("✓ Content population complete!"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write("  • https://www.uadec.mx/cgri/")
        self.stdout.write("  • https://www.uadec.mx/movilidad/")

    def _update_internacional(self, page, short, name):
        page.hero_title = f"Relaciones Internacionales {short}"
        page.hero_subtitle = (
            "Coordinación General de Relaciones Internacionales - Promoviendo la "
            "movilidad académica y la cooperación internacional"
        )
        page.introduction = (
            f"<p>La Coordinación General de Relaciones Internacionales (CGRI) de "
            f"{name} es responsable de promover la movilidad internacional de "
            f"académicos y estudiantes, gestionar convenios de colaboración con "
            f"instituciones educativas y científicas de alta calidad, y buscar la "
            f"acreditación internacional de los programas académicos.</p>"
        )
        page.stat_programs_count = 50
        page.stat_countries_count = 20
        page.stat_students_count = 200
        page.stat_institutions_count = 60
        self._publish_body(
            page,
            [
                _rich(f"<h2>Responsabilidades</h2><p>{RESPONSIBILITIES}</p>"),
            ],
        )

    def _update_cgri(self, cgri_home, name):
        cgri_home.introduction = (
            f"La CGRI es la instancia responsable de promover la internacionalización "
            f"de {name}, facilitando la movilidad académica y fortaleciendo la "
            f"cooperación con instituciones de prestigio internacional."
        )
        cgri_home.show_contact = True
        cgri_home.contact_name = CONTACT["coordinator_name"]
        cgri_home.contact_title = CONTACT["coordinator_title"]
        cgri_home.contact_email = CONTACT["coordinator_email"]
        cgri_home.contact_phone = CONTACT["phone"]
        cgri_home.contact_office = CONTACT["office"]
        self._publish_body(
            cgri_home,
            [
                _rich(f"<h2>Responsabilidades</h2><p>{RESPONSIBILITIES}</p>"),
                _rich(f"<h2>Misión</h2><p>{MISSION}</p>"),
                _rich(f"<h2>Visión</h2><p>{VISION}</p>"),
                _rich("<h2>Objetivos</h2>" + _ul(OBJECTIVES)),
                _rich("<h2>Logros</h2>" + _ul(ACHIEVEMENTS)),
            ],
        )

        mision = self._child(cgri_home, CGRIPage, "mision-vision")
        if mision:
            mision.introduction = (
                "Conoce la misión, visión y objetivos estratégicos de la "
                "Coordinación General de Relaciones Internacionales."
            )
            mision.show_contact = True
            mision.contact_email = CONTACT["office_email"]
            mision.contact_phone = CONTACT["phone"]
            self._publish_body(
                mision,
                [
                    _rich(f"<h2>Misión</h2><p>{MISSION}</p>"),
                    _rich(f"<h2>Visión</h2><p>{VISION}</p>"),
                    _rich("<h2>Objetivos</h2>" + _ul(OBJECTIVES)),
                    _rich("<h2>Logros</h2>" + _ul(ACHIEVEMENTS)),
                ],
            )

        equipo = self._child(cgri_home, CGRIPage, "equipo")
        if equipo:
            equipo.show_contact = True
            equipo.contact_name = CONTACT["coordinator_name"]
            equipo.contact_title = CONTACT["coordinator_title"]
            equipo.contact_email = CONTACT["coordinator_email"]
            equipo.contact_phone = CONTACT["phone"]
            equipo.contact_office = CONTACT["office"]
            self._publish_body(
                equipo,
                [
                    _rich(
                        "<h2>Coordinación General</h2>"
                        f"<p><strong>{CONTACT['coordinator_name']}</strong><br>"
                        f"{CONTACT['coordinator_title']}<br>"
                        f'<a href="mailto:{CONTACT["coordinator_email"]}">'
                        f"{CONTACT['coordinator_email']}</a></p>"
                    ),
                    _rich(
                        "<h2>Oficina</h2>"
                        f"<p>{CONTACT['office']}<br>"
                        f"Tel. {CONTACT['phone']}<br>"
                        f'<a href="mailto:{CONTACT["office_email"]}">'
                        f"{CONTACT['office_email']}</a></p>"
                    ),
                    _cta(
                        "Directorio institucional",
                        "Consulta el directorio general de la universidad.",
                        "Abrir directorio",
                        DIRECTORIO_URL,
                        "secondary",
                    ),
                ],
            )

        organigrama = self._child(cgri_home, CGRIPage, "organigrama")
        if organigrama:
            self._publish_body(
                organigrama,
                [
                    _rich(
                        "<h2>Organigrama</h2><p>Organigrama de la Coordinación General "
                        "de Relaciones Internacionales.</p>"
                    ),
                    _cta(
                        "Descargar organigrama",
                        "PDF oficial de transparencia (Relaciones Internacionales).",
                        "Descargar PDF",
                        ORGANIGRAMA_PDF,
                    ),
                ],
            )

        acreditaciones = self._child(cgri_home, CGRIPage, "acreditaciones")
        if acreditaciones:
            self._publish_body(
                acreditaciones,
                [
                    _rich(
                        "<h2>Acreditaciones internacionales</h2>"
                        f"<p>{RESPONSIBILITIES}</p>"
                        "<p>La CGRI busca la acreditación internacional de los "
                        "programas académicos y fortalece la cooperación con "
                        "instituciones educativas y científicas de alta calidad.</p>"
                    ),
                ],
            )

        idiomas = self._child(cgri_home, CGRIPage, "centros-de-idiomas")
        if idiomas:
            self._publish_body(
                idiomas,
                [
                    _rich(
                        "<h2>Centros de idiomas</h2>"
                        "<p>La misión de la CGRI incluye coadyuvar en la enseñanza de "
                        "lenguas extranjeras. Los centros de idiomas de la universidad "
                        "ofrecen formación para movilidad y cooperación internacional.</p>"
                    ),
                    _cta(
                        "Sitio de idiomas UAdeC",
                        "Consulta oferta, horarios y sedes en el sitio institucional.",
                        "Ir a idiomas",
                        IDIOMAS_URL,
                    ),
                ],
            )

        consular = self._child(cgri_home, CGRIPage, "asesoria-consular")
        if consular:
            self._publish_body(
                consular,
                [
                    _rich(
                        "<h2>Servicios de asesoría consular</h2>"
                        "<p>Orientación para trámites migratorios, pasaporte, visas y "
                        "requisitos sanitarios vinculados a la movilidad internacional.</p>"
                    ),
                    _cta(
                        "Internacionalización de la Lengua (ILE)",
                        "Más información sobre servicios consulares e ILE.",
                        "Abrir ILE",
                        ILE_URL,
                    ),
                ],
            )

        asociaciones = self._child(cgri_home, CGRIPage, "asociaciones")
        if asociaciones:
            cards = [
                {
                    "icon": "bi-globe2",
                    "title": item["name"],
                    "text": item["text"],
                    "link": item["url"],
                    "link_text": item["url"].replace("https://", "").replace("http://", ""),
                }
                for item in ASSOCIATIONS
            ]
            self._publish_body(
                asociaciones,
                [
                    _rich(
                        "<h2>Asociaciones y redes</h2>"
                        "<p>La universidad participa en redes de educación "
                        "internacional que respaldan la movilidad y la cooperación.</p>"
                    ),
                    _cards("Membresías", cards, columns="3"),
                ],
            )

        contacto = self._child(cgri_home, CGRIPage, "contacto")
        if contacto:
            contacto.show_contact = True
            contacto.contact_name = CONTACT["coordinator_name"]
            contacto.contact_title = CONTACT["coordinator_title"]
            contacto.contact_email = CONTACT["coordinator_email"]
            contacto.contact_phone = CONTACT["phone"]
            contacto.contact_office = CONTACT["office"]
            self._publish_body(
                contacto,
                [
                    _rich(
                        "<h2>Contacto CGRI</h2>"
                        f"<p><strong>{CONTACT['coordinator_name']}</strong><br>"
                        f"{CONTACT['coordinator_title']}</p>"
                        "<ul>"
                        f'<li>Email: <a href="mailto:{CONTACT["coordinator_email"]}">'
                        f"{CONTACT['coordinator_email']}</a></li>"
                        f'<li>Email oficina: <a href="mailto:{CONTACT["office_email"]}">'
                        f"{CONTACT['office_email']}</a></li>"
                        f"<li>Teléfono: {CONTACT['phone']}</li>"
                        f"<li>Dirección: {CONTACT['office']}</li>"
                        "</ul>"
                    ),
                ],
            )

        convenios = self._child(cgri_home, ConvenioIndexPage, "convenios")
        if convenios:
            convenios.introduction = (
                "<p>Listados oficiales de universidades para movilidad internacional "
                "2026-2. Los convenios individuales se pueden publicar como páginas "
                "hijas.</p>"
                "<ul>"
                + _file_link(
                    "Universidades con Convenio para Movilidad Internacional 2026-2",
                    FILES["universidades_convenio"],
                )
                + _file_link(
                    "Universidades CONAHEC para Movilidad Internacional 2026-2",
                    FILES["universidades_conahec"],
                )
                + "</ul>"
            )
            convenios.save_revision().publish()
            self.stdout.write(self.style.SUCCESS(f"✓ Updated: {convenios.url}"))

    def _update_movilidad(self, movilidad):
        movilidad.hero_title = "Movilidad Estudiantil Internacional"
        movilidad.hero_subtitle = (
            "Vive una experiencia académica única en el extranjero - Amplía tus "
            "horizontes y desarrolla competencias internacionales"
        )
        movilidad.introduction = (
            "<p>El programa de movilidad estudiantil de la UAdeC te ofrece la "
            "oportunidad de realizar parte de tus estudios en universidades "
            "extranjeras con las que mantenemos convenios de colaboración.</p>"
            "<p>Contamos con convenios en más de 20 países incluyendo Alemania, "
            "Argentina, Brasil, Canadá, Colombia, Corea del Sur, Cuba, Chile, China, "
            "España, Estados Unidos, Finlandia, Francia, Italia, Panamá, Perú y "
            "Taiwán.</p>"
        )
        movilidad.show_quick_links = True
        movilidad.show_application_cta = True
        movilidad.application_cta_text = "Aplicar al Programa de Movilidad"
        self._publish_body(
            movilidad,
            [
                _rich(
                    "<h2>Cooperación virtual</h2>"
                    "<p>Además de las estancias presenciales, la CGRI impulsa:</p>"
                    + _ul(VIRTUAL_COOPERATION)
                ),
            ],
        )

        requisitos = self._child(movilidad, StandardPage, "requisitos")
        if requisitos:
            requisitos.introduction = (
                "Conoce los requisitos académicos y administrativos necesarios para "
                "participar en los programas de movilidad estudiantil de la UAdeC."
            )
            self._publish_body(
                requisitos,
                [
                    _rich("<h2>Convocatoria semestral</h2>" + _ul(CALL_REQUIREMENTS)),
                    _rich(
                        "<h2>Requisitos académicos</h2>"
                        "<ul><li>Promedio mínimo de 80.</li>"
                        "<li>Puntaje en TOEFL (destinos de lengua extranjera).</li>"
                        "<li>Pasaporte vigente (más de seis meses).</li>"
                        "<li>Trámites migratorios y sanitarios según el país destino.</li>"
                        "<li>Entrega completa de documentos en tiempo y forma.</li></ul>"
                    ),
                ],
            )

        documentacion = self._child(movilidad, StandardPage, "documentacion")
        if documentacion:
            documentacion.introduction = (
                "Documentación requerida para trámites de movilidad y formatos "
                "oficiales de la CGRI."
            )
            docs_html = "<h2>Documentación Requerida para Trámites de Movilidad</h2>" + _ul(
                REQUIRED_DOCUMENTS
            )
            formats_html = (
                "<h2>Formatos de Movilidad Entrante</h2><ul>"
                + _file_link(
                    "Solicitud de Participación",
                    FILES["solicitud_participacion_entrante"],
                )
                + "</ul><h2>Formatos de Movilidad Saliente</h2><ul>"
                + _file_link(
                    "Solicitud de Participación",
                    FILES["solicitud_participacion_saliente"],
                )
                + _file_link("Lineamientos y Disposiciones", FILES["lineamientos"])
                + _file_link("Carta Compromiso", FILES["carta_compromiso"])
                + _file_link(
                    "Carta Compromiso de Adhesión al Programa de Retorno",
                    FILES["carta_retorno"],
                )
                + _file_link("Carta de Postulación", FILES["carta_postulacion"])
                + _file_link("Homologación de Materias", FILES["homologacion"])
                + "</ul>"
            )
            self._publish_body(documentacion, [_rich(docs_html), _rich(formats_html)])

        entrante = self._child(movilidad, StandardPage, "entrante")
        if entrante:
            self._publish_body(
                entrante,
                [
                    _rich(
                        "<h2>Movilidad Internacional Entrante</h2>"
                        "<p>Convocatoria y formatos para estudiantes internacionales "
                        "que desean cursar un periodo académico en la UAdeC.</p>"
                    ),
                    _cta(
                        "Convocatoria",
                        "Descarga la convocatoria oficial de movilidad entrante.",
                        "Descargar convocatoria",
                        FILES["convocatoria_entrante"],
                    ),
                    _cta(
                        "Solicitud en línea",
                        "Completa el formulario de solicitud entrante.",
                        "Abrir formulario",
                        FORMS["solicitud_entrante"],
                    ),
                    _cta(
                        "Solicitud de Participación",
                        "Formato AF para movilidad entrante.",
                        "Descargar formato",
                        FILES["solicitud_participacion_entrante"],
                        "secondary",
                    ),
                ],
            )

        saliente = self._child(movilidad, StandardPage, "saliente")
        if saliente:
            self._publish_body(
                saliente,
                [
                    _rich(
                        "<h2>Movilidad Internacional Saliente</h2>"
                        "<p>Convocatoria y formatos para estudiantes UAdeC. El portal "
                        "SEIM es la vía principal para aplicar y dar seguimiento.</p>"
                        '<p><a href="/seim/login/">Aplicar en SEIM</a> — crea tu cuenta '
                        "o inicia sesión para enviar tu solicitud.</p>"
                    ),
                    _cta(
                        "Convocatoria",
                        "Descarga la convocatoria oficial de movilidad saliente.",
                        "Descargar convocatoria",
                        FILES["convocatoria_saliente"],
                        "secondary",
                    ),
                    _cta(
                        "Formulario alterno",
                        "Solicitud saliente en Microsoft Forms (vía CGRI).",
                        "Abrir formulario",
                        FORMS["solicitud_saliente"],
                        "info",
                    ),
                    _rich(
                        "<h3>Formatos oficiales</h3><ul>"
                        + _file_link(
                            "Solicitud de Participación",
                            FILES["solicitud_participacion_saliente"],
                        )
                        + _file_link(
                            "Lineamientos y Disposiciones", FILES["lineamientos"]
                        )
                        + _file_link("Carta Compromiso", FILES["carta_compromiso"])
                        + _file_link(
                            "Carta Compromiso de Adhesión al Programa de Retorno",
                            FILES["carta_retorno"],
                        )
                        + _file_link("Carta de Postulación", FILES["carta_postulacion"])
                        + _file_link("Homologación de Materias", FILES["homologacion"])
                        + "</ul>"
                    ),
                ],
            )

        beneficios = self._child(movilidad, StandardPage, "beneficios")
        if beneficios:
            beneficios.introduction = (
                "Beneficios de la movilidad, requisitos de la convocatoria semestral "
                "y regiones con convenios."
            )
            self._publish_body(
                beneficios,
                [
                    _rich("<h2>Beneficios de la Movilidad</h2>" + _ul(BENEFITS)),
                    _rich("<h2>Convocatoria semestral</h2>" + _ul(CALL_REQUIREMENTS)),
                    _rich("<h2>Convenios internacionales</h2>" + _ul(REGIONS)),
                ],
            )

        calendario = self._child(movilidad, StandardPage, "calendario")
        if calendario:
            calendario.introduction = (
                "Fechas importantes y calendario de convocatorias para programas de "
                "movilidad estudiantil."
            )
            self._publish_body(
                calendario,
                [
                    _rich(
                        "<h2>Convocatoria 2026</h2>"
                        "<p><strong>Movilidad académica internacional enero–junio 2026."
                        "</strong> Apertura de la convocatoria: 22 de enero de 2026.</p>"
                    ),
                    _rich(
                        "<h2>Movilidad de otoño</h2>"
                        "<ul><li>Publicación de convocatoria: febrero</li>"
                        "<li>Cierre de solicitudes: marzo</li>"
                        "<li>Entrevistas y selección: abril</li>"
                        "<li>Resultados: mayo</li>"
                        "<li>Trámites migratorios: mayo–julio</li>"
                        "<li>Inicio de estancia: agosto–septiembre</li></ul>"
                    ),
                    _rich(
                        "<h2>Movilidad de primavera</h2>"
                        "<ul><li>Publicación de convocatoria: septiembre</li>"
                        "<li>Cierre de solicitudes: octubre</li>"
                        "<li>Entrevistas y selección: noviembre</li>"
                        "<li>Resultados: diciembre</li>"
                        "<li>Trámites migratorios: diciembre–enero</li>"
                        "<li>Inicio de estancia: enero–febrero</li></ul>"
                    ),
                ],
            )

        como_aplicar = self._child(movilidad, StandardPage, "como-aplicar")
        if como_aplicar:
            como_aplicar.introduction = (
                "Inicia tu experiencia de intercambio académico internacional creando "
                "tu cuenta en el Sistema SEIM y completando tu solicitud en línea."
            )
            self._publish_body(
                como_aplicar,
                [
                    _rich(
                        "<h2>Proceso de Aplicación</h2>"
                        "<p>Para aplicar a un programa de intercambio académico de la "
                        "UAdeC, sigue estos pasos:</p>"
                        '<p><a href="/seim/register/">Crear cuenta en SEIM</a> · '
                        '<a href="/seim/login/">Iniciar sesión</a></p>'
                    ),
                    _rich(
                        "<h3>Documentos</h3>"
                        "<p>Reúne kárdex, carta de motivos, CV, pasaporte, credencial "
                        "UAdeC, carátula Santander y tres cartas de recomendación. "
                        "Consulta la lista completa en Documentación.</p>"
                    ),
                ],
            )
