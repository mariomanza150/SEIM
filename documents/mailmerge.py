"""Word MERGEFIELD prefilling for document-type templates.

Templates are standard .docx files with Word mail-merge fields
(Insert → Field → MergeField). Field values come from the student profile
(``merge_values_for_student``) and, when an application is present, from
program / host / application fields (``merge_values_for_application``).
"""

from __future__ import annotations

import io
import re
import zipfile
from datetime import date, datetime
from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from lxml import etree

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"
NSMAP = {"w": W_NS}
FLD_INSTR_RE = re.compile(r"MERGEFIELD\s+([A-Za-z][A-Za-z0-9_]*)", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"\{\{([A-Za-z][A-Za-z0-9_]*)\}\}")

# Catalog shown to admins when authoring templates.
MERGE_FIELD_CATALOG: list[dict[str, str]] = [
    {"name": "FirstName", "group": "student", "description": "Student first name"},
    {"name": "MiddleName", "group": "student", "description": "Student middle name"},
    {"name": "LastName", "group": "student", "description": "Student last name"},
    {
        "name": "MothersLastName",
        "group": "student",
        "description": "Student mother's last name",
    },
    {"name": "FullName", "group": "student", "description": "Student full name"},
    {"name": "Email", "group": "student", "description": "Student email"},
    {"name": "Username", "group": "student", "description": "Student username"},
    {"name": "Matricula", "group": "student", "description": "Student ID / matrícula"},
    {"name": "GPA", "group": "student", "description": "Promedio"},
    {"name": "CurrentSemester", "group": "student", "description": "Current semester"},
    {
        "name": "CreditsApprovedPercent",
        "group": "student",
        "description": "Credits approved percent",
    },
    {"name": "School", "group": "student", "description": "Home school / faculty"},
    {"name": "Unidad", "group": "student", "description": "Unidad"},
    {"name": "AcademicLevel", "group": "student", "description": "Academic level"},
    {
        "name": "HomeAcademicProgram",
        "group": "student",
        "description": "Home academic program",
    },
    {"name": "Gender", "group": "student", "description": "Gender"},
    {"name": "Birthplace", "group": "student", "description": "Birthplace"},
    {"name": "BirthCountry", "group": "student", "description": "Birth country"},
    {"name": "BirthState", "group": "student", "description": "Birth state"},
    {"name": "BirthCity", "group": "student", "description": "Birth city"},
    {"name": "CreditsApproved", "group": "student", "description": "Credits approved"},
    {"name": "CreditsTotal", "group": "student", "description": "Total credits"},
    {"name": "PostalCode", "group": "student", "description": "Postal code"},
    {"name": "PassportNumber", "group": "student", "description": "Passport number"},
    {"name": "MobilePhone", "group": "student", "description": "Mobile phone"},
    {"name": "RFC", "group": "student", "description": "RFC"},
    {"name": "DateOfBirth", "group": "student", "description": "Date of birth"},
    {"name": "Language", "group": "student", "description": "Primary language"},
    {"name": "LanguageLevel", "group": "student", "description": "CEFR language level"},
    {"name": "BankInstitution", "group": "student", "description": "Bank institution"},
    {"name": "CLABE", "group": "student", "description": "CLABE"},
    {"name": "ProgramName", "group": "program", "description": "Exchange program name"},
    {
        "name": "ProgramStartDate",
        "group": "program",
        "description": "Program start date",
    },
    {"name": "ProgramEndDate", "group": "program", "description": "Program end date"},
    {
        "name": "ApplicationDeadline",
        "group": "program",
        "description": "Program application deadline",
    },
    {
        "name": "HostInstitution",
        "group": "application",
        "description": "Selected host institution",
    },
    {
        "name": "HostSchool",
        "group": "application",
        "description": "Selected host school",
    },
    {
        "name": "HostAcademicProgram",
        "group": "application",
        "description": "Selected host academic program",
    },
    {
        "name": "ApplicationId",
        "group": "application",
        "description": "Application UUID",
    },
]


def _fmt(value) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return format(value, "f")
    return str(value)


def _related_name(obj, attr: str) -> str:
    related = getattr(obj, attr, None) if obj is not None else None
    if related is None:
        return ""
    return _fmt(getattr(related, "name", related))


