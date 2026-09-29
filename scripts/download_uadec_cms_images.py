#!/usr/bin/env python
"""Download uadec.mx CMS inspiration images (logos, CGRI photos, homepage slides).

Official assets from https://www.uadec.mx/ and https://www.uadec.mx/movilidad/
are saved locally under branding/uadec/ and are not committed to git.

After download, run inside Django:
    python manage.py sync_uadec_cms_assets
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seim.settings.development")

import django  # noqa: E402

django.setup()

from cms.utils.official_assets import (  # noqa: E402
    download_all_cms_assets,
    images_dir,
    logos_dir,
)


def main() -> None:
    print("=" * 60)
    print("UAdeC CMS asset downloader")
    print("Sources: uadec.mx, uadec.mx/movilidad")
    print("=" * 60)
    saved = download_all_cms_assets()
    print(f"\nLogos:  {logos_dir()}")
    print(f"Images: {images_dir()}")
    print(f"Saved {len(saved)} files.")
    print("\nNext: python manage.py sync_uadec_cms_assets")
    print("=" * 60)


if __name__ == "__main__":
    main()
