"""Umbrella file-type families (PDF, Image, Word, …) mapped to extensions.

Admins can change mappings in Django admin; this catalog is the seed/default.
"""

from __future__ import annotations

FILE_TYPE_FAMILY_SPECS = (
    {
        "slug": "pdf",
        "name": "PDF",
        "aliases": "portable document, acrobat",
        "extensions": "pdf",
        "sort_order": 10,
    },
    {
        "slug": "image",
        "name": "Image",
        "aliases": "photo, picture, imagen, foto, jpg, jpeg, png, gif, webp, heic",
        "extensions": "jpg,jpeg,png,gif,webp,bmp,tif,tiff,heic,heif",
        "sort_order": 20,
    },
    {
        "slug": "word",
        "name": "Word",
        "aliases": "microsoft word, documento, doc, docx, odt, rtf",
        "extensions": "doc,docx,odt,rtf",
        "sort_order": 30,
    },
    {
        "slug": "spreadsheet",
        "name": "Spreadsheet",
        "aliases": "excel, hoja de cálculo, xls, xlsx, ods, csv",
        "extensions": "xls,xlsx,ods,csv",
        "sort_order": 40,
    },
    {
        "slug": "presentation",
        "name": "Presentation",
        "aliases": "powerpoint, diapositivas, ppt, pptx, odp",
        "extensions": "ppt,pptx,odp",
        "sort_order": 50,
    },
    {
        "slug": "text",
        "name": "Text",
        "aliases": "plain text, markdown, txt, md",
        "extensions": "txt,md",
        "sort_order": 60,
    },
    {
        "slug": "archive",
        "name": "Archive",
        "aliases": "zip, compressed, 7z, rar",
        "extensions": "zip,7z,rar",
        "sort_order": 70,
    },
    {
        "slug": "audio",
        "name": "Audio",
        "aliases": "sound, mp3, wav, m4a",
        "extensions": "mp3,wav,m4a",
        "sort_order": 80,
    },
    {
        "slug": "video",
        "name": "Video",
        "aliases": "movie, mp4, mov, webm",
        "extensions": "mp4,mov,webm",
        "sort_order": 90,
    },
    {
        "slug": "email",
        "name": "Email",
        "aliases": "message, eml, msg, outlook",
        "extensions": "eml,msg",
        "sort_order": 100,
    },
)


def infer_family_slugs_from_extensions(extensions: str | list[str] | None) -> list[str]:
    """Map a comma list of extensions onto family slugs (order preserved)."""
    if isinstance(extensions, str):
        exts = [e.strip().lower().lstrip(".") for e in extensions.split(",") if e.strip()]
    else:
        exts = [str(e).strip().lower().lstrip(".") for e in (extensions or []) if e]
    if not exts:
        return []
    ext_to_slug: dict[str, str] = {}
    for spec in FILE_TYPE_FAMILY_SPECS:
        for ext in spec["extensions"].split(","):
            ext = ext.strip().lower()
            if ext:
                ext_to_slug[ext] = spec["slug"]
    seen: list[str] = []
    for ext in exts:
        slug = ext_to_slug.get(ext)
        if slug and slug not in seen:
            seen.append(slug)
    return seen


def seed_file_type_families():
    """Create/update catalog rows. Returns the queryset ordered for admin/API."""
    from documents.models import FileTypeFamily

    for spec in FILE_TYPE_FAMILY_SPECS:
        FileTypeFamily.objects.update_or_create(
            slug=spec["slug"],
            defaults={
                "name": spec["name"],
                "aliases": spec["aliases"],
                "extensions": spec["extensions"],
                "sort_order": spec["sort_order"],
                "is_active": True,
            },
        )
    return FileTypeFamily.objects.filter(is_active=True).order_by("sort_order", "name")