def merge_values_for_student(student) -> dict[str, str]:
    """Build MERGEFIELD name → value map from a user and their profile.

    Program / host / ApplicationId keys are always present but blank when
    there is no application context.
    """
    try:
        profile = student.profile
    except ObjectDoesNotExist:
        profile = None
    full_name = (
        " ".join(
            part
            for part in (
                student.first_name,
                getattr(student, "middle_name", "") or "",
                student.last_name,
                getattr(student, "mothers_last_name", "") or "",
            )
            if part
        ).strip()
        or student.get_full_name()
    )

    values = {
        "FirstName": _fmt(student.first_name),
        "MiddleName": _fmt(getattr(student, "middle_name", "")),
        "LastName": _fmt(student.last_name),
        "MothersLastName": _fmt(getattr(student, "mothers_last_name", "")),
        "FullName": _fmt(full_name),
        "Email": _fmt(student.email),
        "Username": _fmt(student.username),
        "ProgramName": "",
        "ProgramStartDate": "",
        "ProgramEndDate": "",
        "ApplicationDeadline": "",
        "HostInstitution": "",
        "HostSchool": "",
        "HostAcademicProgram": "",
        "ApplicationId": "",
        "Matricula": "",
        "GPA": "",
        "CurrentSemester": "",
        "CreditsApprovedPercent": "",
        "School": "",
        "Unidad": "",
        "AcademicLevel": "",
        "HomeAcademicProgram": "",
        "Gender": "",
        "Birthplace": "",
        "BirthCountry": "",
        "BirthState": "",
        "BirthCity": "",
        "CreditsApproved": "",
        "CreditsTotal": "",
        "PostalCode": "",
        "PassportNumber": "",
        "MobilePhone": "",
        "RFC": "",
        "DateOfBirth": "",
        "Language": "",
        "LanguageLevel": "",
        "BankInstitution": "",
        "CLABE": "",
    }
    if profile is None:
        return values

    values.update(
        {
            "Matricula": _fmt(profile.matricula),
            "GPA": _fmt(profile.gpa),
            "CurrentSemester": _fmt(profile.current_semester),
            "CreditsApprovedPercent": _fmt(profile.credits_approved_percent),
            "School": _related_name(profile, "school"),
            "Unidad": _related_name(profile, "unidad"),
            "AcademicLevel": _related_name(profile, "academic_level"),
            "HomeAcademicProgram": _related_name(profile, "home_academic_program"),
            "Gender": _fmt(profile.gender),
            "Birthplace": _fmt(profile.birthplace),
            "BirthCountry": _fmt(getattr(profile, "birth_country", "")),
            "BirthState": _fmt(getattr(profile, "birth_state", "")),
            "BirthCity": _fmt(getattr(profile, "birth_city", "")),
            "CreditsApproved": _fmt(getattr(profile, "credits_approved", None)),
            "CreditsTotal": _fmt(getattr(profile, "credits_total", None)),
            "PostalCode": _fmt(profile.postal_code),
            "PassportNumber": _fmt(profile.passport_number),
            "MobilePhone": _fmt(profile.mobile_phone),
            "RFC": _fmt(profile.rfc),
            "DateOfBirth": _fmt(profile.date_of_birth),
            "Language": _fmt(profile.language),
            "LanguageLevel": _fmt(profile.language_level),
            "BankInstitution": _related_name(profile, "bank_institution"),
            "CLABE": _fmt(profile.clabe),
        }
    )
    return values


def merge_values_for_application(application) -> dict[str, str]:
    """Build MERGEFIELD name → value map from an application.

    Student / profile fields come from ``merge_values_for_student``; program
    and host keys are filled from the application.
    """
    values = merge_values_for_student(application.student)
    program = application.program
    values.update(
        {
            "ProgramName": _fmt(program.name if program else ""),
            "ProgramStartDate": _fmt(getattr(program, "start_date", None)),
            "ProgramEndDate": _fmt(getattr(program, "end_date", None)),
            "ApplicationDeadline": _fmt(getattr(program, "application_deadline", None)),
            "HostInstitution": _related_name(application, "host_institution"),
            "HostSchool": _related_name(application, "host_school"),
            "HostAcademicProgram": _related_name(application, "host_academic_program"),
            "ApplicationId": _fmt(application.id),
        }
    )
    return values


def is_docx_filename(name: str | None) -> bool:
    return bool(name) and str(name).lower().endswith(".docx")


def _is_merge_part(name: str) -> bool:
    if not (name.startswith("word/") and name.endswith(".xml")):
        return False
    base = name.rsplit("/", 1)[-1]
    return (
        base == "document.xml" or base.startswith("header") or base.startswith("footer")
    )


def _make_value_lookup(values: dict[str, str]):
    """Exact key match wins; otherwise case-insensitive fallback."""
    lower_map = {key.lower(): value for key, value in values.items()}

    def lookup(name: str) -> str:
        if name in values:
            return values[name]
        return lower_map.get(name.lower(), "")

    return lookup


