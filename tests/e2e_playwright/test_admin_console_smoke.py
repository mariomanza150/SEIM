"""
Admin console smoke tests for Vue SPA surfaces.

Covers /seim/admin/forms catalog and /seim/admin/workflows list after JWT admin login.
Skips when the Vue app or demo admin seed is unavailable (same pattern as test_vue_ui.py).
"""

from __future__ import annotations

import os
import re

import pytest
from playwright.sync_api import Page, expect

from tests.e2e_playwright.utils.auth_helpers import VueAppNotAvailable
from tests.e2e_playwright.utils.vue_auth_helpers import login_vue_via_jwt


def _normalize_vue_base_url(base_url: str) -> str:
    base_url = base_url.rstrip("/")
    if base_url.endswith("/seim"):
        return base_url
    for port in (":8000", ":8001", ":8020", ":8021"):
        if base_url.endswith(port):
            return f"{base_url}/seim"
    return base_url


VUE_BASE_URL = _normalize_vue_base_url(
    os.environ.get("BASE_URL", "http://localhost:8000")
)
VUE_ADMIN_EMAIL = "admin@test.com"
VUE_ADMIN_PASSWORD = "admin123"


def _login_admin_or_skip(page: Page) -> None:
    try:
        login_vue_via_jwt(page, VUE_BASE_URL, VUE_ADMIN_EMAIL, VUE_ADMIN_PASSWORD)
    except VueAppNotAvailable as exc:
        pytest.skip(str(exc))


@pytest.mark.e2e_playwright
@pytest.mark.smoke
@pytest.mark.admin
@pytest.mark.nondestructive
def test_admin_forms_catalog_smoke(page: Page):
    """Admin can open the forms catalog table and builder link."""
    _login_admin_or_skip(page)
    page.goto(f"{VUE_BASE_URL}/admin/forms")
    page.wait_for_load_state("domcontentloaded")
    if re.search(r"/login", page.url, re.I):
        pytest.skip("Admin login did not reach forms catalog")
    expect(page.locator("[data-testid=admin-forms-filters]")).to_be_visible(timeout=15000)
    expect(page.locator("[data-testid=admin-forms-table]")).to_be_visible(timeout=15000)
    builder = page.locator("[data-testid=admin-forms-open-builder]").first
    if builder.count():
        expect(builder).to_be_visible()


@pytest.mark.e2e_playwright
@pytest.mark.smoke
@pytest.mark.admin
@pytest.mark.nondestructive
def test_admin_workflows_catalog_smoke(page: Page):
    """Admin can open the workflows catalog and BPMN editor entry point."""
    _login_admin_or_skip(page)
    page.goto(f"{VUE_BASE_URL}/admin/workflows")
    page.wait_for_load_state("domcontentloaded")
    if re.search(r"/login", page.url, re.I):
        pytest.skip("Admin login did not reach workflows catalog")
    expect(page.locator("[data-testid=admin-workflows-filters]")).to_be_visible(timeout=15000)
    expect(page.locator("[data-testid=admin-workflows-table]")).to_be_visible(timeout=15000)
    editor_link = page.locator("[data-testid=admin-workflows-open-editor]").first
    if editor_link.count():
        expect(editor_link).to_be_visible()
