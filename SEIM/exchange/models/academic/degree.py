from django.db import models
from ..university import University
from ..institution import Institution
from ..campus import Campus
from ..config_model import ConfigModel

class Degree(ConfigModel):
    code = models.CharField(max_length=20, blank=True)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.university.name})"
