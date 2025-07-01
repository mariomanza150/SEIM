from django.db import models
from ..config_model import ConfigModel

class AcademicTerm(ConfigModel):
    SEASONS = (
        ("SPRING", "Spring"),
        ("SUMMER", "Summer"),
        ("AUTUMN", "Autumn"),
        ("WINTER", "Winter"),
    )

    start_date = models.DateField()
    end_date = models.DateField()

    

