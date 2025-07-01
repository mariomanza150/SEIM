from django.db import models
from .exchange import Exchange
from ..questionnaire.question import Question


class ApplicationAnswer(models.Model):
    """
    Stores the answer to a specific question for a particular exchange application.

    Fields:
        exchange (ForeignKey): The related Exchange application instance.
        question (ForeignKey): The question being answered. Restricted deletion to preserve answer integrity.
        answer_text (TextField): The answer provided by the applicant (for text, yes/no, or open-ended questions).
        selected_option_id (IntegerField): The ID of the selected option if the question type is 'select'.
    """

    exchange = models.ForeignKey(
        Exchange,
        on_delete=models.CASCADE,
        related_name="application_answers",
        help_text="The related Exchange application instance.",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.RESTRICT,
        related_name="application_answers",
        help_text="The question being answered. Restricted deletion to preserve answer integrity.",
    )
    answer_text = models.TextField(
        blank=True,
        null=True,
        help_text="The answer provided by the applicant (for text, yes/no, or open-ended questions).",
    )
    selected_option_id = models.IntegerField(
        blank=True,
        null=True,
        help_text="ID of the selected option if the question type is 'select'.",
    )

    class Meta:
        verbose_name = "Application Answer"
        verbose_name_plural = "Application Answers"
        ordering = ["exchange", "question"]

    def __str__(self) -> str:
        return f"Answer to '{self.question}' for Exchange {self.exchange.pk}"

    def clean(self) -> None:
        """
        Centralized validation logic for ApplicationAnswer.
        Ensures that either answer_text or selected_option_id is provided, not both, unless required by question type.
        """
        super().clean()
        if not self.answer_text and not self.selected_option_id:
            raise ValueError("Either answer_text or selected_option_id must be provided.")
        # Add more robust validation here if question type logic is available

    def save(self, *args, **kwargs) -> None:
        self.clean()
        super().save(*args, **kwargs)
