import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0003_alter_document_uploaded_by"),
        ("exchange", "0009_exchange_agreement"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ExchangeAgreementDocument",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("signed_copy", "Signed copy"),
                            ("amendment", "Amendment / addendum"),
                            ("mou", "Memorandum of understanding"),
                            ("annex", "Annex / schedule"),
                            ("correspondence", "Correspondence"),
                            ("other", "Other"),
                        ],
                        db_index=True,
                        default="other",
                        max_length=32,
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Optional label shown in lists (defaults to filename if empty).",
                        max_length=255,
                    ),
                ),
                (
                    "file",
                    models.FileField(upload_to="agreement_repository/%Y/%m/"),
                ),
                ("notes", models.TextField(blank=True, default="")),
                (
                    "agreement",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="repository_documents",
                        to="exchange.exchangeagreement",
                    ),
                ),
                (
                    "supersedes",
                    models.ForeignKey(
                        blank=True,
                        help_text="Prior upload this file replaces (keeps history). Same agreement and category.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="successors",
                        to="documents.exchangeagreementdocument",
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Agreement repository document",
                "verbose_name_plural": "Agreement repository documents",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="exchangeagreementdocument",
            index=models.Index(
                fields=["agreement", "category", "-created_at"],
                name="agrdoc_agr_cat_crt_idx",
            ),
        ),
    ]
