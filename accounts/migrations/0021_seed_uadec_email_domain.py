# Add uadec.edu.mx allowed email domain; deactivate uanl.edu.mx

from django.db import migrations


def seed_uadec_email_domain(apps, schema_editor):
    AllowedEmailDomain = apps.get_model("accounts", "AllowedEmailDomain")
    AllowedEmailDomain.objects.update_or_create(
        name="uadec.edu.mx",
        defaults={"code": "uadec", "is_active": True, "ordering": 100},
    )
    AllowedEmailDomain.objects.filter(name="uanl.edu.mx").update(is_active=False)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0020_uadec_catalog_alignment"),
    ]

    operations = [
        migrations.RunPython(seed_uadec_email_domain, migrations.RunPython.noop),
    ]
