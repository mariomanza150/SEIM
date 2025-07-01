"""
File validators for secure document uploads.
"""

import hashlib
import mimetypes
import os
from typing import List, Optional

import magic
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile


class FileTypeValidator:
    """
    Validates file types based on extensions and MIME types.
    """

    def __init__(
        self,
        allowed_extensions: Optional[List[str]] = None,
        allowed_mime_types: Optional[List[str]] = None,
    ):
        self.allowed_extensions = allowed_extensions or getattr(
            settings,
            "ALLOWED_UPLOAD_EXTENSIONS",
            ["pdf", "doc", "docx", "jpg", "jpeg", "png"],
        )
        self.allowed_mime_types = allowed_mime_types or [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "image/jpeg",
            "image/png",
        ]

    def validate(self, file: UploadedFile) -> None:
        """
        Validate file type using both extension and MIME type detection.
        """
        # Check file extension
        ext = os.path.splitext(file.name)[1].lower().strip(".")
        if ext not in self.allowed_extensions:
            raise ValidationError(
                f"File type '{ext}' is not allowed. Allowed types: {', '.join(self.allowed_extensions)}"
            )

        # Check MIME type using python-magic
        file.seek(0)
        mime = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)

        if mime not in self.allowed_mime_types:
            raise ValidationError(
                f"File MIME type '{mime}' is not allowed. Detected as {mime} but expected one of: {', '.join(self.allowed_mime_types)}"
            )

        # Cross-check extension with MIME type
        expected_mime = mimetypes.guess_type(file.name)[0]
        if expected_mime and mime != expected_mime:
            raise ValidationError(
                f"File extension does not match content. Extension suggests {expected_mime} but content is {mime}"
            )


class FileSizeValidator:
    """
    Validates file size against configured maximum.
    """

    def __init__(self, max_size_mb: Optional[float] = None):
        self.max_size = (
            max_size_mb * 1024 * 1024
            if max_size_mb
            else getattr(settings, "FILE_UPLOAD_MAX_MEMORY_SIZE", 10 * 1024 * 1024)
        )

    def validate(self, file: UploadedFile) -> None:
        """
        Validate file size.
        """
        if file.size > self.max_size:
            max_size_mb = self.max_size / (1024 * 1024)
            file_size_mb = file.size / (1024 * 1024)
            raise ValidationError(
                f"File size ({file_size_mb:.1f}MB) exceeds maximum allowed size ({max_size_mb:.1f}MB)"
            )


class FileContentValidator:
    """
    Validates file content for specific threats and patterns.
    """

    # Known malicious patterns and signatures
    MALICIOUS_PATTERNS = {
        # JavaScript in PDF
        b"/JavaScript": "JavaScript code detected in PDF",
        b"/JS": "JavaScript code detected in PDF",
        # Executable content
        b"\x4d\x5a": "Windows executable detected",
        b"\x7fELF": "Linux executable detected",
        # Common exploit patterns
        b"<script": "Script tag detected",
        b"<%": "Server-side code detected",
        b"<?php": "PHP code detected",
    }

    def validate(self, file: UploadedFile) -> None:
        """
        Scan file content for malicious patterns.
        """
        file.seek(0)
        content = file.read()
        file.seek(0)

        for pattern, message in self.MALICIOUS_PATTERNS.items():
            if pattern in content:
                raise ValidationError(f"Potentially malicious content detected: {message}")

        # Additional checks for specific file types
        mime = magic.from_buffer(content, mime=True)

        if "pdf" in mime:
            self._validate_pdf_content(content)
        elif "image" in mime:
            self._validate_image_content(content)

    def _validate_pdf_content(self, content: bytes) -> None:
        """
        Additional validation for PDF files.
        """
        # Check for embedded files
        if b"/EmbeddedFiles" in content:
            raise ValidationError("PDF contains embedded files which are not allowed")

        # Check for forms
        if b"/AcroForm" in content:
            raise ValidationError("PDF contains interactive forms which are not allowed")

    def _validate_image_content(self, content: bytes) -> None:
        """
        Additional validation for image files.
        """
        # Basic check for steganography patterns
        # This is a simplified check; real implementation would need more sophisticated detection
        pass


class FileIntegrityValidator:
    """
    Validates file integrity using checksums and ensures files haven't been tampered with.
    """

    @staticmethod
    def calculate_checksum(file: UploadedFile, algorithm: str = "sha256") -> str:
        """
        Calculate file checksum.
        """
        hasher = hashlib.new(algorithm)
        file.seek(0)

        for chunk in iter(lambda: file.read(4096), b""):
            hasher.update(chunk)

        file.seek(0)
        return hasher.hexdigest()

    @staticmethod
    def validate_checksum(file: UploadedFile, expected_checksum: str, algorithm: str = "sha256") -> None:
        """
        Validate file checksum against expected value.
        """
        actual_checksum = FileIntegrityValidator.calculate_checksum(file, algorithm)

        if actual_checksum != expected_checksum:
            raise ValidationError(
                f"File integrity check failed. Expected {algorithm} checksum: {expected_checksum}, "
                f"but got: {actual_checksum}. File may have been tampered with."
            )


class MalwareScanner:
    """
    Integrates with anti-virus/malware scanning services.
    """

    def __init__(self, scanner_type: str = "clamav"):
        self.scanner_type = scanner_type

        # Initialize scanner based on type
        if scanner_type == "clamav":
            try:
                import pyclamd

                self.scanner = pyclamd.ClamdAgnostic()
                if not self.scanner.ping():
                    self.scanner = None
            except ImportError:
                self.scanner = None
        else:
            self.scanner = None

    def scan(self, file: UploadedFile) -> bool:
        """
        Scan file for malware. Returns True if file is clean, False otherwise.
        """
        if not self.scanner:
            # If no scanner available, log warning but don't block
            # In production, you might want to raise an exception
            return True

        file.seek(0)
        content = file.read()
        file.seek(0)

        if self.scanner_type == "clamav":
            result = self.scanner.scan_stream(content)
            return result is None  # None means no virus found

        return True


class VirusScanValidator:
    """
    Validator for virus/malware scanning integration.
    Wraps the MalwareScanner functionality for consistency with other validators.
    """

    def __init__(self, scanner_type: str = "clamav"):
        self.scanner = MalwareScanner(scanner_type)

    def validate(self, file: UploadedFile) -> None:
        """
        Validate file through virus/malware scanning.
        Raises ValidationError if virus is detected.
        """
        if not self.scanner.scan(file):
            raise ValidationError("File contains malware or virus")


class CompositeFileValidator:
    """
    Combines multiple validators into a single validator.
    """

    def __init__(self):
        self.validators = [
            FileTypeValidator(),
            FileSizeValidator(),
            FileContentValidator(),
            VirusScanValidator(),
        ]

    def validate(self, file: UploadedFile) -> str:
        """
        Run all validators and return the file checksum if valid.
        """
        for validator in self.validators:
            validator.validate(file)

        # Calculate and return checksum for integrity tracking
        return FileIntegrityValidator.calculate_checksum(file)
