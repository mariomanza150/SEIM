"""
Comment and Review models for the exchange app.

This module contains models for user comments and (optionally) reviews on exchange applications.
- Comment: For internal notes, student-visible comments, and official communications.
- Review: (Consider splitting into a separate file if it grows large.)
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Comment(models.Model):
    """
    Model for comments on exchange applications.

    Fields:
        exchange (ForeignKey): The related Exchange application.
        author (ForeignKey): The user who wrote the comment.
        comment_type (CharField): Type of comment (internal, student, official).
        text (TextField): The comment content.
        created_at (DateTimeField): When the comment was created.
        is_edited (BooleanField): Whether the comment has been edited.
        edited_at (DateTimeField): When the comment was last edited.
        original_text (TextField): The original text before editing.
        is_viewed_by_student (BooleanField): If the student has viewed the comment.
        viewed_at (DateTimeField): When the student viewed the comment.
    """

    # Comment types
    COMMENT_TYPES = (
        ("INTERNAL", "Internal Note"),
        ("STUDENT", "Student Visible"),
        ("OFFICIAL", "Official Communication"),
    )

    exchange = models.ForeignKey("Exchange", on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exchange_comments")
    comment_type = models.CharField(max_length=10, choices=COMMENT_TYPES, default="INTERNAL")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # For tracking comment edits
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(blank=True, null=True)
    original_text = models.TextField(blank=True, null=True)

    # For tracking if the student has viewed the comment
    is_viewed_by_student = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(blank=True, null=True)

    def edit(self, new_text: str) -> None:
        """Edit a comment, preserving the original text and updating timestamps."""
        if not self.is_edited:
            self.original_text = self.text

        self.text = new_text
        self.is_edited = True
        self.edited_at = timezone.now()
        self.save()
        # Trigger any hooks or signals for comment edit here if needed

    def mark_as_viewed(self) -> None:
        """Mark comment as viewed by the student and update timestamp."""
        if not self.is_viewed_by_student:
            self.is_viewed_by_student = True
            self.viewed_at = timezone.now()
            self.save()
        # Trigger any hooks or signals for comment viewed here if needed

    def __str__(self):
        # Defensive fallback for display methods
        comment_type = dict(self.COMMENT_TYPES).get(self.comment_type, self.comment_type)
        author = getattr(self.author, 'username', str(self.author))
        created = self.created_at.strftime('%Y-%m-%d') if self.created_at else ''
        return f"{comment_type} by {author} on {created}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Comment"
        verbose_name_plural = "Comments"


# Consider moving Review model to its own file if it grows large or complex.
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

    exchange = models.ForeignKey("Exchange", on_delete=models.CASCADE, related_name="reviews")
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

    def revise(self, new_decision: str, reason: str) -> None:
        """Revise a review decision"""
        self.previous_decision = self.decision
        self.decision = new_decision
        self.is_revised = True
        self.revised_at = timezone.now()
        self.revision_reason = reason
        self.save()
        # Trigger any hooks or signals for review revision here if needed

    def __str__(self):
        review_type = dict(self.REVIEW_TYPES).get(self.review_type, self.review_type)
        decision = dict(self.DECISION_CHOICES).get(self.decision, self.decision)
        reviewer = getattr(self.reviewer, 'username', str(self.reviewer))
        return f"{review_type} by {reviewer} - {decision}"

    class Meta:
        ordering = ["-reviewed_at"]
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
