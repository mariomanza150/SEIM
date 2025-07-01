from django.db import models
from ..base import Timestamped
import re

class ApplicationStatus(Timestamped):
    """
    Represents a possible status for an exchange application (e.g., Submitted, Under Review, Approved).

    Fields:
        name (CharField): The display name of the status.
        color_code (CharField): Hex color code for UI representation.
    """
    name = models.CharField(max_length=100, help_text="Display name of the status.")
    color_code = models.CharField(max_length=7, default='#000000', help_text="Hex color code for UI tags.")

    def __str__(self):
        return self.name

    def clean(self):
        """
        Validate that color_code is a valid hex color string.
        """
        super().clean()
        if not re.match(r'^#[0-9A-Fa-f]{6}$', self.color_code):
            raise ValueError(f"color_code '{self.color_code}' is not a valid hex color.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def is_terminal(self):
        """
        Return True if this status is a terminal state (e.g., Approved, Rejected).
        """
        return self.name in ["Approved", "Rejected"]
