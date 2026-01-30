"""
Management command to populate Wagtail CMS with Universidad Autónoma de Coahuila content.

This creates realistic content for UAdeC's international exchange department including:
- Updated homepage
- About page
- Program pages
- Blog posts
- FAQs
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from wagtail.models import Page, Site
from cms.models import (
    HomePage, BlogIndexPage, BlogPostPage, BlogCategory,
    ProgramIndexPage, ProgramPage, FAQIndexPage, FAQPage,
    StandardPage
)


class Command(BaseCommand):
    help = 'Populate CMS with Universidad Autónoma de Coahuila content'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Populating UAdeC Exchange Department content...'))
        
        # Get or create homepage
        try:
            home_page = HomePage.objects.get(slug='home')
        except HomePage.DoesNotExist:
            self.stdout.write(self.style.ERROR('  ✗ HomePage not found. Run initialize_wagtail first.'))
            return
        
        # Update HomePage with UAdeC branding
        home_page.title = 'UAdeC - Dirección de Intercambio Académico'
        home_page.hero_title = 'Bienvenido a la Dirección de Intercambio Académico'
        home_page.hero_subtitle = 'Universidad Autónoma de Coahuila - Transformando vidas a través de experiencias internacionales'
        home_page.hero_cta_text = 'Explorar Programas'
        home_page.save_revision().publish()
        self.stdout.write(self.style.SUCCESS('  ✓ Updated HomePage with UAdeC branding'))
        
        # Create or update About page
        about_page = self.create_about_page(home_page)
        
        # Create or update Blog Index and posts
        blog_index = self.create_blog_content(home_page)
        
        # Create or update Program Index and programs
        program_index = self.create_program_content(home_page)
        
        # Create or update FAQ Index and FAQs
        faq_index = self.create_faq_content(home_page)
        
        # Create additional pages
        self.create_additional_pages(home_page)
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n✅ UAdeC content population complete!'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                'Visit http://localhost:8000/ to see the new content'
            )
        )

    def create_about_page(self, parent):
        """Create About page for UAdeC exchange department."""
        about_slug = 'sobre-nosotros'
        
        try:
            about_page = StandardPage.objects.get(slug=about_slug)
            self.stdout.write(self.style.WARNING('  ⚠ About page already exists'))
        except StandardPage.DoesNotExist:
            about_page = StandardPage(
                title='Sobre la Dirección de Intercambio Académico',
                slug=about_slug,
                show_in_menus=True
            )
            parent.add_child(instance=about_page)
            
            # Add content using StreamField
            from wagtail.blocks import StreamValue
            from cms.blocks import BaseStreamBlock
            
            content_data = [
                {
                    'type': 'heading',
                    'value': {
                        'heading_text': 'Nuestra Misión',
                        'size': '2'
                    }
                },
                {
                    'type': 'paragraph',
                    'value': '<p>La Dirección de Intercambio Académico de la Universidad Autónoma de Coahuila tiene como misión facilitar experiencias educativas internacionales de alta calidad que enriquezcan la formación académica y personal de nuestros estudiantes, promoviendo el entendimiento intercultural y la excelencia académica.</p>'
                },
                {
                    'type': 'heading',
                    'value': {
                        'heading_text': 'Nuestra Visión',
                        'size': '2'
                    }
                },
                {
                    'type': 'paragraph',
                    'value': '<p>Ser reconocidos como líderes en movilidad estudiantil internacional en el norte de México, ofreciendo programas innovadores y diversificados que preparen a nuestros estudiantes para un mundo globalizado.</p>'
                },
                {
                    'type': 'heading',
                    'value': {
                        'heading_text': 'Historia',
                        'size': '2'
                    }
                },
                {
                    'type': 'paragraph',
                    'value': '<p>Desde 1995, la UAdeC ha mantenido convenios de intercambio con más de 80 instituciones en 25 países. Nuestra oficina de intercambio académico trabaja incansablemente para expandir estas oportunidades y garantizar experiencias exitosas para cada participante.</p>'
                },
            ]
            
            about_page.body = content_data
            about_page.save_revision().publish()
            self.stdout.write(self.style.SUCCESS('  ✓ Created About page'))
        
        return about_page

    def create_blog_content(self, parent):
        """Create blog index and blog posts."""
        # Get or create blog index
        try:
            blog_index = BlogIndexPage.objects.get(slug='blog')
        except BlogIndexPage.DoesNotExist:
            blog_index = BlogIndexPage(
                title='Noticias y Experiencias',
                slug='blog',
                show_in_menus=True
            )
            parent.add_child(instance=blog_index)
            blog_index.save_revision().publish()
            self.stdout.write(self.style.SUCCESS('  ✓ Created Blog Index'))
        
        # Create categories with slugs
        from django.utils.text import slugify
        categories = [
            ('Experiencias', 'experiencias'),
            ('Convocatorias', 'convocatorias'),
            ('Consejos', 'consejos'),
            ('Noticias', 'noticias')
        ]
        for cat_name, cat_slug in categories:
            BlogCategory.objects.get_or_create(
                name=cat_name,
                defaults={'slug': cat_slug}
            )
        
        # Create blog posts
        blog_posts = [
            {
                'title': 'Mi Semestre en la Universidad de Salamanca',
                'slug': 'semestre-salamanca',
                'excerpt': 'Una experiencia transformadora estudiando en una de las universidades más antiguas de Europa.',
                'date': timezone.now().date(),
                'author': None,
                'content': [
                    {
                        'type': 'paragraph',
                        'value': '<p>Cuando decidí aplicar al programa de intercambio con la Universidad de Salamanca en España, no imaginaba el impacto que tendría en mi vida académica y personal. Estos seis meses han sido una aventura increíble llena de aprendizaje y crecimiento.</p>'
                    },
                    {
                        'type': 'heading',
                        'value': {
                            'heading_text': 'La Experiencia Académica',
                            'size': '3'
                        }
                    },
                    {
                        'type': 'paragraph',
                        'value': '<p>Las clases en Salamanca fueron desafiantes pero gratificantes. Los profesores utilizan metodologías diferentes a las que estaba acostumbrada en México, fomentando más el debate y la participación activa. Cursé materias de mi carrera de Relaciones Internacionales que me dieron una perspectiva europea única.</p>'
                    },
                    {
                        'type': 'heading',
                        'value': {
                            'heading_text': 'Inmersión Cultural',
                            'size': '3'
                        }
                    },
                    {
                        'type': 'paragraph',
                        'value': '<p>Vivir en Salamanca me permitió sumergirme completamente en la cultura española. Desde las tertulias en la Plaza Mayor hasta las excursiones a ciudades cercanas como Madrid y Ávila, cada día fue una oportunidad para aprender y crecer.</p>'
                    },
                ],
                'category': 'Experiencias'
            },
            {
                'title': 'Convocatoria Abierta: Intercambio Primavera 2026',
                'slug': 'convocatoria-primavera-2026',
                'excerpt': 'Ya están abiertas las aplicaciones para el programa de intercambio del semestre Primavera 2026.',
                'date': timezone.now().date(),
                'author': None,
                'content': [
                    {
                        'type': 'paragraph',
                        'value': '<p>Nos complace anunciar que la convocatoria para el programa de intercambio académico del semestre Primavera 2026 está oficialmente abierta. Esta es tu oportunidad de estudiar en una de nuestras instituciones socias alrededor del mundo.</p>'
                    },
                    {
                        'type': 'heading',
                        'value': {
                            'heading_text': 'Fechas Importantes',
                            'size': '3'
                        }
                    },
                    {
                        'type': 'paragraph',
                        'value': '<ul><li><strong>Apertura de convocatoria:</strong> 20 de noviembre de 2025</li><li><strong>Cierre de aplicaciones:</strong> 15 de enero de 2026</li><li><strong>Publicación de resultados:</strong> 1 de febrero de 2026</li><li><strong>Inicio del intercambio:</strong> Marzo de 2026</li></ul>'
                    },
                    {
                        'type': 'heading',
                        'value': {
                            'heading_text': 'Requisitos',
                            'size': '3'
                        }
                    },
                    {
                        'type': 'paragraph',
                        'value': '<ul><li>Ser estudiante activo de la UAdeC</li><li>Promedio mínimo de 8.5</li><li>Haber cursado al menos el 40% de la carrera</li><li>Carta de recomendación de un profesor</li><li>Comprobante de nivel de idioma (según destino)</li></ul>'
                    },
                ],
                'category': 'Convocatorias'
            },
            {
                'title': '10 Consejos para Preparar tu Intercambio',
                'slug': 'consejos-preparar-intercambio',
                'excerpt': 'Guía práctica para prepararte antes de tu experiencia internacional.',
                'date': timezone.now().date(),
                'author': None,
                'content': [
                    {
                        'type': 'paragraph',
                        'value': '<p>Prepararse para un intercambio académico puede parecer abrumador, pero con la planificación adecuada, puedes asegurar que tu experiencia sea exitosa desde el inicio. Aquí te compartimos nuestros mejores consejos:</p>'
                    },
                    {
                        'type': 'paragraph',
                        'value': '<ol><li><strong>Investiga tu destino:</strong> Aprende sobre la cultura, el clima y las costumbres del país.</li><li><strong>Organiza tus documentos:</strong> Pasaporte, visa, seguro médico y documentación académica.</li><li><strong>Presupuesta cuidadosamente:</strong> Calcula gastos de vivienda, alimentación, transporte y entretenimiento.</li><li><strong>Aprende el idioma:</strong> Aunque sea lo básico, te ayudará enormemente.</li><li><strong>Mantén contacto con la oficina:</strong> Estamos aquí para ayudarte en cada paso.</li></ol>'
                    },
                ],
                'category': 'Consejos'
            }
        ]
        
        for post_data in blog_posts:
            try:
                BlogPostPage.objects.get(slug=post_data['slug'])
                self.stdout.write(self.style.WARNING(f"  ⚠ Blog post '{post_data['title']}' already exists"))
            except BlogPostPage.DoesNotExist:
                post = BlogPostPage(
                    title=post_data['title'],
                    slug=post_data['slug'],
                    introduction=post_data['excerpt'],
                    published_date=post_data['date'],
                    author=post_data['author'],
                    body=post_data['content']
                )
                blog_index.add_child(instance=post)
                
                # Add category
                category = BlogCategory.objects.get(name=post_data['category'])
                post.categories.add(category)
                
                post.save_revision().publish()
                self.stdout.write(self.style.SUCCESS(f"  ✓ Created blog post: {post_data['title']}"))
        
        return blog_index

    def create_program_content(self, parent):
        """Create program index and program pages."""
        # Get or create program index
        try:
            program_index = ProgramIndexPage.objects.get(slug='programas')
        except ProgramIndexPage.DoesNotExist:
            program_index = ProgramIndexPage(
                title='Programas de Intercambio',
                slug='programas',
                show_in_menus=True
            )
            parent.add_child(instance=program_index)
            program_index.save_revision().publish()
            self.stdout.write(self.style.SUCCESS('  ✓ Created Program Index'))
        
        # Create program pages
        programs = [
            {
                'title': 'Universidad de Salamanca - España',
                'slug': 'salamanca-espana',
                'institution': 'Universidad de Salamanca',
                'location': 'Salamanca, España',
                'duration': '1 semestre (5-6 meses)',
                'description': 'Estudia en una de las universidades más antiguas y prestigiosas de Europa, fundada en 1218.',
                'available_spots': 4,
                'content': [
                    {
                        'type': 'heading',
                        'value': {
                            'heading_text': 'Sobre la Universidad',
                            'size': '3'
                        }
                    },
                    {
                        'type': 'paragraph',
                        'value': '<p>La Universidad de Salamanca es una institución de educación superior con más de 800 años de historia. Ofrece una amplia gama de programas en humanidades, ciencias sociales y ciencias exactas.</p>'
                    },
                    {
                        'type': 'heading',
                        'value': {
                            'heading_text': 'Carreras Disponibles',
                            'size': '3'
                        }
                    },
                    {
                        'type': 'paragraph',
                        'value': '<ul><li>Derecho</li><li>Relaciones Internacionales</li><li>Economía</li><li>Historia</li><li>Filología</li></ul>'
                    },
                    {
                        'type': 'heading',
                        'value': {
                            'heading_text': 'Requisitos de Idioma',
                            'size': '3'
                        }
                    },
                    {
                        'type': 'paragraph',
                        'value': '<p>Se requiere nivel B2 de español certificado (DELE o equivalente).</p>'
                    },
                ],
                'requirements': '<p><strong>Requisitos académicos:</strong></p><ul><li>Promedio mínimo: 8.5</li><li>Haber cursado al menos 60% de créditos</li><li>Carta de recomendación académica</li><li>Certificado de idioma español nivel B2</li></ul>'
            },
            {
                'title': 'Texas A&M University - Estados Unidos',
                'slug': 'texas-am-usa',
                'institution': 'Texas A&M University',
                'location': 'College Station, Texas, USA',
                'duration': '1 semestre (4-5 meses)',
                'description': 'Una de las universidades públicas más grandes de Estados Unidos con excelencia en ingeniería y ciencias.',
                'available_spots': 3,
                'content': [
                    {
                        'type': 'heading',
                        'value': {
                            'heading_text': 'Sobre Texas A&M',
                            'size': '3'
                        }
                    },
                    {
                        'type': 'paragraph',
                        'value': '<p>Texas A&M University es reconocida mundialmente por sus programas de ingeniería, ciencias agrícolas y negocios. Como institución vecina, ofrece una excelente oportunidad para estudiantes del norte de México.</p>'
                    },
                    {
                        'type': 'heading',
                        'value': {
                            'heading_text': 'Programas Destacados',
                            'size': '3'
                        }
                    },
                    {
                        'type': 'paragraph',
                        'value': '<ul><li>Ingeniería Mecánica</li><li>Ingeniería Industrial</li><li>Agronomía</li><li>Administración de Empresas</li><li>Sistemas Computacionales</li></ul>'
                    },
                    {
                        'type': 'heading',
                        'value': {
                            'heading_text': 'Requisitos de Idioma',
                            'size': '3'
                        }
                    },
                    {
                        'type': 'paragraph',
                        'value': '<p>TOEFL iBT mínimo 79 o IELTS 6.5</p>'
                    },
                ],
                'requirements': '<p><strong>Requisitos académicos:</strong></p><ul><li>Promedio mínimo: 8.0</li><li>Haber cursado al menos 50% de créditos</li><li>Carta de recomendación</li><li>Certificado TOEFL o IELTS</li></ul>'
            },
            {
                'title': 'Università di Bologna - Italia',
                'slug': 'bologna-italia',
                'institution': 'Università di Bologna',
                'location': 'Bologna, Italia',
                'duration': '1 semestre (5 meses)',
                'description': 'La universidad más antigua del mundo occidental, fundada en 1088.',
                'available_spots': 2,
                'content': [
                    {
                        'type': 'heading',
                        'value': {
                            'heading_text': 'Historia y Prestigio',
                            'size': '3'
                        }
                    },
                    {
                        'type': 'paragraph',
                        'value': '<p>La Università di Bologna, fundada en 1088, es considerada la universidad más antigua del mundo en funcionamiento continuo. Ofrece una experiencia única combinando tradición académica con innovación.</p>'
                    },
                    {
                        'type': 'heading',
                        'value': {
                            'heading_text': 'Áreas de Estudio',
                            'size': '3'
                        }
                    },
                    {
                        'type': 'paragraph',
                        'value': '<ul><li>Arquitectura</li><li>Derecho Internacional</li><li>Ciencias Políticas</li><li>Artes y Humanidades</li><li>Ingeniería</li></ul>'
                    },
                    {
                        'type': 'heading',
                        'value': {
                            'heading_text': 'Requisitos de Idioma',
                            'size': '3'
                        }
                    },
                    {
                        'type': 'paragraph',
                        'value': '<p>Italiano nivel B1 o inglés nivel B2 (según programa elegido).</p>'
                    },
                ],
                'requirements': '<p><strong>Requisitos académicos:</strong></p><ul><li>Promedio mínimo: 8.5</li><li>Haber cursado al menos 60% de créditos</li><li>Dos cartas de recomendación</li><li>Certificado de idioma</li></ul>'
            },
        ]
        
        for prog_data in programs:
            try:
                ProgramPage.objects.get(slug=prog_data['slug'])
                self.stdout.write(self.style.WARNING(f"  ⚠ Program '{prog_data['title']}' already exists"))
            except ProgramPage.DoesNotExist:
                program = ProgramPage(
                    title=prog_data['title'],
                    slug=prog_data['slug'],
                    location=prog_data['location'],
                    duration=prog_data['duration'],
                    introduction=prog_data['description'],
                    body=prog_data['content']
                )
                program_index.add_child(instance=program)
                program.save_revision().publish()
                self.stdout.write(self.style.SUCCESS(f"  ✓ Created program: {prog_data['title']}"))
        
        return program_index

    def create_faq_content(self, parent):
        """Create FAQ index and FAQ pages."""
        # Get or create FAQ index
        try:
            faq_index = FAQIndexPage.objects.get(slug='preguntas-frecuentes')
        except FAQIndexPage.DoesNotExist:
            faq_index = FAQIndexPage(
                title='Preguntas Frecuentes',
                slug='preguntas-frecuentes',
                show_in_menus=True
            )
            parent.add_child(instance=faq_index)
            faq_index.save_revision().publish()
            self.stdout.write(self.style.SUCCESS('  ✓ Created FAQ Index'))
        
        # Create FAQ pages
        faqs = [
            {
                'title': '¿Cuáles son los requisitos para aplicar?',
                'slug': 'requisitos-aplicar',
                'answer': '<p>Los requisitos generales para aplicar a un programa de intercambio son:</p><ul><li>Ser estudiante activo de la UAdeC</li><li>Tener un promedio mínimo de 8.0 (puede variar según el programa)</li><li>Haber cursado al menos el 40-50% de tu carrera</li><li>Contar con el aval de tu coordinador de carrera</li><li>Presentar certificación de idioma del país destino</li><li>No tener adeudos académicos o administrativos</li></ul><p>Los requisitos específicos pueden variar según la universidad destino.</p>'
            },
            {
                'title': '¿Cuánto cuesta participar en un intercambio?',
                'slug': 'costo-intercambio',
                'answer': '<p>Los costos varían según el destino, pero generalmente incluyen:</p><ul><li><strong>Matrícula:</strong> En la mayoría de convenios, está exenta por reciprocidad</li><li><strong>Viáticos:</strong> Alojamiento, alimentación y transporte local (aprox. $800-1500 USD/mes)</li><li><strong>Viaje:</strong> Boleto de avión ($500-2000 USD según destino)</li><li><strong>Seguro médico:</strong> Obligatorio ($50-100 USD/mes)</li><li><strong>Visa y trámites:</strong> Variable según país ($0-400 USD)</li></ul><p>La UAdeC cuenta con becas y apoyos económicos para estudiantes destacados.</p>'
            },
            {
                'title': '¿Mis créditos serán revalidados?',
                'slug': 'revalidacion-creditos',
                'answer': '<p>Sí, los créditos cursados en la universidad de intercambio son revalidados de acuerdo a las siguientes consideraciones:</p><ul><li>Las materias deben estar previamente aprobadas por tu coordinador de carrera</li><li>Debes aprobar las materias con calificación mínima de 7.0 (o equivalente)</li><li>Al regresar, presentarás tu certificado oficial de calificaciones</li><li>La Dirección Escolar realizará el proceso de equivalencia</li><li>Los créditos aparecerán en tu historial académico</li></ul><p>Es importante que antes de viajar, apruebes tu carga académica con tu coordinador.</p>'
            },
            {
                'title': '¿Puedo trabajar durante mi intercambio?',
                'slug': 'trabajar-intercambio',
                'answer': '<p>Esto depende de las regulaciones migratorias del país destino:</p><ul><li><strong>España:</strong> Estudiantes de intercambio pueden trabajar medio tiempo con permiso</li><li><strong>Estados Unidos:</strong> Solo trabajos dentro del campus con visa F-1</li><li><strong>Italia:</strong> Permitido trabajo medio tiempo para estudiantes</li><li><strong>Otros países:</strong> Verifica las regulaciones específicas</li></ul><p>Recuerda que tu visa es de estudiante y tu prioridad debe ser el aspecto académico.</p>'
            },
            {
                'title': '¿Qué pasa si tengo una emergencia en el extranjero?',
                'slug': 'emergencia-extranjero',
                'answer': '<p>La UAdeC y la universidad destino tienen protocolos establecidos:</p><ul><li>Todos los estudiantes deben tener seguro médico internacional</li><li>Contarás con contactos de emergencia 24/7</li><li>La Dirección de Intercambio mantiene comunicación constante</li><li>Las embajadas y consulados mexicanos ofrecen apoyo</li><li>Coordinamos con las familias en caso necesario</li></ul><p>Antes de viajar, recibirás una guía completa de procedimientos de emergencia.</p>'
            },
        ]
        
        for faq_data in faqs:
            try:
                FAQPage.objects.get(slug=faq_data['slug'])
                self.stdout.write(self.style.WARNING(f"  ⚠ FAQ '{faq_data['title']}' already exists"))
            except FAQPage.DoesNotExist:
                faq = FAQPage(
                    title=faq_data['title'],
                    slug=faq_data['slug'],
                    body=[
                        {
                            'type': 'paragraph',
                            'value': faq_data['answer']
                        }
                    ]
                )
                faq_index.add_child(instance=faq)
                faq.save_revision().publish()
                self.stdout.write(self.style.SUCCESS(f"  ✓ Created FAQ: {faq_data['title']}"))
        
        return faq_index

    def create_additional_pages(self, parent):
        """Create additional supporting pages."""
        pages = [
            {
                'title': 'Contacto',
                'slug': 'contacto',
                'content': [
                    {
                        'type': 'heading',
                        'value': {
                            'heading_text': 'Dirección de Intercambio Académico',
                            'size': '2'
                        }
                    },
                    {
                        'type': 'paragraph',
                        'value': '<p><strong>Universidad Autónoma de Coahuila</strong></p><p>Boulevard V. Carranza y González Lobo s/n<br>Col. República Oriente<br>Saltillo, Coahuila, México<br>C.P. 25280</p>'
                    },
                    {
                        'type': 'heading',
                        'value': {
                            'heading_text': 'Horario de Atención',
                            'size': '3'
                        }
                    },
                    {
                        'type': 'paragraph',
                        'value': '<p>Lunes a Viernes: 9:00 AM - 6:00 PM<br>Teléfono: +52 (844) 412-8800 ext. 2345<br>Email: intercambio@uadec.edu.mx</p>'
                    },
                    {
                        'type': 'heading',
                        'value': {
                            'heading_text': 'Redes Sociales',
                            'size': '3'
                        }
                    },
                    {
                        'type': 'paragraph',
                        'value': '<p>Síguenos en nuestras redes sociales para estar al día con convocatorias y noticias:</p><ul><li>Facebook: @IntercambioUAdeC</li><li>Instagram: @intercambio_uadec</li><li>Twitter: @UAdeC_Intercambio</li></ul>'
                    },
                ]
            },
            {
                'title': 'Proceso de Aplicación',
                'slug': 'proceso-aplicacion',
                'content': [
                    {
                        'type': 'heading',
                        'value': {
                            'heading_text': 'Pasos para Aplicar',
                            'size': '2'
                        }
                    },
                    {
                        'type': 'paragraph',
                        'value': '<ol><li><strong>Información:</strong> Asiste a nuestras sesiones informativas o agenda una cita</li><li><strong>Selección de destino:</strong> Elige la universidad que mejor se adapte a tu perfil</li><li><strong>Documentación:</strong> Reúne todos los documentos requeridos</li><li><strong>Solicitud en línea:</strong> Completa el formulario de aplicación en nuestro portal</li><li><strong>Evaluación:</strong> El comité evaluará tu solicitud</li><li><strong>Resultados:</strong> Recibirás notificación de aceptación</li><li><strong>Preparativos:</strong> Realiza trámites de visa, seguro y documentación</li><li><strong>Viaje:</strong> ¡Inicia tu aventura académica!</li></ol>'
                    },
                    {
                        'type': 'heading',
                        'value': {
                            'heading_text': 'Documentos Necesarios',
                            'size': '3'
                        }
                    },
                    {
                        'type': 'paragraph',
                        'value': '<ul><li>Formato de solicitud completo</li><li>Historial académico actualizado</li><li>Carta de motivos (1-2 páginas)</li><li>Dos cartas de recomendación académicas</li><li>Certificado de idioma</li><li>Copia de pasaporte vigente</li><li>Fotografías tamaño pasaporte</li><li>Carta de aval del coordinador de carrera</li></ul>'
                    },
                ]
            }
        ]
        
        for page_data in pages:
            try:
                StandardPage.objects.get(slug=page_data['slug'])
                self.stdout.write(self.style.WARNING(f"  ⚠ Page '{page_data['title']}' already exists"))
            except StandardPage.DoesNotExist:
                page = StandardPage(
                    title=page_data['title'],
                    slug=page_data['slug'],
                    show_in_menus=True,
                    body=page_data['content']
                )
                parent.add_child(instance=page)
                page.save_revision().publish()
                self.stdout.write(self.style.SUCCESS(f"  ✓ Created page: {page_data['title']}"))

