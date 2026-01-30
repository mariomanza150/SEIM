"""Management command to enhance the homepage with content blocks."""

from django.core.management.base import BaseCommand
from cms.models import HomePage, ProgramIndexPage


class Command(BaseCommand):
    help = 'Enhance homepage with content blocks for students and teachers'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Enhancing UAdeC homepage...'))
        
        try:
            home = HomePage.objects.get(slug='home')
        except HomePage.DoesNotExist:
            self.stdout.write(self.style.ERROR('  ✗ HomePage not found'))
            return
        
        # Enhanced homepage content with StreamField blocks
        enhanced_content = [
            # Hero/Welcome block
            {
                'type': 'hero',
                'value': {
                    'title': 'Vive una Experiencia Internacional',
                    'subtitle': 'Amplía tus horizontes académicos y culturales con nuestros programas de intercambio',
                    'background_color': 'primary',
                    'button_text': 'Ver Programas',
                    'button_link': 'http://localhost:8000/programas/'
                }
            },
            # Feature cards for students and teachers
            {
                'type': 'card_grid',
                'value': {
                    'heading': '¿Por qué elegir un intercambio académico?',
                    'subheading': 'Beneficios para tu desarrollo académico y profesional',
                    'columns': '3',
                    'cards': [
                        {
                            'icon': 'bi-globe2',
                            'title': 'Experiencia Internacional',
                            'text': 'Estudia en universidades prestigiosas de Europa y América, ampliando tu perspectiva global y enriqueciendo tu perfil profesional.',
                            'link': '/sobre-nosotros/',
                            'link_text': 'Conoce más'
                        },
                        {
                            'icon': 'bi-mortarboard',
                            'title': 'Créditos Revalidables',
                            'text': 'Todas las materias cursadas en el extranjero son revalidadas automáticamente. Tu progreso académico continúa sin interrupciones.',
                            'link': '/preguntas-frecuentes/',
                            'link_text': 'Ver FAQs'
                        },
                        {
                            'icon': 'bi-people',
                            'title': 'Apoyo Integral',
                            'text': 'Desde la aplicación hasta tu regreso, te acompañamos en cada paso. Orientación académica, trámites y soporte constante.',
                            'link': '/contacto/',
                            'link_text': 'Contacta'
                        },
                        {
                            'icon': 'bi-currency-dollar',
                            'title': 'Becas Disponibles',
                            'text': 'Accede a becas y apoyos económicos para estudiantes destacados. No dejes que el costo sea una barrera.',
                            'link': '/proceso-aplicacion/',
                            'link_text': 'Aplicar'
                        },
                        {
                            'icon': 'bi-translate',
                            'title': 'Desarrollo de Idiomas',
                            'text': 'Perfecciona inglés, italiano, francés u otros idiomas mientras estudias. Inmersión total en el idioma y cultura.',
                            'link': '/programas/',
                            'link_text': 'Ver destinos'
                        },
                        {
                            'icon': 'bi-briefcase',
                            'title': 'Ventaja Competitiva',
                            'text': 'Diferénciate en el mercado laboral. Los empleadores valoran altamente la experiencia internacional.',
                            'link': '/blog/',
                            'link_text': 'Experiencias'
                        }
                    ]
                }
            },
            # Call to action for current call
            {
                'type': 'call_to_action',
                'value': {
                    'title': '📢 ¡Convocatoria Abierta para Primavera 2026!',
                    'text': 'Las aplicaciones están abiertas hasta el 15 de enero de 2026. No pierdas esta oportunidad única de estudiar en el extranjero.',
                    'button_text': 'Ver Convocatoria',
                    'button_link': 'http://localhost:8000/blog/',
                    'style': 'success'
                }
            },
            # Process steps for students
            {
                'type': 'process_steps',
                'value': {
                    'heading': '¿Cómo aplicar?',
                    'subheading': 'Sigue estos simples pasos para iniciar tu aventura internacional',
                    'steps': [
                        {
                            'number': '1',
                            'title': 'Infórmate',
                            'description': 'Consulta los programas disponibles, requisitos y destinos. Asiste a nuestras sesiones informativas.',
                            'icon': 'bi-info-circle'
                        },
                        {
                            'number': '2',
                            'title': 'Prepara Documentos',
                            'description': 'Reúne tu historial académico, cartas de recomendación, certificados de idioma y carta de motivos.',
                            'icon': 'bi-file-earmark-text'
                        },
                        {
                            'number': '3',
                            'title': 'Aplica en Línea',
                            'description': 'Completa el formulario de aplicación en nuestro sistema. Asegúrate de incluir toda la información.',
                            'icon': 'bi-laptop'
                        },
                        {
                            'number': '4',
                            'title': 'Evaluación',
                            'description': 'El comité evaluará tu solicitud. Recibirás notificación de resultados en las fechas establecidas.',
                            'icon': 'bi-clipboard-check'
                        },
                        {
                            'number': '5',
                            'title': 'Preparativos',
                            'description': 'Una vez aceptado, realiza trámites de visa, seguro médico y documentación migratoria.',
                            'icon': 'bi-airplane'
                        },
                        {
                            'number': '6',
                            'title': '¡Viaja!',
                            'description': 'Inicia tu experiencia internacional. Te acompañaremos durante toda tu estancia.',
                            'icon': 'bi-star'
                        }
                    ]
                }
            },
            # Testimonial
            {
                'type': 'testimonial',
                'value': {
                    'quote': 'Mi experiencia en la Universidad de Salamanca cambió mi vida. No solo mejoré mi nivel académico, sino que hice amigos de todo el mundo y descubrí una nueva perspectiva de mi carrera. Fue la mejor decisión que pude tomar.',
                    'author': 'María Rodríguez',
                    'author_title': 'Estudiante de Relaciones Internacionales - Intercambio en España 2024'
                }
            },
            # FAQ block
            {
                'type': 'faq',
                'value': {
                    'heading': 'Preguntas Frecuentes',
                    'items': [
                        {
                            'question': '¿Cuál es el promedio mínimo requerido?',
                            'answer': '<p>El promedio mínimo general es de 8.0, aunque algunos programas pueden requerir 8.5 o más. Revisa los requisitos específicos de cada destino.</p>'
                        },
                        {
                            'question': '¿Necesito saber el idioma del país?',
                            'answer': '<p>Sí, debes demostrar un nivel intermedio o avanzado del idioma. Para inglés: TOEFL 79+ o IELTS 6.5+. Para español: DELE B2. Para otros idiomas, consulta los requisitos específicos.</p>'
                        },
                        {
                            'question': '¿Cuánto tiempo dura un intercambio?',
                            'answer': '<p>La mayoría de nuestros programas son de un semestre (4-6 meses). Algunos programas también ofrecen estancias de verano (2-3 meses).</p>'
                        },
                        {
                            'question': '¿Puedo elegir mis materias en el extranjero?',
                            'answer': '<p>Sí, pero deben ser aprobadas previamente por tu coordinador de carrera para asegurar su equivalencia y revalidación.</p>'
                        }
                    ]
                }
            },
            # Final CTA
            {
                'type': 'call_to_action',
                'value': {
                    'title': '¿Listo para tu aventura internacional?',
                    'text': 'Aprende cómo crear tu cuenta y enviar tu solicitud de intercambio. Te guiamos paso a paso en el proceso.',
                    'button_text': '¿Cómo Aplicar?',
                    'button_link': 'http://localhost:8000/como-aplicar/',
                    'style': 'primary'
                }
            }
        ]
        
        # Update homepage with enhanced content
        home.body = enhanced_content
        home.save_revision().publish()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Homepage enhanced successfully!'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'   Added {len(enhanced_content)} content blocks'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'   Visit http://localhost:8000/ to see the changes'
            )
        )

