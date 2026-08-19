# Re-seed UAdeC profile catalogs after SchoolFaculty.unidad FK is available.

from django.db import migrations

from accounts.profile_catalogs import seed_profile_catalogs


def seed_uadec_catalogs(apps, schema_editor):
    seed_profile_catalogs(
        school_model=apps.get_model("accounts", "SchoolFaculty"),
        program_model=apps.get_model("accounts", "HomeAcademicProgram"),
        bank_model=apps.get_model("accounts", "BankInstitution"),
        unidad_model=apps.get_model("accounts", "Unidad"),
    )


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0021_seed_uadec_email_domain"),
    ]

    operations = [
        migrations.RunPython(seed_uadec_catalogs, migrations.RunPython.noop),
    ]
