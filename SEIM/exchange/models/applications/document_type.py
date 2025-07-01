from django.db import models
from ..base_models.timestamped_model import TimestampedModel

class DocumentStage(models.TextChoices):
    APPLICATION = 'APPLICATION', 'Application'
    REVIEW = 'REVIEW', 'Review'
    ACCEPTANCE = 'ACCEPTANCE', 'Acceptance'
    FINALIZATION = 'FINALIZATION', 'Finalization'

class DocumentType(TimestampedModel):
    """
    Represents a type of document required in the exchange process.

    Fields:
        name (CharField): Name of the document type.
        description (TextField): Description of the document type.
        required_for_stage (CharField): Stage at which the document is required.
        upload_instructions (TextField): Instructions for uploading the document.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    required_for_stage = models.CharField(max_length=20, choices=DocumentStage.choices)
    upload_instructions = models.TextField(blank=True)

    def __str__(self):
        return self.name
