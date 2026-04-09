from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("application_forms", "0004_formsteptemplate"),
    ]

    operations = [
        migrations.AlterField(
            model_name="formtype",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="created_application_forms",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
