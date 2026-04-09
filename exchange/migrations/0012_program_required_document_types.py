# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0004_exchangeagreementdocument"),
        ("exchange", "0011_application_dynamic_form_current_step"),
    ]

    operations = [
        migrations.AddField(
            model_name="program",
            name="required_document_types",
            field=models.ManyToManyField(
                blank=True,
                help_text="Applicants must upload these document types and have them marked valid before submitting.",
                related_name="programs_requiring",
                to="documents.documenttype",
            ),
        ),
    ]
