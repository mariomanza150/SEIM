"""
Vue SPA auth helpers for E2E tests.

Uses JWT login (email + password) and sets access_token/refresh_token in localStorage
so the Vue app at base_url considers the user logged in.
Caches tokens per (email, password) to avoid throttle (429) when many tests run.
"""

import json
import os
import re
import time

from playwright.sync_api import Page

def api_base_url() -> str:
    """Django origin for JWT/API calls (not the Vue `/seim` mount)."""
    raw = (
        os.environ.get("API_URL")
        or os.environ.get("BASE_URL")
        or "http://localhost:8000"
    ).rstrip("/")
    if raw.endswith("/seim"):
        raw = raw[: -len("/seim")]
    return raw


# Resolved at import for callers that still use the module constant.
API_BASE_URL = api_base_url()

_TOKEN_PERSIST_JS = """
(args) => {
    localStorage.setItem('access_token', args.access);
    localStorage.setItem('seim_access_token', args.access);
    localStorage.setItem('refresh_token', args.refresh || '');
    localStorage.setItem('seim_refresh_token', args.refresh || '');
}
"""

# Cache: (email, password) -> (access, refresh, expiry_ts). TTL 5 minutes.
_JWT_CACHE: dict[tuple[str, str], tuple[str, str, float]] = {}
_JWT_CACHE_TTL = 300


def _json_headers(extra: dict | None = None) -> dict:
    headers = {"Content-Type": "application/json"}
    if extra:
        headers.update(extra)
    return headers


def _request_json(page: Page, method: str, url: str, payload=None, headers=None):
    """Playwright 1.41 has no request.json=; send a JSON body via data=."""
    kwargs = {"headers": _json_headers(headers)}
    if payload is not None:
        kwargs["data"] = json.dumps(payload)
    return getattr(page.context.request, method)(url, **kwargs)


def _apply_tokens_and_open_dashboard(page: Page, vue_base_url: str, access: str, refresh: str) -> None:
    from tests.e2e_playwright.utils.auth_helpers import VueAppNotAvailable

    page.goto(vue_base_url)
    page.wait_for_load_state("domcontentloaded")
    page.evaluate(_TOKEN_PERSIST_JS, {"access": access, "refresh": refresh})
    page.goto(f"{vue_base_url}/dashboard")
    page.wait_for_load_state("domcontentloaded")
    dashboard = page.locator("[data-testid=dashboard-page]")
    try:
        dashboard.wait_for(state="visible", timeout=15000)
    except Exception as exc:
        title = (page.title() or "").lower()
        if "not found" in title:
            raise VueAppNotAvailable(
                f"Vue app not available at {vue_base_url}. "
                "Build frontend-vue or run with BASE_URL=http://localhost:5173"
            ) from exc
        if page.locator("[data-testid=login-email]").count():
            raise VueAppNotAvailable(
                f"JWT login did not reach dashboard (url={page.url}). "
                "Profile/API may be throttled (429); set DISABLE_THROTTLE_E2E=1 on the backend."
            ) from exc
        raise VueAppNotAvailable(
            f"Dashboard did not load at {vue_base_url}/dashboard (url={page.url})"
        ) from exc


