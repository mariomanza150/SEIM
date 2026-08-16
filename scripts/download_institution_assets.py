#!/usr/bin/env python
"""Download institution logos/assets. UAdeC is the default source."""

from __future__ import annotations

import os
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_WEBSITE = "https://www.uadec.mx/"
DEFAULT_ASSET_PATHS = (
    "/images/logo.png",
    "/images/logo-uadec.png",
    "/img/logo.png",
    "/img/logo-uadec.png",
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


def _website() -> str:
    url = _env("INSTITUTION_WEBSITE", DEFAULT_WEBSITE)
    return url if url.endswith("/") else f"{url}/"


def _output_dir() -> Path:
    path = Path(_env("INSTITUTION_ASSET_DIR", "staticfiles/images"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def _ssl_verify() -> bool:
    return _bool_env("INSTITUTION_ASSET_SSL_VERIFY", False)


def _logo_filename() -> str:
    return _env("INSTITUTION_LOGO_FILENAME", "institution-logo.png")


def _compat_filename() -> str:
    return _env("INSTITUTION_LOGO_COMPAT_FILENAME", "uadec-logo.png")


def _asset_paths() -> list[str]:
    extra = _env("INSTITUTION_ASSET_PATHS", "")
    if extra:
        return [p.strip() for p in extra.split(",") if p.strip()]
    return list(DEFAULT_ASSET_PATHS)


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
    website = _website()
    output_dir = _output_dir()
    verify = _ssl_verify()
    logo_name = _logo_filename()
    compat_name = _compat_filename()
    short_name = _env("INSTITUTION_SHORT_NAME", "UAdeC")

    print("=" * 60)
    print(f"{short_name} asset downloader")
    print("=" * 60)

    print("\n1. Trying common logo paths...")
    downloaded = False
    for asset_path in _asset_paths():
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
    print("=" * 60)


if __name__ == "__main__":
    main()
