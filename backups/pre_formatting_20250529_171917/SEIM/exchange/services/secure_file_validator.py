"""
Enhanced security measures for file uploads and validation.
"""

import hashlib
import logging
import os
import re

import magic
from django.conf import settings
from django.core.exceptions import ValidationError

from ..models import Document

# Setup logger
logger = logging.getLogger(__name__)


class SecureFileValidator:
    """
    Service for validating and securing file uploads
    """

    # Define allowed file types and maximum sizes
    ALLOWED_MIME_TYPES = {
        "application/pdf": [".pdf"],
        "image/jpeg": [".jpg", ".jpeg"],
        "image/png": [".png"],
        "application/msword": [".doc"],
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [
            ".docx"
        ],
        "application/vnd.ms-excel": [".xls"],
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
        "text/plain": [".txt"],
    }

    # Maximum file size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    # Suspicious patterns (potential malware signatures)
    SUSPICIOUS_PATTERNS = [
        rb"<%.*%>",  # ASP/JSP tags
        rb"<\?php",  # PHP open tag
        rb"eval\s*\(",  # JavaScript eval
        rb"system\s*\(",  # System calls
        rb"exec\s*\(",  # Exec calls
        rb"function\s*\(\)\s*{",  # JavaScript functions
        rb"\.bash_history",  # Unix shell history
        rb"VIRUS",  # Generic virus signature
    ]

    @classmethod
    def validate_file(cls, file_obj, allowed_extensions=None):
        """
        Validate a file upload for security

        Args:
            file_obj: The uploaded file object
            allowed_extensions: Optional list of allowed extensions to override defaults

        Returns:
            bool, str: Tuple of (is_valid, error_message)

        Raises:
            ValidationError: If the file fails validation
        """
        if not file_obj:
            raise ValidationError("No file was submitted.")

        # Check file size
        if file_obj.size > cls.MAX_FILE_SIZE:
            raise ValidationError(
                f"The file is too large. Maximum size is {cls.MAX_FILE_SIZE / (1024 * 1024)}MB."
            )

        # Verify extension matches content type
        original_filename = file_obj.name
        extension = os.path.splitext(original_filename)[1].lower()

        if allowed_extensions and extension not in allowed_extensions:
            raise ValidationError(
                f"Invalid file extension. Allowed extensions are {', '.join(allowed_extensions)}."
            )

        # Check MIME type using python-magic
        file_content = file_obj.read()
        file_obj.seek(0)  # Reset file pointer

        try:
            mime_type = magic.from_buffer(file_content, mime=True)

            # Verify MIME type is allowed
            if mime_type not in cls.ALLOWED_MIME_TYPES:
                raise ValidationError(
                    f"File type '{mime_type}' is not allowed. Allowed types are: "
                    f"{', '.join([ext for exts in cls.ALLOWED_MIME_TYPES.values() for ext in exts])}."
                )

            # Verify extension matches MIME type
            allowed_extensions_for_mime = cls.ALLOWED_MIME_TYPES.get(mime_type, [])
            if extension not in allowed_extensions_for_mime:
                raise ValidationError(
                    f"File extension '{extension}' does not match the actual file type '{mime_type}'."
                )

            # Scan for suspicious patterns
            for pattern in cls.SUSPICIOUS_PATTERNS:
                if re.search(pattern, file_content):
                    logger.warning(
                        f"Suspicious content detected in uploaded file: {original_filename}. "
                        f"Pattern: {pattern}"
                    )
                    raise ValidationError(
                        "This file contains potentially unsafe content and cannot be uploaded."
                    )

        except magic.MagicException as e:
            logger.error(f"Error analyzing file content: {str(e)}")
            raise ValidationError("Unable to verify file type. Please try again.")

        # Calculate file hash for integrity checking
        file_hash = hashlib.sha256(file_content).hexdigest()

        return file_hash

    @classmethod
    def scan_file_content(cls, file_path):
        """
        Perform a deeper scan of a file's content for malicious code

        Args:
            file_path: Path to the file

        Returns:
            bool, str: Tuple of (is_safe, reason)
        """
        try:
            with open(file_path, "rb") as f:
                content = f.read()

            # Scan for suspicious patterns
            for pattern in cls.SUSPICIOUS_PATTERNS:
                if re.search(pattern, content):
                    logger.warning(
                        f"Suspicious content detected in file: {file_path}. "
                        f"Pattern: {pattern}"
                    )
                    return False, f"Suspicious pattern detected: {pattern}"

            # Additional security checks could be added here
            # For example, integrating with external virus scanning API

            return True, "File passed security scan"

        except Exception as e:
            logger.error(f"Error scanning file content: {str(e)}")
            return False, f"Error scanning file: {str(e)}"

    @classmethod
    def verify_file_integrity(cls, document):
        """
        Verify the integrity of a stored document

        Args:
            document: Document model instance

        Returns:
            bool: True if integrity check passes
        """
        try:
            # Get file path
            file_path = document.file.path

            # Calculate current hash
            with open(file_path, "rb") as f:
                current_hash = hashlib.sha256(f.read()).hexdigest()

            # Compare with stored hash
            return current_hash == document.file_hash

        except Exception as e:
            logger.error(f"Error verifying file integrity: {str(e)}")
            return False
