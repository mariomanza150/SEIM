#!/usr/bin/env python
"""Download institution logos/assets from tenant/branding config or env vars.

Reads tenant_config.json, branding overlays, and INSTITUTION_* env vars.
UAdeC URLs are the packaged fallback when no tenant config is set.
Prefer this script over download_uadec_assets.py.
Default output: branding/<slug>/logos. See docs/white_labeling.md.

Do not commit downloaded university logos. Keep branding/<slug>/logos/.gitkeep.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.branding import DEFAULT_INSTITUTION, DEFAULT_SLUG, merge_institution_config  # noqa: E402, I001

DEFAULT_WEBSITE = DEFAULT_INSTITUTION["INSTITUTION_WEBSITE"]
GENERIC_ASSET_PATHS = (
    "/images/logo.png",
    "/img/logo.png",
    "/assets/img/logo.png",
    "/assets/images/logo.png",
    "/static/img/logo.png",
    "/static/images/logo.png",
)


def _env(name: str, default: str) -> str:
    value = os.environ.get(name)
    return value if value not in (None, "") else default


def _bool_env(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def load_asset_config(base_dir: Path | None = None) -> dict[str, str]:
    """Merge branding JSON + env overrides for the downloader."""
    root = Path(base_dir) if base_dir else ROOT
    merged = merge_institution_config(root)
    slug = _env("INSTITUTION_SLUG", merged.get("INSTITUTION_SLUG") or DEFAULT_SLUG)
    website = _env(
        "INSTITUTION_WEBSITE", merged.get("INSTITUTION_WEBSITE") or DEFAULT_WEBSITE
    )
    if not website.endswith("/"):
        website = f"{website}/"
    return {
        "slug": slug,
        "short_name": _env(
            "INSTITUTION_SHORT_NAME", merged.get("INSTITUTION_SHORT_NAME") or slug
        ),
        "website": website,
        "asset_dir": _env("INSTITUTION_ASSET_DIR", f"branding/{slug}/logos"),
        "logo_filename": _env("INSTITUTION_LOGO_FILENAME", "institution-logo.png"),
        "compat_filename": _env(
            "INSTITUTION_LOGO_COMPAT_FILENAME",
            "uadec-logo.png" if slug.lower() == DEFAULT_SLUG else "",
        ),
        "asset_paths": _env("INSTITUTION_ASSET_PATHS", ""),
    }


def _asset_paths(config: dict[str, str]) -> list[str]:
    extra = config.get("asset_paths") or ""
    if extra:
        return [p.strip() for p in extra.split(",") if p.strip()]
    slug = config.get("slug") or DEFAULT_SLUG
    paths = list(GENERIC_ASSET_PATHS)
    paths.extend(
        (
            f"/images/logo-{slug}.png",
            f"/img/logo-{slug}.png",
        )
    )
    return paths


def download_asset(url: str, filename: str, output_dir: Path, verify: bool) -> bool:
    """Download a single asset."""
    try:
        print(f"Trying to download: {url}")
        response = requests.get(url, timeout=10, allow_redirects=True, verify=verify)

        if response.status_code == 200:
            output_path = output_dir / filename
            output_path.write_bytes(response.content)
            print(f"Downloaded: {filename} ({len(response.content)} bytes)")
            return True
        print(f"Failed: Status {response.status_code}")
        return False
    except Exception as exc:
        print(f"Error: {exc}")
        return False


def scrape_page_for_images(website: str, output_dir: Path, verify: bool) -> None:
    """Scrape the institution homepage to find logo images."""
    try:
        print(f"\nFetching homepage: {website}")
        response = requests.get(website, timeout=10, verify=verify)
        if response.status_code != 200:
            return

        host_token = urlparse(website).netloc.split(".")[0]
        patterns = [
            r'<img[^>]+src=["\']([^"\']*logo[^"\']*)["\']',
            rf'<img[^>]+src=["\']([^"\']*{re.escape(host_token)}[^"\']*)["\']',
            r'background-image:\s*url\(["\']([^"\']*logo[^"\']*)["\']',
        ]

        found_urls: set[str] = set()
        for pattern in patterns:
            found_urls.update(re.findall(pattern, response.text, re.IGNORECASE))

        print(f"Found {len(found_urls)} potential image URLs")
        for i, img_url in enumerate(found_urls):
            if not img_url.startswith("http"):
                img_url = urljoin(website, img_url)
            suffix = Path(urlparse(img_url).path).suffix or ".png"
            download_asset(
                img_url, f"institution-asset-{i + 1}{suffix}", output_dir, verify
            )
    except Exception as exc:
        print(f"Error scraping page: {exc}")


def main() -> None:
    config = load_asset_config()
    output_dir = Path(config["asset_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    verify = _bool_env("INSTITUTION_ASSET_SSL_VERIFY", False)
    logo_name = config["logo_filename"]
    compat_name = config["compat_filename"]
    short_name = config["short_name"]
    website = config["website"]

    print("=" * 60)
    print(f"{short_name} asset downloader")
    print("=" * 60)

    print("\n1. Trying common logo paths...")
    downloaded = False
    for asset_path in _asset_paths(config):
        url = urljoin(website, asset_path)
        if download_asset(url, logo_name, output_dir, verify):
            downloaded = True
            break

    if downloaded and compat_name and compat_name != logo_name:
        src = output_dir / logo_name
        dest = output_dir / compat_name
        if src.exists():
            dest.write_bytes(src.read_bytes())
            print(f"Also saved compatibility copy: {compat_name}")

    print("\n2. Scraping homepage for images...")
    scrape_page_for_images(website, output_dir, verify)

    print("\n" + "=" * 60)
    print(f"Assets saved to: {output_dir.resolve()}")
    print("Do not commit copyrighted logos. Keep logos/.gitkeep only.")
    print("=" * 60)


if __name__ == "__main__":
    main()
