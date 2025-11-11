import pytest
from django.contrib.auth import get_user_model

from accounts.models import Profile


@pytest.mark.django_db
def test_profile_created_on_user_creation():
    User = get_user_model()
    user = User.objects.create(username='signaluser')
    assert Profile.objects.filter(user=user).exists()
