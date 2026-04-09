# Generated manually for multi-step application forms

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exchange", "0010_agreement_expiration_reminder_log"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="dynamic_form_current_step",
            field=models.CharField(
                blank=True,
                help_text="Key of the current step for multi-step program forms (matches FormType.step_definitions).",
                max_length=64,
                null=True,
            ),
        ),
    ]
