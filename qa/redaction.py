"""Server-side scrubbing of tester-supplied diagnostics (defence in depth)."""

from __future__ import annotations

import json
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

SENSITIVE_PARAM = re.compile(
    r"(token|code|password|passwd|secret|key|auth|session|signature|sig|otp)", re.I
)
SENSITIVE_KEYS = re.compile(
    r"^(authorization|cookie|set-cookie|password|access|refresh|token|secret|headers|body|data|request|response)$",
    re.I,
)
JWT_LIKE = re.compile(r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}")
MAX_DIAGNOSTICS_BYTES = 64 * 1024


def scrub_url(url: str, max_len: int = 1000) -> str:
    if not url:
        return ""
    try:
        parts = urlsplit(str(url))
    except ValueError:
        return ""
    query = [
        (k, "[redacted]" if SENSITIVE_PARAM.search(k) else v)
        for k, v in parse_qsl(parts.query, keep_blank_values=True)
    ]
    cleaned = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), ""))
    return JWT_LIKE.sub("[redacted-jwt]", cleaned)[:max_len]


def _scrub(value, depth=0):
    if depth > 6:
        return None
    if isinstance(value, dict):
        out = {}
        for k, v in list(value.items())[:100]:
            key = str(k)[:100]
            if SENSITIVE_KEYS.match(key):
                continue
            if key in ("url", "path", "href", "fullPath", "from", "to"):
                out[key] = scrub_url(v) if isinstance(v, str) else v
            else:
                out[key] = _scrub(v, depth + 1)
        return out
    if isinstance(value, list):
        return [_scrub(v, depth + 1) for v in value[:100]]
    if isinstance(value, str):
        return JWT_LIKE.sub("[redacted-jwt]", value[:4000])
    if isinstance(value, int | float | bool) or value is None:
        return value
    return str(value)[:200]


def scrub_diagnostics(raw) -> dict:
    if isinstance(raw, str):
        try:
            raw = json.loads(raw) if raw.strip() else {}
        except ValueError:
            return {}
    if not isinstance(raw, dict):
        return {}
    cleaned = _scrub(raw)
    encoded = json.dumps(cleaned, default=str)
    if len(encoded.encode("utf-8")) > MAX_DIAGNOSTICS_BYTES:
        # Keep the most useful parts when oversize.
        cleaned = {
            k: cleaned.get(k)
            for k in ("consoleErrors", "failedRequests", "breadcrumbs")
            if k in cleaned
        }
        for k in list(cleaned):
            if isinstance(cleaned[k], list):
                cleaned[k] = cleaned[k][-10:]
        cleaned["truncated"] = True
    return cleaned
