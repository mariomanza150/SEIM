"""Default gender options (codes match the legacy hard-coded Profile choices)."""

from __future__ import annotations

# (code, label_es, label_en)
GENDER_SPECS: tuple[tuple[str, str, str], ...] = (
    ("female", "Femenino", "Female"),
    ("male", "Masculino", "Male"),
    ("non_binary", "No binario", "Non-binary"),
    ("other", "Otro", "Other"),
    ("prefer_not_to_say", "Prefiero no decirlo", "Prefer not to say"),
)


def seed_gender_options(*, gender_model=None, profile_model=None):
    """Create default options (get_or_create by code) and keep legacy values valid.

    Any distinct ``Profile.gender`` value not covered by the defaults gets its own
    active option so no existing profile is left with an unknown code.
    """
    if gender_model is None:
        from accounts.models import GenderOption

        gender_model = GenderOption
    created = []
    for ordering, (code, label_es, label_en) in enumerate(GENDER_SPECS):
        option, was_created = gender_model.objects.get_or_create(
            code=code,
            defaults={
                "name": label_es,
                "label_en": label_en,
                "is_active": True,
                "ordering": ordering,
            },
        )
        if was_created:
            created.append(option)
    if profile_model is not None:
        known = set(gender_model.objects.values_list("code", flat=True))
        legacy = (
            profile_model.objects.exclude(gender="")
            .exclude(gender__isnull=True)
            .exclude(gender__in=known)
            .values_list("gender", flat=True)
            .distinct()
        )
        for offset, code in enumerate(sorted(set(legacy))):
            created.append(
                gender_model.objects.create(
                    code=code,
                    name=code,
                    label_en=code,
                    is_active=True,
                    ordering=len(GENDER_SPECS) + offset,
                )
            )
    return created
