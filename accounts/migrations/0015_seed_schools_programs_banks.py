from django.db import migrations

from accounts.profile_catalogs import seed_profile_catalogs


def seed_schools_programs_banks(apps, schema_editor):
    seed_profile_catalogs(
        school_model=apps.get_model("accounts", "SchoolFaculty"),
        program_model=apps.get_model("accounts", "HomeAcademicProgram"),
        bank_model=apps.get_model("accounts", "BankInstitution"),
    )


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0014_mobility_eligibility_phase1"),
    ]

    operations = [
        migrations.RunPython(
            seed_schools_programs_banks,
            reverse_code=migrations.RunPython.noop,
        )
    ]
