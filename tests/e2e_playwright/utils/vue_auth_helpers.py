"""
Vue SPA auth helpers for E2E tests.

Uses JWT login (email + password) and sets access_token/refresh_token in localStorage
so the Vue app at base_url considers the user logged in.
Caches tokens per (email, password) to avoid throttle (429) when many tests run.
"""
import os
import time
from playwright.sync_api import Page

# API base URL (Django backend) - Vue proxies to this in dev
API_BASE_URL = os.environ.get("VITE_API_BASE_URL", os.environ.get("API_URL", "http://localhost:8001"))

# Cache: (email, password) -> (access, refresh, expiry_ts). TTL 5 minutes.
_JWT_CACHE: dict[tuple[str, str], tuple[str, str, float]] = {}
_JWT_CACHE_TTL = 300


def login_vue_via_jwt(page: Page, vue_base_url: str, email: str, password: str) -> dict:
    """
    Login via JWT API and set tokens in localStorage, then load Vue app.
    Reuses cached tokens when available to avoid API throttle.
    """
    key = (email, password)
    now = time.time()
    if key in _JWT_CACHE:
        access, refresh, expiry = _JWT_CACHE[key]
        if now < expiry:
            page.goto(vue_base_url)
            page.wait_for_load_state("domcontentloaded")
            page.evaluate(
                """
                (args) => {
                    localStorage.setItem('access_token', args.access);
                    localStorage.setItem('refresh_token', args.refresh || '');
                }
                """,
                {"access": access, "refresh": refresh},
            )
            page.goto(f"{vue_base_url}/dashboard")
            page.wait_for_load_state("networkidle")
            if page.title() and "not found" in page.title().lower():
                from tests.e2e_playwright.utils.auth_helpers import VueAppNotAvailable
                raise VueAppNotAvailable(
                    f"Vue app not available at {vue_base_url}. Run with BASE_URL=http://localhost:5173"
                )
            return {"access": access, "refresh": refresh}

    response = page.context.request.post(
        f"{API_BASE_URL}/api/token/",
        data={"email": email, "password": password},
        headers={"Content-Type": "application/json"},
    )
    if response.status == 404:
        from tests.e2e_playwright.utils.auth_helpers import VueAppNotAvailable
        raise VueAppNotAvailable(
            f"API not available at {API_BASE_URL}/api/token/ (404). "
            "Start Vue dev server and Django API; run with BASE_URL=http://localhost:5173 API_URL=http://localhost:8001"
        )
    assert response.ok, f"JWT login failed: {response.status} {response.text()[:200]}"
    data = response.json()
    access = data.get("access", "")
    refresh = data.get("refresh", "")
    _JWT_CACHE[key] = (access, refresh, now + _JWT_CACHE_TTL)

    page.goto(vue_base_url)
    page.wait_for_load_state("domcontentloaded")
    page.evaluate(
        """
        (args) => {
            localStorage.setItem('access_token', args.access);
            localStorage.setItem('refresh_token', args.refresh || '');
        }
        """,
        {"access": access, "refresh": refresh},
    )
    page.goto(f"{vue_base_url}/dashboard")
    page.wait_for_load_state("networkidle")
    if page.title() and "not found" in page.title().lower():
        from tests.e2e_playwright.utils.auth_helpers import VueAppNotAvailable
        raise VueAppNotAvailable(
            f"Vue app not available at {vue_base_url} (dashboard returned Not Found). "
            "Start Vue dev server and run with BASE_URL=http://localhost:5173"
        )
    return data


def is_vue_logged_in(page: Page) -> bool:
    """Check if Vue app has access_token in localStorage."""
    return page.evaluate("localStorage.getItem('access_token') !== null")


def get_cached_access_token(email: str, password: str) -> str | None:
    """Return cached access token if valid; otherwise None."""
    key = (email, password)
    if key not in _JWT_CACHE:
        return None
    access, _, expiry = _JWT_CACHE[key]
    if time.time() >= expiry:
        return None
    return access


def ensure_draft_application_via_api(page: Page, email: str, password: str) -> str | None:
    """
    Ensure the test user has at least one draft application by creating one via API if needed.
    Uses cached JWT or performs token request. Returns application id (UUID string) or None on failure.
    """
    token = get_cached_access_token(email, password)
    if not token:
        response = page.context.request.post(
            f"{API_BASE_URL}/api/token/",
            data={"email": email, "password": password},
            headers={"Content-Type": "application/json"},
        )
        if not response.ok:
            return None
        data = response.json()
        token = data.get("access", "")
        _JWT_CACHE[(email, password)] = (token, data.get("refresh", ""), time.time() + _JWT_CACHE_TTL)
    if not token:
        return None
    # GET first program
    programs_resp = page.context.request.get(
        f"{API_BASE_URL}/api/programs/",
        headers={"Authorization": f"Bearer {token}"},
    )
    if not programs_resp.ok:
        return None
    programs_data = programs_resp.json()
    results = programs_data.get("results", programs_data) if isinstance(programs_data, dict) else programs_data
    if not results or not isinstance(results, list):
        return None
    program_id = results[0].get("id") if isinstance(results[0], dict) else None
    if not program_id:
        return None
    # POST create application (draft)
    create_resp = page.context.request.post(
        f"{API_BASE_URL}/api/applications/",
        data={"program": program_id},
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    if not create_resp.ok:
        return None
    app_data = create_resp.json()
    return app_data.get("id")