def login_vue_via_jwt(page: Page, vue_base_url: str, email: str, password: str) -> dict:
    """
    Login via JWT API and set tokens in localStorage, then load Vue app.
    Reuses cached tokens when available to avoid API throttle.
    """
    from tests.e2e_playwright.utils.auth_helpers import VueAppNotAvailable

    key = (email, password)
    now = time.time()
    origin = api_base_url()
    if key in _JWT_CACHE:
        access, refresh, expiry = _JWT_CACHE[key]
        if now < expiry:
            _apply_tokens_and_open_dashboard(page, vue_base_url, access, refresh)
            return {"access": access, "refresh": refresh}

    response = _request_json(
        page,
        "post",
        f"{origin}/api/token/",
        {"email": email, "password": password},
    )
    if response.status == 404:
        raise VueAppNotAvailable(
            f"API not available at {origin}/api/token/ (404). "
            "Start Vue dev server and Django API; run with BASE_URL=http://localhost:5173 API_URL=http://localhost:8001"
        )
    if response.status == 429:
        raise VueAppNotAvailable(
            f"JWT login throttled (429) at {origin}/api/token/. "
            "Set DISABLE_THROTTLE_E2E=1 on the backend."
        )
    assert response.ok, f"JWT login failed: {response.status} {response.text()[:200]}"
    data = response.json()
    access = data.get("access", "")
    refresh = data.get("refresh", "")
    _JWT_CACHE[key] = (access, refresh, now + _JWT_CACHE_TTL)
    _apply_tokens_and_open_dashboard(page, vue_base_url, access, refresh)
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


def _token_for(page: Page, email: str, password: str) -> str | None:
    token = get_cached_access_token(email, password)
    if token:
        return token
    response = _request_json(
        page,
        "post",
        f"{api_base_url()}/api/token/",
        {"email": email, "password": password},
    )
    if not response.ok:
        return None
    data = response.json()
    token = data.get("access", "")
    _JWT_CACHE[(email, password)] = (
        token,
        data.get("refresh", ""),
        time.time() + _JWT_CACHE_TTL,
    )
    return token or None


def _first_id(payload) -> str | None:
    rows = payload.get("results", payload) if isinstance(payload, dict) else payload
    if isinstance(rows, list) and rows and isinstance(rows[0], dict) and rows[0].get("id"):
        return str(rows[0]["id"])
    if isinstance(payload, dict) and payload.get("id"):
        return str(payload["id"])
    return None


def _ensure_host_destination(page: Page, auth: dict, app_id: str) -> None:
    """Fill host university/school/program on a draft so submit can succeed."""
    app_resp = page.context.request.get(
        f"{api_base_url()}/api/applications/{app_id}/",
        headers=auth,
    )
    if not app_resp.ok:
        return
    app_data = app_resp.json()
    if (
        app_data.get("host_institution")
        and app_data.get("host_school")
        and app_data.get("host_academic_program")
    ):
        return
    program = app_data.get("program")
    program_id = program.get("id") if isinstance(program, dict) else program
    if not program_id:
        return
    hosts_resp = page.context.request.get(
        f"{api_base_url()}/api/programs/{program_id}/host-institutions/",
        headers=auth,
    )
    if not hosts_resp.ok:
        return
    institution_id = _first_id(hosts_resp.json())
    if not institution_id:
        return
    schools_resp = page.context.request.get(
        f"{api_base_url()}/api/host-institutions/{institution_id}/schools/",
        headers=auth,
    )
    if not schools_resp.ok:
        return
    school_id = _first_id(schools_resp.json())
    if not school_id:
        return
    academic_resp = page.context.request.get(
        f"{api_base_url()}/api/schools/{school_id}/academic-programs/",
        headers=auth,
    )
    if not academic_resp.ok:
        return
    academic_id = _first_id(academic_resp.json())
    if not academic_id:
        return
    _request_json(
        page,
        "patch",
        f"{api_base_url()}/api/applications/{app_id}/",
        {
            "host_institution": institution_id,
            "host_school": school_id,
            "host_academic_program": academic_id,
        },
        auth,
    )


