"""
Programmatic UI screenshots via Playwright.

Captures a small route set for the Vue SPA served under /seim/.

Usage (PowerShell):
  $env:BASE_URL="http://localhost:8001/seim"
  $env:API_URL="http://localhost:8001"
  $env:SEIM_EMAIL="student1@example.com"
  $env:SEIM_PASSWORD="student123"
  python scripts\\take_screenshots_playwright.py

Notes:
  - If SEIM_EMAIL/SEIM_PASSWORD are not set, the script runs unauthenticated (screenshots may be login page).
  - Output goes to tests/e2e_playwright/screenshots/manual by default.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from playwright.sync_api import sync_playwright

# Allow running as a standalone script from repo root.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tests.e2e_playwright.utils.screenshot_manager import ScreenshotManager  # noqa: E402
from tests.e2e_playwright.utils.vue_auth_helpers import login_vue_via_jwt  # noqa: E402


@dataclass(frozen=True)
class Viewport:
    name: str
    width: int
    height: int
    is_mobile: bool = False
    has_touch: bool = False


DEFAULT_VIEWPORTS: tuple[Viewport, ...] = (
    Viewport(name="desktop_1440x900", width=1440, height=900),
    Viewport(name="mobile_390x844", width=390, height=844, is_mobile=True, has_touch=True),
)

DEFAULT_ROUTES: tuple[str, ...] = (
    "/login",
    "/dashboard",
    "/applications",
    "/documents",
    "/notifications",
    "/settings",
    "/calendar",
)


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "page"


def _normalize_base_url(base_url: str) -> str:
    base_url = base_url.strip().rstrip("/")
    if base_url.endswith("/seim"):
        return base_url
    if base_url.endswith("/seim/"):
        return base_url[:-1]
    # If user passed host root, default to /seim
    if "/seim" not in base_url:
        return f"{base_url}/seim"
    return base_url


def _iter_routes(routes: Iterable[str]) -> Iterable[str]:
    for r in routes:
        r = str(r).strip()
        if not r:
            continue
        if not r.startswith("/"):
            r = "/" + r
        yield r


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Take SEIM UI screenshots via Playwright.")
    p.add_argument(
        "--auth",
        action="store_true",
        help="Attempt JWT login before capturing (requires SEIM_PASSWORD and SEIM_EMAIL or SEIM_USERNAME).",
    )
    p.add_argument(
        "--no-auth",
        action="store_true",
        help="Never attempt login (always capture as guest).",
    )
    p.add_argument(
        "--base-url",
        default=os.environ.get("BASE_URL", "http://localhost:8001/seim"),
        help="Base URL for the Vue SPA (default: env BASE_URL or http://localhost:8001/seim).",
    )
    p.add_argument(
        "--routes",
        default=os.environ.get("SCREENSHOT_ROUTES", ""),
        help="Comma-separated routes (default: env SCREENSHOT_ROUTES or built-in set).",
    )
    p.add_argument(
        "--out-dir",
        default=os.environ.get("SCREENSHOT_DIR", "tests/e2e_playwright/screenshots/manual"),
        help="Output directory for PNGs.",
    )
    return p.parse_args()


def main() -> int:
    args = _parse_args()

    base_url = _normalize_base_url(args.base_url)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    email = os.environ.get("SEIM_EMAIL")
    password = os.environ.get("SEIM_PASSWORD")
    username = os.environ.get("SEIM_USERNAME")
    if not email and username:
        email = username if "@" in username else f"{username}@example.com"
    headless = os.environ.get("HEADLESS", "true").lower() == "true"

    routes = tuple(_iter_routes(str(args.routes).split(","))) or DEFAULT_ROUTES
    screenshot_manager = ScreenshotManager(str(out_dir))

    # Auth decision:
    # - If --no-auth: never login.
    # - Else if --auth: try login (and fall back on failure).
    # - Else (default): only login if explicit env SCREENSHOT_AUTH=1 is set.
    auth_requested = False
    if args.no_auth:
        auth_requested = False
    elif args.auth:
        auth_requested = True
    else:
        auth_requested = os.environ.get("SCREENSHOT_AUTH") == "1"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        try:
            for vp in DEFAULT_VIEWPORTS:
                context = browser.new_context(
                    viewport={"width": vp.width, "height": vp.height},
                    is_mobile=vp.is_mobile,
                    has_touch=vp.has_touch,
                    ignore_https_errors=True,
                )
                page = context.new_page()
                page.set_default_timeout(30_000)

                # Optional login (JWT tokens in localStorage)
                if auth_requested:
                    if not (email and password):
                        print(
                            "Auth requested but missing credentials. "
                            "Set SEIM_PASSWORD and either SEIM_EMAIL or SEIM_USERNAME. Continuing as guest.",
                            file=sys.stderr,
                        )
                    else:
                        try:
                            login_vue_via_jwt(page, base_url, email, password)
                        except AssertionError as e:
                            print(f"Auth failed ({e}). Continuing as guest.", file=sys.stderr)

                for route in routes:
                    url = f"{base_url}{route}"
                    page.goto(url, wait_until="domcontentloaded")
                    try:
                        page.wait_for_load_state("networkidle", timeout=15_000)
                    except Exception:
                        # Best-effort: some pages keep websockets/long-polls open.
                        pass

                    name = f"{vp.name}__{_slugify(route)}"
                    saved_path = screenshot_manager.capture(page, name=name, full_page=True)
                    print(f"Saved screenshot: {saved_path}")

                page.close()
                context.close()
        finally:
            browser.close()

    print(f"Screenshots saved under: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

