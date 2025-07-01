from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100)
    iso_code = models.CharField(max_length=3, unique=True)
    region = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name
