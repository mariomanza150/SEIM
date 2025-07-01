import pytest
from django.db import models
from exchange.models.base.option import Option

pytestmark = pytest.mark.django_db

class ConcreteOption(Option):
    class Meta:
        app_label = 'test_app'
        managed = True

class TestOption:
    def test_create_option_defaults(self):
        obj = ConcreteOption.objects.create(name="opt1", label="Option 1", description="desc", active=True)
        assert obj.name == "opt1"
        assert obj.label == "Option 1"
        assert obj.description == "desc"
        assert obj.active is True

    def test_str_method(self):
        obj = ConcreteOption.objects.create(name="opt2", label="Label 2", description="", active=True)
        assert str(obj) == "Label 2" 