"""
PDF Form Generator for UAdeC Mobility Program

Generates professional PDF forms for student mobility applications.
Uses ReportLab for PDF generation.
"""

from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus import PageBreak, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from django.conf import settings
import os


def add_header_footer(canvas, doc, title="UAdeC - Movilidad Internacional"):
    """Add header and footer to PDF pages."""
    canvas.saveState()
    
    # Header
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawString(inch, letter[1] - 0.5*inch, "Universidad Autónoma de Coahuila")
    canvas.setFont('Helvetica', 9)
    canvas.drawString(inch, letter[1] - 0.7*inch, "Coordinación General de Relaciones Internacionales")
    
    # Footer
    canvas.setFont('Helvetica', 8)
    canvas.drawString(inch, 0.5*inch, 
                     "CGRI | Tel: 844 415 3077 | relaciones.internacionales@uadec.edu.mx")
    canvas.drawString(letter[0] - 1.5*inch, 0.5*inch, 
                     f"Página {doc.page}")
    
    canvas.restoreState()


def create_styles():
    """Create custom paragraph styles."""
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#003366'),  # UAdeC blue
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#003366'),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_LEFT
    ))
    
    return styles


def generate_participation_form():
    """Generate Participation Application PDF."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=inch, leftMargin=inch,
                           topMargin=1.2*inch, bottomMargin=inch)
    
    story = []
    styles = create_styles()
    
    # Title
    story.append(Paragraph("SOLICITUD DE PARTICIPACIÓN", styles['CustomTitle']))
    story.append(Paragraph("Programa de Movilidad Internacional", styles['CustomHeading']))
    story.append(Spacer(1, 0.3*inch))
    
    # Instructions
    story.append(Paragraph(
        "Complete este formulario con letra legible o a máquina. "
        "Todos los campos son obligatorios a menos que se indique lo contrario.",
        styles['CustomBody']
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Student Information Section
    story.append(Paragraph("I. DATOS PERSONALES", styles['CustomHeading']))
    
    data = [
        ['Nombre completo:', '_______________________________________________'],
        ['Matrícula:', '_______________________________________________'],
        ['Fecha de nacimiento:', '_______________________________________________'],
        ['CURP:', '_______________________________________________'],
        ['Correo electrónico:', '_______________________________________________'],
        ['Teléfono:', '_______________________________________________'],
        ['Dirección:', '_______________________________________________'],
    ]
    
    t = Table(data, colWidths=[2*inch, 4.5*inch])
    t.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*inch))
    
    # Academic Information
    story.append(Paragraph("II. DATOS ACADÉMICOS", styles['CustomHeading']))
    
    data = [
        ['Facultad/Escuela:', '_______________________________________________'],
        ['Carrera:', '_______________________________________________'],
        ['Semestre actual:', '_______________________________________________'],
        ['Promedio general:', '_______________________________________________'],
        ['Créditos cursados:', '_______________________________________________'],
    ]
    
    t = Table(data, colWidths=[2*inch, 4.5*inch])
    t.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*inch))
    
    # Program Selection
    story.append(Paragraph("III. PROGRAMA DE MOVILIDAD", styles['CustomHeading']))
    
    data = [
        ['Universidad destino:', '_______________________________________________'],
        ['País:', '_______________________________________________'],
        ['Período:', '☐ Otoño ____    ☐ Primavera ____'],
        ['Duración:', '☐ Un semestre    ☐ Dos semestres    ☐ Verano'],
    ]
    
    t = Table(data, colWidths=[2*inch, 4.5*inch])
    t.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*inch))
    
    # Language Proficiency
    story.append(Paragraph("IV. IDIOMAS", styles['CustomHeading']))
    
    data = [
        ['Inglés:', '☐ Básico    ☐ Intermedio    ☐ Avanzado'],
        ['Certificación:', '_______________________________________________'],
        ['Otro idioma:', '_______________________________________________'],
    ]
    
    t = Table(data, colWidths=[2*inch, 4.5*inch])
    t.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4*inch))
    
    # Signature
    story.append(Paragraph("DECLARACIÓN DEL SOLICITANTE", styles['CustomHeading']))
    story.append(Paragraph(
        "Declaro que la información proporcionada es verídica y me comprometo a cumplir "
        "con los lineamientos del programa de movilidad internacional de la UAdeC.",
        styles['CustomBody']
    ))
    story.append(Spacer(1, 0.4*inch))
    
    data = [
        ['', ''],
        ['_____________________________', '_____________________________'],
        ['Firma del estudiante', 'Fecha'],
    ]
    
    t = Table(data, colWidths=[3*inch, 3*inch])
    t.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t)
    
    # Build PDF
    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    
    buffer.seek(0)
    return buffer


def generate_commitment_letter():
    """Generate Commitment Letter PDF."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=inch, leftMargin=inch,
                           topMargin=1.2*inch, bottomMargin=inch)
    
    story = []
    styles = create_styles()
    
    # Title
    story.append(Paragraph("CARTA COMPROMISO", styles['CustomTitle']))
    story.append(Paragraph("Programa de Movilidad Internacional", styles['CustomHeading']))
    story.append(Spacer(1, 0.3*inch))
    
    # Letter content
    story.append(Paragraph("Saltillo, Coahuila a ___ de __________ de 20__", styles['CustomBody']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("COORDINACIÓN GENERAL DE RELACIONES INTERNACIONALES", styles['CustomBody']))
    story.append(Paragraph("UNIVERSIDAD AUTÓNOMA DE COAHUILA", styles['CustomBody']))
    story.append(Paragraph("PRESENTE", styles['CustomBody']))
    story.append(Spacer(1, 0.3*inch))
    
    # Main text
    text = """
    Yo, <b>_____________________________________________</b>, estudiante de la carrera de 
    <b>_____________________________________________</b> de la 
    <b>_____________________________________________</b>, con matrícula 
    <b>_____________________________________________</b>, por medio de la presente me comprometo a:
    """
    story.append(Paragraph(text, styles['CustomBody']))
    story.append(Spacer(1, 0.2*inch))
    
    # Commitments
    commitments = [
        "Cumplir con todos los requisitos académicos y administrativos establecidos por el programa de movilidad.",
        "Mantener un comportamiento ejemplar que honre a la Universidad Autónoma de Coahuila.",
        "Cursar satisfactoriamente las materias acordadas en el programa de estudios.",
        "Regresar a la UAdeC al finalizar el período de intercambio acordado.",
        "Presentar la documentación requerida para la revalidación de créditos.",
        "Cumplir con el reglamento de la institución de acogida.",
        "Mantener comunicación constante con la CGRI durante mi estancia.",
        "Informar inmediatamente cualquier situación de emergencia o cambio en mi programa.",
    ]
    
    for i, commitment in enumerate(commitments, 1):
        story.append(Paragraph(f"{i}. {commitment}", styles['CustomBody']))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Signature section
    story.append(Paragraph(
        "Asimismo, autorizo a la CGRI a verificar la información proporcionada y acepto "
        "las consecuencias académicas y administrativas en caso de incumplimiento.",
        styles['CustomBody']
    ))
    story.append(Spacer(1, 0.5*inch))
    
    story.append(Paragraph("ATENTAMENTE", styles['CustomBody']))
    story.append(Spacer(1, 0.8*inch))
    
    data = [
        ['_____________________________________'],
        ['Nombre y firma del estudiante'],
        [''],
        ['_____________________________________'],
        ['Nombre y firma del padre/madre o tutor'],
    ]
    
    t = Table(data, colWidths=[4*inch])
    t.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t)
    
    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    
    buffer.seek(0)
    return buffer


