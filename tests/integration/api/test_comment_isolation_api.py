"""IDOR guards for application and document comments."""

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status

from documents.models import Document, DocumentComment, DocumentType
from exchange.models import Comment
from tests.utils import APITestCase


class TestApplicationCommentIsolationAPI(APITestCase):
    def setUp(self):
        super().setUp()
        self.owner = self.create_user(
            role="student", username="cmt_owner", email="cmt_owner@example.com"
        )
        self.other = self.create_user(
            role="student", username="cmt_other", email="cmt_other@example.com"
        )
        self.coordinator = self.create_user(
            role="coordinator", username="cmt_coord", email="cmt_coord@example.com"
        )
        self.program = self.create_program()
        self.application = self.create_application(
            student=self.owner, program=self.program, status_name="draft"
        )
        self.staff_comment = Comment.objects.create(
            application=self.application,
            author=self.coordinator,
            text="Staff note",
            is_private=False,
        )

    def test_other_student_cannot_create_comment(self):
        self.authenticate_user(self.other)
        response = self.client.post(
            reverse("api:comment-list"),
            {
                "application": str(self.application.id),
                "text": "cross app",
                "is_private": False,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_create_public_comment(self):
        self.authenticate_user(self.owner)
        response = self.client.post(
            reverse("api:comment-list"),
            {
                "application": str(self.application.id),
                "text": "my note",
                "is_private": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = Comment.objects.get(id=response.data["id"])
        self.assertFalse(comment.is_private)

    def test_other_student_cannot_delete_staff_comment(self):
        self.authenticate_user(self.other)
        response = self.client.delete(
            reverse("api:comment-detail", kwargs={"pk": self.staff_comment.pk})
        )
        self.assertIn(
            response.status_code,
            (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND),
        )
        self.assertTrue(Comment.objects.filter(pk=self.staff_comment.pk).exists())

    def test_owner_cannot_delete_staff_comment(self):
        self.authenticate_user(self.owner)
        response = self.client.delete(
            reverse("api:comment-detail", kwargs={"pk": self.staff_comment.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Comment.objects.filter(pk=self.staff_comment.pk).exists())


class TestDocumentCommentIsolationAPI(APITestCase):
    def setUp(self):
        super().setUp()
        self.owner = self.create_user(
            role="student", username="dc_owner", email="dc_owner@example.com"
        )
        self.other = self.create_user(
            role="student", username="dc_other", email="dc_other@example.com"
        )
        self.coordinator = self.create_user(
            role="coordinator", username="dc_coord", email="dc_coord@example.com"
        )
        program = self.create_program()
        application = self.create_application(
            student=self.owner, program=program, status_name="draft"
        )
        doc_type = DocumentType.objects.create(name="comment_iso_type")
        self.document = Document.objects.create(
            application=application,
            type=doc_type,
            file=SimpleUploadedFile(
                "c.pdf", b"%PDF-1.4 c", content_type="application/pdf"
            ),
            uploaded_by=self.owner,
        )
        self.staff_comment = DocumentComment.objects.create(
            document=self.document,
            author=self.coordinator,
            text="Staff doc note",
            is_private=False,
        )

    def test_other_student_cannot_create_document_comment(self):
        self.authenticate_user(self.other)
        response = self.client.post(
            reverse("api:documentcomment-list"),
            {
                "document": str(self.document.id),
                "text": "nope",
                "is_private": False,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_cannot_delete_staff_document_comment(self):
        self.authenticate_user(self.owner)
        response = self.client.delete(
            reverse("api:documentcomment-detail", kwargs={"pk": self.staff_comment.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            DocumentComment.objects.filter(pk=self.staff_comment.pk).exists()
        )
