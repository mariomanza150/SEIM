# Generated manually to add created_at field to Document model
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exchange", "0009_add_profile_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]
