"""Root leftover Django app URLs that now live in the Vue SPA under ``/seim/``.

Registered before Wagtail's ``""`` catch-all so bookmarks, emails, and
notification ``action_url`` values do not fall through to CMS 404s.
"""

from django.http import HttpResponseRedirect
from django.urls import path
from django.views.generic import RedirectView


def _spa(target):
    return RedirectView.as_view(url=f"/seim/{target}", permanent=False)


def legacy_application_detail(request, pk):
    return HttpResponseRedirect(f"/seim/applications/{pk}")


def legacy_application_edit(request, pk):
    return HttpResponseRedirect(f"/seim/applications/{pk}/edit")


urlpatterns = [
    path(
        "applications/create/",
        _spa("applications/new"),
        name="legacy_applications_create",
    ),
    path(
        "applications/new/",
        _spa("applications/new"),
        name="legacy_applications_new",
    ),
    path(
        "applications/<uuid:pk>/edit/",
        legacy_application_edit,
        name="legacy_application_edit",
    ),
    path(
        "applications/<uuid:pk>/",
        legacy_application_detail,
        name="legacy_application_detail",
    ),
    path("applications/", _spa("applications/"), name="legacy_applications"),
    path("profile/", _spa("profile/"), name="legacy_profile"),
    path("settings/", _spa("settings/"), name="legacy_settings"),
    path("preferences/", _spa("settings/"), name="legacy_preferences"),
    path("calendar/", _spa("calendar/"), name="legacy_calendar"),
    path("documents/", _spa("documents/"), name="legacy_documents"),
    path("notifications/", _spa("notifications/"), name="legacy_notifications"),
    path("review-queue/", _spa("review-queue/"), name="legacy_review_queue"),
    path(
        "programs/compare/",
        _spa("programs/compare"),
        name="legacy_program_compare",
    ),
]
