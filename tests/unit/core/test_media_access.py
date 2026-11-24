"""Regression tests: protected MEDIA uploads are not world-readable."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Role
from core.media_access import (
    MediaAccessKind,
    classify_media_path,
    normalize_media_path,
    user_may_access_media,
)
from documents.models import Document, DocumentType
from exchange.models import Application, ApplicationStatus, Program

User = get_user_model()

PDF_BYTES = b"%PDF-1.4 synthetic-test-doc"


def _ensure_role(name: str) -> Role:
    role, _ = Role.objects.get_or_create(name=name)
    return role


def _make_user(*, username: str, email: str, role: str) -> User:
    user = User.objects.create_user(
        username=username, email=email, password="TestPass123!"
    )
    user.roles.add(_ensure_role(role))
    return user


def _make_document(*, student: User, filename: str = "test-doc.pdf") -> Document:
    program = Program.objects.create(
        name="Synthetic Exchange Program",
        description="Synthetic fixture program",
        is_active=True,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 6, 30),
    )
    status, _ = ApplicationStatus.objects.get_or_create(
        name="draft", defaults={"order": 1}
    )
    application = Application.objects.create(
        student=student, program=program, status=status
    )
    doc_type = DocumentType.objects.create(
        name="Synthetic Transcript", description="Synthetic fixture type"
    )
    return Document.objects.create(
        application=application,
        type=doc_type,
        uploaded_by=student,
        file=SimpleUploadedFile(filename, PDF_BYTES, content_type="application/pdf"),
    )


@pytest.mark.django_db
class TestMediaPathHelpers:
    def test_normalize_rejects_traversal(self):
        assert normalize_media_path("../secrets.txt") is None
        assert normalize_media_path("documents/../../secrets.txt") is None
        assert normalize_media_path("") is None
        # Leading slash is stripped; path stays relative to MEDIA_ROOT.
        assert normalize_media_path("/images/logo.png") == "images/logo.png"

    def test_classify_public_and_protected(self):
        assert classify_media_path("images/logo.png") == MediaAccessKind.PUBLIC
        assert (
            classify_media_path("original_images/photo.jpg") == MediaAccessKind.PUBLIC
        )
        assert (
            classify_media_path("documents/test-doc.pdf") == MediaAccessKind.PROTECTED
        )
        assert (
            classify_media_path("agreement_repository/2024/01/x.pdf")
            == MediaAccessKind.PROTECTED
        )


@pytest.mark.django_db
class TestProtectedMediaHttpAccess:
    def test_unauthenticated_media_document_denied(self):
        owner = _make_user(
            username="owner1", email="student1@example.com", role="student"
        )
        document = _make_document(student=owner)
        media_url = document.file.url
        assert media_url.startswith("/media/")

        client = Client()
        response = client.get(media_url)
        assert response.status_code in (401, 403, 404)
        body = (
            b"".join(response.streaming_content)
            if hasattr(response, "streaming_content")
            else response.content
        )
        assert body != PDF_BYTES
        assert PDF_BYTES not in body

    def test_other_student_cannot_fetch_media_path(self):
        owner = _make_user(
            username="owner2", email="student1@example.com", role="student"
        )
        other = _make_user(
            username="other2", email="student2@example.com", role="student"
        )
        document = _make_document(student=owner, filename="other-denied.pdf")
        media_url = document.file.url

        client = Client()
        client.force_login(other)
        response = client.get(media_url)
        assert response.status_code in (403, 404)
        body = (
            b"".join(response.streaming_content)
            if hasattr(response, "streaming_content")
            else response.content
        )
        assert body != PDF_BYTES

    def test_owner_can_fetch_via_media_session(self):
        owner = _make_user(
            username="owner3", email="student1@example.com", role="student"
        )
        document = _make_document(student=owner, filename="owner-ok.pdf")
        media_url = document.file.url

        client = Client()
        client.force_login(owner)
        response = client.get(media_url)
        assert response.status_code == 200
        body = (
            b"".join(response.streaming_content)
            if hasattr(response, "streaming_content")
            else response.content
        )
        assert body == PDF_BYTES

    def test_admin_can_fetch_via_media_session(self):
        owner = _make_user(
            username="owner4", email="student1@example.com", role="student"
        )
        admin = _make_user(username="admin4", email="admin1@example.com", role="admin")
        document = _make_document(student=owner, filename="admin-ok.pdf")
        media_url = document.file.url

        client = Client()
        client.force_login(admin)
        response = client.get(media_url)
        assert response.status_code == 200
        body = (
            b"".join(response.streaming_content)
            if hasattr(response, "streaming_content")
            else response.content
        )
        assert body == PDF_BYTES

    def test_owner_preview_api_still_works(self):
        owner = _make_user(
            username="owner5", email="student1@example.com", role="student"
        )
        document = _make_document(student=owner, filename="preview-ok.pdf")
        api = APIClient()
        api.force_authenticate(user=owner)
        url = reverse("api:document-preview", args=[document.id])
        response = api.get(url)
        assert response.status_code == 200
        body = (
            b"".join(response.streaming_content)
            if hasattr(response, "streaming_content")
            else response.content
        )
        assert body == PDF_BYTES

    def test_staff_preview_api_still_works(self):
        owner = _make_user(
            username="owner6", email="student1@example.com", role="student"
        )
        coordinator = _make_user(
            username="coord6", email="coord1@example.com", role="coordinator"
        )
        document = _make_document(student=owner, filename="preview-staff.pdf")
        api = APIClient()
        api.force_authenticate(user=coordinator)
        url = reverse("api:document-preview", args=[document.id])
        response = api.get(url)
        assert response.status_code == 200

    def test_other_student_preview_api_denied(self):
        owner = _make_user(
            username="owner7", email="student1@example.com", role="student"
        )
        other = _make_user(
            username="other7", email="student2@example.com", role="student"
        )
        document = _make_document(student=owner, filename="preview-denied.pdf")
        api = APIClient()
        api.force_authenticate(user=other)
        url = reverse("api:document-preview", args=[document.id])
        response = api.get(url)
        assert response.status_code in (403, 404)

    def test_jwt_bearer_can_fetch_own_media(self):
        owner = _make_user(
            username="owner8", email="student1@example.com", role="student"
        )
        document = _make_document(student=owner, filename="jwt-ok.pdf")
        token = RefreshToken.for_user(owner).access_token
        client = Client()
        response = client.get(document.file.url, HTTP_AUTHORIZATION=f"Bearer {token}")
        assert response.status_code == 200
        body = (
            b"".join(response.streaming_content)
            if hasattr(response, "streaming_content")
            else response.content
        )
        assert body == PDF_BYTES

    def test_public_cms_image_still_serves(self):
        media_dir = Path(settings.MEDIA_ROOT) / "images"
        media_dir.mkdir(parents=True, exist_ok=True)
        sample = media_dir / "public-brand.png"
        payload = b"\x89PNG\r\n\x1a\npublic-fixture"
        sample.write_bytes(payload)
        try:
            client = Client()
            response = client.get("/media/images/public-brand.png")
            assert response.status_code == 200
            body = (
                b"".join(response.streaming_content)
                if hasattr(response, "streaming_content")
                else response.content
            )
            assert body == payload
        finally:
            sample.unlink(missing_ok=True)

    def test_static_assets_still_reachable(self):
        """Public static URL prefix must not be blocked by the media ACL."""
        client = Client()
        response = client.get("/static/")
        # Missing file/dir may 404, but must not be an auth challenge.
        assert response.status_code != 401
        assert response.status_code != 403

    @override_settings(USE_X_ACCEL_REDIRECT=True, MEDIA_INTERNAL_URL="/internal_media/")
    def test_x_accel_redirect_for_authorized_owner(self):
        owner = _make_user(
            username="owner9", email="student1@example.com", role="student"
        )
        document = _make_document(student=owner, filename="accel-ok.pdf")
        client = Client()
        client.force_login(owner)
        response = client.get(document.file.url)
        assert response.status_code == 200
        assert response["X-Accel-Redirect"].startswith("/internal_media/")
        assert "documents/" in response["X-Accel-Redirect"]


@pytest.mark.django_db
class TestMediaAccessDecisionUnit:
    def test_anonymous_denied_for_document_path(self):
        from django.contrib.auth.models import AnonymousUser

        decision = user_may_access_media(AnonymousUser(), "documents/orphan.pdf")
        assert decision.allowed is False
        assert decision.status == 401
