"""Download official UAdeC CGRI assets for CMS chrome (not committed)."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

import requests
import urllib3
from django.conf import settings
from django.core.files.images import ImageFile
from PIL import Image as PILImage
from wagtail.images.models import Image

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_BASE = "https://www.uadec.mx/wp-content/uploads"
_UPLOADS_2022 = f"{_BASE}/2022/08"

OFFICIAL_ASSETS = {
    "institution-logo.png": f"{_BASE}/2024/08/UAdeC-87x32.png",
    "institution-logo-full.png": f"{_BASE}/2024/08/UAdeC-1.png",
    "cgri-wordmark.png": (
        f"{_UPLOADS_2022}/"
        "Coordinacio%CC%81n-General-de-Relaciones-Internacionales_logo-azul.png"
    ),
    "mi2026.jpg": f"{_BASE}/2026/01/MI2026.jpg",
}

# CGRI service carousel + section photos from uadec.mx/movilidad/
OFFICIAL_IMAGES = {
    "cgri-centros-idiomas.jpg": f"{_UPLOADS_2022}/1CentrosDeIdiomas.jpg",
    "cgri-movilidad.jpg": f"{_UPLOADS_2022}/2MovilidadInternacional.jpg",
    "cgri-asesoria-consular.jpg": (
        f"{_UPLOADS_2022}/3ServiciosDeAsesori%CC%81aConsular.jpg"
    ),
    "cgri-acreditaciones.jpg": (
        f"{_UPLOADS_2022}/4AcreditacionesInternacionales.jpg"
    ),
    "cgri-convenios.jpg": (
        f"{_UPLOADS_2022}/5ConveniosDeCooperacio%CC%81nInternacional.jpg"
    ),
    "cgri-grana.png": f"{_UPLOADS_2022}/GRANA.png",
}

# Homepage hero slides from uadec.mx (campus / institutional photography)
HOMEPAGE_SLIDES = {
    f"homepage-slide-{i}.png": f"{_BASE}/2018/04/{i}.png" for i in range(1, 7)
}

HOMEPAGE_SLIDE_ALT = {
    f"homepage-slide-{i}.png": f"Vista del campus UAdeC {i}"
    for i in range(1, 7)
}

WAGTAIL_TITLES = {
    "institution-logo.png": "UAdeC crest",
    "institution-logo-full.png": "UAdeC logo",
    "cgri-wordmark.png": "CGRI wordmark",
    "mi2026.jpg": "Convocatoria Movilidad Internacional 2026",
    "cgri-centros-idiomas.jpg": "CGRI Centros de Idiomas",
    "cgri-movilidad.jpg": "CGRI Movilidad Internacional",
    "cgri-asesoria-consular.jpg": "CGRI Asesoría Consular",
    "cgri-acreditaciones.jpg": "CGRI Acreditaciones Internacionales",
    "cgri-convenios.jpg": "CGRI Convenios de Cooperación",
    "cgri-grana.png": "CGRI GRANA",
    **{name: f"UAdeC homepage slide {i}" for i, name in enumerate(HOMEPAGE_SLIDES, 1)},
}

# Carousel metadata mirroring uadec.mx/movilidad quick links
CGRI_SERVICE_CAROUSEL = (
    {
        "image": "cgri-centros-idiomas.jpg",
        "title": "Centros de Idiomas",
        "url_suffix": "institucional/centros-de-idiomas/",
    },
    {
        "image": "cgri-movilidad.jpg",
        "title": "Movilidad Internacional",
        "url_suffix": "movilidad-estudiantil/",
    },
    {
        "image": "cgri-asesoria-consular.jpg",
        "title": "Asesoría Consular",
        "url_suffix": "institucional/asesoria-consular/",
    },
    {
        "image": "cgri-acreditaciones.jpg",
        "title": "Acreditaciones Internacionales",
        "url_suffix": "institucional/acreditaciones/",
    },
    {
        "image": "cgri-convenios.jpg",
        "title": "Convenios de Cooperación",
        "url_suffix": "institucional/convenios/",
    },
)

SERVICE_CARDS = (
    {
        "image": "cgri-centros-idiomas.jpg",
        "title": "Centros de idiomas",
        "url_suffix": "institucional/centros-de-idiomas/",
        "icon": "bi-translate",
    },
    {
        "image": "cgri-asesoria-consular.jpg",
        "title": "Asesoría consular",
        "url_suffix": "institucional/asesoria-consular/",
        "icon": "bi-passport",
    },
    {
        "image": "cgri-acreditaciones.jpg",
        "title": "Acreditaciones",
        "url_suffix": "institucional/acreditaciones/",
        "icon": "bi-award",
    },
    {
        "image": "cgri-convenios.jpg",
        "title": "Convenios",
        "url_suffix": "institucional/convenios/",
        "icon": "bi-handshake",
    },
)

MANIFEST_FILENAME = "manifest.json"
CGRI_MAX_WIDTH = 1200
CGRI_JPEG_QUALITY = 80
HOMEPAGE_WEBP_QUALITY = 82


def branding_dir() -> Path:
    return Path(settings.BASE_DIR) / "branding" / "uadec"


def logos_dir() -> Path:
    return branding_dir() / "logos"


def images_dir() -> Path:
    return branding_dir() / "images"


def manifest_path() -> Path:
    return images_dir() / MANIFEST_FILENAME


def _webp_name(filename: str) -> str:
    stem = Path(filename).stem
    return f"{stem}.webp"


def optimize_cgri_image(path: Path) -> tuple[Path, Path | None]:
    """Resize/compress a CGRI JPG and emit a WebP sibling."""
    with PILImage.open(path) as img:
        img = img.convert("RGB")
        if img.width > CGRI_MAX_WIDTH:
            ratio = CGRI_MAX_WIDTH / img.width
            new_size = (CGRI_MAX_WIDTH, int(img.height * ratio))
            img = img.resize(new_size, PILImage.Resampling.LANCZOS)
        img.save(path, format="JPEG", quality=CGRI_JPEG_QUALITY, optimize=True)
        webp_path = path.with_suffix(".webp")
        img.save(webp_path, format="WEBP", quality=CGRI_JPEG_QUALITY, method=6)
        return path, webp_path


def optimize_homepage_slide(path: Path) -> tuple[Path, Path]:
    """Keep PNG fallback and write a WebP variant."""
    with PILImage.open(path) as img:
        webp_path = path.with_suffix(".webp")
        img.save(webp_path, format="WEBP", quality=HOMEPAGE_WEBP_QUALITY, method=6)
        return path, webp_path


def optimize_downloaded_assets(saved: dict[str, Path]) -> None:
    """Post-process downloaded CMS images for size and WebP variants."""
    for filename, path in saved.items():
        if filename.startswith("cgri-") and filename.endswith(".jpg"):
            optimize_cgri_image(path)
        elif filename.startswith("homepage-slide-") and filename.endswith(".png"):
            optimize_homepage_slide(path)


def _static_path(filename: str) -> str:
    return f"uadec/images/{filename}"


def build_manifest(international_base_url: str = "/internacional/") -> dict:
    """Build manifest from files present on disk."""
    img_dir = images_dir()
    cgri_carousel = []
    for item in CGRI_SERVICE_CAROUSEL:
        path = img_dir / item["image"]
        if not path.exists():
            continue
        webp = img_dir / _webp_name(item["image"])
        entry = {
            "title": item["title"],
            "alt": item["title"],
            "static_path": _static_path(item["image"]),
            "url_suffix": item["url_suffix"],
            "width": 1200,
            "height": 400,
        }
        if webp.exists():
            entry["webp_path"] = _static_path(webp.name)
        cgri_carousel.append(entry)

    homepage_slides = []
    for filename in sorted(HOMEPAGE_SLIDES):
        path = img_dir / filename
        if not path.exists():
            continue
        webp = img_dir / _webp_name(filename)
        entry = {
            "static_path": _static_path(filename),
            "alt": HOMEPAGE_SLIDE_ALT.get(filename, "Universidad Autónoma de Coahuila"),
            "width": 1920,
            "height": 420,
        }
        if webp.exists():
            entry["webp_path"] = _static_path(webp.name)
        homepage_slides.append(entry)

    service_cards = []
    for item in SERVICE_CARDS:
        path = img_dir / item["image"]
        if not path.exists():
            continue
        webp = img_dir / _webp_name(item["image"])
        entry = {
            "title": item["title"],
            "alt": item["title"],
            "static_path": _static_path(item["image"]),
            "url_suffix": item["url_suffix"],
            "icon": item["icon"],
            "width": 400,
            "height": 140,
        }
        if webp.exists():
            entry["webp_path"] = _static_path(webp.name)
        service_cards.append(entry)

    return {
        "version": 1,
        "international_base_url": international_base_url,
        "cgri_carousel": cgri_carousel,
        "homepage_slides": homepage_slides,
        "service_cards": service_cards,
    }


def write_manifest(international_base_url: str = "/internacional/") -> Path:
    """Write manifest.json for template context (avoids per-request glob)."""
    img_dir = images_dir()
    img_dir.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest(international_base_url)
    dest = manifest_path()
    dest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return dest


def load_manifest() -> dict | None:
    """Load manifest.json if present."""
    path = manifest_path()
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _download_assets(
    asset_map: dict[str, str], output: Path, timeout: int = 20
) -> dict[str, Path]:
    output.mkdir(parents=True, exist_ok=True)
    saved: dict[str, Path] = {}
    for filename, url in asset_map.items():
        dest = output / filename
        response = requests.get(
            url, timeout=timeout, allow_redirects=True, verify=False
        )
        response.raise_for_status()
        dest.write_bytes(response.content)
        saved[filename] = dest
    return saved


def download_official_assets(timeout: int = 20) -> dict[str, Path]:
    """Save official logos under branding/uadec/logos/. Returns saved paths."""
    return _download_assets(OFFICIAL_ASSETS, logos_dir(), timeout)


def download_cms_images(timeout: int = 20) -> dict[str, Path]:
    """Save CGRI section photos under branding/uadec/images/."""
    return _download_assets(OFFICIAL_IMAGES, images_dir(), timeout)


def download_homepage_slides(timeout: int = 20) -> dict[str, Path]:
    """Save uadec.mx homepage hero slides under branding/uadec/images/."""
    return _download_assets(HOMEPAGE_SLIDES, images_dir(), timeout)


def download_all_cms_assets(timeout: int = 20) -> dict[str, Path]:
    """Download logos, CGRI photos, and homepage slides."""
    saved = download_official_assets(timeout)
    saved.update(download_cms_images(timeout))
    saved.update(download_homepage_slides(timeout))
    optimize_downloaded_assets(saved)
    return saved


def get_or_create_wagtail_image(filename: str, path: Path) -> Image:
    """Create or refresh a Wagtail image from a local official asset file."""
    title = WAGTAIL_TITLES.get(filename, filename)
    existing = Image.objects.filter(title=title).first()
    with path.open("rb") as handle:
        image_file = ImageFile(BytesIO(handle.read()), name=filename)
        if existing:
            existing.file.delete(save=False)
            existing.file.save(filename, image_file, save=True)
            return existing
        image = Image(title=title)
        image.file.save(filename, image_file, save=True)
        return image
