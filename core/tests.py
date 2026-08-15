"""Core app tests collected by pytest (see pytest.ini testpaths)."""

from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model

from application_forms.models import FormType
from core.views import DynamicFormFromSchema

User = get_user_model()


@pytest.mark.django_db
def test_health_live_is_independent_of_backends(client):
    response = client.get("/health/live/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "live"
    assert "version" in payload
    assert "environment" in payload


@pytest.mark.django_db
def test_anonymous_user_sees_marketing_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Student Exchange Information Manager" in response.content


@pytest.mark.django_db
def test_authenticated_user_is_redirected_to_spa_dashboard(client):
    User.objects.create_user(
        username="homeuser", email="home@test.com", password="testpass123"
    )
    assert client.login(username="homeuser", password="testpass123")
    response = client.get("/")
    assert response.status_code == 302
    assert response.url == "/seim/dashboard/"


@pytest.mark.django_db
def test_logout_clears_session_and_sets_jwt_clear_cookie(client):
    User.objects.create_user(
        username="logoutuser", email="logout@test.com", password="testpass123"
    )
    assert client.login(username="logoutuser", password="testpass123")
    assert "_auth_user_id" in client.session

    response = client.get("/logout/")

    assert response.status_code == 302
    assert response.url == "/seim/login/"
    assert "_auth_user_id" not in client.session
    assert response.cookies["clear_jwt_tokens"].value == "true"


def test_missing_form_type_builds_no_fields():
    form = DynamicFormFromSchema(None)
    assert len(form.fields) == 0


def test_form_type_without_schema_builds_no_fields():
    form_type = MagicMock()
    form_type.schema = None
    form = DynamicFormFromSchema(form_type)
    assert len(form.fields) == 0


@pytest.mark.django_db
def test_custom_form_type_is_used_for_contact_when_active(client):
    FormType.objects.create(
        name="Custom Contact",
        form_type="custom",
        is_active=True,
        schema={
            "properties": {"topic": {"type": "string", "title": "Topic"}},
            "required": ["topic"],
        },
    )
    response = client.get("/contact/")
    assert response.status_code == 200
    assert b"topic" in response.content


@pytest.mark.django_db
def test_cache_get_mismatch_marks_unhealthy(client):
    with patch("core.views.cache") as mock_cache:
        mock_cache.set.return_value = True
        mock_cache.get.return_value = "stale"
        response = client.get("/health/")

    assert response.status_code == 503
    assert "unhealthy" in response.json()["services"]["cache"]
