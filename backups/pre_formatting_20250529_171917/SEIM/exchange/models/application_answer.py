from django.db import models

from .exchange import Exchange
from .question import Question


class ApplicationAnswer(models.Model):
    """
    Stores the answer to a specific question for a particular exchange application.
    """

    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    question = models.ForeignKey(
        Question, on_delete=models.RESTRICT
    )  # avoid having answers without a question
    answer_text = models.TextField(blank=True, null=True)  # For text and yes/no answers
    selected_option_id = models.IntegerField(
        blank=True,
        null=True,
        help_text="ID of the selected option if the question type is 'select'.",
    )