def ensure_draft_application_via_api(
    page: Page,
    email: str,
    password: str,
    *,
    program_name: str | None = None,
    force_new: bool = False,
) -> str | None:
    """
    Ensure the test user has at least one draft application by creating one via API if needed.
    Uses cached JWT or performs token request. Returns application id (UUID string) or None on failure.
    """
    token = _token_for(page, email, password)
    if not token:
        return None
    auth = {"Authorization": f"Bearer {token}"}

    if not force_new:
        list_resp = page.context.request.get(
            f"{api_base_url()}/api/applications/",
            params={"status": "draft", "withdrawn": False, "page_size": 100},
            headers=auth,
        )
        if list_resp.ok:
            list_data = list_resp.json()
            drafts = (
                list_data.get("results", list_data)
                if isinstance(list_data, dict)
                else list_data
            )
            if isinstance(drafts, list):
                preferred_id = None
                fallback_id = None
                for item in drafts:
                    if not isinstance(item, dict) or not item.get("id"):
                        continue
                    if item.get("withdrawn"):
                        continue
                    fallback_id = fallback_id or str(item["id"])
                    name = item.get("program_name") or ""
                    program = item.get("program")
                    if isinstance(program, dict):
                        name = name or program.get("name") or ""
                    if name == "Vue E2E Test Program":
                        preferred_id = str(item["id"])
                        break
                    if program_name and name == program_name:
                        preferred_id = str(item["id"])
                        break
                chosen = preferred_id or (None if program_name else fallback_id)
                if chosen:
                    _ensure_host_destination(page, auth, chosen)
                    detail = page.context.request.get(
                        f"{api_base_url()}/api/applications/{chosen}/",
                        headers=auth,
                    )
                    if detail.ok:
                        status = detail.json().get("status")
                        status_name = (
                            status.get("name")
                            if isinstance(status, dict)
                            else str(status or "")
                        )
                        if status_name == "draft":
                            return chosen

    programs_resp = page.context.request.get(
        f"{api_base_url()}/api/programs/",
        headers=auth,
    )
    if not programs_resp.ok:
        return None
    programs_data = programs_resp.json()
    results = (
        programs_data.get("results", programs_data)
        if isinstance(programs_data, dict)
        else programs_data
    )
    if not results or not isinstance(results, list):
        return None

    existing_resp = page.context.request.get(
        f"{api_base_url()}/api/applications/",
        headers=auth,
    )
    used_program_ids: set[str] = set()
    if existing_resp.ok:
        existing_data = existing_resp.json()
        existing = (
            existing_data.get("results", existing_data)
            if isinstance(existing_data, dict)
            else existing_data
        )
        if isinstance(existing, list):
            for item in existing:
                if not isinstance(item, dict):
                    continue
                if item.get("withdrawn"):
                    continue
                status = item.get("status")
                status_name = (
                    status.get("name")
                    if isinstance(status, dict)
                    else str(status or "")
                )
                if status_name not in {"submitted", "under_review", "waitlist"}:
                    continue
                program = item.get("program")
                if isinstance(program, dict) and program.get("id"):
                    used_program_ids.add(str(program["id"]))
                elif program:
                    used_program_ids.add(str(program))

    preferred = next(
        (
            item
            for item in results
            if isinstance(item, dict)
            and item.get("name") == (program_name or "Vue E2E Test Program")
            and str(item.get("id")) not in used_program_ids
        ),
        None,
    )
    candidates = ([preferred] if preferred else []) + [
        item
        for item in results
        if isinstance(item, dict)
        and item.get("id")
        and str(item["id"]) not in used_program_ids
        and item is not preferred
    ]
    for program in candidates:
        program_id = program.get("id")
        create_resp = _request_json(
            page,
            "post",
            f"{api_base_url()}/api/applications/",
            {"program": program_id},
            auth,
        )
        if create_resp.ok:
            app_data = create_resp.json()
            app_id = app_data.get("id")
            if app_id:
                _ensure_host_destination(page, auth, str(app_id))
                return str(app_id)
    return None


