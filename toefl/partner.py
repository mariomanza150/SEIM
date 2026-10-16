"""Client for the TOEFL Practice partner API."""

from __future__ import annotations

import json
import logging
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class ToeflPartnerError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def create_launch_token(
    *,
    exam_code: str,
    client_ref: str,
    callback_url: str,
    return_url: str,
    macro_id: str = "all",
    categories: list[str] | None = None,
    n: int = 20,
) -> dict[str, Any]:
    base = (getattr(settings, "TOEFL_API_BASE_URL", "") or "").rstrip("/")
    api_key = getattr(settings, "TOEFL_API_KEY", "") or ""
    if not base or not api_key:
        raise ToeflPartnerError("TOEFL partner API is not configured", status_code=503)

    payload = {
        "exam_code": exam_code,
        "client_ref": client_ref,
        "callback_url": callback_url,
        "return_url": return_url,
        "macro_id": macro_id or "all",
        "categories": categories or [],
        "n": int(n),
    }
    body = json.dumps(payload).encode("utf-8")
    if not base.startswith(("https://", "http://")):
        raise ToeflPartnerError(
            "TOEFL_API_BASE_URL must be an http(s) URL", status_code=502
        )
    try:
        resp = requests.post(
            f"{base}/api/v1/launch-token",
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key,
                "User-Agent": "SEIM-TOEFL/1.0",
            },
            timeout=15,
        )
    except requests.RequestException as exc:
        logger.exception("TOEFL launch-token request error")
        raise ToeflPartnerError(str(exc), status_code=502) from exc
    if resp.status_code >= 400:
        logger.warning(
            "TOEFL launch-token failed: %s %s", resp.status_code, resp.text[:500]
        )
        raise ToeflPartnerError(
            f"TOEFL launch failed: {resp.status_code}", status_code=502
        )
    try:
        data = resp.json()
    except ValueError as exc:
        raise ToeflPartnerError(
            "TOEFL launch returned invalid JSON", status_code=502
        ) from exc

    if not isinstance(data, dict) or not data.get("launch_url"):
        raise ToeflPartnerError("Invalid launch-token response", status_code=502)
    return data
