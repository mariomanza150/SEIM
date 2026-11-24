"""Guarded MEDIA_URL serving with session/JWT auth and object-level ACLs."""

from __future__ import annotations

import logging
import mimetypes
import os
from pathlib import Path

from django.conf import settings
from django.http import (
    FileResponse,
    Http404,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseNotFound,
)
from django.views.decorators.http import require_GET
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from core.media_access import (
    MediaAccessKind,
    classify_media_path,
    normalize_media_path,
    user_may_access_media,
)

logger = logging.getLogger(__name__)


def _authenticate_request(request):
    """Prefer the session user; fall back to Bearer JWT (API clients)."""
    user = getattr(request, "user", None)
    if user is not None and getattr(user, "is_authenticated", False):
        return user

    try:
        result = JWTAuthentication().authenticate(request)
    except (InvalidToken, TokenError, Exception):
        return user
    if result is not None:
        request.user = result[0]
        return result[0]
    return user


def _deny(status: int) -> HttpResponse:
    if status == 401:
        response = HttpResponse(status=401)
        response["WWW-Authenticate"] = 'Bearer realm="media"'
        return response
    if status == 403:
        return HttpResponseForbidden()
    return HttpResponseNotFound()


def _absolute_media_file(relative_path: str) -> Path:
    media_root = Path(settings.MEDIA_ROOT).resolve()
    absolute = (media_root / relative_path).resolve()
    try:
        absolute.relative_to(media_root)
    except ValueError as exc:
        raise Http404("Invalid media path.") from exc
    return absolute


def _content_type_for(path: str) -> str:
    content_type, _ = mimetypes.guess_type(path)
    return content_type or "application/octet-stream"


def _serve_file(request, relative_path: str) -> HttpResponse:
    absolute = _absolute_media_file(relative_path)
    if not absolute.is_file():
        raise Http404("Media file not found.")

    content_type = _content_type_for(relative_path)
    use_accel = bool(getattr(settings, "USE_X_ACCEL_REDIRECT", False))
    if use_accel:
        internal_prefix = getattr(settings, "MEDIA_INTERNAL_URL", "/internal_media/")
        if not internal_prefix.endswith("/"):
            internal_prefix = f"{internal_prefix}/"
        response = HttpResponse(content_type=content_type)
        response["X-Accel-Redirect"] = f"{internal_prefix}{relative_path}"
        response["Content-Disposition"] = (
            f'inline; filename="{os.path.basename(relative_path)}"'
        )
        # Hint caches not to store private uploads.
        if classify_media_path(relative_path) != MediaAccessKind.PUBLIC:
            response["Cache-Control"] = "private, no-store"
        return response

    # Local / DEBUG / SERVE_MEDIA: stream from disk via Django.
    handle = absolute.open("rb")
    response = FileResponse(handle, content_type=content_type)
    response["Content-Disposition"] = (
        f'inline; filename="{os.path.basename(relative_path)}"'
    )
    if classify_media_path(relative_path) != MediaAccessKind.PUBLIC:
        response["Cache-Control"] = "private, no-store"
    return response


@require_GET
def serve_media(request, path: str = ""):
    """
    Serve a file under MEDIA_ROOT with auth/ACL for protected prefixes.

    Public prefixes (Wagtail images, etc.) remain readable without login.
    Protected uploads require session or JWT auth plus object-level checks.
    """
    relative = normalize_media_path(path)
    if not relative:
        return _deny(404)

    user = _authenticate_request(request)
    decision = user_may_access_media(user, relative)
    if not decision.allowed:
        logger.info(
            "media_access_denied path=%s status=%s reason=%s user=%s",
            relative,
            decision.status,
            decision.reason,
            getattr(user, "pk", None),
        )
        return _deny(decision.status)

    try:
        return _serve_file(request, relative)
    except Http404:
        return _deny(404)
