from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("exchange", "0039_program_name_search_indexes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="exchangeagreement",
            name="agreement_type",
            field=models.CharField(
                choices=[
                    ("bilateral", "Bilateral"),
                    ("multilateral", "Multilateral"),
                    ("erasmus", "Erasmus+"),
                    ("conahec", "CONAHEC"),
                    ("specific", "Specific program"),
                    ("other", "Other"),
                ],
                default="bilateral",
                max_length=32,
            ),
        ),
    ]
