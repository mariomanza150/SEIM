import pytest
from rest_framework import serializers

from accounts.serializers import ProfileSerializer


def test_validate_additional_languages_ok():
    ser = ProfileSerializer()
    out = ser.validate_additional_languages(
        [{"name": "  French  ", "level": "B1"}, {"name": "Japanese", "level": ""}]
    )
    assert out == [{"name": "French", "level": "B1"}, {"name": "Japanese", "level": ""}]


def test_validate_additional_languages_rejects_bad_level():
    ser = ProfileSerializer()
    with pytest.raises(serializers.ValidationError):
        ser.validate_additional_languages([{"name": "x", "level": "X9"}])


def test_validate_additional_languages_rejects_empty_name():
    ser = ProfileSerializer()
    with pytest.raises(serializers.ValidationError):
        ser.validate_additional_languages([{"name": "  ", "level": "A1"}])


def test_validate_additional_languages_max_length():
    ser = ProfileSerializer()
    with pytest.raises(serializers.ValidationError):
        ser.validate_additional_languages([{"name": "x", "level": "A1"}] * 21)
