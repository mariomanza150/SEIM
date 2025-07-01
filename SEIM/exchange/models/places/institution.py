from django.db import models
from ..base_models.config_model import ConfigModel
from .campus import Campus
from ..people.contact_profile import ContactProfile

class Institution(ConfigModel):
    main_contact = models.ForeignKey(ContactProfile, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name} - {self.university.name}"
