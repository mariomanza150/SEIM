# Ensure Django is properly installed and configured.
from django.db import models

class State(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name

    @staticmethod
    def prepopulate_states():
        states = [
            {"name": "California", "abbreviation": "CA"},
            {"name": "Texas", "abbreviation": "TX"},
            {"name": "New York", "abbreviation": "NY"},
            # Add more states as needed
        ]
        for state in states:
            State.objects.get_or_create(name=state["name"], abbreviation=state["abbreviation"])
