from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exchange", "0006_savedsearch"),
    ]

    operations = [
        migrations.AddField(
            model_name="program",
            name="application_deadline",
            field=models.DateField(
                blank=True,
                help_text="Last date students can create a new application for this program.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="program",
            name="application_open_date",
            field=models.DateField(
                blank=True,
                help_text="Date when students can begin submitting new applications.",
                null=True,
            ),
        ),
    ]
