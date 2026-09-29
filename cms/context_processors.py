"""CMS template context for uadec.mx-inspired static assets."""

from __future__ import annotations

from cms.utils.official_assets import (
    CGRI_SERVICE_CAROUSEL,
    HOMEPAGE_SLIDE_ALT,
    SERVICE_CARDS,
    images_dir,
    load_manifest,
)


def _international_base_url() -> str:
    try:
        from cms.models import InternationalHomePage

        page = InternationalHomePage.objects.live().first()
        if page:
            return page.url
    except Exception:
        pass
    return "/internacional/"


def _slides_from_manifest(manifest: dict) -> tuple[list, list, list, bool, bool]:
    base_url = manifest.get("international_base_url") or _international_base_url()
    cgri = []
    for item in manifest.get("cgri_carousel", []):
        cgri.append(
            {
                "title": item["title"],
                "alt": item.get("alt", item["title"]),
                "static_path": item["static_path"],
                "webp_path": item.get("webp_path"),
                "url": f"{base_url}{item['url_suffix']}",
                "width": item.get("width", 1200),
                "height": item.get("height", 400),
            }
        )
    homepage = []
    for item in manifest.get("homepage_slides", []):
        homepage.append(
            {
                "static_path": item["static_path"],
                "webp_path": item.get("webp_path"),
                "alt": item.get("alt", "Universidad Autónoma de Coahuila"),
                "width": item.get("width", 1920),
                "height": item.get("height", 420),
            }
        )
    service_cards = []
    for item in manifest.get("service_cards", []):
        service_cards.append(
            {
                "title": item["title"],
                "alt": item.get("alt", item["title"]),
                "static_path": item["static_path"],
                "webp_path": item.get("webp_path"),
                "url": f"{base_url}{item['url_suffix']}",
                "icon": item.get("icon", "bi-image"),
                "width": item.get("width", 400),
                "height": item.get("height", 140),
            }
        )
    return (
        cgri,
        homepage,
        service_cards,
        bool(cgri),
        bool(homepage),
    )


def _slides_from_filesystem() -> tuple[list, list, list, bool, bool]:
    """Fallback when manifest.json has not been generated yet."""
    img_dir = images_dir()
    base_url = _international_base_url()
    cgri = []
    for item in CGRI_SERVICE_CAROUSEL:
        path = img_dir / item["image"]
        if not path.exists():
            continue
        webp = img_dir / f"{path.stem}.webp"
        cgri.append(
            {
                "title": item["title"],
                "alt": item["title"],
                "static_path": f"uadec/images/{item['image']}",
                "webp_path": f"uadec/images/{webp.name}" if webp.exists() else None,
                "url": f"{base_url}{item['url_suffix']}",
                "width": 1200,
                "height": 400,
            }
        )
    homepage = []
    for path in sorted(img_dir.glob("homepage-slide-*.png")):
        webp = path.with_suffix(".webp")
        homepage.append(
            {
                "static_path": f"uadec/images/{path.name}",
                "webp_path": f"uadec/images/{webp.name}" if webp.exists() else None,
                "alt": HOMEPAGE_SLIDE_ALT.get(path.name, "Universidad Autónoma de Coahuila"),
                "width": 1920,
                "height": 420,
            }
        )
    service_cards = []
    for item in SERVICE_CARDS:
        path = img_dir / item["image"]
        if not path.exists():
            continue
        webp = img_dir / f"{path.stem}.webp"
        service_cards.append(
            {
                "title": item["title"],
                "alt": item["title"],
                "static_path": f"uadec/images/{item['image']}",
                "webp_path": f"uadec/images/{webp.name}" if webp.exists() else None,
                "url": f"{base_url}{item['url_suffix']}",
                "icon": item["icon"],
                "width": 400,
                "height": 140,
            }
        )
    return cgri, homepage, service_cards, bool(cgri), bool(homepage)


def uadec_cms_assets(request):
    """Expose downloaded CGRI carousel slides and homepage hero slides if present."""
    manifest = load_manifest()
    if manifest:
        cgri, homepage, service_cards, has_cgri, has_homepage = _slides_from_manifest(
            manifest
        )
    else:
        cgri, homepage, service_cards, has_cgri, has_homepage = _slides_from_filesystem()

    return {
        "cgri_carousel_slides": cgri,
        "homepage_slides": homepage,
        "cms_service_cards": service_cards,
        "has_cgri_carousel": has_cgri,
        "has_homepage_slides": has_homepage,
    }


def refresh_cms_assets_manifest():
    """Rebuild manifest after asset sync (called from management command)."""
    from cms.utils.official_assets import write_manifest

    return write_manifest(_international_base_url())