def withdraw_blocking_applications_via_api(
    page: Page,
    email: str,
    password: str,
    program_name: str = "Vue E2E Test Program",
) -> None:
    """Withdraw submitted/waitlisted apps so a new draft can be created for the program."""
    token = _token_for(page, email, password)
    if not token:
        return
    auth = {"Authorization": f"Bearer {token}"}
    list_resp = page.context.request.get(
        f"{api_base_url()}/api/applications/",
        params={"page_size": 100},
        headers=auth,
    )
    if not list_resp.ok:
        return
    payload = list_resp.json()
    rows = payload.get("results", payload) if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        return
    blocking = {"submitted", "under_review", "waitlist"}
    for item in rows:
        if not isinstance(item, dict) or not item.get("id"):
            continue
        name = item.get("program_name") or ""
        program = item.get("program")
        if isinstance(program, dict):
            name = name or program.get("name") or ""
        status = item.get("status")
        status_name = (
            status.get("name") if isinstance(status, dict) else str(status or "")
        )
        if name != program_name or status_name not in blocking:
            continue
        _request_json(
            page,
            "patch",
            f"{api_base_url()}/api/applications/{item['id']}/",
            {"withdrawn": True},
            auth,
        )


def ensure_unread_notification_via_api(page: Page, email: str, password: str) -> bool:
    """Guarantee at least one unread notification for the user (PATCH is_read=false)."""
    token = _token_for(page, email, password)
    if not token:
        return False
    auth = {"Authorization": f"Bearer {token}"}
    list_resp = page.context.request.get(
        f"{api_base_url()}/api/notifications/",
        headers=auth,
    )
    if not list_resp.ok:
        return False
    payload = list_resp.json()
    rows = payload.get("results", payload) if isinstance(payload, dict) else payload
    if not isinstance(rows, list) or not rows:
        return False
    unread = next((n for n in rows if isinstance(n, dict) and not n.get("is_read")), None)
    target = unread or (rows[0] if isinstance(rows[0], dict) else None)
    if not target or not target.get("id"):
        return False
    if unread:
        return True
    patch_resp = _request_json(
        page,
        "patch",
        f"{api_base_url()}/api/notifications/{target['id']}/",
        {"is_read": False},
        auth,
    )
    return patch_resp.ok


def wait_for_program_select_options(page: Page, timeout: int = 20000) -> None:
    """Wait until the new-application program select has at least one real option."""
    page.locator("[data-testid=program-select]").wait_for(state="visible", timeout=timeout)
    clear_btn = page.get_by_role("button", name=re.compile(r"Clear filters", re.I))
    if clear_btn.count() > 0:
        clear_btn.first.click()
    page.wait_for_function(
        """() => {
          const el = document.querySelector('[data-testid=program-select]');
          return el && el.querySelectorAll('option').length >= 2;
        }""",
        timeout=timeout,
    )


def select_preferred_program(page: Page, label: str = "Vue E2E Test Program") -> None:
    """Select the Vue E2E program when present, otherwise the first real option."""
    program_select = page.locator("[data-testid=program-select]")
    preferred = program_select.locator("option", has_text=label)
    if preferred.count() > 0:
        program_select.select_option(label=label)
    else:
        program_select.select_option(index=1)


def fill_host_destination_cascade(page: Page, timeout: int = 8000) -> None:
    """Select the first host institution → school → academic program on the form."""
    host_select = page.locator("[data-testid=host-institution-select]")
    host_select.wait_for(state="visible", timeout=timeout)
    page.wait_for_function(
        """() => {
          const el = document.querySelector('[data-testid=host-institution-select]');
          return el && el.querySelectorAll('option').length >= 2;
        }""",
        timeout=timeout,
    )
    host_select.select_option(index=1)
    page.wait_for_function(
        """() => {
          const el = document.querySelector('[data-testid=host-school-select]');
          return el && !el.disabled && el.querySelectorAll('option').length >= 2;
        }""",
        timeout=timeout,
    )
    page.locator("[data-testid=host-school-select]").select_option(index=1)
    page.wait_for_function(
        """() => {
          const el = document.querySelector('[data-testid=host-academic-program-select]');
          return el && !el.disabled && el.querySelectorAll('option').length >= 2;
        }""",
        timeout=timeout,
    )
    page.locator("[data-testid=host-academic-program-select]").select_option(index=1)
