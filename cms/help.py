"""SPA help-center helpers for FAQ pages (audiences, surfaces, API serialization)."""

from django.db.models import Q

FAQ_AUDIENCE_STUDENT = "student"
FAQ_AUDIENCE_COORDINATOR = "coordinator"
FAQ_AUDIENCE_PARTNER = "partner"
FAQ_AUDIENCE_ADMIN = "admin"
FAQ_AUDIENCE_ALL = "all"

FAQ_AUDIENCE_CHOICES = [
    (FAQ_AUDIENCE_STUDENT, "Student"),
    (FAQ_AUDIENCE_COORDINATOR, "Coordinator"),
    (FAQ_AUDIENCE_PARTNER, "Partner"),
    (FAQ_AUDIENCE_ADMIN, "Admin"),
    (FAQ_AUDIENCE_ALL, "All roles"),
]

FAQ_SURFACE_PUBLIC = "public"
FAQ_SURFACE_SPA = "spa"

FAQ_SURFACE_CHOICES = [
    (FAQ_SURFACE_PUBLIC, "Public site"),
    (FAQ_SURFACE_SPA, "In-app (SPA)"),
]

FAQ_INDEX_KIND_PUBLIC = "public"
FAQ_INDEX_KIND_SPA_HELP = "spa_help"

FAQ_INDEX_KIND_CHOICES = [
    (FAQ_INDEX_KIND_PUBLIC, "Public FAQ index"),
    (FAQ_INDEX_KIND_SPA_HELP, "SPA help index (not public)"),
]

FAQ_TOPIC_CHOICES = [
    ("getting_started", "Getting started"),
    ("applications", "Applications"),
    ("documents", "Documents"),
    ("review", "Review"),
    ("partner", "Partner"),
    ("admin", "Admin"),
    ("account", "Account"),
]

# SPA auth store uses ``responsible``; CMS audience labels stay Coordinator.
# ``coordinator`` remains as a legacy role-name alias during/after rename.
HELP_AUDIENCE_BY_ROLE = {
    "student": (FAQ_AUDIENCE_STUDENT, FAQ_AUDIENCE_ALL),
    "responsible": (
        FAQ_AUDIENCE_COORDINATOR,
        FAQ_AUDIENCE_STUDENT,
        FAQ_AUDIENCE_ALL,
    ),
    "coordinator": (
        FAQ_AUDIENCE_COORDINATOR,
        FAQ_AUDIENCE_STUDENT,
        FAQ_AUDIENCE_ALL,
    ),
    "partner": (FAQ_AUDIENCE_PARTNER, FAQ_AUDIENCE_ALL),
    "admin": (
        FAQ_AUDIENCE_ADMIN,
        FAQ_AUDIENCE_COORDINATOR,
        FAQ_AUDIENCE_STUDENT,
        FAQ_AUDIENCE_ALL,
    ),
}

SPA_HELP_INDEX_SLUG = "ayuda-seim"
PUBLIC_FAQ_INDEX_SLUG = "preguntas-frecuentes"

PUBLIC_FAQ_SLUGS = (
    "requisitos-aplicar",
    "costo-intercambio",
    "revalidacion-creditos",
    "trabajar-intercambio",
    "emergencia-extranjero",
)


def default_faq_audiences():
    return [FAQ_AUDIENCE_STUDENT]


def default_faq_surfaces():
    return [FAQ_SURFACE_PUBLIC, FAQ_SURFACE_SPA]


def _as_token_list(value):
    if not value:
        return []
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    if isinstance(value, (list, tuple, set)):
        return [str(part).strip() for part in value if str(part).strip()]
    return []


def parse_contextual_keys(value):
    return _as_token_list(value)


def has_surface(page, surface):
    return surface in _as_token_list(getattr(page, "surfaces", None))


def is_publicly_servable_faq(page):
    return has_surface(page, FAQ_SURFACE_PUBLIC)


def is_spa_help_index(page):
    return getattr(page, "index_kind", FAQ_INDEX_KIND_PUBLIC) == FAQ_INDEX_KIND_SPA_HELP


def audience_codes_for_user(user):
    if user is None or not getattr(user, "is_authenticated", False):
        return ()
    if getattr(user, "is_superuser", False) or getattr(user, "is_admin", False):
        role = "admin"
    else:
        role = getattr(user, "primary_role", None) or "student"
    return HELP_AUDIENCE_BY_ROLE.get(role, (FAQ_AUDIENCE_ALL,))


def help_article_queryset_for_user(user):
    from cms.models import FAQPage

    allowed = audience_codes_for_user(user)
    audience_q = Q()
    for code in allowed:
        audience_q |= Q(audiences__contains=[code])
    if not allowed:
        return FAQPage.objects.none()
    return (
        FAQPage.objects.live()
        .filter(surfaces__contains=[FAQ_SURFACE_SPA])
        .filter(audience_q)
        .order_by("topic", "title")
    )


def render_faq_body_html(page):
    body = getattr(page, "body", None)
    if not body:
        return ""
    return "".join(block.render() for block in body)


def serialize_help_article(page):
    return {
        "slug": page.slug,
        "title": page.title,
        "introduction": page.introduction or "",
        "topic": page.topic or "",
        "contextual_keys": parse_contextual_keys(page.contextual_keys),
        "body_html": render_faq_body_html(page),
    }


def spa_only_faq_page_ids():
    from cms.models import FAQPage

    return list(
        FAQPage.objects.exclude(surfaces__contains=[FAQ_SURFACE_PUBLIC]).values_list(
            "id", flat=True
        )
    )


def spa_help_index_page_ids():
    from cms.models import FAQIndexPage

    return list(
        FAQIndexPage.objects.filter(index_kind=FAQ_INDEX_KIND_SPA_HELP).values_list(
            "id", flat=True
        )
    )
