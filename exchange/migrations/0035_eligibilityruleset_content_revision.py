# Generated manually for eligibility ruleset document schema v2 + content_revision

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exchange", "0034_lifecycle_requirement_schedule"),
    ]

    operations = [
        migrations.AddField(
            model_name="eligibilityruleset",
            name="content_revision",
            field=models.PositiveIntegerField(
                default=1,
                help_text="Increments when rules_json changes (edit versioning).",
            ),
        ),
        migrations.AlterField(
            model_name="eligibilityruleset",
            name="schema_version",
            field=models.PositiveIntegerField(default=2),
        ),
    ]
