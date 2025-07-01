import pytest
from exchange.models.base.logged import Logged
from exchange.models.base.base_profile import BaseProfile

pytestmark = pytest.mark.django_db

class TestLogged:
    def test_logged_fields_and_relations(self):
        user1 = BaseProfile.objects.create_user(username="creator", password="pass")
        user2 = BaseProfile.objects.create_user(username="updater", password="pass")
        log = Logged.objects.create(created_by=user1, updated_by=user2)
        assert log.created_by.username == "creator"
        assert log.updated_by.username == "updater"
        # Test related_name
        assert log in user1.logged_created_set.all()
        assert log in user2.logged_updated_set.all() 