"""Seed GenderOption with the legacy hard-coded choices (and any stray codes)."""

from django.db import migrations

from accounts.gender_catalog import seed_gender_options


def seed(apps, schema_editor):
    seed_gender_options(
        gender_model=apps.get_model("accounts", "GenderOption"),
        profile_model=apps.get_model("accounts", "Profile"),
    )


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0025_gender_option_birthplace_credits"),
    ]

    operations = [
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
