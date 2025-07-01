import hashlib
import mimetypes
import os
import uuid

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_file_size(file):
    """Validate file size (max 10MB)"""
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size > max_size:
        raise ValidationError(_("File size must not exceed 10MB."))


def validate_image_size(file):
    """Validate image size (max 5MB)"""
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        raise ValidationError(_("Image size must not exceed 5MB."))


def get_file_hash(file):
    """
    Calculate SHA-256 hash of a file to verify integrity
    """
    sha256_hash = hashlib.sha256()
    for byte_block in iter(lambda: file.read(4096), b""):
        sha256_hash.update(byte_block)
    file.seek(0)  # Reset file pointer to beginning
    return sha256_hash.hexdigest()


def document_upload_path(instance, filename):
    """
    Generate file path for uploaded documents

    Pattern: documents/exchange_<id>/<document_type>/<uuid>_<filename>
    """
    filename_base, filename_ext = os.path.splitext(filename)
    unique_filename = f"{uuid.uuid4().hex}{filename_ext}"
    return f"documents/exchange_{instance.exchange.id}/{instance.category}/{unique_filename}"
def photo_upload_path(instance, filename):
    """
    Generate a path for uploaded student photos
    Format: exchanges/student_id/photos/filename_with_uuid
    """
    ext = filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join(
        "exchanges", str(instance.student.id), "photos", unique_filename
    )


def get_mime_type(file):
    """
    Get MIME type of a file
    """
    mime_type, _ = mimetypes.guess_type(file.name)
    return mime_type
