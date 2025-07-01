"""
Comment and Review models for the exchange app.
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Comment(models.Model):
    """
    Model for comments on exchange applications
    """

    # Comment types
    COMMENT_TYPES = (
        ("INTERNAL", "Internal Note"),
        ("STUDENT", "Student Visible"),
        ("OFFICIAL", "Official Communication"),
    )

    exchange = models.ForeignKey(
        "Exchange", on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="exchange_comments"
    )
    comment_type = models.CharField(
        max_length=10, choices=COMMENT_TYPES, default="INTERNAL"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # For tracking comment edits
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(blank=True, null=True)
    original_text = models.TextField(blank=True, null=True)

    # For tracking if the student has viewed the comment
    is_viewed_by_student = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(blank=True, null=True)

    def edit(self, new_text):
        """Edit a comment, preserving the original text"""
        if not self.is_edited:
            self.original_text = self.text

        self.text = new_text
        self.is_edited = True
        self.edited_at = timezone.now()
        self.save()

    def mark_as_viewed(self):
        """Mark comment as viewed by the student"""
        if not self.is_viewed_by_student:
            self.is_viewed_by_student = True
            self.viewed_at = timezone.now()
            self.save()

    def __str__(self):
        return f"{self.get_comment_type_display()} by {self.author} on {self.created_at.strftime('%Y-%m-%d')}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Comment"
        verbose_name_plural = "Comments"


class Review(models.Model):
    """
    Model for formal reviews of exchange applications
    """

    # Review types
    REVIEW_TYPES = (
        ("ACADEMIC", "Academic Review"),
        ("FINANCIAL", "Financial Review"),
        ("ADMINISTRATIVE", "Administrative Review"),
        ("FINAL", "Final Decision"),
    )

    # Review decisions
    DECISION_CHOICES = (
        ("APPROVED", "Approved"),
        ("CONDITIONALLY_APPROVED", "Conditionally Approved"),
        ("REJECTED", "Rejected"),
        ("DEFERRED", "Deferred"),
        ("MORE_INFO", "More Information Needed"),
    )

    exchange = models.ForeignKey(
        "Exchange", on_delete=models.CASCADE, related_name="reviews"
    )
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    review_type = models.CharField(max_length=15, choices=REVIEW_TYPES)
    decision = models.CharField(max_length=25, choices=DECISION_CHOICES)

    # Review details
    comments = models.TextField()
    conditions = models.TextField(blank=True, null=True)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    # For tracking if the review was revised
    is_revised = models.BooleanField(default=False)
    revised_at = models.DateTimeField(blank=True, null=True)
    revision_reason = models.TextField(blank=True, null=True)
    previous_decision = models.CharField(max_length=25, blank=True, null=True)

    def revise(self, new_decision, reason):
        """Revise a review decision"""
        self.previous_decision = self.decision
        self.decision = new_decision
        self.is_revised = True
        self.revised_at = timezone.now()
        self.revision_reason = reason
        self.save()

    def __str__(self):
        return f"{self.get_review_type_display()} by {self.reviewer} - {self.get_decision_display()}"

    class Meta:
        ordering = ["-reviewed_at"]
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
