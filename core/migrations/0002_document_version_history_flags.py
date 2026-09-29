# Generated manually for document version history institution flags

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_institution_feature_settings"),
    ]

    operations = [
        migrations.AddField(
            model_name="institutionfeaturesettings",
            name="document_version_history_enabled",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "Master switch for application-document version history UI/API. "
                    "When false, no role sees prior file versions."
                ),
            ),
        ),
        migrations.AddField(
            model_name="institutionfeaturesettings",
            name="document_version_history_student",
            field=models.BooleanField(
                default=False,
                help_text="When history is enabled, students may see prior versions.",
            ),
        ),
        migrations.AddField(
            model_name="institutionfeaturesettings",
            name="document_version_history_coordinator",
            field=models.BooleanField(
                default=True,
                help_text="When history is enabled, coordinators may see prior versions.",
            ),
        ),
        migrations.AddField(
            model_name="institutionfeaturesettings",
            name="document_version_history_admin",
            field=models.BooleanField(
                default=True,
                help_text="When history is enabled, admins may see prior versions.",
            ),
        ),
    ]