def generate_nomination_letter_template():
    """Generate Nomination Letter Template PDF."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=inch, leftMargin=inch,
                           topMargin=1.2*inch, bottomMargin=inch)
    
    story = []
    styles = create_styles()
    
    # Title
    story.append(Paragraph("CARTA DE POSTULACIÓN", styles['CustomTitle']))
    story.append(Paragraph("(Formato para Director de Facultad/Escuela)", styles['CustomHeading']))
    story.append(Spacer(1, 0.3*inch))
    
    # Letter format
    story.append(Paragraph("Saltillo, Coahuila a ___ de __________ de 20__", styles['CustomBody']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("DRA. LOURDES MORALES OYERVIDES", styles['CustomBody']))
    story.append(Paragraph("COORDINADORA GENERAL DE RELACIONES INTERNACIONALES", styles['CustomBody']))
    story.append(Paragraph("UNIVERSIDAD AUTÓNOMA DE COAHUILA", styles['CustomBody']))
    story.append(Paragraph("PRESENTE", styles['CustomBody']))
    story.append(Spacer(1, 0.3*inch))
    
    # Main text
    text = """
    Por medio de la presente, me permito POSTULAR al estudiante 
    <b>_____________________________________________</b>, con matrícula 
    <b>_____________________________________________</b>, de la carrera de 
    <b>_____________________________________________</b>, para participar en el Programa de 
    Movilidad Internacional con destino a <b>_____________________________________________</b> 
    durante el período <b>_____________________________________________</b>.
    """
    story.append(Paragraph(text, styles['CustomBody']))
    story.append(Spacer(1, 0.2*inch))
    
    # Student qualifications
    text = """
    El estudiante mencionado cumple con los siguientes requisitos:
    """
    story.append(Paragraph(text, styles['CustomBody']))
    story.append(Spacer(1, 0.1*inch))
    
    qualifications = [
        "Promedio general de <b>_______</b>",
        "Ha cursado el <b>_______</b>% de los créditos de su carrera",
        "Se encuentra regular en su inscripción y no tiene adeudos con la universidad",
        "Ha demostrado excelente desempeño académico y conducta ejemplar",
        "Cuenta con el nivel de idioma requerido por la institución de destino",
    ]
    
    for qual in qualifications:
        story.append(Paragraph(f"• {qual}", styles['CustomBody']))
        story.append(Spacer(1, 0.05*inch))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Closing
    text = """
    Considero que el estudiante es un candidato idóneo para representar a nuestra institución 
    y aprovechar al máximo esta oportunidad de movilidad académica internacional.
    """
    story.append(Paragraph(text, styles['CustomBody']))
    story.append(Spacer(1, 0.5*inch))
    
    story.append(Paragraph("Sin más por el momento, quedo de usted.", styles['CustomBody']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("ATENTAMENTE", styles['CustomBody']))
    story.append(Spacer(1, 0.8*inch))
    
    data = [
        ['_____________________________________'],
        ['Nombre y firma'],
        ['Director(a) de Facultad/Escuela'],
        [''],
        ['Sello de la Facultad/Escuela'],
    ]
    
    t = Table(data, colWidths=[4*inch])
    t.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t)
    
    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    
    buffer.seek(0)
    return buffer


def generate_course_equivalency_form():
    """Generate Course Equivalency Form PDF."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=inch, leftMargin=inch,
                           topMargin=1.2*inch, bottomMargin=inch)
    
    story = []
    styles = create_styles()
    
    # Title
    story.append(Paragraph("FORMULARIO DE EQUIVALENCIAS", styles['CustomTitle']))
    story.append(Paragraph("Programa de Movilidad Internacional", styles['CustomHeading']))
    story.append(Spacer(1, 0.3*inch))
    
    # Student info
    data = [
        ['Estudiante:', '_______________________________________________'],
        ['Matrícula:', '_______________________________________________'],
        ['Carrera:', '_______________________________________________'],
        ['Universidad destino:', '_______________________________________________'],
    ]
    
    t = Table(data, colWidths=[2*inch, 4.5*inch])
    t.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*inch))
    
    # Instructions
    story.append(Paragraph(
        "Complete la siguiente tabla con las materias que cursará en la universidad destino "
        "y sus equivalencias en la UAdeC. Este formulario debe ser aprobado por su coordinador académico.",
        styles['CustomBody']
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Course table
    data = [
        ['Materia en UAdeC', 'Créditos', 'Materia en Universidad Destino', 'Créditos'],
        ['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', ''],
    ]
    
    t = Table(data, colWidths=[2.5*inch, 0.8*inch, 2.5*inch, 0.8*inch])
    t.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
        ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWHEIGHT', (0, 1), (-1, -1), 0.5*inch),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*inch))
    
    # Approval section
    story.append(Paragraph("APROBACIONES", styles['CustomHeading']))
    story.append(Spacer(1, 0.3*inch))
    
    data = [
        ['Coordinador Académico', '', 'CGRI'],
        ['', '', ''],
        ['_________________________', '', '_________________________'],
        ['Nombre y firma', '', 'Nombre y firma'],
        ['Fecha: ______________', '', 'Fecha: ______________'],
    ]
    
    t = Table(data, colWidths=[2.5*inch, 1*inch, 2.5*inch])
    t.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t)
    
    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    
    buffer.seek(0)
    return buffer


def generate_guidelines_document():
    """Generate Guidelines and Provisions PDF."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=inch, leftMargin=inch,
                           topMargin=1.2*inch, bottomMargin=inch)
    
    story = []
    styles = create_styles()
    
    # Title
    story.append(Paragraph("LINEAMIENTOS Y DISPOSICIONES", styles['CustomTitle']))
    story.append(Paragraph("Programa de Movilidad Internacional", styles['CustomHeading']))
    story.append(Spacer(1, 0.3*inch))
    
    # Introduction
    story.append(Paragraph(
        "Los siguientes lineamientos rigen el Programa de Movilidad Internacional de la Universidad "
        "Autónoma de Coahuila. Todo estudiante participante debe conocer y aceptar estas disposiciones.",
        styles['CustomBody']
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Guidelines
    guidelines = [
        ("REQUISITOS ACADÉMICOS", [
            "Promedio mínimo de 80/100",
            "Haber cursado al menos el 45% de los créditos de la carrera",
            "No estar cursando el último semestre durante la movilidad",
            "Estar inscrito de manera regular en la UAdeC",
        ]),
        ("REQUISITOS ADMINISTRATIVOS", [
            "No tener adeudos con la universidad",
            "Carta de postulación del director de facultad/escuela",
            "Cumplir con los requisitos específicos de la institución destino",
        ]),
        ("DURANTE LA MOVILIDAD", [
            "Mantener comunicación constante con la CGRI",
            "Cumplir con el reglamento de la institución de acogida",
            "Cursar satisfactoriamente las materias acordadas",
            "Mantener un comportamiento ejemplar",
        ]),
        ("AL REGRESAR", [
            "Presentar carta de la institución con calificaciones obtenidas",
            "Solicitar revalidación de créditos en tiempo y forma",
            "Presentar informe de actividades",
            "Compartir experiencia con futuros candidatos",
        ]),
    ]
    
    for title, items in guidelines:
        story.append(Paragraph(title, styles['CustomHeading']))
        for item in items:
            story.append(Paragraph(f"• {item}", styles['CustomBody']))
            story.append(Spacer(1, 0.05*inch))
        story.append(Spacer(1, 0.2*inch))
    
    # Acceptance
    story.append(PageBreak())
    story.append(Paragraph("ACEPTACIÓN DE LINEAMIENTOS", styles['CustomHeading']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph(
        "Yo, _________________________________, declaro que he leído y comprendido los lineamientos "
        "y disposiciones del Programa de Movilidad Internacional de la UAdeC y me comprometo a cumplirlos.",
        styles['CustomBody']
    ))
    story.append(Spacer(1, 0.5*inch))
    
    data = [
        ['', ''],
        ['_____________________________', '_____________________________'],
        ['Firma del estudiante', 'Fecha'],
    ]
    
    t = Table(data, colWidths=[3*inch, 3*inch])
    t.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t)
    
    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    
    buffer.seek(0)
    return buffer


def generate_return_program_form():
    """Generate Return Program Form PDF."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=inch, leftMargin=inch,
                           topMargin=1.2*inch, bottomMargin=inch)
    
    story = []
    styles = create_styles()
    
    # Title
    story.append(Paragraph("PROGRAMA DE RETORNO", styles['CustomTitle']))
    story.append(Paragraph("Informe Final de Movilidad", styles['CustomHeading']))
    story.append(Spacer(1, 0.3*inch))
    
    # Student info
    data = [
        ['Estudiante:', '_______________________________________________'],
        ['Matrícula:', '_______________________________________________'],
        ['Universidad destino:', '_______________________________________________'],
        ['País:', '_______________________________________________'],
        ['Período:', '_______________________________________________'],
    ]
    
    t = Table(data, colWidths=[2*inch, 4.5*inch])
    t.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*inch))
    
    # Sections
    sections = [
        ("MATERIAS CURSADAS", "Liste las materias que cursó durante su movilidad:"),
        ("EXPERIENCIA ACADÉMICA", "Describa su experiencia académica en la institución de acogida:"),
        ("EXPERIENCIA CULTURAL", "Describa los aspectos culturales más relevantes de su experiencia:"),
        ("RECOMENDACIONES", "¿Qué recomendaciones daría a futuros estudiantes?"),
    ]
    
    for title, description in sections:
        story.append(Paragraph(title, styles['CustomHeading']))
        story.append(Paragraph(description, styles['CustomBody']))
        story.append(Spacer(1, 0.1*inch))
        
        # Lines for writing
        for _ in range(4):
            story.append(Paragraph("_" * 90, styles['CustomBody']))
        
        story.append(Spacer(1, 0.2*inch))
    
    # Signature
    story.append(Spacer(1, 0.3*inch))
    data = [
        ['', ''],
        ['_____________________________', '_____________________________'],
        ['Firma del estudiante', 'Fecha'],
    ]
    
    t = Table(data, colWidths=[3*inch, 3*inch])
    t.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t)
    
    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    
    buffer.seek(0)
    return buffer


