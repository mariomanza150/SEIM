# Generated migration for SGII Phase 3 - Bulk Action models

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("exchange", "0002_comment_course_grade_review_timeline_workflowlog_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="BulkAction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "action_type",
                    models.CharField(
                        choices=[
                            ("APPROVE", "Bulk Approve"),
                            ("REJECT", "Bulk Reject"),
                            ("STATUS_UPDATE", "Status Update"),
                            ("ASSIGN", "Bulk Assign"),
                            ("DELETE", "Bulk Delete"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("IN_PROGRESS", "In Progress"),
                            ("COMPLETED", "Completed"),
                            ("FAILED", "Failed"),
                            ("CANCELLED", "Cancelled"),
                        ],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                ("performed_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "comment",
                    models.TextField(
                        blank=True, help_text="Comment or reason for the bulk action"
                    ),
                ),
                (
                    "target_status",
                    models.CharField(
                        blank=True,
                        help_text="Target status for status updates",
                        max_length=50,
                    ),
                ),
                ("total_items", models.PositiveIntegerField(default=0)),
                ("successful_items", models.PositiveIntegerField(default=0)),
                ("failed_items", models.PositiveIntegerField(default=0)),
                (
                    "metadata",
                    models.JSONField(
                        blank=True, default=dict, help_text="Additional action metadata"
                    ),
                ),
                (
                    "error_details",
                    models.TextField(
                        blank=True,
                        help_text="Detailed error information if action failed",
                    ),
                ),
                (
                    "assigned_to",
                    models.ForeignKey(
                        blank=True,
                        help_text="User assigned to for bulk assignment actions",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="assigned_bulk_actions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "performed_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bulk_actions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-performed_at"],
            },
        ),
        migrations.CreateModel(
            name="BulkActionLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "level",
                    models.CharField(
                        choices=[
                            ("DEBUG", "Debug"),
                            ("INFO", "Info"),
                            ("WARNING", "Warning"),
                            ("ERROR", "Error"),
                            ("CRITICAL", "Critical"),
                        ],
                        default="INFO",
                        max_length=10,
                    ),
                ),
                ("message", models.TextField()),
                ("details", models.JSONField(blank=True, default=dict)),
                (
                    "bulk_action",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="logs",
                        to="exchange.bulkaction",
                    ),
                ),
            ],
            options={
                "ordering": ["timestamp"],
            },
        ),
        migrations.CreateModel(
            name="BulkActionItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("SUCCESS", "Success"),
                            ("FAILED", "Failed"),
                            ("SKIPPED", "Skipped"),
                        ],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                ("processed_at", models.DateTimeField(blank=True, null=True)),
                ("error_message", models.TextField(blank=True)),
                ("original_values", models.JSONField(blank=True, default=dict)),
                ("new_values", models.JSONField(blank=True, default=dict)),
                (
                    "bulk_action",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="exchange.bulkaction",
                    ),
                ),
                (
                    "exchange",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bulk_action_items",
                        to="exchange.exchange",
                    ),
                ),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.AddIndex(
            model_name="bulkactionlog",
            index=models.Index(
                fields=["bulk_action", "timestamp"],
                name="exchange_bu_bulk_ac_c89c5d_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="bulkactionlog",
            index=models.Index(fields=["level"], name="exchange_bu_level_5c9a0f_idx"),
        ),
        migrations.AddIndex(
            model_name="bulkactionitem",
            index=models.Index(
                fields=["bulk_action", "status"], name="exchange_bu_bulk_ac_0c8b5a_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="bulkactionitem",
            index=models.Index(
                fields=["exchange"], name="exchange_bu_exchang_47e4c1_idx"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="bulkactionitem",
            unique_together={("bulk_action", "exchange")},
        ),
        migrations.AddIndex(
            model_name="bulkaction",
            index=models.Index(
                fields=["action_type", "performed_at"],
                name="exchange_bu_action__4f7e2d_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="bulkaction",
            index=models.Index(
                fields=["performed_by", "performed_at"],
                name="exchange_bu_perform_9a1c8e_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="bulkaction",
            index=models.Index(fields=["status"], name="exchange_bu_status_d2e5a3_idx"),
        ),
    ]
