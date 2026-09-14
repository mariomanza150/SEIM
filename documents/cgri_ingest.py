"""Ingest official CGRI binaries from SAMPLES/ into Wagtail + DocumentType templates."""

from __future__ import annotations

from pathlib import Path

from django.apps import apps
from django.core.files import File

from cms.cgri_samples import (
    CGRI_COLLECTION_NAME,
    CGRI_OFFICIAL_TAG,
    CGRI_SAMPLE_SPECS,
    key_tag,
    samples_dir,
)
from documents.mobility_document_catalog import seed_mobility_document_types
from documents.models import DocumentType
from exchange.cgri_partner_catalog import seed_official_university_lists
from exchange.mobility_schemes import seed_mobility_schemes


def _wagtail_available() -> bool:
    return apps.is_installed("wagtail.documents") and apps.is_installed("cms")


def ingest_cgri_samples(
    *,
    skip_universities: bool = False,
    skip_wagtail: bool = False,
    skip_templates: bool = False,
    stdout=None,
) -> dict[str, int]:
    """
    Upload SAMPLES files, attach DocumentType templates, seed university lists.

    Returns counts: wagtail, templates, missing, institutions, agreements.
    """

    def _write(msg: str):
        if stdout is not None:
            stdout.write(msg)

    base = samples_dir()
    result = {
        "wagtail": 0,
        "templates": 0,
        "missing": 0,
        "institutions": 0,
        "agreements": 0,
    }

    if not base.is_dir():
        _write(f"SAMPLES directory not found at {base}; skipping binary ingest.")
        if not skip_universities:
            seed_mobility_schemes()
            counts = seed_official_university_lists()
            result["institutions"] = counts["institutions"]
            result["agreements"] = counts["agreements"]
            _write(
                f"  universities: {counts['institutions']} institutions, "
                f"{counts['agreements']} new agreements"
            )
        return result

    seed_mobility_document_types()
    do_wagtail = (not skip_wagtail) and _wagtail_available()
    collection = _ensure_collection() if do_wagtail else None
    admin_user = None
    if do_wagtail:
        from accounts.models import User

        admin_user = User.objects.filter(is_superuser=True).first()

    for spec in CGRI_SAMPLE_SPECS:
        path = base / spec["filename"]
        if not path.is_file():
            result["missing"] += 1
            _write(f"  missing: {spec['filename']}")
            continue

        if do_wagtail and collection is not None:
            _upsert_wagtail_document(spec, path, collection, admin_user)
            result["wagtail"] += 1
            _write(f"  wagtail: {spec['key']}")

        slug = spec.get("document_type_slug")
        if slug and not skip_templates:
            if _attach_template(slug, path):
                result["templates"] += 1
                _write(f"  template: {slug} <- {spec['filename']}")

    _write(
        f"Wagtail upserts: {result['wagtail']}; templates: {result['templates']}; "
        f"missing files: {result['missing']}"
    )

    if not skip_universities:
        seed_mobility_schemes()
        counts = seed_official_university_lists()
        result["institutions"] = counts["institutions"]
        result["agreements"] = counts["agreements"]
        _write(
            f"  universities: {counts['institutions']} institutions, "
            f"{counts['agreements']} new agreements"
        )

    _write("CGRI sample ingest complete.")
    return result


def _ensure_collection():
    from wagtail.models import Collection

    root = Collection.get_first_root_node()
    existing = Collection.objects.filter(name=CGRI_COLLECTION_NAME).first()
    if existing:
        return existing
    collection = Collection(name=CGRI_COLLECTION_NAME)
    root.add_child(instance=collection)
    return collection


def _upsert_wagtail_document(spec, path: Path, collection, admin_user):
    from wagtail.documents.models import Document

    title = spec["title"]
    tag = key_tag(spec["key"])
    doc = (
        Document.objects.filter(tags__name=tag).first()
        or Document.objects.filter(title=title).first()
    )
    if doc is None:
        doc = Document(title=title, collection=collection)
        if admin_user:
            doc.uploaded_by_user = admin_user
        with path.open("rb") as handle:
            doc.file.save(path.name, File(handle), save=False)
        doc.save()
    else:
        doc.title = title
        doc.collection = collection
        with path.open("rb") as handle:
            if doc.file:
                doc.file.delete(save=False)
            doc.file.save(path.name, File(handle), save=False)
        doc.save()

    doc.tags.add(CGRI_OFFICIAL_TAG, tag)
    return doc


def _attach_template(slug: str, path: Path) -> bool:
    doc_type = DocumentType.objects.filter(slug=slug).first()
    if doc_type is None:
        return False
    with path.open("rb") as handle:
        if doc_type.template_file:
            doc_type.template_file.delete(save=False)
        doc_type.template_file.save(path.name, File(handle), save=True)
    return True
