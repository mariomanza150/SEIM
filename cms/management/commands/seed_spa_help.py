"""Seed spa-only FAQ help articles and retag public FAQs."""

from django.core.management.base import BaseCommand, CommandError
from wagtail.models import Site

from cms.help import (
    FAQ_AUDIENCE_ADMIN,
    FAQ_AUDIENCE_ALL,
    FAQ_AUDIENCE_COORDINATOR,
    FAQ_AUDIENCE_PARTNER,
    FAQ_AUDIENCE_STUDENT,
    FAQ_INDEX_KIND_SPA_HELP,
    FAQ_SURFACE_PUBLIC,
    FAQ_SURFACE_SPA,
    PUBLIC_FAQ_SLUGS,
    SPA_HELP_INDEX_SLUG,
)
from cms.models import FAQIndexPage, FAQPage

P = FAQ_SURFACE_PUBLIC
S = FAQ_SURFACE_SPA


def _paragraph_body(html):
    return [{"type": "paragraph", "value": html}]


SPA_HELP_ARTICLES = [
    {
        "title": "Usar el panel",
        "slug": "usar-el-panel",
        "introduction": "Cómo leer el panel después de iniciar sesión.",
        "topic": "getting_started",
        "audiences": [FAQ_AUDIENCE_ALL],
        "contextual_keys": "Dashboard",
        "body": "<p>El panel resume lo más urgente para tu rol: solicitudes, documentos, avisos y tareas pendientes.</p><ul><li>Usa las tarjetas de conteo para saltar a la lista correspondiente.</li><li>La actividad reciente muestra cambios de estado y comentarios nuevos.</li><li>El menú lateral abre el resto de herramientas; Ayuda está siempre visible.</li></ul>",
    },
    {
        "title": "Perfil y ajustes",
        "slug": "perfil-y-ajustes",
        "introduction": "Datos personales, apariencia y sesiones.",
        "topic": "account",
        "audiences": [FAQ_AUDIENCE_ALL],
        "contextual_keys": "Profile,Settings",
        "body": "<p>En Perfil actualizas datos de contacto e información académica o institucional. En Ajustes controlas idioma, apariencia, notificaciones y sesiones activas.</p><p>Cierra sesiones que no reconozcas. Los cambios de correo pueden requerir verificación.</p>",
    },
    {
        "title": "Notificaciones",
        "slug": "ayuda-notificaciones",
        "introduction": "Bandeja de avisos del sistema.",
        "topic": "account",
        "audiences": [FAQ_AUDIENCE_ALL],
        "contextual_keys": "Notifications",
        "body": "<p>La bandeja lista avisos de solicitudes, documentos y plazos. Márcalos como leídos cuando ya los atendiste.</p><p>Puedes ajustar qué categorías recibes por correo desde Ajustes. El personal de movilidad configura el enrutamiento; tú solo ves lo que aplica a tu cuenta.</p>",
    },
    {
        "title": "Calendario de plazos",
        "slug": "calendario-de-plazos",
        "introduction": "Fechas límite de convocatorias y trámites.",
        "topic": "getting_started",
        "audiences": [FAQ_AUDIENCE_ALL],
        "contextual_keys": "DeadlinesCalendar",
        "body": "<p>El calendario muestra fechas de cierre de convocatoria, entrega de documentos y otros hitos del intercambio.</p><p>Filtra por programa o solicitud cuando esté disponible. Una fecha en el calendario no sustituye el estado de tu solicitud.</p>",
    },
    {
        "title": "Comparar programas",
        "slug": "comparar-programas",
        "introduction": "Diferencias entre destinos y convocatorias.",
        "topic": "getting_started",
        "audiences": [FAQ_AUDIENCE_ALL],
        "contextual_keys": "ProgramCompare",
        "body": "<p>La comparación pone lado a lado duración, requisitos, destinos anfitriones e idiomas.</p><p>Úsala para decidir a qué programa aplicar. Iniciar una solicitud se hace desde Programas o Solicitudes, no desde la tabla de comparación.</p>",
    },
    {
        "title": "Buscar un programa y empezar una solicitud",
        "slug": "buscar-programa-y-aplicar",
        "introduction": "Del catálogo al borrador de solicitud.",
        "topic": "applications",
        "audiences": [FAQ_AUDIENCE_STUDENT],
        "contextual_keys": "Applications,ApplicationNew,ApplicationForm",
        "body": "<p>Revisa el catálogo, compara destinos y pulsa aplicar en el programa elegido. Se crea un borrador ligado a tu cuenta.</p><p>No envíes hasta completar el formulario dinámico y la lista de documentos. Puedes guardar y volver más tarde.</p>",
    },
    {
        "title": "Borrador, elegibilidad y envío",
        "slug": "borrador-elegibilidad-enviar",
        "introduction": "Qué revisar antes de enviar.",
        "topic": "applications",
        "audiences": [FAQ_AUDIENCE_STUDENT],
        "contextual_keys": "ApplicationNew,ApplicationEdit,ApplicationForm",
        "body": "<p>El borrador guarda respuestas del formulario. Las reglas de elegibilidad pueden bloquear el envío si faltan créditos, idioma o promedio.</p><p>Corrige los campos marcados y vuelve a enviar. Después del envío, algunos datos se bloquean hasta que coordinación pida cambios.</p>",
    },
    {
        "title": "Documentos, reenvío y tipos",
        "slug": "documentos-reenvio-tipos",
        "introduction": "Subir archivos y atender solicitudes de reenvío.",
        "topic": "documents",
        "audiences": [FAQ_AUDIENCE_STUDENT],
        "contextual_keys": "Documents,DocumentDetail",
        "body": "<p>Cada tipo de documento tiene formato, tamaño y, a veces, una nota de ayuda. Sube el archivo en la solicitud o en Documentos.</p><p>Si coordinación pide reenvío, verás el motivo y un plazo. Sustituye el archivo; no crees un duplicado salvo que el sistema lo pida.</p>",
    },
    {
        "title": "Seguimiento de estado y comentarios",
        "slug": "seguimiento-estado-comentarios",
        "introduction": "Qué significa cada estado y cómo responder.",
        "topic": "applications",
        "audiences": [FAQ_AUDIENCE_STUDENT],
        "contextual_keys": "ApplicationDetail,Applications",
        "body": "<p>La ficha de la solicitud muestra el estado actual, la línea de tiempo y los comentarios del personal.</p><p>Responde en el hilo cuando te pidan aclaraciones. Un comentario no cambia el estado por sí solo; espera la actualización formal.</p>",
    },
    {
        "title": "Becas en una solicitud",
        "slug": "becas-en-solicitud",
        "introduction": "Cuando el programa muestra puntuación o becas.",
        "topic": "applications",
        "audiences": [FAQ_AUDIENCE_STUDENT],
        "contextual_keys": "ApplicationDetail",
        "body": "<p>Algunos programas muestran factores de beca o un puntaje. Completa los campos que pida el formulario; no inventes datos.</p><p>La decisión de apoyo económico la toma el personal con las reglas de puntuación. Pregunta a coordinación si no ves el bloque de becas y creías calificar.</p>",
    },
    {
        "title": "Cola de revisión y cambios de estado",
        "slug": "cola-de-revision",
        "introduction": "Revisar solicitudes enviadas y avanzar el flujo.",
        "topic": "review",
        "audiences": [FAQ_AUDIENCE_COORDINATOR],
        "contextual_keys": "CoordinatorReviewQueue",
        "body": "<p>La cola lista solicitudes en revisión. Abre una ficha para ver formulario, documentos y el flujo de estados permitido.</p><p>Cambia el estado solo cuando los requisitos del paso estén cubiertos. El historial queda en la línea de tiempo.</p>",
    },
    {
        "title": "Comentarios y validación de documentos",
        "slug": "comentarios-validacion-documentos",
        "introduction": "Pedir correcciones sin perder el expediente.",
        "topic": "documents",
        "audiences": [FAQ_AUDIENCE_COORDINATOR],
        "contextual_keys": "CoordinatorReviewQueue,Documents,DocumentDetail",
        "body": "<p>Valida o rechaza cada archivo. Si falta información, solicita reenvío con un motivo claro.</p><p>Usa comentarios para el estudiante y notas internas según el tipo de comentario. No sustituyas un rechazo de documento solo con un comentario.</p>",
    },
    {
        "title": "Carga de trabajo",
        "slug": "carga-de-trabajo",
        "introduction": "Distribución de revisiones entre coordinación.",
        "topic": "review",
        "audiences": [FAQ_AUDIENCE_COORDINATOR],
        "contextual_keys": "CoordinatorWorkload",
        "body": "<p>La vista de carga muestra cuántas solicitudes tiene cada persona responsable.</p><p>Úsala para reasignar o priorizar picos de convocatoria. No cambia estados; solo ayuda a planear el trabajo.</p>",
    },
    {
        "title": "Conjuntos de reglas de elegibilidad",
        "slug": "reglas-de-elegibilidad",
        "introduction": "Quién puede enviar una solicitud.",
        "topic": "review",
        "audiences": [FAQ_AUDIENCE_COORDINATOR],
        "contextual_keys": "EligibilityRulesets",
        "body": "<p>Un conjunto de reglas se asocia a programas o convocatorias. Evalúa promedio, créditos, idioma u otros campos del perfil.</p><p>Publica una versión antes de usarla en producción. Probar con un estudiante de ejemplo evita bloqueos masivos el día del cierre.</p>",
    },
    {
        "title": "Reglas de puntuación de becas",
        "slug": "reglas-puntuacion-becas",
        "introduction": "Cómo se calcula el puntaje de apoyo.",
        "topic": "review",
        "audiences": [FAQ_AUDIENCE_COORDINATOR],
        "contextual_keys": "ScholarshipScoringRulesets",
        "body": "<p>Los conjuntos de puntuación ponderan factores (académicos, socioeconómicos u otros) definidos por tu institución.</p><p>Ajusta pesos con cuidado: las solicitudes ya enviadas pueden conservar una instantánea. Coordina con administración antes de cambiar reglas a mitad de convocatoria.</p>",
    },
    {
        "title": "Nominaciones",
        "slug": "nominaciones",
        "introduction": "Enviar postulantes a la institución anfitriona.",
        "topic": "review",
        "audiences": [FAQ_AUDIENCE_COORDINATOR],
        "contextual_keys": "Nominations",
        "body": "<p>Las nominaciones agrupan estudiantes aceptados internamente para notificar al socio.</p><p>Revisa cupos del convenio y documentos pendientes antes de nominar. El portal del socio refleja el estado que aquí confirmes.</p>",
    },
    {
        "title": "Convenios y documentos de convenio",
        "slug": "convenios-y-documentos",
        "introduction": "Acuerdos de intercambio y archivos asociados.",
        "topic": "review",
        "audiences": [FAQ_AUDIENCE_COORDINATOR],
        "contextual_keys": "StaffExchangeAgreements,StaffAgreementDocuments",
        "body": "<p>Cada convenio liga programas, cupos, vigencia y destinos anfitriones.</p><p>Sube el PDF firmado y los anexos en documentos de convenio. Un convenio vencido puede impedir nuevas solicitudes aunque el programa siga visible.</p>",
    },
    {
        "title": "Enrutamiento de notificaciones",
        "slug": "enrutamiento-notificaciones",
        "introduction": "Quién recibe cada aviso del flujo.",
        "topic": "review",
        "audiences": [FAQ_AUDIENCE_COORDINATOR],
        "contextual_keys": "NotificationRouting",
        "body": "<p>El mapa de enrutamiento indica qué roles reciben cada tipo de aviso (envío, rechazo de documento, recordatorio de plazo).</p><p>Los estudiantes siguen controlando preferencias personales. Aquí solo se define el destino institucional por categoría.</p>",
    },
    {
        "title": "Pronósticos de demanda",
        "slug": "pronosticos-de-demanda",
        "introduction": "Analítica de volumen de solicitudes.",
        "topic": "review",
        "audiences": [FAQ_AUDIENCE_COORDINATOR],
        "contextual_keys": "AnalyticsForecasts",
        "body": "<p>Los pronósticos estiman carga futura a partir del historial de solicitudes.</p><p>Úsalos para cupos y personal, no como decisión individual sobre un expediente. Los filtros de programa y periodo cambian el gráfico.</p>",
    },
    {
        "title": "Portal de socio: resumen",
        "slug": "portal-socio-resumen",
        "introduction": "Qué ve una institución socia al entrar.",
        "topic": "partner",
        "audiences": [FAQ_AUDIENCE_PARTNER],
        "contextual_keys": "PartnerPortal",
        "body": "<p>El portal muestra convenios ligados a tu cuenta, postulantes nominados y documentos que tu institución debe cargar.</p><p>No incluye el formulario completo de cada estudiante ni herramientas de administración del sitio público.</p>",
    },
    {
        "title": "Convenios y documentos requeridos (socio)",
        "slug": "socio-convenios-documentos",
        "introduction": "Revisar acuerdos y archivos pendientes.",
        "topic": "partner",
        "audiences": [FAQ_AUDIENCE_PARTNER],
        "contextual_keys": "PartnerPortal",
        "body": "<p>Abre cada convenio para ver vigencia, cupos y la lista de documentos institucionales.</p><p>Los archivos del estudiante los gestiona coordinación de origen; tú completas lo que el convenio marca como responsabilidad del socio.</p>",
    },
    {
        "title": "Checklist y estado de postulantes",
        "slug": "socio-checklist-postulantes",
        "introduction": "Seguimiento de nominados hacia tu campus.",
        "topic": "partner",
        "audiences": [FAQ_AUDIENCE_PARTNER],
        "contextual_keys": "PartnerPortal",
        "body": "<p>La lista de postulantes resume estado de nominación y checklist de requisitos del anfitrión.</p><p>Un estado interno de la universidad de origen puede no coincidir con lo que ves aquí. Contacta a tu contraparte de movilidad si falta un nombre esperado.</p>",
    },
    {
        "title": "Subir documentos del socio",
        "slug": "socio-subir-documentos",
        "introduction": "Carga de archivos institucionales.",
        "topic": "partner",
        "audiences": [FAQ_AUDIENCE_PARTNER],
        "contextual_keys": "PartnerPortal",
        "body": "<p>Desde el portal puedes adjuntar cartas, confirmaciones de plaza u otros tipos definidos en el convenio.</p><p>Respeta el tipo de documento pedido. Si el archivo se rechaza, lee el comentario y vuelve a cargar una versión corregida.</p>",
    },
    {
        "title": "Programas y destinos anfitriones",
        "slug": "admin-programas-destinos",
        "introduction": "Alta de programas y árbol de destinos.",
        "topic": "admin",
        "audiences": [FAQ_AUDIENCE_ADMIN],
        "contextual_keys": "AdminPrograms,AdminProgramDestinations",
        "body": "<p>En administración SPA creas programas, periodos y destinos anfitriones (campus, facultad o ciudad según tu modelo).</p><p>Publicar un programa no sustituye el convenio vigente ni las reglas de elegibilidad. Revisa ambos antes de abrir convocatoria.</p>",
    },
    {
        "title": "Catálogos",
        "slug": "admin-catalogos",
        "introduction": "Valores maestros usados en formularios y perfiles.",
        "topic": "admin",
        "audiences": [FAQ_AUDIENCE_ADMIN],
        "contextual_keys": "AdminCatalogs",
        "body": "<p>Los catálogos (países, idiomas, facultades, etc.) alimentan desplegables del perfil y de las solicitudes.</p><p>Evita borrar un valor ya usado en expedientes; desactívalo si el producto lo permite. Los cambios impactan formularios dinámicos.</p>",
    },
    {
        "title": "Usuarios, roles y sesiones",
        "slug": "admin-usuarios-roles-sesiones",
        "introduction": "Cuentas, roles SEIM y control de sesiones.",
        "topic": "admin",
        "audiences": [FAQ_AUDIENCE_ADMIN],
        "contextual_keys": "AdminUsers,AdminSessions",
        "body": "<p>Asigna roles <em>student</em>, <em>responsible</em> (coordinación), <em>partner</em> o <em>admin</em>. El rol principal define el panel y la ayuda visible.</p><p>Puedes revocar sesiones. No uses el CMS de Wagtail para crear usuarios de la SPA.</p>",
    },
    {
        "title": "Flujos de trabajo frente al constructor de formularios",
        "slug": "admin-flujos-vs-formularios",
        "introduction": "Estados de solicitud vs campos del expediente.",
        "topic": "admin",
        "audiences": [FAQ_AUDIENCE_ADMIN],
        "contextual_keys": "AdminWorkflows,AdminWorkflowEditor,AdminDynforms,AdminForms",
        "body": "<p>El flujo define transiciones de estado (borrador, enviado, en revisión). El constructor de formularios define pasos y campos que llena el estudiante.</p><p>Cambia el flujo cuando el proceso institucional cambie. Cambia el formulario cuando cambien los datos a capturar. No mezcles ambos en un solo editor.</p>",
    },
    {
        "title": "Tipos de documento",
        "slug": "admin-tipos-de-documento",
        "introduction": "Requisitos de archivo y textos de ayuda al estudiante.",
        "topic": "admin",
        "audiences": [FAQ_AUDIENCE_ADMIN],
        "contextual_keys": "AdminDocuments,AdminDocumentTypeEdit",
        "body": "<p>Cada tipo define extensiones, obligatoriedad y textos de FAQ que el estudiante ve al subir archivos.</p><p>Esos textos no aparecen en el sitio público de preguntas frecuentes salvo que copies el contenido a una página FAQ con superficie pública.</p>",
    },
    {
        "title": "Importación y exportación de datos",
        "slug": "admin-importacion-exportacion",
        "introduction": "Operaciones masivas desde data management.",
        "topic": "admin",
        "audiences": [FAQ_AUDIENCE_ADMIN],
        "contextual_keys": "AdminDataManagement",
        "body": "<p>La consola de datos permite importar y exportar catálogos y registros operativos según los recursos habilitados.</p><p>Ejecuta primero en un entorno de prueba. Un import erróneo puede duplicar programas o usuarios. Revisa los registros de ejecución al terminar.</p>",
    },
    {
        "title": "Escalas de calificación",
        "slug": "admin-escalas-calificacion",
        "introduction": "Conversión entre sistemas de notas.",
        "topic": "admin",
        "audiences": [FAQ_AUDIENCE_ADMIN],
        "contextual_keys": "AdminGrades",
        "body": "<p>Las escalas permiten traducir calificaciones extranjeras al sistema local.</p><p>Edita mapeos con personal académico. Un cambio no recalcula automáticamente historiales ya guardados en solicitudes cerradas.</p>",
    },
    {
        "title": "Cuándo usar Wagtail y cuándo el admin SPA",
        "slug": "wagtail-vs-admin-spa",
        "introduction": "CMS público frente a operación de movilidad.",
        "topic": "admin",
        "audiences": [FAQ_AUDIENCE_ADMIN],
        "contextual_keys": "AdminPrograms,AdminDocuments",
        "body": "<p>Usa <strong>/cms/</strong> (Wagtail) para el sitio público, noticias y estas páginas de ayuda. Usa <strong>/seim/admin/</strong> para programas operativos, usuarios, flujos, formularios dinámicos y tipos de documento.</p><p>No publiques copias de coordinación en el FAQ público: deja la superficie solo en SPA y elige audiencias de coordinador o admin.</p>",
    },
]

