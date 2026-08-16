#!/usr/bin/env python
"""Backward-compatible entry point for institution asset download.

UAdeC remains the default source. Prefer:

    python scripts/download_institution_assets.py

Configure INSTITUTION_WEBSITE, INSTITUTION_ASSET_DIR, and related env vars.
See documentation/white_labeling.md.
"""

import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(
        str(
            Path(__file__).resolve().parent
            / "scripts"
            / "download_institution_assets.py"
        ),
        run_name="__main__",
    )
