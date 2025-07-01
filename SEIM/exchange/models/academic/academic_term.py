from django.db import models
from ..base import Option

class AcademicTerm(Option):
    SEASONS = (
        ("SPRING", "Spring"),
        ("SUMMER", "Summer"),
        ("AUTUMN", "Autumn"),
        ("WINTER", "Winter"),
    )

    start_date = models.DateField()
    end_date = models.DateField()

    

