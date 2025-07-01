from django.db import models
from ..config_model import ConfigModel
from ...timestamp_base import TimestampedModel

class ProficiencyLevels(ConfigModel):
    SCALE_TYPES = (
        ("NUMERIC", "Numeric"),
        ("ALPHABETIC", "Alphabetic"),
        ("ALPHANUMERIC", "Alphanumeric"),
    )
    scale_type = models.CharField(choices=SCALE_TYPES)
    min_level = models.CharField()
    max_level = models.CharField()
    has_plus = models.BooleanField()

class Language(ConfigModel, TimestampedModel):
    iso_code = models.CharField(max_length=10)

    def __str__(self):
        pass

class LanguageProficiencyTest(ConfigModel, TimestampedModel):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    scale = models.ForeignKey(ProficiencyLevels, on_delete=models.CASCADE)
    min_score = models.CharField()
    max_score = models.CharField()
