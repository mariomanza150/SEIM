from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounts", "0024_rename_coordinator_role_to_responsible"),
    ]

    operations = [
        migrations.CreateModel(
            name="PracticeAttempt",
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
                    "external_session_id",
                    models.CharField(db_index=True, max_length=64, unique=True),
                ),
                ("exam_code", models.CharField(blank=True, default="", max_length=128)),
                ("macro_id", models.CharField(blank=True, default="", max_length=128)),
                ("client_ref", models.CharField(blank=True, default="", max_length=128)),
                ("earned", models.PositiveIntegerField(default=0)),
                ("total", models.PositiveIntegerField(default=0)),
                ("percent", models.FloatField(default=0.0)),
                ("categories", models.JSONField(blank=True, default=list)),
                ("weakest", models.JSONField(blank=True, default=list)),
                ("items", models.JSONField(blank=True, default=list)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("raw_payload", models.JSONField(blank=True, default=dict)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="toefl_practice_attempts",
                        to="accounts.user",
                    ),
                ),
            ],
            options={
                "ordering": ["-completed_at", "-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="practiceattempt",
            index=models.Index(
                fields=["user", "-completed_at"],
                name="toefl_pract_user_id_c8a0f0_idx",
            ),
        ),
    ]
