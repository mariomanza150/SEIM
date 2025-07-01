from django.apps import apps
from django.db import models as djm

from ..config_model import ConfigModel


class Question(djm.Model):
    QUESTION_TYPES = [
        ("yes_no", "Yes/No"),
        ("text", "Text"),
        ("select", "Select"),
    ]

    text = djm.CharField(max_length=255)
    question_type = djm.CharField(max_length=10, choices=QUESTION_TYPES)
    select_model = djm.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Specify model for select (e.g., 'app_label.ModelName').",
    )

    @staticmethod
    def prepopulate_questions():
        questions = [
            {"text": "Do you agree?", "question_type": "yes_no"},
            {"text": "Provide your feedback.", "question_type": "text"},
            {"text": "Select your preference.", "question_type": "select"},
        ]
        for question in questions:
            Question.objects.get_or_create(
                text=question["text"], question_type=question["question_type"]
            )

    def validate_select_model(self):
        """Validates the select_model to ensure it references a valid Django model."""
        if self.select_model:
            try:
                apps.get_model(self.select_model)
            except LookupError:
                raise ValueError(f"Invalid model reference: {self.select_model}")

    def save(self, *args, **kwargs):
        self.validate_select_model()
        super().save(*args, **kwargs)

class QuestionSet(ConfigModel):
    questions = djm.ManyToManyField(Question, related_name="question_set")
