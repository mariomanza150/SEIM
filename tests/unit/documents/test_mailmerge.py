"""Focused unit tests for Word mail-merge split-run and case-insensitive fill."""

from __future__ import annotations

import io
import re
import zipfile

from django.test import SimpleTestCase
from lxml import etree

from documents.mailmerge import (
    W_NS,
    XML_SPACE,
    docx_has_fillable_fields,
    merge_docx,
)

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>
  <Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>
</Types>"""

RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

BOLD_RPR = "<w:rPr><w:b/></w:rPr>"


def _pack_docx(**parts: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("[Content_Types].xml", CONTENT_TYPES)
        zf.writestr("_rels/.rels", RELS)
        for name, xml in parts.items():
            zf.writestr(name, xml)
    return buf.getvalue()


def _doc(body_inner: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W_NS}">
  <w:body>
    {body_inner}
  </w:body>
</w:document>"""


def _header(inner: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:hdr xmlns:w="{W_NS}">
  {inner}
</w:hdr>"""


def _footer(inner: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="{W_NS}">
  {inner}
</w:ftr>"""


def _blank_docx() -> bytes:
    return _pack_docx(
        **{
            "word/document.xml": _doc(
                "<w:p><w:r><w:t>Blank form with no fields</w:t></w:r></w:p>"
            )
        }
    )


def _read_part(docx_bytes: bytes, part: str = "word/document.xml") -> etree._Element:
    with zipfile.ZipFile(io.BytesIO(docx_bytes)) as zf:
        return etree.fromstring(zf.read(part))


def _joined_text(root) -> str:
    return "".join((node.text or "") for node in root.iter(f"{{{W_NS}}}t"))


def _first_run_has_bold(root) -> bool:
    for run in root.iter(f"{{{W_NS}}}r"):
        texts = [t for t in run if t.tag == f"{{{W_NS}}}t" and (t.text or "").strip()]
        if not texts:
            continue
        rpr = run.find(f"{{{W_NS}}}rPr")
        if rpr is not None and rpr.find(f"{{{W_NS}}}b") is not None:
            return True
    return False


def _space_preserve_on_value(root, value: str) -> bool:
    for node in root.iter(f"{{{W_NS}}}t"):
        if value in (node.text or "") and node.get(XML_SPACE) == "preserve":
            return True
    return False


class SplitRunPlaceholderTests(SimpleTestCase):
    def test_prooferr_split_fullname_and_school_preserves_space_and_formatting(self):
        body = f"""
        <w:p>
          <w:r>{BOLD_RPR}<w:t xml:space="preserve"> {{{{</w:t></w:r>
          <w:proofErr w:type="spellStart"/>
          <w:r><w:t>FullName</w:t></w:r>
          <w:proofErr w:type="spellEnd"/>
          <w:r><w:t>}}}}</w:t></w:r>
          <w:r>{BOLD_RPR}<w:t xml:space="preserve"> {{{{</w:t></w:r>
          <w:proofErr w:type="spellStart"/>
          <w:r><w:t>School</w:t></w:r>
          <w:proofErr w:type="spellEnd"/>
          <w:r><w:t>}}}}</w:t></w:r>
        </w:p>
        """
        raw = _pack_docx(**{"word/document.xml": _doc(body)})
        # Intact {{Name}} is absent from raw XML; only split-run detection finds it.
        self.assertIsNone(
            re.search(r"\{\{[A-Za-z]", raw.decode("utf-8", errors="ignore"))
        )
        self.assertTrue(docx_has_fillable_fields(raw))

        filled = merge_docx(
            raw,
            {
                "FullName": "Jane Doe",
                "School": "School of Engineering",
            },
        )
        root = _read_part(filled)
        text = _joined_text(root)
        self.assertIn(" Jane Doe", text)
        self.assertIn(" School of Engineering", text)
        self.assertNotIn("{{", text)
        self.assertTrue(_first_run_has_bold(root))
        self.assertTrue(_space_preserve_on_value(root, "Jane Doe"))

    def test_character_split_matricula(self):
        body = """
        <w:p>
          <w:r><w:t>{</w:t></w:r>
          <w:r><w:t>{</w:t></w:r>
          <w:r><w:t>Matricula</w:t></w:r>
          <w:r><w:t>}</w:t></w:r>
          <w:r><w:t>}</w:t></w:r>
        </w:p>
        """
        raw = _pack_docx(**{"word/document.xml": _doc(body)})
        filled = merge_docx(raw, {"Matricula": "12345678"})
        self.assertEqual(_joined_text(_read_part(filled)), "12345678")

    def test_intact_unidad_alongside_split_runs(self):
        body = """
        <w:p>
          <w:r><w:t>{{Unidad}}</w:t></w:r>
          <w:r><w:t> / </w:t></w:r>
          <w:r><w:t>{{</w:t></w:r>
          <w:r><w:t>School</w:t></w:r>
          <w:r><w:t>}}</w:t></w:r>
        </w:p>
        """
        raw = _pack_docx(**{"word/document.xml": _doc(body)})
        filled = merge_docx(
            raw,
            {"Unidad": "Campus North", "School": "School of Engineering"},
        )
        self.assertEqual(
            _joined_text(_read_part(filled)),
            "Campus North / School of Engineering",
        )

    def test_multiple_placeholders_and_adjacent_tokens_sharing_wt(self):
        body = """
        <w:p>
          <w:r><w:t>{{FirstName}}{{LastName}}</w:t></w:r>
          <w:r><w:t> </w:t></w:r>
          <w:r><w:t>{{Email}}</w:t></w:r>
        </w:p>
        """
        raw = _pack_docx(**{"word/document.xml": _doc(body)})
        filled = merge_docx(
            raw,
            {
                "FirstName": "Jane",
                "LastName": "Doe",
                "Email": "jane.doe@example.edu",
            },
        )
        self.assertEqual(
            _joined_text(_read_part(filled)),
            "JaneDoe jane.doe@example.edu",
        )

    def test_split_placeholder_in_table_header_footer_and_textbox(self):
        body = """
        <w:tbl>
          <w:tr>
            <w:tc>
              <w:p>
                <w:r><w:t>{{</w:t></w:r>
                <w:r><w:t>FullName</w:t></w:r>
                <w:r><w:t>}}</w:t></w:r>
              </w:p>
            </w:tc>
          </w:tr>
        </w:tbl>
        <w:p>
          <w:r>
            <w:pict>
              <w:txbxContent>
                <w:p>
                  <w:r><w:t>{{</w:t></w:r>
                  <w:r><w:t>School</w:t></w:r>
                  <w:r><w:t>}}</w:t></w:r>
                </w:p>
              </w:txbxContent>
            </w:pict>
          </w:r>
        </w:p>
        """
        header = """
        <w:p>
          <w:r><w:t>{{</w:t></w:r>
          <w:r><w:t>Matricula</w:t></w:r>
          <w:r><w:t>}}</w:t></w:r>
        </w:p>
        """
        footer = """
        <w:p>
          <w:r><w:t>{{</w:t></w:r>
          <w:r><w:t>Email</w:t></w:r>
          <w:r><w:t>}}</w:t></w:r>
        </w:p>
        """
        raw = _pack_docx(
            **{
                "word/document.xml": _doc(body),
                "word/header1.xml": _header(header),
                "word/footer1.xml": _footer(footer),
            }
        )
        filled = merge_docx(
            raw,
            {
                "FullName": "Jane Doe",
                "School": "School of Engineering",
                "Matricula": "12345678",
                "Email": "jane.doe@example.edu",
            },
        )
        doc_text = _joined_text(_read_part(filled, "word/document.xml"))
        header_text = _joined_text(_read_part(filled, "word/header1.xml"))
        footer_text = _joined_text(_read_part(filled, "word/footer1.xml"))
        self.assertIn("Jane Doe", doc_text)
        self.assertIn("School of Engineering", doc_text)
        self.assertEqual(header_text, "12345678")
        self.assertEqual(footer_text, "jane.doe@example.edu")
        self.assertNotIn("{{", doc_text + header_text + footer_text)


class CaseInsensitiveLookupTests(SimpleTestCase):
    def test_placeholder_case_insensitive_resolution(self):
        body = """
        <w:p>
          <w:r><w:t>{{matricula}}</w:t></w:r>
          <w:r><w:t> </w:t></w:r>
          <w:r><w:t>{{FULLNAME}}</w:t></w:r>
        </w:p>
        """
        raw = _pack_docx(**{"word/document.xml": _doc(body)})
        filled = merge_docx(
            raw,
            {"Matricula": "12345678", "FullName": "Jane Doe"},
        )
        self.assertEqual(_joined_text(_read_part(filled)), "12345678 Jane Doe")

    def test_mergefield_case_insensitive_resolution(self):
        body = """
        <w:p>
          <w:fldSimple w:instr=" MERGEFIELD matricula ">
            <w:r><w:t>«matricula»</w:t></w:r>
          </w:fldSimple>
        </w:p>
        <w:p>
          <w:r><w:fldChar w:fldCharType="begin"/></w:r>
          <w:r><w:instrText xml:space="preserve"> MERGEFIELD fullname </w:instrText></w:r>
          <w:r><w:fldChar w:fldCharType="separate"/></w:r>
          <w:r><w:t>«FullName»</w:t></w:r>
          <w:r><w:fldChar w:fldCharType="end"/></w:r>
        </w:p>
        """
        raw = _pack_docx(**{"word/document.xml": _doc(body)})
        filled = merge_docx(
            raw,
            {"Matricula": "12345678", "FullName": "Jane Doe"},
        )
        text = _joined_text(_read_part(filled))
        self.assertIn("12345678", text)
        self.assertIn("Jane Doe", text)
        self.assertNotIn("MERGEFIELD", text)


class DocxHasFillableFieldsTests(SimpleTestCase):
    def test_detects_only_split_run_placeholders(self):
        # Character-split braces so raw XML has no intact "{{Name}}" for the
        # fast path; paragraph-concatenated w:t text still matches.
        body = """
        <w:p>
          <w:r><w:t>{</w:t></w:r>
          <w:r><w:t>{</w:t></w:r>
          <w:r><w:t>FullName</w:t></w:r>
          <w:r><w:t>}</w:t></w:r>
          <w:r><w:t>}</w:t></w:r>
        </w:p>
        """
        raw = _pack_docx(**{"word/document.xml": _doc(body)})
        raw_text = raw.decode("utf-8", errors="ignore")
        self.assertIsNone(re.search(r"\{\{[A-Za-z]", raw_text))
        self.assertIsNone(re.search(r"MERGEFIELD", raw_text, re.IGNORECASE))
        self.assertTrue(docx_has_fillable_fields(raw))

    def test_blank_docx_has_no_fillable_fields(self):
        raw = _blank_docx()
        self.assertFalse(docx_has_fillable_fields(raw))