def _iter_paragraph_text_nodes(para):
    """Yield ``w:t`` nodes owned by ``para``, skipping nested paragraphs.

    Nested ``w:p`` (e.g. inside ``w:txbxContent``) are handled by their own
    paragraph iteration. Intervening siblings such as ``w:proofErr`` and
    bookmarks are ignored automatically.
    """

    def walk(elem):
        for child in elem:
            if child.tag == f"{{{W_NS}}}p":
                continue
            if child.tag == f"{{{W_NS}}}t":
                yield child
            else:
                yield from walk(child)

    yield from walk(para)


def _xml_has_fillable_fields(xml_bytes: bytes) -> bool:
    """Detect MERGEFIELD / ``{{Name}}`` after concatenating split runs."""
    try:
        root = etree.fromstring(xml_bytes)
    except etree.XMLSyntaxError:
        return False

    for para in root.xpath(".//w:p", namespaces=NSMAP):
        full_text = "".join(
            (node.text or "") for node in _iter_paragraph_text_nodes(para)
        )
        if PLACEHOLDER_RE.search(full_text):
            return True

    instr_text = "".join(
        (node.text or "") for node in root.xpath(".//w:instrText", namespaces=NSMAP)
    )
    if FLD_INSTR_RE.search(instr_text):
        return True

    for el in root.xpath(".//w:fldSimple", namespaces=NSMAP):
        instr = el.get(f"{{{W_NS}}}instr") or ""
        if FLD_INSTR_RE.search(instr):
            return True

    return False


def docx_has_fillable_fields(template_bytes: bytes) -> bool:
    """True when the package contains MERGEFIELD or ``{{Name}}`` placeholders.

    Blank forms with neither must stay untouched: calling ``merge_docx`` on them
    rewrites XML/ZIP bytes and must be skipped. Placeholders split across Word
    runs are detected by concatenating each paragraph's ``w:t`` text.
    """
    try:
        with zipfile.ZipFile(io.BytesIO(template_bytes), "r") as src:
            for name in src.namelist():
                if not _is_merge_part(name):
                    continue
                raw = src.read(name)
                text = raw.decode("utf-8", errors="ignore")
                if FLD_INSTR_RE.search(text) or PLACEHOLDER_RE.search(text):
                    return True
                if _xml_has_fillable_fields(raw):
                    return True
    except zipfile.BadZipFile:
        return False
    return False


def _set_run_text(run, text: str) -> None:
    """Replace all w:t nodes in a run with a single text node."""
    texts = run.findall(f"{{{W_NS}}}t")
    if texts:
        texts[0].text = text
        texts[0].set(XML_SPACE, "preserve")
        for extra in texts[1:]:
            run.remove(extra)
        return
    t_el = etree.SubElement(run, f"{{{W_NS}}}t")
    t_el.set(XML_SPACE, "preserve")
    t_el.text = text


def _replace_simple_fields(root, lookup) -> None:
    for el in root.xpath(".//w:fldSimple", namespaces=NSMAP):
        instr = el.get(f"{{{W_NS}}}instr") or ""
        match = FLD_INSTR_RE.search(instr)
        if not match:
            continue
        value = lookup(match.group(1))
        runs = el.findall(f"{{{W_NS}}}r")
        if runs:
            _set_run_text(runs[0], value)
            for extra in runs[1:]:
                el.remove(extra)
        else:
            run = etree.SubElement(el, f"{{{W_NS}}}r")
            _set_run_text(run, value)


def _replace_complex_fields(parent, lookup) -> None:
    """Replace begin/separate/end MERGEFIELD sequences under ``parent``."""
    children = list(parent)
    i = 0
    while i < len(children):
        child = children[i]
        fld = child.find(f"{{{W_NS}}}fldChar") if child.tag == f"{{{W_NS}}}r" else None
        if fld is None or fld.get(f"{{{W_NS}}}fldCharType") != "begin":
            # Recurse into containers (hyperlinks, sdt, etc.)
            if child.tag != f"{{{W_NS}}}r":
                _replace_complex_fields(child, lookup)
            i += 1
            continue

        instr_parts: list[str] = []
        begin_idx = i
        j = i + 1
        found_end = False
        separate_idx = None
        while j < len(children):
            run = children[j]
            if run.tag != f"{{{W_NS}}}r":
                j += 1
                continue
            inner_fld = run.find(f"{{{W_NS}}}fldChar")
            if inner_fld is not None:
                kind = inner_fld.get(f"{{{W_NS}}}fldCharType")
                if kind == "separate":
                    separate_idx = j
                elif kind == "end":
                    found_end = True
                    j += 1
                    break
            else:
                for instr in run.findall(f"{{{W_NS}}}instrText"):
                    instr_parts.append(instr.text or "")
            j += 1

        if not found_end:
            i += 1
            continue

        instr = "".join(instr_parts)
        match = FLD_INSTR_RE.search(instr)
        if not match:
            i = j
            children = list(parent)
            continue

        value = lookup(match.group(1))
        end_idx = j  # exclusive

        # Keep the first result run (after separate, or the begin run) as the value.
        keep_idx = (separate_idx + 1) if separate_idx is not None else begin_idx
        if keep_idx >= end_idx:
            keep_idx = begin_idx
        keep_run = children[keep_idx]
        # Strip field chars / instrText from the kept run and set text.
        for tag in ("fldChar", "instrText"):
            for node in keep_run.findall(f"{{{W_NS}}}{tag}"):
                keep_run.remove(node)
        _set_run_text(keep_run, value)

        # Remove every other run in the field.
        for remove_i in range(end_idx - 1, begin_idx - 1, -1):
            if remove_i == keep_idx:
                continue
            parent.remove(children[remove_i])

        children = list(parent)
        i = 0
        # Restart scan from the kept run's new index
        try:
            i = children.index(keep_run) + 1
        except ValueError:
            i = begin_idx + 1


