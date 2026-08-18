"""Official UAdeC CGRI / Movilidad URLs and copy for CMS seed and templates.

Links point at www2.uadec.mx / uadec.mx; binaries are not copied into the repo.
"""

CGRI_FILES_BASE = "http://www2.uadec.mx/pub/CGRI/"

FILES = {
    "convocatoria_entrante": f"{CGRI_FILES_BASE}ConvocatoriaMIEntrante.pdf",
    "convocatoria_saliente": f"{CGRI_FILES_BASE}ConvocatoriaMISaliente.pdf",
    "solicitud_participacion_entrante": f"{CGRI_FILES_BASE}AF.pdf",
    "solicitud_participacion_saliente": f"{CGRI_FILES_BASE}FS-SP.pdf",
    "lineamientos": f"{CGRI_FILES_BASE}FS-LD.pdf",
    "carta_compromiso": f"{CGRI_FILES_BASE}FS-CC.docx",
    "carta_retorno": "https://www2.uadec.mx/pub/CGRI/FS-PR.docx",
    "carta_postulacion": f"{CGRI_FILES_BASE}FS-CP.docx",
    "homologacion": f"{CGRI_FILES_BASE}FS-HM.pdf",
    "universidades_convenio": f"{CGRI_FILES_BASE}UniversidadesPorConvenio.pdf",
    "universidades_conahec": f"{CGRI_FILES_BASE}UniversidadesPorCONAHEC.pdf",
}

FORMS = {
    "solicitud_entrante": "https://forms.cloud.microsoft/r/QBdXdy53Bb",
    "solicitud_saliente": "https://forms.cloud.microsoft/r/pQ7ikwCHME",
}

ORGANIGRAMA_PDF = (
    "http://www2.uadec.mx/transparencia/sassit/docs/"
    "ORGANIGRAMA_RELACIONES_INTERNACIONALES.pdf"
)
DIRECTORIO_URL = "http://www2.uadec.mx/pub/directorio/"
IDIOMAS_URL = "https://www.uadec.mx/idiomas/"
ILE_URL = "https://www.uadec.mx/ile/"
CGRI_SITE_URL = "http://www.uadec.mx/cgri/"
MOVILIDAD_SITE_URL = "http://www.uadec.mx/movilidad/"

MAP_EMBED = (
    "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d1801.4859435704268"
    "!2d-100.99182705772793!3d25.439203398632632!2m3!1f0!2f0!3f0!3m2!1i1024"
    "!2i768!4f13.1!3m3!1m2!1s0x86886d57efb6a657%3A0x89fe3ab0439f74d9"
    "!2sCoordinacion+de+Relaciones+Internacionales+UADEC!5e0!3m2!1ses-419!2smx"
    "!4v1549569970812"
)

YOUTUBE_PLAYLIST_EMBED = (
    "https://www.youtube.com/embed/videoseries?list=PLdq68rAvMCQyPeE5QyjLBwlvDkDr-derl"
)

CONTACT = {
    "coordinator_name": "Dra. Lourdes Morales Oyervides",
    "coordinator_title": "Coordinadora General de Relaciones Internacionales",
    "coordinator_email": "lourdesmorales@uadec.edu.mx",
    "office_email": "relaciones.internacionales@uadec.edu.mx",
    "phone": "844 415 3077 | 844 416 9995",
    "office": (
        "Lic. Salvador González Lobo s/n. Colonia República Oriente. "
        "Saltillo, Coahuila. C.P. 25280."
    ),
}

ASSOCIATIONS = [
    {
        "name": "CONAHEC",
        "url": "https://www.conahec.org/",
        "text": "Consortium for North American Higher Education Collaboration.",
    },
    {
        "name": "NAFSA",
        "url": "https://www.nafsa.org/",
        "text": "Association of International Educators.",
    },
    {
        "name": "HACU",
        "url": "https://www.hacu.net/",
        "text": "Hispanic Association of Colleges and Universities.",
    },
    {
        "name": "COLUMBUS",
        "url": "https://www.columbus-web.com/",
        "text": "Cooperación entre Europa y América Latina.",
    },
    {
        "name": "AMPEI",
        "url": "https://www.ampei.org.mx/",
        "text": "Asociación Mexicana para la Educación Internacional.",
    },
    {
        "name": "ECOES",
        "url": "https://www.ecoes.unam.mx/",
        "text": "Espacio Común de Educación Superior.",
    },
    {
        "name": "ANUIES",
        "url": "https://www.anuies.org.mx/",
        "text": "Asociación Nacional de Universidades e Instituciones de Educación Superior.",
    },
]

