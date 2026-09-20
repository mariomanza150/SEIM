"""PDF generation helpers for system-filled mobility documents."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Image as RLImage
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _safe_getattr(obj, attr: str, default: str = "—"):
    if obj is None:
        return default
    value = getattr(obj, attr, None)
    if value is None or value == "":
        return default
    return str(value)


def _blank(value) -> str:
    """Empty string for wet-ink blanks; strip placeholder dashes."""
    if value is None:
        return ""
    text = str(value).strip()
    if not text or text == "—":
        return ""
    return text


def _check_mark(checked: bool) -> str:
    return "[X]" if checked else "[ ]"


def _line_field(label: str, value: str, body_style, label_style) -> list:
    """Label + value (or underline gap) as a two-cell row fragment."""
    filled = _blank(value)
    return [
        Paragraph(f"<b>{label}</b>", label_style),
        Paragraph(filled if filled else "&nbsp;", body_style),
    ]


def _resolve_brand_logo(*names: str):
    """Return filesystem path to the first existing branding logo, if any."""
    try:
        from django.conf import settings

        base = Path(settings.BASE_DIR) / "branding"
        slug = getattr(settings, "INSTITUTION_SLUG", "uadec") or "uadec"
    except Exception:
        return None

    for name in names:
        for folder in (slug, "uadec"):
            candidate = base / folder / "logos" / name
            if candidate.is_file():
                return str(candidate)
    return None


def _brand_logo_flowable(
    max_width: float = 2.4 * inch,
    max_height: float = 0.65 * inch,
):
    """Institution logo scaled to fit within max box without stretching."""
    logo_path = _resolve_brand_logo(
        "institution-logo-full.png",
        "institution-logo.png",
    )
    if not logo_path:
        return None
    try:
        from PIL import Image as PILImage

        with PILImage.open(logo_path) as im:
            px_w, px_h = im.size
    except Exception:
        px_w, px_h = 192, 72
    if px_w <= 0 or px_h <= 0:
        return None
    aspect = px_w / px_h
    width = max_width
    height = width / aspect
    if height > max_height:
        height = max_height
        width = height * aspect
    return RLImage(logo_path, width=width, height=height)


def _cgri_brand_header(brand_blue, cgri_style) -> Table:
    """Shared CGRI letterhead: institution logo left, CGRI title right."""
    header_right = Paragraph(
        "COORDINACIÓN GENERAL<br/>DE RELACIONES INTERNACIONALES",
        cgri_style,
    )
    logo = _brand_logo_flowable()
    if logo is not None:
        header = Table([[logo, header_right]], colWidths=[3.6 * inch, 3.7 * inch])
    else:
        header = Table([["", header_right]], colWidths=[3.6 * inch, 3.7 * inch])
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return header


def _boxed_section(title: str, inner, brand_blue, section_title_style, content_width):
    """Section heading + blue-bordered content block (FS-SP rounded-box look)."""
    box = Table([[inner]], colWidths=[content_width])
    box.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1.5, brand_blue),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return [Paragraph(title, section_title_style), Spacer(1, 4), box]


def _mobility_period_flags(program) -> tuple[bool, bool, str]:
    """Infer enero–junio / agosto–diciembre and year from program start_date."""
    start = getattr(program, "start_date", None)
    if not start:
        return False, False, ""
    month = start.month
    year = str(start.year)
    if month <= 6:
        return True, False, year
    return False, True, year


def _mobility_program_flags(program) -> tuple[bool, bool, bool, str]:
    """Map scheme name / agreements to FS-SP program checkboxes."""
    name = (getattr(program, "name", None) or "").strip()
    lower = name.lower()
    bilateral = "bilateral" in lower or "convenio" in lower
    conahec = "conahec" in lower
    indep = "independ" in lower
    try:
        types = set(
            program.exchange_agreements.values_list("agreement_type", flat=True)
        )
        if "bilateral" in types:
            bilateral = True
        if "conahec" in types:
            conahec = True
    except Exception:
        pass
    other = "" if (bilateral or conahec or indep) else name
    return bilateral, conahec, indep, other


def _student_name_parts(student) -> tuple[str, str]:
    """Split into Nombre(s) / Apellidos for the official FS-SP layout."""
    first = _blank(getattr(student, "first_name", ""))
    middle = _blank(getattr(student, "middle_name", ""))
    last = _blank(getattr(student, "last_name", ""))
    mothers = _blank(getattr(student, "mothers_last_name", ""))
    given = " ".join(p for p in (first, middle) if p).strip()
    surnames = " ".join(p for p in (last, mothers) if p).strip()
    if not given and not surnames:
        full = ""
        if hasattr(student, "get_full_name"):
            full = _blank(student.get_full_name())
        if not full:
            full = _blank(getattr(student, "username", ""))
        return full, ""
    return given, surnames


def render_solicitud_participacion_pdf(application) -> bytes:
    """
    Prefill Solicitud de Participación (FS-SP / CGRI-SP) from profile + application.

    Layout follows ``SAMPLES/FS-SP Solicitud de Participacion Saliente.pdf``.
    Missing profile/destination fields stay blank for wet-ink completion.
    """
    student = application.student
    program = application.program
    profile = getattr(student, "profile", None)

    brand_blue = _brand_hex("BRAND_PRIMARY", "#2E5790")
    brand_gold = _brand_hex("BRAND_ACCENT", "#BF9B4C")
    black = colors.black
    content_width = 7.3 * inch

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
        topMargin=0.45 * inch,
        bottomMargin=0.55 * inch,
        title="Solicitud de Participación",
        pageCompression=0,
    )
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "FsSpBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=black,
    )
    field_label = ParagraphStyle(
        "FsSpFieldLabel",
        parent=body,
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=brand_blue,
    )
    section_title = ParagraphStyle(
        "FsSpSectionTitle",
        parent=body,
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=brand_blue,
        alignment=1,
        spaceBefore=8,
        spaceAfter=2,
    )
    title_style = ParagraphStyle(
        "FsSpTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=16,
        textColor=brand_gold,
        alignment=1,
        spaceBefore=8,
        spaceAfter=10,
    )
    cgri_style = ParagraphStyle(
        "FsSpCgri",
        parent=body,
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=black,
        alignment=2,
    )
    photo_style = ParagraphStyle(
        "FsSpPhoto",
        parent=body,
        fontName="Helvetica-Bold",
        fontSize=10,
        alignment=1,
        textColor=brand_blue,
    )
    sig_label = ParagraphStyle(
        "FsSpSigLabel",
        parent=body,
        fontSize=8,
        leading=10,
        alignment=1,
    )
    small = ParagraphStyle(
        "FsSpSmall",
        parent=body,
        fontSize=7,
        leading=9,
        textColor=brand_blue,
    )
    footer_style = ParagraphStyle(
        "FsSpFooter",
        parent=body,
        fontSize=8,
        leading=10,
        textColor=brand_blue,
        alignment=2,
    )

    given_names, surnames = _student_name_parts(student)
    gender = _blank(getattr(profile, "gender", "") if profile else "")
    male = gender == "male"
    female = gender == "female"
    dob = ""
    if profile and getattr(profile, "date_of_birth", None):
        dob = profile.date_of_birth.strftime("%d/%m/%Y")

    jan_jun, aug_dec, year = _mobility_period_flags(program)
    bilateral, conahec, indep, other_prog = _mobility_program_flags(program)

    def _field_row(label: str, value: str, width_label=1.35 * inch, width_value=5.7 * inch):
        row = Table(
            [_line_field(label, value, body, field_label)],
            colWidths=[width_label, width_value],
        )
        row.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ("LINEBELOW", (1, 0), (1, 0), 0.6, brand_blue),
                ]
            )
        )
        return row

    def _two_col_fields(left_label, left_val, right_label, right_val):
        left = _field_row(left_label, left_val, 1.25 * inch, 2.2 * inch)
        right = _field_row(right_label, right_val, 1.15 * inch, 2.3 * inch)
        pair = Table([[left, right]], colWidths=[3.55 * inch, 3.55 * inch])
        pair.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        return pair

    story: list = []

    # --- Page 1: mobility info + personal data ---
    story.append(_cgri_brand_header(brand_blue, cgri_style))
    story.append(Spacer(1, 6))
    story.append(
        HRFlowable(
            width="100%",
            thickness=2.5,
            color=brand_blue,
            spaceBefore=2,
            spaceAfter=2,
        )
    )
    story.append(Paragraph("SOLICITUD DE PARTICIPACIÓN", title_style))

    period_line = Paragraph(
        f"<b>Periodo de Intercambio:</b>&nbsp;&nbsp;"
        f"{_check_mark(jan_jun)} enero – junio&nbsp;&nbsp;&nbsp;"
        f"{_check_mark(aug_dec)} agosto – diciembre&nbsp;&nbsp;&nbsp;"
        f"<b>Año:</b> {_blank(year) or '______________'}",
        body,
    )
    prog_line = Paragraph(
        f"<b>Programa de intercambio:</b>&nbsp;&nbsp;"
        f"{_check_mark(bilateral)} Convenio bilateral&nbsp;&nbsp;"
        f"{_check_mark(conahec)} CONAHEC&nbsp;&nbsp;"
        f"{_check_mark(indep)} Mov. Independiente",
        body,
    )
    other_line = _field_row("Otro:", other_prog, 0.55 * inch, 4.55 * inch)
    mobility_inner = Table(
        [[period_line], [Spacer(1, 4)], [prog_line], [Spacer(1, 4)], [other_line]],
        colWidths=[5.85 * inch],
    )
    mobility_inner.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )
    mobility_box = Table([[mobility_inner]], colWidths=[5.95 * inch])
    mobility_box.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1.5, brand_blue),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    photo_box = Table(
        [[Paragraph("FOTO", photo_style)]],
        colWidths=[1.15 * inch],
        rowHeights=[1.15 * inch],
    )
    photo_box.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1.5, brand_blue),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]
        )
    )
    story.append(Paragraph("INFORMACIÓN DE MOVILIDAD", section_title))
    story.append(Spacer(1, 2))
    mobility_block = Table(
        [[photo_box, mobility_box]],
        colWidths=[1.25 * inch, 6.05 * inch],
    )
    mobility_block.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (0, 0), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story.append(mobility_block)
    story.append(Spacer(1, 10))

    sexo_line = Paragraph(
        f"<b>Sexo:</b>&nbsp;&nbsp;"
        f"{_check_mark(male)} Masculino&nbsp;&nbsp;&nbsp;&nbsp;"
        f"{_check_mark(female)} Femenino",
        field_label,
    )
    personal_rows = [
        [_field_row("Nombre(s):", given_names)],
        [_field_row("Apellidos:", surnames)],
        [_field_row("Nacionalidad:", "")],
        [sexo_line],
        [_field_row("Fecha de nacimiento:", dob)],
        [_field_row("Lugar de nacimiento:", _blank(getattr(profile, "birthplace", "") if profile else ""))],
        [
            _two_col_fields(
                "Nº Pasaporte:",
                _blank(getattr(profile, "passport_number", "") if profile else ""),
                "RFC:",
                _blank(getattr(profile, "rfc", "") if profile else ""),
            )
        ],
        [
            _two_col_fields(
                "CURP:",
                "",
                "Email:",
                _blank(getattr(student, "email", "")),
            )
        ],
        [
            _two_col_fields("Calle con Nº:", "", "Colonia:", ""),
        ],
        [
            _two_col_fields("Ciudad:", "", "Estado:", ""),
        ],
        [
            _two_col_fields(
                "Teléfono casa:",
                "",
                "Celular:",
                _blank(getattr(profile, "mobile_phone", "") if profile else ""),
            )
        ],
        [_field_row("Código postal:", _blank(getattr(profile, "postal_code", "") if profile else ""))],
        [Spacer(1, 6)],
        [
            Paragraph(
                "<b>INFORMACIÓN DEL SEGURO MÉDICO</b> "
                "(SOLO SI YA SE CUENTA CON ÉL, SI NO DEJAR EN BLANCO)",
                small,
            )
        ],
        [_two_col_fields("Número de póliza:", "", "Company / Aseguradora:", "")],
        [_two_col_fields("Expedida en:", "", "Expires / Expira en:", "")],
        [Spacer(1, 4)],
        [Paragraph("<b>CONTACTO DE EMERGENCIA:</b>", small)],
        [_two_col_fields("Nombre:", "", "Parentesco:", "")],
        [_two_col_fields("Teléfono:", "", "Email:", "")],
    ]
    personal_inner = Table(personal_rows, colWidths=[content_width - 0.2 * inch])
    personal_inner.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )
    story.extend(
        _boxed_section(
            "DATOS PERSONALES DEL ESTUDIANTE",
            personal_inner,
            brand_blue,
            section_title,
            content_width,
        )
    )
    story.append(Spacer(1, 12))
    story.append(Paragraph("(CGRI-SP)<br/>20/01/26", footer_style))

    # --- Page 2: origin + destination + signatures ---
    story.append(PageBreak())
    story.append(_cgri_brand_header(brand_blue, cgri_style))
    story.append(Spacer(1, 6))
    story.append(
        HRFlowable(
            width="100%",
            thickness=2.5,
            color=brand_blue,
            spaceBefore=2,
            spaceAfter=2,
        )
    )

    home_school = ""
    home_unidad = ""
    home_carrera = ""
    if profile:
        home_school = _blank(_safe_getattr(getattr(profile, "school", None), "name", ""))
        home_unidad = _blank(_safe_getattr(getattr(profile, "unidad", None), "name", ""))
        home_carrera = _blank(
            _safe_getattr(getattr(profile, "home_academic_program", None), "name", "")
        )
    matricula = _blank(getattr(profile, "matricula", "") if profile else "")
    gpa = _blank(
        getattr(application, "gpa_at_apply", None)
        or (getattr(profile, "gpa", None) if profile else None)
    )
    credits_pct = _blank(
        getattr(application, "credits_percent_at_apply", None)
        or (getattr(profile, "credits_approved_percent", None) if profile else None)
    )
    semester = _blank(
        getattr(application, "semester_at_apply", None)
        or (getattr(profile, "current_semester", None) if profile else None)
    )

    def _pair_underlined(a_label, a_val, b_label, b_val, widths):
        pair = Table(
            [
                [
                    *_line_field(a_label, a_val, body, field_label),
                    *_line_field(b_label, b_val, body, field_label),
                ]
            ],
            colWidths=widths,
        )
        pair.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ("LINEBELOW", (1, 0), (1, 0), 0.6, brand_blue),
                    ("LINEBELOW", (3, 0), (3, 0), 0.6, brand_blue),
                ]
            )
        )
        return pair

    origin_inner = Table(
        [
            [
                _pair_underlined(
                    "Facultad:",
                    home_school,
                    "Unidad:",
                    home_unidad,
                    [1.0 * inch, 3.5 * inch, 0.75 * inch, 1.75 * inch],
                )
            ],
            [
                _pair_underlined(
                    "Ciudad:",
                    "",
                    "Carrera:",
                    home_carrera,
                    [0.85 * inch, 2.0 * inch, 0.85 * inch, 3.3 * inch],
                )
            ],
            [_field_row("Matrícula:", matricula, 1.0 * inch, 6.0 * inch)],
            [
                Paragraph(
                    f"<b>Promedio general:</b> {_blank(gpa) or '___________'}&nbsp;&nbsp;&nbsp;"
                    f"<b>Créditos aprobados (%):</b> {_blank(credits_pct) or '______________'}&nbsp;&nbsp;&nbsp;"
                    f"<b>Créditos cursados:</b> ___________ de ___________",
                    body,
                )
            ],
            [
                Paragraph(
                    f"<b>Semestre actual:</b> {_blank(semester) or '__________'} de __________",
                    body,
                )
            ],
        ],
        colWidths=[content_width - 0.2 * inch],
    )
    origin_inner.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )

    story.extend(
        _boxed_section(
            "INSTITUCIÓN DE ORIGEN",
            origin_inner,
            brand_blue,
            section_title,
            content_width,
        )
    )
    story.append(Spacer(1, 12))

    host_inst = getattr(application, "host_institution", None)
    host_school = getattr(application, "host_school", None)
    host_prog = getattr(application, "host_academic_program", None)
    dest_univ = _blank(_safe_getattr(host_inst, "name", "")) if host_inst else ""
    dest_fac = _blank(_safe_getattr(host_school, "name", "")) if host_school else ""
    dest_carr = _blank(_safe_getattr(host_prog, "name", "")) if host_prog else ""
    dest_country = _blank(_safe_getattr(host_inst, "country", "")) if host_inst else ""

    dest_inner = Table(
        [
            [_field_row("Universidad destino:", dest_univ, 1.45 * inch, 5.55 * inch)],
            [
                _pair_underlined(
                    "Facultad:",
                    dest_fac,
                    "Campus:",
                    "",
                    [1.0 * inch, 3.3 * inch, 0.85 * inch, 1.85 * inch],
                )
            ],
            [_field_row("Carrera:", dest_carr, 0.9 * inch, 6.1 * inch)],
            [
                _pair_underlined(
                    "Ciudad:",
                    "",
                    "País:",
                    dest_country,
                    [0.85 * inch, 2.6 * inch, 0.7 * inch, 2.85 * inch],
                )
            ],
        ],
        colWidths=[content_width - 0.2 * inch],
    )
    dest_inner.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )

    story.extend(
        _boxed_section(
            "INSTITUCIÓN DESTINO",
            dest_inner,
            brand_blue,
            section_title,
            content_width,
        )
    )
    story.append(Spacer(1, 14))

    sig_inner = Table(
        [
            [
                Paragraph("", body),
                Paragraph("", body),
            ],
            [
                Paragraph("Firma del estudiante", sig_label),
                Paragraph(
                    "Firma del titular de la dirección en Facultad de origen",
                    sig_label,
                ),
            ],
        ],
        colWidths=[3.5 * inch, 3.5 * inch],
        rowHeights=[1.1 * inch, 0.4 * inch],
    )
    sig_inner.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, 0), "BOTTOM"),
                ("VALIGN", (0, 1), (-1, 1), "TOP"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("LINEABOVE", (0, 1), (0, 1), 1.0, brand_blue),
                ("LINEABOVE", (1, 1), (1, 1), 1.0, brand_blue),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 1), (-1, 1), 6),
            ]
        )
    )
    story.extend(
        _boxed_section(
            "SIGNATURES / FIRMAS",
            sig_inner,
            brand_blue,
            section_title,
            content_width,
        )
    )
    story.append(Spacer(1, 18))
    story.append(Paragraph("(CGRI-SP)<br/>20/01/26", footer_style))

    doc.build(story)
    return buffer.getvalue()


def _brand_hex(name: str, default: str) -> colors.Color:
    try:
        from django.conf import settings

        raw = getattr(settings, name, None) or default
    except Exception:
        raw = default
    return colors.HexColor(str(raw))


def _selection_host_fields(sel) -> tuple[str, str, str]:
    """Host (destino) code, name, and credits for FS-HM rows."""
    subj = getattr(sel, "host_subject", None)
    code = (
        getattr(sel, "host_course_code", None)
        or _safe_getattr(subj, "code", "")
        or getattr(sel, "custom_code", "")
        or ""
    )
    name = (
        getattr(sel, "host_course_name", None)
        or _safe_getattr(subj, "name", "")
        or getattr(sel, "custom_name", "")
        or ""
    )
    if sel.credits is not None:
        credits_val = _safe_getattr(sel, "credits")
    elif subj is not None and getattr(subj, "credits", None) is not None:
        credits_val = _safe_getattr(subj, "credits")
    elif getattr(sel, "custom_credits", None) is not None:
        credits_val = _safe_getattr(sel, "custom_credits")
    else:
        credits_val = ""
    return (code if code != "—" else "", name if name != "—" else "", credits_val)


def render_carta_homologacion_pdf(application) -> bytes:
    """
    Prefill Homologación de Materias (FS-HM / CGRI-MAT) from subject selections.

    Layout follows ``SAMPLES/FS-HM Homologacion de Materias.pdf``. Empty
    selections still produce a blank official-style form for wet-ink use.
    """
    student = application.student
    profile = getattr(student, "profile", None)

    selections = list(
        application.subject_selections.select_related(
            "host_subject",
            "host_subject__academic_program",
        ).order_by("created_at")
    )

    brand_blue = _brand_hex("BRAND_PRIMARY", "#2E5790")
    brand_gold = _brand_hex("BRAND_ACCENT", "#BF9B4C")
    label_bg = brand_blue
    header_bg = brand_blue
    white = colors.white
    black = colors.black

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
        topMargin=0.45 * inch,
        bottomMargin=0.45 * inch,
        title="Homologación de Materias",
        pageCompression=0,
    )
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "HomologBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        textColor=black,
    )
    cell = ParagraphStyle(
        "HomologCell",
        parent=body,
        fontSize=8,
        leading=10,
    )
    cell_center = ParagraphStyle(
        "HomologCellCenter",
        parent=cell,
        alignment=1,
    )
    label_style = ParagraphStyle(
        "HomologLabel",
        parent=body,
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=white,
    )
    header_cell = ParagraphStyle(
        "HomologHeaderCell",
        parent=body,
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=9,
        textColor=white,
        alignment=1,
    )
    title_style = ParagraphStyle(
        "HomologTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=16,
        textColor=brand_gold,
        alignment=1,
        spaceBefore=10,
        spaceAfter=14,
    )
    cgri_style = ParagraphStyle(
        "HomologCgri",
        parent=body,
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=black,
        alignment=2,
    )
    sig_label = ParagraphStyle(
        "HomologSigLabel",
        parent=body,
        fontSize=8,
        leading=10,
        alignment=1,
    )
    footer_style = ParagraphStyle(
        "HomologFooter",
        parent=body,
        fontSize=8,
        leading=10,
        textColor=brand_blue,
        alignment=2,
    )

    full_name = (
        student.get_full_name().strip()
        if hasattr(student, "get_full_name")
        else f"{_safe_getattr(student, 'first_name', '')} {_safe_getattr(student, 'last_name', '')}".strip()
    ) or _safe_getattr(student, "username")

    home_program = _safe_getattr(
        getattr(profile, "home_academic_program", None) if profile else None,
        "name",
        "",
    )
    if not home_program or home_program == "—":
        home_program = ""
    home_school = _safe_getattr(
        getattr(profile, "school", None) if profile else None,
        "name",
        "",
    )
    if not home_school or home_school == "—":
        home_school = ""

    host_inst = getattr(application, "host_institution", None)
    dest_inst = _safe_getattr(host_inst, "name", "") if host_inst else ""
    if dest_inst == "—":
        dest_inst = ""
    dest_country = _safe_getattr(host_inst, "country", "") if host_inst else ""
    if dest_country == "—":
        dest_country = ""

    story: list = []

    story.append(_cgri_brand_header(brand_blue, cgri_style))
    story.append(Spacer(1, 6))
    story.append(
        HRFlowable(
            width="100%",
            thickness=2.5,
            color=brand_blue,
            spaceBefore=2,
            spaceAfter=2,
        )
    )
    story.append(Paragraph("HOMOLOGACIÓN DE MATERIAS", title_style))

    info_rows = [
        ("Nombre del alumno", full_name),
        ("Matrícula", _safe_getattr(profile, "matricula", "") if profile else ""),
        ("Programa educativo", home_program),
        ("Escuela o Facultad de origen", home_school),
        ("Institución destino", dest_inst if dest_inst else ""),
        ("País destino", dest_country),
    ]
    info_data = [
        [
            Paragraph(label, label_style),
            Paragraph(value if value and value != "—" else "", body),
        ]
        for label, value in info_rows
    ]
    info_table = Table(info_data, colWidths=[2.35 * inch, 4.95 * inch])
    info_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), label_bg),
                ("TEXTCOLOR", (0, 0), (0, -1), white),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.8, brand_blue),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(info_table)
    story.append(Spacer(1, 14))

    subject_header = [
        Paragraph("CLAVE", header_cell),
        Paragraph("MATERIAS UNIVERSIDAD DE ORIGEN", header_cell),
        Paragraph("CRÉDITOS", header_cell),
        Paragraph("CLAVE", header_cell),
        Paragraph("MATERIAS UNIVERSIDAD DESTINO", header_cell),
        Paragraph("CRÉDITOS", header_cell),
    ]
    subject_rows = [subject_header]
    min_rows = 5
    for sel in selections:
        host_code, host_name, host_credits = _selection_host_fields(sel)
        home_code = (sel.home_course_code or "").strip()
        home_name = (sel.home_course_label or "").strip()
        # Homologación credits apply to the origin (home) mapping column.
        home_credits = (
            _safe_getattr(sel, "credits") if sel.credits is not None else host_credits
        )
        subject_rows.append(
            [
                Paragraph(home_code, cell_center),
                Paragraph(home_name, cell),
                Paragraph(home_credits if home_credits != "—" else "", cell_center),
                Paragraph(host_code, cell_center),
                Paragraph(host_name, cell),
                Paragraph(host_credits if host_credits != "—" else "", cell_center),
            ]
        )
    while len(subject_rows) - 1 < min_rows:
        subject_rows.append([Paragraph("", cell) for _ in range(6)])

    col_widths = [
        0.75 * inch,
        2.0 * inch,
        0.7 * inch,
        0.75 * inch,
        2.0 * inch,
        0.7 * inch,
    ]
    subjects = Table(subject_rows, colWidths=col_widths, rowHeights=[22] + [28] * (len(subject_rows) - 1))
    subjects.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), header_bg),
                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.8, brand_blue),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(subjects)
    story.append(Spacer(1, 28))

    # Signature rows: label left, solid blue line right (matches FS-HM).
    sig_entries = [
        (
            "Nombre, Firma y Sello del<br/>"
            "<b>Titular de la Dirección</b><br/>"
            "de la Escuela o Facultad de Origen"
        ),
        (
            "Nombre, Firma y Sello de la<br/>"
            "<b>Secretaría Académica</b><br/>"
            "de la Escuela o Facultad de Origen"
        ),
        (
            "<b>VoBo.</b><br/>"
            "Dr. Juan Roberto Benavente Valdés<br/>"
            "Subcoordinador General Académico<br/>"
            "de Relaciones Internacionales"
        ),
    ]
    signatures = [
        [Paragraph(label, sig_label), Paragraph("", cell)]
        for label in sig_entries
    ]
    sig_table = Table(signatures, colWidths=[3.5 * inch, 3.8 * inch])
    sig_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("LINEBELOW", (1, 0), (1, -1), 1.2, brand_blue),
            ]
        )
    )
    story.append(sig_table)
    story.append(Spacer(1, 18))
    # Official FS-HM form revision stamp from SAMPLES/.
    story.append(Paragraph("(CGRI-MAT)<br/>20/01/2026", footer_style))

    doc.build(story)
    return buffer.getvalue()
