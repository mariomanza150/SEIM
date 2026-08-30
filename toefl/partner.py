"""Client for the TOEFL Practice partner API."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any

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
    req = urllib.request.Request(
        f"{base}/api/v1/launch-token",
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key,
            "User-Agent": "SEIM-TOEFL/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        logger.warning("TOEFL launch-token failed: %s %s", exc.code, detail)
        raise ToeflPartnerError(
            f"TOEFL launch failed: {exc.code}", status_code=502
        ) from exc
    except Exception as exc:
        logger.exception("TOEFL launch-token request error")
        raise ToeflPartnerError(str(exc), status_code=502) from exc

    if not isinstance(data, dict) or not data.get("launch_url"):
        raise ToeflPartnerError("Invalid launch-token response", status_code=502)
    return data