REQUIRED_DOCUMENTS = [
    "Kárdex con historial académico actualizado al último semestre cursado.",
    (
        "Carta de exposición de motivos. Redactar en máximo 1 cuartilla tus motivos "
        "para realizar Movilidad. En caso de ser a un país de lengua extranjera "
        "redactarla en inglés."
    ),
    "Currículum Vitae actualizado en máximo 2 cuartillas.",
    "Copia del pasaporte mexicano con vigencia mayor a seis meses.",
    "Copia de la credencial de estudiante de la UAdeC.",
    "Carátula inicial de la cuenta Santander con número de cuenta y clabe interbancaria.",
    "3 cartas de recomendación de docentes.",
]

BENEFITS = [
    "Valor curricular.",
    "Experiencia intercultural.",
    "Generación de relaciones y contactos.",
    "Visión profesional global.",
    "Apertura de oportunidades laborales y académicas.",
    "Desarrollo personal.",
]

CALL_REQUIREMENTS = [
    "Promedio mínimo de 80.",
    "Puntaje en TOEFL.",
    "Entrega de documentos.",
    "Trámites migratorios.",
    "Pasaporte vigente.",
    "Trámites sanitarios.",
]

REGIONS = [
    "Canadá.",
    "Estados Unidos de América.",
    "América Latina.",
    "Europa.",
    "Asia.",
]

VIRTUAL_COOPERATION = [
    "Clases Espejo.",
    "Seminarios.",
    "Conversatorios.",
    "Webinars.",
]

RESPONSIBILITIES = (
    "La UAdeC a través de la Coordinación General de Relaciones Internacionales "
    "es la responsable de promover la movilidad internacional tanto en académicos "
    "como en estudiantes, además de gestionar convenios de colaboración con "
    "instituciones educativas y científicas de alta calidad, y buscar la "
    "acreditación internacional de los programas académicos."
)

MISSION = (
    "Incorporar la dimensión internacional en los procesos académicos y "
    "administrativos de la Universidad, fomentar la interculturalidad, coordinar "
    "y administrar los esfuerzos institucionales de cooperación académica, becas "
    "de intercambio y movilidad, así como coadyuvar en la enseñanza de lenguas "
    "extranjeras."
)

VISION = (
    "Ser la instancia institucional que ayude a mejorar la calidad académica en "
    "la docencia, la investigación y la extensión mediante el desarrollo de "
    "características de desempeño internacional de los estudiantes, del personal "
    "académico y administrativo."
)

OBJECTIVES = [
    "Construir una red internacional académica que ofrezca a los estudiantes la "
    "facilidad para interactuar con otros países a través de la movilidad internacional.",
    "Desarrollar convenios de cooperación con instituciones internacionales para "
    "posicionar a la Universidad dentro de un nivel académico de excelencia.",
    "Fomentar la participación de nuestros académicos en experiencias internacionales.",
    "Promover la estancia académica de alumnos extranjeros en nuestra universidad.",
    "Enriquecer los procesos de enseñanza y aprendizaje mediante estancias de "
    "académicos visitantes.",
]

ACHIEVEMENTS = [
    "Colocar estudiantes en universidades del extranjero para estancias académicas.",
    "Recibir estudiantes del extranjero para realizar estancias académicas en la Universidad.",
    "Se realizaron eventos masivos para la concientización de la importancia de la "
    "movilidad internacional.",
    "Se han firmado convenios con prestigiadas universidades de educación superior "
    "alrededor del mundo.",
    "Estancias cortas y semestrales de maestros en el extranjero y visita de maestros "
    "extranjeros en las facultades de la UAdeC.",
    "Participación de académicos en foros de investigación en Estados Unidos.",
    "Participación exitosa de Bachilleratos en el programa “Jóvenes en Acción” "
    "llevado a cabo en Estados Unidos.",
]


def template_context() -> dict:
    """Context dict for CGRI/Movilidad templates."""
    return {
        "files": FILES,
        "forms": FORMS,
        "organigrama_pdf": ORGANIGRAMA_PDF,
        "directorio_url": DIRECTORIO_URL,
        "idiomas_url": IDIOMAS_URL,
        "ile_url": ILE_URL,
        "cgri_site_url": CGRI_SITE_URL,
        "movilidad_site_url": MOVILIDAD_SITE_URL,
        "map_embed": MAP_EMBED,
        "youtube_playlist_embed": YOUTUBE_PLAYLIST_EMBED,
        "contact": CONTACT,
        "associations": ASSOCIATIONS,
        "required_documents": REQUIRED_DOCUMENTS,
        "benefits": BENEFITS,
        "call_requirements": CALL_REQUIREMENTS,
        "regions": REGIONS,
        "virtual_cooperation": VIRTUAL_COOPERATION,
    }