def _char_index_to_node(
    texts: list[str], pos: int, *, exclusive_end: bool = False
) -> tuple[int, int]:
    """Map a character offset in ``"".join(texts)`` to ``(node_index, offset)``.

    Start indices use strict ``<`` so a match that begins exactly on a ``<w:t>``
    boundary lands in the following run (skipping empty ``w:t`` nodes). Exclusive
    end indices keep ``<=`` so the end offset stays on the correct node.
    """
    remaining = pos
    for index, text in enumerate(texts):
        if exclusive_end:
            if remaining <= len(text):
                return index, remaining
        elif remaining < len(text):
            return index, remaining
        remaining -= len(text)
    if not texts:
        return 0, 0
    return len(texts) - 1, len(texts[-1])


def _splice_replacement(
    texts: list[str], start: int, end: int, value: str
) -> tuple[int, int]:
    """Replace ``texts`` span ``[start:end)`` with ``value``; return touched range."""
    start_i, start_off = _char_index_to_node(texts, start)
    end_i, end_off = _char_index_to_node(texts, end, exclusive_end=True)
    if start_i == end_i:
        node_text = texts[start_i]
        texts[start_i] = node_text[:start_off] + value + node_text[end_off:]
        return start_i, start_i

    texts[start_i] = texts[start_i][:start_off] + value
    for index in range(start_i + 1, end_i):
        texts[index] = ""
    texts[end_i] = texts[end_i][end_off:]
    return start_i, end_i


def _replace_placeholders_in_paragraph(para, lookup) -> None:
    t_nodes = list(_iter_paragraph_text_nodes(para))
    if not t_nodes:
        return

    texts = [node.text or "" for node in t_nodes]
    full_text = "".join(texts)
    matches = list(PLACEHOLDER_RE.finditer(full_text))
    if not matches:
        return

    touched: set[int] = set()
    # Right-to-left so earlier match offsets stay valid as later spans shrink/grow.
    for match in reversed(matches):
        value = lookup(match.group(1))
        start_i, end_i = _splice_replacement(texts, match.start(), match.end(), value)
        touched.update(range(start_i, end_i + 1))

    for index in sorted(touched):
        t_nodes[index].text = texts[index]
        t_nodes[index].set(XML_SPACE, "preserve")


def _replace_placeholders(root, lookup) -> None:
    """Fill ``{{Name}}`` placeholders, including those split across Word runs."""
    for para in root.xpath(".//w:p", namespaces=NSMAP):
        _replace_placeholders_in_paragraph(para, lookup)


def _merge_xml_bytes(xml_bytes: bytes, values: dict[str, str]) -> bytes:
    root = etree.fromstring(xml_bytes)
    lookup = _make_value_lookup(values)
    _replace_simple_fields(root, lookup)
    for para in root.xpath(".//w:p", namespaces=NSMAP):
        _replace_complex_fields(para, lookup)
    _replace_placeholders(root, lookup)
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def merge_docx(template_bytes: bytes, values: dict[str, str]) -> bytes:
    """Return a new .docx with MERGEFIELD / {{Name}} placeholders filled."""
    src = zipfile.ZipFile(io.BytesIO(template_bytes), "r")
    out_buf = io.BytesIO()
    with zipfile.ZipFile(out_buf, "w", compression=zipfile.ZIP_DEFLATED) as dest:
        for info in src.infolist():
            data = src.read(info.filename)
            name = info.filename
            if _is_merge_part(name):
                try:
                    data = _merge_xml_bytes(data, values)
                except etree.XMLSyntaxError:
                    pass
            dest.writestr(info, data)
    src.close()
    return out_buf.getvalue()
