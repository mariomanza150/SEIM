"""Spoken-language catalog and canonical profile/program language values."""

import uuid

from django.db import migrations, models

from accounts.language_catalog import LANGUAGE_SPECS, seed_spoken_languages


def _norm(value):
    return (value or "").strip().casefold()


def _build_index(languages):
    index = {}
    for row in languages:
        canonical = (row.get("name") or "").strip()
        if not canonical:
            continue
        index[_norm(canonical)] = canonical
        for alias in row.get("aliases") or []:
            alias_text = str(alias or "").strip()
            if alias_text:
                index[_norm(alias_text)] = canonical
    return index


def seed_and_normalize_languages(apps, schema_editor):
    SpokenLanguage = apps.get_model("accounts", "SpokenLanguage")
    Profile = apps.get_model("accounts", "Profile")
    Program = apps.get_model("exchange", "Program")

    seed_spoken_languages(spoken_language_model=SpokenLanguage)
    index = _build_index(
        SpokenLanguage.objects.all().values("name", "aliases")
    )

    for profile in Profile.objects.exclude(language__isnull=True).exclude(language=""):
        canonical = index.get(_norm(profile.language))
        if canonical and profile.language != canonical:
            profile.language = canonical
            profile.save(update_fields=["language", "updated_at"])

    for profile in Profile.objects.all():
        rows = profile.additional_languages or []
        if not rows:
            continue
        normalized = []
        changed = False
        for item in rows:
            if not isinstance(item, dict):
                changed = True
                continue
            name = str(item.get("name", "")).strip()
            if not name:
                changed = True
                continue
            canonical = index.get(_norm(name)) or name
            if canonical != name:
                changed = True
            level = str(item.get("level", "")).strip() or ""
            normalized.append({"name": canonical, "level": level})
        if changed:
            profile.additional_languages = normalized
            profile.save(update_fields=["additional_languages", "updated_at"])

    for program in Program.objects.exclude(required_language__isnull=True).exclude(
        required_language=""
    ):
        canonical = index.get(_norm(program.required_language))
        if canonical and program.required_language != canonical:
            program.required_language = canonical
            program.save(update_fields=["required_language", "updated_at"])

    Program.objects.filter(name__icontains="Maestria").update(
        required_language=None,
        min_language_level=None,
    )

    try:
        from exchange.views import _invalidate_program_api_caches

        _invalidate_program_api_caches()
    except Exception:
        pass


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0023_deactivate_orphan_unidades"),
    ]

    operations = [
        migrations.CreateModel(
            name="SpokenLanguage",
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
                ("name", models.CharField(max_length=150)),
                ("code", models.CharField(blank=True, default="", max_length=50)),
                ("is_active", models.BooleanField(default=True)),
                ("ordering", models.PositiveIntegerField(default=0)),
                (
                    "aliases",
                    models.JSONField(
                        blank=True,
                        default=list,
                        help_text="Alternate spellings that resolve to this language (case-insensitive).",
                    ),
                ),
            ],
            options={
                "ordering": ["ordering", "name"],
            },
        ),
        migrations.RunPython(seed_and_normalize_languages, migrations.RunPython.noop),
    ]
