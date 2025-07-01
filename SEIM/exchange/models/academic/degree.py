from django.db import models

from ..places.university import University
from ..places.institution import Institution
from ..places.campus import Campus
from ..base import Option

class Degree(Option):
    code = models.CharField(max_length=20, blank=True)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.university.name})"
