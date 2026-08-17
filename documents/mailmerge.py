"""Word MERGEFIELD prefilling for document-type templates.

Templates are standard .docx files with Word mail-merge fields
(Insert → Field → MergeField). When a student downloads a template in the
context of an application, field values are filled from the student profile,
application, and program.
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
    {"name": "GPA", "group": "student", "description": "GPA"},
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
    {"name": "HostSchool", "group": "application", "description": "Selected host school"},
    {
        "name": "HostAcademicProgram",
        "group": "application",
        "description": "Selected host academic program",
    },
    {"name": "ApplicationId", "group": "application", "description": "Application UUID"},
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


def merge_values_for_application(application) -> dict[str, str]:
    """Build MERGEFIELD name → value map from an application."""
    student = application.student
    try:
        profile = student.profile
    except ObjectDoesNotExist:
        profile = None
    program = application.program
    full_name = " ".join(
        part
        for part in (
            student.first_name,
            getattr(student, "middle_name", "") or "",
            student.last_name,
            getattr(student, "mothers_last_name", "") or "",
        )
        if part
    ).strip() or student.get_full_name()

    values = {
        "FirstName": _fmt(student.first_name),
        "MiddleName": _fmt(getattr(student, "middle_name", "")),
        "LastName": _fmt(student.last_name),
        "MothersLastName": _fmt(getattr(student, "mothers_last_name", "")),
        "FullName": _fmt(full_name),
        "Email": _fmt(student.email),
        "Username": _fmt(student.username),
        "ProgramName": _fmt(program.name if program else ""),
        "ProgramStartDate": _fmt(getattr(program, "start_date", None)),
        "ProgramEndDate": _fmt(getattr(program, "end_date", None)),
        "ApplicationDeadline": _fmt(getattr(program, "application_deadline", None)),
        "HostInstitution": _related_name(application, "host_institution"),
        "HostSchool": _related_name(application, "host_school"),
        "HostAcademicProgram": _related_name(application, "host_academic_program"),
        "ApplicationId": _fmt(application.id),
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


def is_docx_filename(name: str | None) -> bool:
    return bool(name) and str(name).lower().endswith(".docx")


def _set_run_text(run, text: str) -> None:
    """Replace all w:t nodes in a run with a single text node."""
    texts = run.findall(f"{{{W_NS}}}t")
    if texts:
        texts[0].text = text
        texts[0].set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        for extra in texts[1:]:
            run.remove(extra)
        return
    t_el = etree.SubElement(run, f"{{{W_NS}}}t")
    t_el.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t_el.text = text


def _replace_simple_fields(root, values: dict[str, str]) -> None:
    for el in root.xpath(".//w:fldSimple", namespaces=NSMAP):
        instr = el.get(f"{{{W_NS}}}instr") or ""
        match = FLD_INSTR_RE.search(instr)
        if not match:
            continue
        name = match.group(1)
        value = values.get(name, values.get(name.lower(), ""))
        runs = el.findall(f"{{{W_NS}}}r")
        if runs:
            _set_run_text(runs[0], value)
            for extra in runs[1:]:
                el.remove(extra)
        else:
            run = etree.SubElement(el, f"{{{W_NS}}}r")
            _set_run_text(run, value)


def _replace_complex_fields(parent, values: dict[str, str]) -> None:
    """Replace begin/separate/end MERGEFIELD sequences under ``parent``."""
    children = list(parent)
    i = 0
    while i < len(children):
        child = children[i]
        fld = child.find(f"{{{W_NS}}}fldChar") if child.tag == f"{{{W_NS}}}r" else None
        if fld is None or fld.get(f"{{{W_NS}}}fldCharType") != "begin":
            # Recurse into containers (hyperlinks, sdt, etc.)
            if child.tag != f"{{{W_NS}}}r":
                _replace_complex_fields(child, values)
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

        name = match.group(1)
        value = values.get(name, values.get(name.lower(), ""))
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


def _replace_placeholders(root, values: dict[str, str]) -> None:
    for t_el in root.xpath(".//w:t", namespaces=NSMAP):
        if not t_el.text or "{{" not in t_el.text:
            continue

        def _sub(match: re.Match) -> str:
            name = match.group(1)
            return values.get(name, values.get(name.lower(), ""))

        t_el.text = PLACEHOLDER_RE.sub(_sub, t_el.text)


def _merge_xml_bytes(xml_bytes: bytes, values: dict[str, str]) -> bytes:
    root = etree.fromstring(xml_bytes)
    _replace_simple_fields(root, values)
    for para in root.xpath(".//w:p", namespaces=NSMAP):
        _replace_complex_fields(para, values)
    _replace_placeholders(root, values)
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def merge_docx(template_bytes: bytes, values: dict[str, str]) -> bytes:
    """Return a new .docx with MERGEFIELD / {{Name}} placeholders filled."""
    src = zipfile.ZipFile(io.BytesIO(template_bytes), "r")
    out_buf = io.BytesIO()
    with zipfile.ZipFile(out_buf, "w", compression=zipfile.ZIP_DEFLATED) as dest:
        for info in src.infolist():
            data = src.read(info.filename)
            name = info.filename
            if name.startswith("word/") and name.endswith(".xml"):
                base = name.rsplit("/", 1)[-1]
                if (
                    base == "document.xml"
                    or base.startswith("header")
                    or base.startswith("footer")
                ):
                    try:
                        data = _merge_xml_bytes(data, values)
                    except etree.XMLSyntaxError:
                        pass
            dest.writestr(info, data)
    src.close()
    return out_buf.getvalue()
