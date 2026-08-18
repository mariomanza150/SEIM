"""Download official UAdeC CGRI assets for CMS chrome (not committed)."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import requests
import urllib3
from django.conf import settings
from django.core.files.images import ImageFile
from wagtail.images.models import Image

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

OFFICIAL_ASSETS = {
    "institution-logo.png": (
        "https://www.uadec.mx/wp-content/uploads/2024/08/UAdeC-87x32.png"
    ),
    "cgri-wordmark.png": (
        "http://www.uadec.mx/wp-content/uploads/2022/08/"
        "Coordinacio%CC%81n-General-de-Relaciones-Internacionales_logo-azul.png"
    ),
    "mi2026.jpg": "https://www.uadec.mx/wp-content/uploads/2026/01/MI2026.jpg",
}

WAGTAIL_TITLES = {
    "institution-logo.png": "UAdeC crest",
    "cgri-wordmark.png": "CGRI wordmark",
    "mi2026.jpg": "Convocatoria Movilidad Internacional 2026",
}


def logos_dir() -> Path:
    return Path(settings.BASE_DIR) / "branding" / "uadec" / "logos"


def download_official_assets(timeout: int = 20) -> dict[str, Path]:
    """Save official logos under branding/uadec/logos/. Returns saved paths."""
    output = logos_dir()
    output.mkdir(parents=True, exist_ok=True)
    saved: dict[str, Path] = {}
    for filename, url in OFFICIAL_ASSETS.items():
        dest = output / filename
        response = requests.get(
            url, timeout=timeout, allow_redirects=True, verify=False
        )
        response.raise_for_status()
        dest.write_bytes(response.content)
        saved[filename] = dest
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
