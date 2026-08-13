from django.db import migrations


def seed_student_profile_catalogs(apps, schema_editor):
    AcademicLevel = apps.get_model("accounts", "AcademicLevel")
    AllowedEmailDomain = apps.get_model("accounts", "AllowedEmailDomain")
    Unidad = apps.get_model("accounts", "Unidad")

    levels = (
        ("Licenciatura", "licenciatura"),
        ("Maestría", "maestria"),
        ("Bachillerato", "bachillerato"),
        ("Investigación", "investigacion"),
    )
    for ordering, (name, code) in enumerate(levels):
        AcademicLevel.objects.update_or_create(
            name=name,
            defaults={"code": code, "is_active": True, "ordering": ordering},
        )

    unidades = ("Sureste", "Laguna", "Norte")
    for ordering, name in enumerate(unidades):
        Unidad.objects.update_or_create(
            name=name,
            defaults={
                "code": name.lower(),
                "is_active": True,
                "ordering": ordering,
            },
        )

    AllowedEmailDomain.objects.update_or_create(
        name="uanl.edu.mx",
        defaults={"code": "uanl", "is_active": True, "ordering": 0},
    )


class Migration(migrations.Migration):
    dependencies = [
        (
            "accounts",
            "0012_academiclevel_allowedemaildomain_bankinstitution_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(
            seed_student_profile_catalogs,
            reverse_code=migrations.RunPython.noop,
        )
    ]
