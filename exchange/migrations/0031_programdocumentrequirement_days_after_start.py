from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("exchange", "0030_host_subject_grades"),
    ]

    operations = [
        migrations.AddField(
            model_name="programdocumentrequirement",
            name="deadline_days_after_program_start",
            field=models.PositiveIntegerField(
                blank=True,
                help_text=(
                    "Relative deadline: N days after the program start_date "
                    "(e.g. arrival certificates due after mobility begins)."
                ),
                null=True,
            ),
        ),
    ]
