"""Tests for uadec CMS asset manifest and context processor."""

import json

import pytest


@pytest.mark.django_db
def test_build_manifest_includes_carousel_metadata(tmp_path, monkeypatch):
    from cms.utils.official_assets import build_manifest

    monkeypatch.setattr(
        "cms.utils.official_assets.images_dir",
        lambda: tmp_path,
    )
    (tmp_path / "cgri-centros-idiomas.jpg").write_bytes(b"jpg")
    (tmp_path / "cgri-centros-idiomas.webp").write_bytes(b"webp")
    (tmp_path / "homepage-slide-1.png").write_bytes(b"png")
    (tmp_path / "homepage-slide-1.webp").write_bytes(b"webp")

    manifest = build_manifest("/internacional/")

    assert manifest["international_base_url"] == "/internacional/"
    assert len(manifest["cgri_carousel"]) == 1
    assert manifest["cgri_carousel"][0]["webp_path"] == "uadec/images/cgri-centros-idiomas.webp"
    assert len(manifest["homepage_slides"]) == 1
    assert manifest["homepage_slides"][0]["alt"].startswith("Vista del campus")
    assert len(manifest["service_cards"]) == 1


@pytest.mark.django_db
def test_slides_from_manifest_builds_urls():
    from cms.context_processors import _slides_from_manifest

    manifest = {
        "international_base_url": "/internacional/",
        "cgri_carousel": [
            {
                "title": "Centros de Idiomas",
                "alt": "Centros de Idiomas",
                "static_path": "uadec/images/cgri-centros-idiomas.jpg",
                "webp_path": "uadec/images/cgri-centros-idiomas.webp",
                "url_suffix": "institucional/centros-de-idiomas/",
                "width": 1200,
                "height": 400,
            }
        ],
        "homepage_slides": [
            {
                "static_path": "uadec/images/homepage-slide-1.png",
                "webp_path": "uadec/images/homepage-slide-1.webp",
                "alt": "Campus 1",
                "width": 1920,
                "height": 420,
            }
        ],
        "service_cards": [],
    }

    cgri, homepage, service_cards, has_cgri, has_homepage = _slides_from_manifest(manifest)

    assert has_cgri is True
    assert has_homepage is True
    assert cgri[0]["url"] == "/internacional/institucional/centros-de-idiomas/"
    assert homepage[0]["webp_path"].endswith(".webp")
    assert service_cards == []


@pytest.mark.django_db
def test_write_manifest_persists_json(tmp_path, monkeypatch):
    from cms.utils.official_assets import write_manifest

    monkeypatch.setattr(
        "cms.utils.official_assets.images_dir",
        lambda: tmp_path,
    )
    (tmp_path / "cgri-movilidad.jpg").write_bytes(b"jpg")

    path = write_manifest("/internacional/")
    data = json.loads(path.read_text(encoding="utf-8"))

    assert path.name == "manifest.json"
    assert data["version"] == 1
    assert any(item["title"] == "Movilidad Internacional" for item in data["cgri_carousel"])
