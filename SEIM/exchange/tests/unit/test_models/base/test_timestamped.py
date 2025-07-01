import pytest
import time
from django.utils import timezone
from exchange.models.base.timestamped import Timestamped

pytestmark = pytest.mark.django_db

class ConcreteTimestamped(Timestamped):
    class Meta:
        app_label = 'test_app'
        managed = True

class TestTimestamped:
    def test_created_and_updated_fields(self):
        obj = ConcreteTimestamped.objects.create()
        assert obj.created_at is not None
        assert obj.updated_at is not None
        assert abs((obj.updated_at - obj.created_at).total_seconds()) < 1

    def test_is_new_property(self):
        obj = ConcreteTimestamped.objects.create()
        assert obj.is_new is True
        # Simulate old object
        obj.created_at = timezone.now() - timezone.timedelta(hours=2)
        obj.save()
        assert obj.is_new is False

    def test_recently_updated_property(self):
        obj = ConcreteTimestamped.objects.create()
        assert obj.recently_updated is True
        # Simulate old update
        obj.updated_at = timezone.now() - timezone.timedelta(minutes=20)
        obj.save()
        assert obj.recently_updated is False 