import pytest
from django.core.management import call_command

from accounts.models import Role, User


@pytest.mark.django_db
def test_assign_user_roles_command():
    # Create a regular user (not staff, not superuser)
    user = User.objects.create(username='testuser', email='test@example.com')

    # Run the command
    call_command('assign_user_roles')

    # Refresh the user from database
    user.refresh_from_db()

    # Check that the user has been assigned the student role
    assert user.roles.exists()
    Role.objects.get(name='student')
    assert user.roles.filter(name='student').exists()
