import hashlib
import io
from datetime import datetime

from django.conf import settings
from django.core.files.base import ContentFile
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

from ..models import Document


class DocumentGenerator:
    """Service class for generating PDF documents"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Create custom styles for PDF generation"""
        self.styles.add(
            ParagraphStyle(
                name="CustomTitle",
                parent=self.styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#003366"),
                spaceAfter=30,
                alignment=1,  # Center
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="CustomHeading",
                parent=self.styles["Heading2"],
                fontSize=14,
                textColor=colors.HexColor("#003366"),
                spaceAfter=12,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="CustomBody",
                parent=self.styles["Normal"],
                fontSize=11,
                spaceAfter=12,
            )
        )

    def generate_acceptance_letter(self, exchange):
        """Generate an acceptance letter PDF for an exchange"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []

        # University header
        story.append(Paragraph(f"{exchange.university}", self.styles["CustomTitle"]))
        story.append(
            Paragraph("International Exchange Program", self.styles["Heading2"])
        )
        story.append(Spacer(1, 0.5 * inch))

        # Date
        today = datetime.now().strftime("%B %d, %Y")
        story.append(Paragraph(today, self.styles["Normal"]))
        story.append(Spacer(1, 0.3 * inch))

        # Student info
        story.append(
            Paragraph(
                f"Dear {exchange.first_name} {exchange.last_name},",
                self.styles["CustomBody"],
            )
        )
        story.append(Spacer(1, 0.2 * inch))

        # Letter content
        content = f"""
        We are pleased to inform you that your application for the exchange program to 
        <b>{exchange.destination_university}</b> in <b>{exchange.destination_country}</b> 
        has been accepted.
        
        Your exchange period will begin on <b>{exchange.start_date.strftime("%B %d, %Y")}</b> 
        and end on <b>{exchange.end_date.strftime("%B %d, %Y")}</b>.
        
        Below are the important details regarding your exchange:
        """
        story.append(Paragraph(content, self.styles["CustomBody"]))
        story.append(Spacer(1, 0.3 * inch))

        # Details table
        data = [
            ["Program:", exchange.program],
            ["Academic Year:", exchange.academic_year],
            [
                "Destination:",
                f"{exchange.destination_university}, {exchange.destination_country}",
            ],
            ["Duration:", f"{(exchange.end_date - exchange.start_date).days} days"],
        ]

        table = Table(data, colWidths=[2 * inch, 4 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("FONT", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 11),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                    ("RIGHTPADDING", (0, 0), (0, -1), 12),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 0.5 * inch))

        # Closing
        closing = """
        Please contact the International Office for next steps in preparing for your exchange.
        
        Congratulations on your acceptance!
        
        Sincerely,
        
        International Exchange Office
        """
        story.append(Paragraph(closing, self.styles["CustomBody"]))

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    def generate_progress_report(self, exchange):
        """Generate a progress report PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []

        # Header
        story.append(Paragraph("Exchange Progress Report", self.styles["CustomTitle"]))
        story.append(
            Paragraph(
                f"{exchange.first_name} {exchange.last_name}", self.styles["Heading2"]
            )
        )
        story.append(Spacer(1, 0.3 * inch))

        # Report details
        data = [
            ["Student ID:", exchange.student.username],
            ["Home University:", exchange.university],
            ["Exchange University:", exchange.destination_university],
            ["Program:", exchange.program],
            ["Status:", exchange.get_status_display()],
            ["Start Date:", exchange.start_date.strftime("%B %d, %Y")],
            ["End Date:", exchange.end_date.strftime("%B %d, %Y")],
        ]

        # Add timeline data if available
        if exchange.submitted_at:
            data.append(["Submitted:", exchange.submitted_at.strftime("%B %d, %Y")])
        if exchange.reviewed_at:
            data.append(["Reviewed:", exchange.reviewed_at.strftime("%B %d, %Y")])
        if exchange.approved_at:
            data.append(["Approved:", exchange.approved_at.strftime("%B %d, %Y")])

        table = Table(data, colWidths=[2 * inch, 4 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("FONT", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 11),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                    ("RIGHTPADDING", (0, 0), (0, -1), 12),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 0.5 * inch))

        # Documents section
        story.append(Paragraph("Submitted Documents", self.styles["CustomHeading"]))
        docs = exchange.documents.all()
        if docs:
            doc_data = [["Document Type", "Status", "Upload Date"]]
            for doc in docs:
                doc_data.append(
                    [
                        doc.get_document_type_display(),
                        "Verified" if doc.is_verified else "Pending",
                        doc.created.strftime("%Y-%m-%d"),
                    ]
                )

            doc_table = Table(doc_data, colWidths=[3 * inch, 1.5 * inch, 1.5 * inch])
            doc_table.setStyle(
                TableStyle(
                    [
                        ("FONT", (0, 0), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 10),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ]
                )
            )
            story.append(doc_table)
        else:
            story.append(
                Paragraph("No documents submitted yet.", self.styles["Normal"])
            )

        story.append(Spacer(1, 0.5 * inch))

        # Notes section if any
        if exchange.notes:
            story.append(Paragraph("Additional Notes", self.styles["CustomHeading"]))
            story.append(Paragraph(exchange.notes, self.styles["Normal"]))

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    def generate_grade_sheet(self, exchange, grades_data):
        """Generate a grade sheet PDF

        Args:
            exchange: Exchange instance
            grades_data: List of dicts with course info and grades
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []

        # Header
        story.append(Paragraph("Academic Transcript", self.styles["CustomTitle"]))
        story.append(
            Paragraph(f"{exchange.destination_university}", self.styles["Heading2"])
        )
        story.append(Spacer(1, 0.3 * inch))

        # Student information
        student_info = f"""
        <b>Student Name:</b> {exchange.first_name} {exchange.last_name}<br/>
        <b>Home University:</b> {exchange.university}<br/>
        <b>Exchange Period:</b> {exchange.start_date.strftime("%B %Y")} - {exchange.end_date.strftime("%B %Y")}
        """
        story.append(Paragraph(student_info, self.styles["CustomBody"]))
        story.append(Spacer(1, 0.3 * inch))

        # Grades table
        table_data = [["Course Code", "Course Name", "Credits", "Grade"]]
        total_credits = 0

        for grade in grades_data:
            table_data.append(
                [
                    grade.get("course_code", ""),
                    grade.get("course_name", ""),
                    str(grade.get("credits", 0)),
                    grade.get("grade", ""),
                ]
            )
            total_credits += grade.get("credits", 0)

        # Add total row
        table_data.append(["", "Total Credits:", str(total_credits), ""])

        table = Table(table_data, colWidths=[1.5 * inch, 3 * inch, 1 * inch, 1 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("FONT", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 11),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                    ("ALIGN", (2, 0), (3, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -2), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 0.5 * inch))

        # Signature section
        signature_date = datetime.now().strftime("%B %d, %Y")
        signature_text = f"""
        This transcript is issued on {signature_date}.
        
        
        _______________________
        Academic Registrar
        {exchange.destination_university}
        """
        story.append(Paragraph(signature_text, self.styles["Normal"]))

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    def save_generated_document(self, exchange, document_type, title, pdf_buffer):
        """Save a generated PDF document to the database"""
        # Calculate file hash
        pdf_buffer.seek(0)
        file_hash = hashlib.sha256(pdf_buffer.read()).hexdigest()
        pdf_buffer.seek(0)

        # Create file
        filename = f"{document_type}_{exchange.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        file_content = ContentFile(pdf_buffer.read(), name=filename)

        # Create or update document
        document, created = Document.objects.update_or_create(
            exchange=exchange,
            document_type=document_type,
            title=title,
            defaults={
                "file": file_content,
                "file_size": file_content.size,
                "file_hash": file_hash,
                "is_generated": True,
                "description": f"System generated {title}",
            },
        )

        return document
