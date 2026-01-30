"""
Management command to create "How to Apply" page explaining the application process.
"""

from django.core.management.base import BaseCommand
from cms.models import HomePage, StandardPage


class Command(BaseCommand):
    help = 'Create "How to Apply" page with registration instructions'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating "How to Apply" page...'))
        
        try:
            home = HomePage.objects.get(slug='home')
        except HomePage.DoesNotExist:
            self.stdout.write(self.style.ERROR('  ✗ HomePage not found'))
            return
        
        # Check if page already exists
        try:
            apply_page = StandardPage.objects.get(slug='como-aplicar')
            self.stdout.write(self.style.WARNING('  ⚠ Page already exists, updating...'))
            # Delete and recreate
            apply_page.delete()
        except StandardPage.DoesNotExist:
            pass
        
        # Create the "How to Apply" page
        apply_page = StandardPage(
            title='¿Cómo Aplicar al Programa de Intercambio?',
            slug='como-aplicar',
            show_in_menus=True,
            introduction='Guía completa para aplicar a un programa de intercambio académico en la UAdeC'
        )
        
        # Content for the page
        content = [
            {
                'type': 'hero',
                'value': {
                    'title': '¿Cómo Aplicar al Intercambio?',
                    'subtitle': 'Sigue estos pasos para iniciar tu aventura internacional',
                    'background_color': 'primary'
                }
            },
            {
                'type': 'paragraph',
                'value': '<p class="lead">Aplicar a un programa de intercambio es un proceso emocionante. Aquí te explicamos paso a paso cómo hacerlo.</p>'
            },
            {
                'type': 'heading',
                'value': {
                    'heading_text': 'Paso 1: Verifica que Cumples los Requisitos',
                    'size': '2'
                }
            },
            {
                'type': 'paragraph',
                'value': '''
                <p>Antes de aplicar, asegúrate de cumplir con los requisitos generales:</p>
                <ul>
                    <li>Ser estudiante activo de la UAdeC</li>
                    <li>Tener un promedio mínimo de 8.0 (varía según el programa)</li>
                    <li>Haber cursado al menos el 40-50% de tu carrera</li>
                    <li>Contar con el aval de tu coordinador de carrera</li>
                    <li>Presentar certificación de idioma del país destino</li>
                    <li>No tener adeudos académicos o administrativos</li>
                </ul>
                <p><strong>Nota:</strong> Los requisitos específicos pueden variar según la universidad destino. 
                Consulta la página de cada <a href="/programas/">programa</a> para más detalles.</p>
                '''
            },
            {
                'type': 'heading',
                'value': {
                    'heading_text': 'Paso 2: Reúne tu Documentación',
                    'size': '2'
                }
            },
            {
                'type': 'paragraph',
                'value': '''
                <p>Prepara los siguientes documentos:</p>
                <ul>
                    <li>Historial académico actualizado</li>
                    <li>Carta de motivos (1-2 páginas explicando por qué quieres participar)</li>
                    <li>Dos cartas de recomendación académicas</li>
                    <li>Certificado de idioma (TOEFL, DELE, etc.)</li>
                    <li>Copia de pasaporte vigente</li>
                    <li>Fotografías tamaño pasaporte</li>
                    <li>Carta de aval del coordinador de carrera</li>
                </ul>
                <p class="alert alert-info">
                    <strong>💡 Consejo:</strong> Comienza a preparar tus documentos con anticipación. 
                    Las cartas de recomendación pueden tomar tiempo y los certificados de idioma tienen 
                    fechas específicas de examen.
                </p>
                '''
            },
            {
                'type': 'heading',
                'value': {
                    'heading_text': 'Paso 3: Crea tu Cuenta en el Sistema',
                    'size': '2'
                }
            },
            {
                'type': 'paragraph',
                'value': '''
                <p>Para aplicar formalmente, necesitas crear una cuenta en nuestro sistema de gestión de intercambios:</p>
                <ol>
                    <li>Haz clic en el botón "Crear Cuenta" a continuación</li>
                    <li>Completa el formulario de registro con tus datos personales</li>
                    <li>Verifica tu correo electrónico (recibirás un enlace de confirmación)</li>
                    <li>Inicia sesión en el sistema</li>
                    <li>Completa tu perfil con tu información académica</li>
                </ol>
                '''
            },
            {
                'type': 'call_to_action',
                'value': {
                    'title': 'Crea Tu Cuenta de Aplicación',
                    'text': 'Regístrate en nuestro sistema para iniciar tu solicitud de intercambio',
                    'button_text': 'Crear Cuenta Ahora',
                    'button_link': 'http://localhost:8000/seim/register/',
                    'style': 'success'
                }
            },
            {
                'type': 'heading',
                'value': {
                    'heading_text': 'Paso 4: Completa tu Solicitud en Línea',
                    'size': '2'
                }
            },
            {
                'type': 'paragraph',
                'value': '''
                <p>Una vez que tengas tu cuenta:</p>
                <ol>
                    <li><strong>Selecciona tu programa:</strong> Elige hasta 3 opciones en orden de preferencia</li>
                    <li><strong>Sube tus documentos:</strong> Digitaliza y carga todos los documentos requeridos</li>
                    <li><strong>Completa la información:</strong> Llena todos los campos del formulario de aplicación</li>
                    <li><strong>Revisa cuidadosamente:</strong> Verifica que toda la información sea correcta</li>
                    <li><strong>Envía tu solicitud:</strong> Una vez enviada, recibirás un número de folio</li>
                </ol>
                <p class="alert alert-warning">
                    <strong>⚠️ Importante:</strong> Una vez enviada la solicitud, no podrás modificarla. 
                    Asegúrate de revisar toda la información antes de enviar.
                </p>
                '''
            },
            {
                'type': 'heading',
                'value': {
                    'heading_text': 'Paso 5: Proceso de Evaluación',
                    'size': '2'
                }
            },
            {
                'type': 'paragraph',
                'value': '''
                <p>Después de enviar tu solicitud:</p>
                <ul>
                    <li><strong>Revisión inicial:</strong> Verificamos que cumplas con los requisitos básicos</li>
                    <li><strong>Evaluación académica:</strong> El comité revisa tu expediente académico</li>
                    <li><strong>Entrevista (si aplica):</strong> Algunos programas requieren entrevista personal</li>
                    <li><strong>Decisión final:</strong> El comité toma la decisión de aceptación</li>
                </ul>
                <p>Recibirás notificación por correo electrónico del resultado de tu solicitud. 
                También podrás consultar el estatus en tu cuenta del sistema.</p>
                '''
            },
            {
                'type': 'heading',
                'value': {
                    'heading_text': 'Paso 6: Si Eres Aceptado',
                    'size': '2'
                }
            },
            {
                'type': 'paragraph',
                'value': '''
                <p>¡Felicidades! Si eres aceptado, deberás:</p>
                <ol>
                    <li>Confirmar tu aceptación en el sistema</li>
                    <li>Asistir a la sesión de orientación obligatoria</li>
                    <li>Iniciar trámites de visa (si aplica)</li>
                    <li>Contratar seguro médico internacional</li>
                    <li>Coordinar tu carga académica con tu coordinador</li>
                    <li>Realizar trámites migratorios necesarios</li>
                    <li>Preparar tu viaje</li>
                </ol>
                <p>Nuestro equipo te acompañará en cada uno de estos pasos.</p>
                '''
            },
            {
                'type': 'heading',
                'value': {
                    'heading_text': 'Fechas Importantes',
                    'size': '2'
                }
            },
            {
                'type': 'paragraph',
                'value': '''
                <div class="alert alert-info">
                    <h5>Convocatoria Primavera 2026</h5>
                    <ul>
                        <li><strong>Apertura:</strong> 20 de noviembre de 2025</li>
                        <li><strong>Cierre de aplicaciones:</strong> 15 de enero de 2026</li>
                        <li><strong>Publicación de resultados:</strong> 1 de febrero de 2026</li>
                        <li><strong>Sesión de orientación:</strong> 15 de febrero de 2026</li>
                        <li><strong>Inicio del intercambio:</strong> Marzo de 2026</li>
                    </ul>
                </div>
                <p class="lead text-center mt-4">
                    <a href="/blog/" class="btn btn-primary btn-lg">Ver Convocatoria Actual</a>
                </p>
                '''
            },
            {
                'type': 'heading',
                'value': {
                    'heading_text': '¿Tienes Preguntas?',
                    'size': '2'
                }
            },
            {
                'type': 'paragraph',
                'value': '''
                <p>Si tienes dudas sobre el proceso de aplicación, consulta nuestras 
                <a href="/preguntas-frecuentes/">Preguntas Frecuentes</a> o 
                <a href="/contacto/">contáctanos directamente</a>.</p>
                <p>Nuestro equipo está disponible para ayudarte en cada paso del proceso.</p>
                '''
            },
            {
                'type': 'call_to_action',
                'value': {
                    'title': '¿Listo para Comenzar?',
                    'text': 'Crea tu cuenta ahora y da el primer paso hacia tu experiencia internacional',
                    'button_text': 'Crear Mi Cuenta',
                    'button_link': 'http://localhost:8000/seim/register/',
                    'style': 'primary'
                }
            }
        ]
        
        apply_page.body = content
        home.add_child(instance=apply_page)
        apply_page.save_revision().publish()
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n✅ "How to Apply" page created successfully!'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                '   URL: http://localhost:8000/como-aplicar/'
            )
        )

