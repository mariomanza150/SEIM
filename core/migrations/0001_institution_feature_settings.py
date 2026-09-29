# Generated manually for InstitutionFeatureSettings singleton

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="InstitutionFeatureSettings",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "scholarships_enabled",
                    models.BooleanField(
                        default=True,
                        help_text=(
                            "When false, hide scholarship scoring, ruleset editor, awards, "
                            "and cohort exports (data is retained)."
                        ),
                    ),
                ),
            ],
            options={
                "verbose_name": "Institution feature settings",
                "verbose_name_plural": "Institution feature settings",
            },
        ),
    ]
