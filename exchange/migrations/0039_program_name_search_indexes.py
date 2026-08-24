from django.db import migrations, models


def create_program_search_gin(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(
        """
        CREATE INDEX IF NOT EXISTS program_name_desc_search_gin
        ON exchange_program
        USING GIN (to_tsvector('simple', coalesce(name, '') || ' ' || coalesce(description, '')));
        """
    )


def drop_program_search_gin(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute("DROP INDEX IF EXISTS program_name_desc_search_gin;")


class Migration(migrations.Migration):
    dependencies = [
        ("exchange", "0038_application_eligibility_ruleset_snapshot"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="program",
            index=models.Index(fields=["name"], name="program_name_idx"),
        ),
        migrations.RunPython(create_program_search_gin, drop_program_search_gin),
    ]
