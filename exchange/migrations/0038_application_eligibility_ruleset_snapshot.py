# Apply-time freeze of eligibility ruleset document for historical evaluation

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exchange", "0037_scholarship_scoring_ruleset"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="eligibility_ruleset_snapshot",
            field=models.JSONField(
                blank=True,
                help_text=(
                    "Frozen eligibility ruleset document at apply/submit "
                    "(id, schema_version, content_revision, rules_json). "
                    "Re-evaluations prefer this over the live program ruleset."
                ),
                null=True,
            ),
        ),
    ]
