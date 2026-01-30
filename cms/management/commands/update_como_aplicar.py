"""
Update the Cómo Aplicar page with SEIM application instructions.

Usage:
    python manage.py update_como_aplicar
"""

from django.core.management.base import BaseCommand
from cms.models import StandardPage
from wagtail.blocks import StreamValue
from cms.blocks import BaseStreamBlock


class Command(BaseCommand):
    help = 'Update Cómo Aplicar page with SEIM application instructions'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Updating Cómo Aplicar page...')
        
        try:
            page = StandardPage.objects.get(slug='como-aplicar')
        except StandardPage.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Page not found'))
            return
        
        # Update introduction
        page.introduction = "Inicia tu experiencia de intercambio académico internacional creando tu cuenta en el Sistema SEIM y completando tu solicitud en línea."
        
        # Build content with StreamField
        content_data = [
            {
                'type': 'rich_text',
                'value': {
                    'content': '<h2>Proceso de Aplicación</h2><p>Para aplicar a un programa de intercambio académico de la UAdeC, sigue estos pasos:</p>'
                }
            },
            {
                'type': 'rich_text',
                'value': {
                    'content': '<h3>1. Crea tu Cuenta en SEIM</h3><p>El primer paso es registrarte en nuestro Sistema de Intercambio Estudiantil y Movilidad (SEIM). Necesitarás tu correo institucional de la UAdeC para crear tu cuenta.</p>'
                }
            },
            {
                'type': 'call_to_action',
                'value': {
                    'title': '¿Aún no tienes cuenta?',
                    'text': 'Regístrate ahora en SEIM para comenzar tu solicitud de intercambio.',
                    'button_text': 'Crear Cuenta',
                    'button_link': '/accounts/register/',
                    'style': 'primary'
                }
            },
            {
                'type': 'rich_text',
                'value': {
                    'content': '<h3>2. Completa tu Perfil</h3><p>Una vez que hayas verificado tu correo y activado tu cuenta, inicia sesión en SEIM y completa tu perfil estudiantil con tu información académica.</p>'
                }
            },
            {
                'type': 'rich_text',
                'value': {
                    'content': '<h3>3. Explora Programas Disponibles</h3><p>Revisa los programas de intercambio disponibles en el sistema. Cada programa incluye información sobre:</p><ul><li>Universidad destino y país</li><li>Requisitos académicos (promedio mínimo, nivel de idioma)</li><li>Duración del intercambio</li><li>Fechas de aplicación</li><li>Documentos requeridos</li></ul>'
                }
            },
            {
                'type': 'rich_text',
                'value': {
                    'content': '<h3>4. Inicia tu Solicitud</h3><p>Selecciona el programa al que deseas aplicar y completa el formulario de solicitud en línea. El sistema te guiará paso a paso.</p>'
                }
            },
            {
                'type': 'rich_text',
                'value': {
                    'content': '<h3>5. Sube tus Documentos</h3><p>Adjunta todos los documentos requeridos en formato PDF:</p><ul><li>Carta de motivación</li><li>Kardex actualizado</li><li>Carta de recomendación</li><li>Comprobante de idioma (si aplica)</li><li>Identificación oficial</li></ul>'
                }
            },
            {
                'type': 'rich_text',
                'value': {
                    'content': '<h3>6. Envía tu Solicitud</h3><p>Revisa cuidadosamente toda tu información antes de enviar. Una vez enviada, tu solicitud será revisada por el equipo de la Dirección de Intercambio Académico.</p>'
                }
            },
            {
                'type': 'call_to_action',
                'value': {
                    'title': '¿Ya tienes cuenta?',
                    'text': 'Inicia sesión en SEIM para continuar con tu solicitud.',
                    'button_text': 'Iniciar Sesión',
                    'button_link': '/accounts/login/',
                    'style': 'secondary'
                }
            },
            {
                'type': 'rich_text',
                'value': {
                    'content': '<h2>Seguimiento de tu Solicitud</h2><p>Una vez enviada tu solicitud, podrás dar seguimiento a su estatus en tiempo real desde tu panel de SEIM. Recibirás notificaciones por correo electrónico en cada etapa del proceso:</p><ul><li><strong>Recibida:</strong> Tu solicitud ha sido recibida</li><li><strong>En Revisión:</strong> El equipo está evaluando tu solicitud</li><li><strong>Aprobada:</strong> ¡Felicidades! Has sido seleccionado</li><li><strong>Documentación Adicional:</strong> Se requieren más documentos</li></ul>'
                }
            },
            {
                'type': 'rich_text',
                'value': {
                    'content': '<h2>¿Necesitas Ayuda?</h2><p>Si tienes dudas sobre el proceso de aplicación o problemas técnicos con el sistema SEIM, no dudes en contactarnos.</p><p><strong>Dirección de Intercambio Académico</strong><br>Email: <a href="mailto:intercambio@uadec.edu.mx">intercambio@uadec.edu.mx</a><br>Teléfono: +52 (844) 416-1234 ext. 1500</p>'
                }
            }
        ]
        
        # Update the body StreamField
        page.body = StreamValue(
            BaseStreamBlock(),
            content_data,
            is_lazy=True
        )
        
        page.save()
        
        # Publish the changes
        revision = page.save_revision()
        revision.publish()
        
        self.stdout.write(self.style.SUCCESS(f'✅ Updated: {page.title}'))
        self.stdout.write(f'   URL: http://localhost:8000{page.url}')
        self.stdout.write('')
        self.stdout.write('The page now includes:')
        self.stdout.write('  ✅ Instructions to create a SEIM account')
        self.stdout.write('  ✅ Link to registration page (/accounts/register/)')
        self.stdout.write('  ✅ Link to login page (/accounts/login/)')
        self.stdout.write('  ✅ Step-by-step application process')
        self.stdout.write('  ✅ Document requirements')
        self.stdout.write('  ✅ Application status tracking info')

