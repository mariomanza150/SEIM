from django.contrib.auth.models import User
from django.db import models

class BaseProfile(models.Model):
    """
    Abstract base class for user profile containing common fields
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.user.username}"