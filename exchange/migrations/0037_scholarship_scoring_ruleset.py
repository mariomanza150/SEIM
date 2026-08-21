# Generated manually for ScholarshipScoringRuleset (factor weight editor)

import uuid

from django.db import migrations, models


def seed_default_ruleset(apps, schema_editor):
    ScholarshipScoringRuleset = apps.get_model("exchange", "ScholarshipScoringRuleset")
    if ScholarshipScoringRuleset.objects.exists():
        return
    ScholarshipScoringRuleset.objects.create(
        id=uuid.uuid4(),
        slug="default_v1",
        label="Default scholarship rubric (v1)",
        description=(
            "Built-in transparent rubric. Edit factor max weights to "
            "rebalance academic, language, fit, quality, and timeliness."
        ),
        factor_weights={
            "academic": 25.0,
            "language": 20.0,
            "program_fit": 15.0,
            "application_quality": 25.0,
            "timeliness": 15.0,
        },
        is_active=True,
    )


def unseed_default_ruleset(apps, schema_editor):
    ScholarshipScoringRuleset = apps.get_model("exchange", "ScholarshipScoringRuleset")
    ScholarshipScoringRuleset.objects.filter(slug="default_v1").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("exchange", "0036_nomination_cycles_and_partner_allocations"),
    ]

    operations = [
        migrations.CreateModel(
            name="ScholarshipScoringRuleset",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("slug", models.SlugField(max_length=64, unique=True)),
                ("label", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, default="")),
                ("factor_weights", models.JSONField(blank=True, default=dict)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
            ],
            options={
                "verbose_name": "Scholarship scoring ruleset",
                "verbose_name_plural": "Scholarship scoring rulesets",
                "ordering": ["label", "-created_at"],
            },
        ),
        migrations.RunPython(seed_default_ruleset, unseed_default_ruleset),
    ]
