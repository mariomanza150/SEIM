"""PDF generation helpers for system-filled mobility documents."""

from __future__ import annotations

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _safe_getattr(obj, attr: str, default: str = "—"):
    if obj is None:
        return default
    value = getattr(obj, attr, None)
    if value is None or value == "":
        return default
    return str(value)


def _destination_lines(application) -> list[tuple[str, str]]:
    """Read host destination if Phase 2 FKs exist; otherwise graceful placeholders."""
    lines: list[tuple[str, str]] = []
    host_inst = getattr(application, "host_institution", None)
    host_school = getattr(application, "host_school", None)
    host_prog = getattr(application, "host_academic_program", None)
    if host_inst is not None:
        lines.append(("Institución anfitriona", _safe_getattr(host_inst, "name")))
        country = _safe_getattr(host_inst, "country", "")
        if country and country != "—":
            lines.append(("País", country))
    else:
        lines.append(("Institución anfitriona", "Pendiente de selección"))
    if host_school is not None:
        lines.append(("Escuela / Facultad", _safe_getattr(host_school, "name")))
    if host_prog is not None:
        lines.append(("Programa académico anfitrión", _safe_getattr(host_prog, "name")))
    return lines


def render_solicitud_participacion_pdf(application) -> bytes:
    """
    Prefill Solicitud de Participación from profile + application (+ destination if present).
    """
    student = application.student
    program = application.program
    profile = getattr(student, "profile", None)

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title="Solicitud de Participación",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "SolicitudTitle",
        parent=styles["Title"],
        fontSize=16,
        spaceAfter=12,
    )
    section_style = ParagraphStyle(
        "SolicitudSection",
        parent=styles["Heading2"],
        fontSize=12,
        spaceBefore=14,
        spaceAfter=6,
    )
    body = styles["Normal"]

    institution = "SEIM"
    try:
        from django.conf import settings

        institution = getattr(settings, "INSTITUTION_NAME", "SEIM")
    except Exception:
        pass

    story = [
        Paragraph(institution, body),
        Paragraph("Solicitud de Participación en Movilidad", title_style),
        Paragraph(
            "Documento generado por SEIM. Imprima, firme y cargue el escaneo firmado.",
            body,
        ),
        Spacer(1, 8),
        Paragraph("1. Datos del estudiante", section_style),
    ]

    full_name = (
        student.get_full_name().strip()
        if hasattr(student, "get_full_name")
        else f"{_safe_getattr(student, 'first_name', '')} {_safe_getattr(student, 'last_name', '')}".strip()
    ) or _safe_getattr(student, "username")

    student_rows = [
        ["Nombre completo", full_name],
        ["Correo", _safe_getattr(student, "email")],
        ["Matrícula", _safe_getattr(profile, "matricula")],
        ["GPA", _safe_getattr(profile, "gpa")],
        [
            "Escala",
            _safe_getattr(getattr(profile, "grade_scale", None), "name")
            if profile
            else "—",
        ],
        ["Semestre (perfil)", _safe_getattr(profile, "current_semester")],
        [
            "Créditos aprobados %",
            _safe_getattr(profile, "credits_approved_percent"),
        ],
        ["Idioma", _safe_getattr(profile, "language")],
        ["Nivel idioma", _safe_getattr(profile, "language_level")],
    ]

    story.append(_kv_table(student_rows))
    story.append(Paragraph("2. Programa / esquema de movilidad", section_style))
    program_rows = [
        ["Esquema", _safe_getattr(program, "name")],
        [
            "Ventana de solicitud",
            f"{_safe_getattr(program, 'application_open_date')} – "
            f"{_safe_getattr(program, 'application_deadline')}",
        ],
        [
            "Periodo del programa",
            f"{_safe_getattr(program, 'start_date')} – {_safe_getattr(program, 'end_date')}",
        ],
    ]
    story.append(_kv_table(program_rows))

    story.append(Paragraph("3. Destino (anfitrión)", section_style))
    story.append(_kv_table(_destination_lines(application)))

    story.append(Paragraph("4. Datos al momento de la solicitud", section_style))
    apply_rows = [
        ["Semestre al aplicar", _safe_getattr(application, "semester_at_apply")],
        ["GPA al aplicar", _safe_getattr(application, "gpa_at_apply")],
        [
            "Créditos % al aplicar",
            _safe_getattr(application, "credits_percent_at_apply"),
        ],
        ["Idioma al aplicar", _safe_getattr(application, "language_at_apply")],
        [
            "Nivel idioma al aplicar",
            _safe_getattr(application, "language_level_at_apply"),
        ],
        ["ID de solicitud", str(application.id)],
    ]
    story.append(_kv_table(apply_rows))

    story.append(Spacer(1, 28))
    story.append(Paragraph("5. Declaración y firma", section_style))
    story.append(
        Paragraph(
            "Declaro que la información proporcionada es verídica y me comprometo a "
            "cumplir el Reglamento de Movilidad vigente.",
            body,
        )
    )
    story.append(Spacer(1, 36))
    story.append(
        Paragraph("Firma del estudiante: _______________________________", body)
    )
    story.append(Spacer(1, 12))
    story.append(Paragraph("Fecha: ____________________", body))

    doc.build(story)
    return buffer.getvalue()