# Dictionary of all available forms
FORMS = {
    'participation': {
        'generator': generate_participation_form,
        'filename': 'Solicitud_Participacion.pdf',
        'title': 'Solicitud de Participación',
        'description': 'Formulario oficial para aplicar al programa de movilidad internacional',
    },
    'commitment': {
        'generator': generate_commitment_letter,
        'filename': 'Carta_Compromiso.pdf',
        'title': 'Carta Compromiso',
        'description': 'Carta de compromiso del estudiante con el programa de movilidad',
    },
    'nomination': {
        'generator': generate_nomination_letter_template,
        'filename': 'Carta_Postulacion_Template.pdf',
        'title': 'Plantilla de Carta de Postulación',
        'description': 'Formato para que el director de facultad/escuela postule al estudiante',
    },
    'equivalency': {
        'generator': generate_course_equivalency_form,
        'filename': 'Formulario_Equivalencias.pdf',
        'title': 'Formulario de Equivalencias',
        'description': 'Para establecer las equivalencias de materias entre UAdeC y universidad destino',
    },
    'guidelines': {
        'generator': generate_guidelines_document,
        'filename': 'Lineamientos_Disposiciones.pdf',
        'title': 'Lineamientos y Disposiciones',
        'description': 'Reglas y disposiciones del programa de movilidad internacional',
    },
    'return': {
        'generator': generate_return_program_form,
        'filename': 'Programa_Retorno.pdf',
        'title': 'Programa de Retorno',
        'description': 'Informe final y revalidación de créditos al regresar del intercambio',
    },
}

