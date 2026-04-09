# Generated manually for multi-step application forms

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("application_forms", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="formtype",
            name="step_definitions",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='Optional list of steps: [{"key": "step1", "title": "...", "field_names": ["a","b"]}, ...]. '
                "When empty, the form is single-step (all fields at once).",
            ),
        ),
    ]
