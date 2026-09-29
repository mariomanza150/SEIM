"""HMAC helpers matching TOEFL Practice ``api_security``."""

from __future__ import annotations

import hashlib
import hmac


def sign_payload(body: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def verify_signature(body: bytes, signature: str, secret: str) -> bool:
    expected = sign_payload(body, secret)
    return hmac.compare_digest(expected, signature or "")
