# Generated to align DB schema state with Application.dynamic_form_current_step help_text

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exchange", "0012_program_required_document_types"),
    ]

    operations = [
        migrations.AlterField(
            model_name="application",
            name="dynamic_form_current_step",
            field=models.CharField(
                blank=True,
                help_text="Current step key when the program uses a multi-step application form (see FormType.step_definitions).",
                max_length=64,
                null=True,
            ),
        ),
    ]
