from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("exchange", "0027_application_nomination_rank"),
    ]

    operations = [
        migrations.AlterField(
            model_name="savedsearch",
            name="search_type",
            field=models.CharField(
                choices=[
                    ("program", "Program Search"),
                    ("application", "Application Search"),
                    ("exchange_agreement", "Exchange agreement registry"),
                    ("document", "Application document list"),
                    ("agreement_document", "Agreement document repository"),
                    ("calendar", "Deadlines / calendar view"),
                    ("analytics_forecast", "Analytics forecasts"),
                ],
                help_text="Type of search (programs, applications, or staff list views)",
                max_length=20,
            ),
        ),
    ]
