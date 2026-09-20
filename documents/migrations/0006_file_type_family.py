from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0005_documenttype_catalog_phase4"),
    ]

    operations = [
        migrations.CreateModel(
            name="FileTypeFamily",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("slug", models.SlugField(max_length=40, unique=True)),
                ("name", models.CharField(max_length=80)),
                (
                    "aliases",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Search synonyms, comma-separated.",
                        max_length=240,
                    ),
                ),
                (
                    "extensions",
                    models.CharField(
                        help_text="Comma-separated extensions without dots (e.g. jpg,jpeg,png).",
                        max_length=240,
                    ),
                ),
                ("sort_order", models.PositiveIntegerField(default=100)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "File type family",
                "verbose_name_plural": "File type families",
                "ordering": ["sort_order", "name"],
            },
        ),
        migrations.AlterField(
            model_name="documenttype",
            name="accepted_extensions",
            field=models.CharField(
                blank=True,
                default="",
                help_text=(
                    "Extra extensions beyond selected families, comma-separated without dots. "
                    "Empty with no families = global defaults."
                ),
                max_length=120,
            ),
        ),
        migrations.AddField(
            model_name="documenttype",
            name="file_type_families",
            field=models.ManyToManyField(
                blank=True,
                help_text="Umbrella file groups (Image, Word, PDF, …).",
                related_name="document_types",
                to="documents.filetypefamily",
            ),
        ),
    ]
