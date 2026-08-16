#!/usr/bin/env python
"""Backward-compatible entry point for institution asset download.

Prefer::

    python scripts/download_institution_assets.py

Reads tenant_config.json / INSTITUTION_* env vars. UAdeC is only the fallback
when no tenant overlay is present. See docs/white_labeling.md.
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
