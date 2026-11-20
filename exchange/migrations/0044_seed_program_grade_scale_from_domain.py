"""Seed outgoing Program grade-scale settings from AllowedEmailDomain (non-destructive).

When active domains agree on a single (default_grade_scale, lock_grade_scale) pair,
copy that onto outgoing programs that still have no default. Conflicting domain
policies are left alone so runtime domain fallback keeps working.
"""

from django.db import migrations


def seed_program_grade_scales_from_domains(apps, schema_editor):
    from exchange.models import seed_outgoing_programs_from_domain_policy

    seed_outgoing_programs_from_domain_policy(
        apps.get_model("exchange", "Program"),
        apps.get_model("accounts", "AllowedEmailDomain"),
    )


def unseed_program_grade_scales_from_domains(apps, schema_editor):
    from exchange.models import unseed_outgoing_programs_from_domain_policy

    unseed_outgoing_programs_from_domain_policy(
        apps.get_model("exchange", "Program"),
        apps.get_model("accounts", "AllowedEmailDomain"),
    )


class Migration(migrations.Migration):
    dependencies = [
        ("exchange", "0043_program_host_dest_and_grade_scale"),
        ("accounts", "0027_allowed_domain_grade_scale_lock"),
    ]

    operations = [
        migrations.RunPython(
            seed_program_grade_scales_from_domains,
            unseed_program_grade_scales_from_domains,
        ),
    ]
