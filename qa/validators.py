"""Upload validation for QA attachments (size, type sniffing, image re-encode)."""

from __future__ import annotations

import io
import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.translation import gettext as _

IMAGE_EXTS = {
    ".png": "PNG",
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".webp": "WEBP",
    ".gif": "GIF",
}
VIDEO_EXTS = {".webm", ".mp4"}
TEXT_EXTS = {".txt", ".log", ".json"}
ALLOWED_EXTS = set(IMAGE_EXTS) | VIDEO_EXTS | TEXT_EXTS

CONTENT_TYPES = {
    "PNG": "image/png",
    "JPEG": "image/jpeg",
    "WEBP": "image/webp",
    "GIF": "image/gif",
    ".webm": "video/webm",
    ".mp4": "video/mp4",
    ".txt": "text/plain",
    ".log": "text/plain",
    ".json": "application/json",
}


def _mb(n: int) -> int:
    return int(n) * 1024 * 1024


def _read_head(f, n=64) -> bytes:
    f.seek(0)
    head = f.read(n)
    f.seek(0)
    return head or b""


def _is_webm(head: bytes) -> bool:
    return head.startswith(b"\x1a\x45\xdf\xa3")


def _is_mp4(head: bytes) -> bool:
    return len(head) >= 12 and head[4:8] == b"ftyp"


def _validate_image(upload, ext):
    from PIL import Image, UnidentifiedImageError

    try:
        upload.seek(0)
        img = Image.open(upload)
        img.verify()
        upload.seek(0)
        img = Image.open(upload)
        detected = img.format
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError) as exc:
        raise ValidationError(_("The image file is not valid.")) from exc
    if detected not in set(IMAGE_EXTS.values()):
        raise ValidationError(_("Unsupported image format."))
    if img.width * img.height > 50_000_000:
        raise ValidationError(_("The image is too large."))
    if detected == "GIF":
        # Keep animation; GIFs carry no EXIF.
        upload.seek(0)
        return upload, CONTENT_TYPES["GIF"], ".gif"
    # Re-encode to strip metadata (EXIF/GPS) and any trailing payload.
    out = io.BytesIO()
    fmt = "PNG" if detected == "PNG" else detected
    if fmt == "JPEG" and img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    img.save(out, format=fmt)
    size = out.tell()
    out.seek(0)
    new_ext = {"PNG": ".png", "JPEG": ".jpg", "WEBP": ".webp"}[fmt]
    name = os.path.splitext(os.path.basename(upload.name or "image"))[0] + new_ext
    clean = InMemoryUploadedFile(out, "file", name, CONTENT_TYPES[fmt], size, None)
    return clean, CONTENT_TYPES[fmt], new_ext


def validate_attachment(upload):
    """
    Validate one uploaded file. Returns ``(file, content_type, kind)``.

    Raises ``ValidationError`` with a user-facing message.
    """
    name = os.path.basename(getattr(upload, "name", "") or "")
    ext = os.path.splitext(name)[1].lower()
    if ext not in ALLOWED_EXTS:
        raise ValidationError(
            _(
                "File type not allowed. Use PNG, JPG, WEBP, GIF, WEBM, MP4, TXT, LOG or JSON."
            )
        )
    size = getattr(upload, "size", 0) or 0
    if size <= 0:
        raise ValidationError(_("The file is empty."))
    image_limit = _mb(getattr(settings, "QA_MAX_IMAGE_MB", 10))
    video_limit = _mb(getattr(settings, "QA_MAX_VIDEO_MB", 25))

    if ext in IMAGE_EXTS:
        if size > image_limit:
            raise ValidationError(
                _("Images and logs must be %(mb)s MB or smaller.")
                % {"mb": image_limit // (1024 * 1024)}
            )
        clean, ctype, _ext = _validate_image(upload, ext)
        return clean, ctype, "screenshot"

    head = _read_head(upload)
    if ext in VIDEO_EXTS:
        if size > video_limit:
            raise ValidationError(
                _("Recordings must be %(mb)s MB or smaller.")
                % {"mb": video_limit // (1024 * 1024)}
            )
        ok = _is_webm(head) if ext == ".webm" else _is_mp4(head)
        if not ok:
            raise ValidationError(_("The recording does not match its file type."))
        return upload, CONTENT_TYPES[ext], "recording"

    # Text / logs
    if size > image_limit:
        raise ValidationError(
            _("Images and logs must be %(mb)s MB or smaller.")
            % {"mb": image_limit // (1024 * 1024)}
        )
    upload.seek(0)
    sample = upload.read(min(size, 65536))
    upload.seek(0)
    if b"\x00" in sample:
        raise ValidationError(_("Text files must not contain binary data."))
    try:
        sample.decode("utf-8")
    except UnicodeDecodeError:
        # A multi-byte char may be cut at the sample edge; only reject early failures.
        try:
            sample[:-4].decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValidationError(_("Text files must be UTF-8.")) from exc
    return upload, CONTENT_TYPES[ext], "log"


def scan_attachment(upload) -> None:
    """Run the configured virus scanner (mock on test servers by default)."""
    import tempfile

    from documents.virus_scanner import scan_file_for_viruses

    upload.seek(0)
    suffix = os.path.splitext(getattr(upload, "name", "") or "")[1][:10]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        for chunk in iter(lambda: upload.read(1024 * 1024), b""):
            tmp.write(chunk)
        path = tmp.name
    upload.seek(0)
    try:
        # Raises ValidationError when infected (or when the scan fails and
        # VIRUS_SCAN_FAIL_SECURE is on).
        scan_file_for_viruses(path)
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