PUBLIC_FAQ_RETAG = {
    "requisitos-aplicar": {
        "topic": "applications",
        "contextual_keys": "ApplicationNew,ApplicationEdit,ApplicationForm,Applications",
    },
    "costo-intercambio": {
        "topic": "applications",
        "contextual_keys": "Applications,ProgramCompare",
    },
    "revalidacion-creditos": {
        "topic": "applications",
        "contextual_keys": "ApplicationDetail,Applications",
    },
    "trabajar-intercambio": {
        "topic": "getting_started",
        "contextual_keys": "ProgramCompare,Dashboard",
    },
    "emergencia-extranjero": {
        "topic": "getting_started",
        "contextual_keys": "Dashboard,Profile",
    },
}


class Command(BaseCommand):
    help = (
        "Create the SPA help FAQ index and per-role articles; "
        "retag existing public FAQs as public+spa+student."
    )

    def handle(self, *args, **options):
        site = Site.objects.filter(is_default_site=True).first()
        if site is None:
            raise CommandError("No default Wagtail site. Run initialize_wagtail first.")
        parent = site.root_page.specific

        spa_index = self._get_or_create_spa_index(parent)
        created = 0
        updated = 0
        for article in SPA_HELP_ARTICLES:
            _, was_created = self._upsert_article(spa_index, article)
            if was_created:
                created += 1
            else:
                updated += 1

        retagged = self._retag_public_faqs()
        self.stdout.write(
            self.style.SUCCESS(
                f"SPA help index '{SPA_HELP_INDEX_SLUG}': "
                f"{created} created, {updated} updated, {retagged} public FAQs retagged."
            )
        )

    def _get_or_create_spa_index(self, parent):
        try:
            index = FAQIndexPage.objects.get(slug=SPA_HELP_INDEX_SLUG)
            index.index_kind = FAQ_INDEX_KIND_SPA_HELP
            index.show_in_menus = False
            if not index.introduction:
                index.introduction = (
                    "Artículos de ayuda de la aplicación. No aparecen en el sitio público."
                )
            index.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("  [ok] Updated SPA help index"))
            return index
        except FAQIndexPage.DoesNotExist:
            index = FAQIndexPage(
                title="Ayuda de la aplicación",
                slug=SPA_HELP_INDEX_SLUG,
                show_in_menus=False,
                index_kind=FAQ_INDEX_KIND_SPA_HELP,
                introduction=(
                    "Artículos de ayuda de la aplicación. No aparecen en el sitio público."
                ),
            )
            parent.add_child(instance=index)
            index.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("  [ok] Created SPA help index"))
            return index

    def _upsert_article(self, parent, article):
        payload = {
            "title": article["title"],
            "introduction": article["introduction"],
            "body": _paragraph_body(article["body"]),
            "audiences": article["audiences"],
            "surfaces": [S],
            "topic": article["topic"],
            "contextual_keys": article["contextual_keys"],
        }
        try:
            page = FAQPage.objects.child_of(parent).get(slug=article["slug"])
            for field, value in payload.items():
                setattr(page, field, value)
            page.save_revision().publish()
            self.stdout.write(
                self.style.SUCCESS(f"  [ok] Updated help: {article['title']}")
            )
            return page, False
        except FAQPage.DoesNotExist:
            page = FAQPage(slug=article["slug"], **payload)
            parent.add_child(instance=page)
            page.save_revision().publish()
            self.stdout.write(
                self.style.SUCCESS(f"  [ok] Created help: {article['title']}")
            )
            return page, True

    def _retag_public_faqs(self):
        count = 0
        for slug in PUBLIC_FAQ_SLUGS:
            meta = PUBLIC_FAQ_RETAG[slug]
            page = FAQPage.objects.filter(slug=slug).first()
            if page is None:
                self.stdout.write(
                    self.style.WARNING(f"  [warn] Public FAQ missing: {slug}")
                )
                continue
            page.audiences = [FAQ_AUDIENCE_STUDENT]
            page.surfaces = [P, S]
            page.topic = meta["topic"]
            page.contextual_keys = meta["contextual_keys"]
            page.save_revision().publish()
            count += 1
            self.stdout.write(
                self.style.SUCCESS(f"  [ok] Retagged public FAQ: {slug}")
            )
        return count
