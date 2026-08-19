# UADEC catalog alignment: Program.min_toefl_score

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exchange", "0032_application_subject_plan_version"),
    ]

    operations = [
        migrations.AddField(
            model_name="program",
            name="min_toefl_score",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Minimum TOEFL score required for eligibility (when set).",
                null=True,
            ),
        ),
    ]