def _kv_table(rows: list) -> Table:
    table = Table(rows, colWidths=[2.4 * inch, 4.4 * inch])
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f3f5")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def render_carta_homologacion_pdf(application) -> bytes:
    """
    Prefill Carta de Homologación from application subject selections.

    Empty selections still produce a downloadable PDF with a clear notice.
    """
    student = application.student
    program = application.program
    profile = getattr(student, "profile", None)

    selections = list(
        application.subject_selections.select_related(
            "host_subject",
            "host_subject__academic_program",
            "proposed_host_grade",
            "proposed_host_grade__grade_scale",
            "confirmed_host_grade",
            "confirmed_host_grade__grade_scale",
            "home_grade",
            "home_grade__grade_scale",
        ).order_by("created_at")
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title="Carta de Homologación",
        pageCompression=0,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "HomologTitle",
        parent=styles["Title"],
        fontSize=16,
        spaceAfter=12,
    )
    section_style = ParagraphStyle(
        "HomologSection",
        parent=styles["Heading2"],
        fontSize=12,
        spaceBefore=14,
        spaceAfter=6,
    )
    body = styles["Normal"]
    notice_style = ParagraphStyle(
        "HomologNotice",
        parent=styles["Normal"],
        textColor=colors.HexColor("#856404"),
        backColor=colors.HexColor("#fff3cd"),
        borderPadding=6,
        spaceBefore=8,
        spaceAfter=8,
    )

    full_name = (
        student.get_full_name().strip()
        if hasattr(student, "get_full_name")
        else f"{_safe_getattr(student, 'first_name', '')} {_safe_getattr(student, 'last_name', '')}".strip()
    ) or _safe_getattr(student, "username")

    story = [
        Paragraph("Carta de Homologación de Asignaturas", title_style),
        Paragraph(
            "Documento generado por SEIM a partir de las asignaturas seleccionadas. "
            "Imprima, firme y cargue el escaneo firmado.",
            body,
        ),
        Spacer(1, 8),
        Paragraph("1. Datos del estudiante", section_style),
        _kv_table(
            [
                ["Nombre completo", full_name],
                ["Correo", _safe_getattr(student, "email")],
                ["Matrícula", _safe_getattr(profile, "matricula")],
                ["Esquema de movilidad", _safe_getattr(program, "name")],
                ["ID de solicitud", str(application.id)],
            ]
        ),
        Paragraph("2. Destino (anfitrión)", section_style),
        _kv_table(_destination_lines(application)),
        Paragraph("3. Asignaturas a homologar", section_style),
    ]

    if not selections:
        story.append(
            Paragraph(
                "No hay asignaturas seleccionadas en esta solicitud. "
                "Puede agregar asignaturas opcionales en el paso «Asignaturas» "
                "y volver a descargar esta carta, o firmar este formato en blanco "
                "si no requiere homologación de materias.",
                notice_style,
            )
        )
    else:
        include_grades = any(
            getattr(sel, "grade_status", "none") in ("proposed", "confirmed", "rejected")
            or getattr(sel, "proposed_host_grade_id", None)
            or getattr(sel, "confirmed_host_grade_id", None)
            for sel in selections
        )
        header = [
            Paragraph("<b>Código anfitrión</b>", body),
            Paragraph("<b>Asignatura anfitriona</b>", body),
            Paragraph("<b>Créditos</b>", body),
            Paragraph("<b>Código casa</b>", body),
            Paragraph("<b>Asignatura casa</b>", body),
        ]
        if include_grades:
            header.extend(
                [
                    Paragraph("<b>Calificación anfitriona</b>", body),
                    Paragraph("<b>Calificación casa</b>", body),
                    Paragraph("<b>Escala</b>", body),
                ]
            )
        else:
            header.append(Paragraph("<b>Notas</b>", body))
        rows = [header]
        for sel in selections:
            subj = getattr(sel, "host_subject", None)
            host_code = (
                getattr(sel, "host_course_code", None)
                or _safe_getattr(subj, "code", "")
                or getattr(sel, "custom_code", "")
            )
            host_name = (
                getattr(sel, "host_course_name", None)
                or _safe_getattr(subj, "name")
                or getattr(sel, "custom_name", "")
            )
            credits_val = (
                _safe_getattr(sel, "credits")
                if sel.credits is not None
                else (
                    _safe_getattr(subj, "credits", "")
                    if subj is not None
                    else _safe_getattr(sel, "custom_credits", "")
                )
            )
            row = [
                Paragraph(host_code or "—", body),
                Paragraph(host_name or "—", body),
                Paragraph(credits_val, body),
                Paragraph(sel.home_course_code or "—", body),
                Paragraph(sel.home_course_label or "—", body),
            ]
            if include_grades:
                confirmed = getattr(sel, "confirmed_host_grade", None)
                proposed = getattr(sel, "proposed_host_grade", None)
                host_grade = confirmed or proposed
                host_label = _safe_getattr(host_grade, "label", "—")
                status = getattr(sel, "grade_status", "none")
                if host_grade is not None and status == "proposed":
                    host_label = f"{host_label} (pendiente)"
                elif host_grade is not None and status == "rejected":
                    host_label = f"{host_label} (rechazada)"
                home_grade = getattr(sel, "home_grade", None)
                home_label = _safe_getattr(home_grade, "label", "—")
                host_scale = _safe_getattr(
                    getattr(host_grade, "grade_scale", None), "name", ""
                )
                home_scale = _safe_getattr(
                    getattr(home_grade, "grade_scale", None), "name", ""
                )
                scale_bits = [s for s in (host_scale, home_scale) if s and s != "—"]
                scale_text = " → ".join(scale_bits) if scale_bits else "—"
                row.extend(
                    [
                        Paragraph(host_label, body),
                        Paragraph(home_label, body),
                        Paragraph(scale_text, body),
                    ]
                )
            else:
                row.append(Paragraph(sel.notes or "—", body))
            rows.append(row)
        if include_grades:
            col_widths = [
                0.75 * inch,
                1.2 * inch,
                0.6 * inch,
                0.75 * inch,
                1.1 * inch,
                1.0 * inch,
                0.9 * inch,
                1.1 * inch,
            ]
        else:
            col_widths = [
                0.9 * inch,
                1.5 * inch,
                0.7 * inch,
                0.9 * inch,
                1.4 * inch,
                1.4 * inch,
            ]
        table = Table(rows, colWidths=col_widths)
        table.setStyle(
            TableStyle(
                [
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e9ecef")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )
        story.append(table)

    story.append(Spacer(1, 28))
    story.append(Paragraph("4. Declaración y firma", section_style))
    story.append(
        Paragraph(
            "Solicito la homologación de las asignaturas listadas conforme al "
            "reglamento de movilidad vigente.",
            body,
        )
    )
    story.append(Spacer(1, 36))
    story.append(
        Paragraph("Firma del estudiante: _______________________________", body)
    )
    story.append(Spacer(1, 12))
    story.append(Paragraph("Fecha: ____________________", body))

    doc.build(story)
    return buffer.getvalue()
