# Deactivate legacy Unidad rows with no linked faculties (blocks profile completion).

from django.db import migrations


def deactivate_orphan_unidades(apps, schema_editor):
    Unidad = apps.get_model("accounts", "Unidad")
    SchoolFaculty = apps.get_model("accounts", "SchoolFaculty")
    for unidad in Unidad.objects.filter(is_active=True):
        has_schools = SchoolFaculty.objects.filter(
            unidad_id=unidad.id, is_active=True
        ).exists()
        if not has_schools:
            unidad.is_active = False
            unidad.save(update_fields=["is_active"])


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0022_seed_uadec_profile_catalogs"),
    ]

    operations = [
        migrations.RunPython(deactivate_orphan_unidades, migrations.RunPython.noop),
    ]
