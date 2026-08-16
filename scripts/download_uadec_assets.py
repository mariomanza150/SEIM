#!/usr/bin/env python
"""Backward-compatible name. Delegates to download_institution_assets.py."""

import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(
        str(Path(__file__).resolve().parent / "download_institution_assets.py"),
        run_name="__main__",
    )
