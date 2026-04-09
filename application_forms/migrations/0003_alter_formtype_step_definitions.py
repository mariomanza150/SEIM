# Generated to align DB schema state with FormType.step_definitions help_text

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("application_forms", "0002_formtype_step_definitions"),
    ]

    operations = [
        migrations.AlterField(
            model_name="formtype",
            name="step_definitions",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='Multi-step layout: list of {"key", "title", "field_names": [...]}. Empty = single-step form.',
            ),
        ),
    ]
