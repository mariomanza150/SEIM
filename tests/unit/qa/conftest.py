import io

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Role

User = get_user_model()


@pytest.fixture
def tools_on(settings):
    settings.TESTER_TOOLS_ENABLED = True
    settings.DEPLOY_TIER = "test"
    return settings


def _user(email, *, role=None, **extra):
    user = User.objects.create_user(
        username=email.split("@")[0], email=email, password="x-Long-pass-123", **extra
    )
    if role:
        user.roles.add(Role.objects.get_or_create(name=role)[0])
    return user


@pytest.fixture
def make_user(db):
    return _user


@pytest.fixture
def tester(db):
    return _user("tester@example.com", role="student", is_tester=True)


@pytest.fixture
def admin_tester(db):
    return _user("boss@example.com", role="admin", is_tester=True, is_staff=True)


@pytest.fixture
def plain_user(db):
    return _user("plain@example.com", role="student")


def client_for(user, **claims):
    client = APIClient()
    token = RefreshToken.for_user(user)
    access = token.access_token
    for k, v in claims.items():
        access[k] = v
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    return client


@pytest.fixture
def png_file():
    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", (20, 10), (200, 10, 10)).save(buf, format="PNG")
    return SimpleUploadedFile("shot.png", buf.getvalue(), content_type="image/png")
