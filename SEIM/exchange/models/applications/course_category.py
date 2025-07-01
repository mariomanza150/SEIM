from django.db import models
from ..base_models.timestamped_model import TimestampedModel

class CourseCategory(TimestampedModel):
    """
    Represents a category for courses (e.g., Core, Elective, Language, etc.).

    Fields:
        name (CharField): The name of the course category.
        description (TextField): A description of the category and its use cases.
        is_mandatory (BooleanField): Whether this category is mandatory for a program.
    """
    name = models.CharField(max_length=100, help_text="Name of the course category.")
    description = models.TextField(blank=True, help_text="Description and use cases for this category.")
    is_mandatory = models.BooleanField(default=False, help_text="Is this category mandatory?")

    def __str__(self):
        return self.name

    def is_language_category(self) -> bool:
        return 'language' in self.name.lower()
