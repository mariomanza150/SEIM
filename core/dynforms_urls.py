"""
Legacy /dynforms/ operator URLs now redirect into the Vue visual builder.

Keeps login + admin checks so non-admins still receive 403.
"""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import path
from django.views import View


class _DynformsAdminRequired(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        return bool(getattr(user, "is_admin", False))


class DynformsSpaRedirect(LoginRequiredMixin, _DynformsAdminRequired, View):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        if pk:
            return redirect(f"/seim/admin/dynforms/{pk}")
        return redirect("/seim/admin/dynforms")

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


_redirect = DynformsSpaRedirect.as_view()

urlpatterns = [
    path("", _redirect, name="dynforms-list"),
    path("new/", _redirect, name="dynforms-create-type"),
    path("builder/<int:pk>/", _redirect, name="dynforms-builder"),
    path("<int:pk>/run/", _redirect, name="dynforms-run"),
    path("<int:pk>/check/", _redirect, name="dynforms-check"),
    path("<int:pk>/edit/", _redirect, name="dynforms-edit-template"),
    path("<int:pk>/delete/", _redirect, name="dynforms-delete-type"),
    path(
        "<int:pk>/<int:page>/add/<slug:type>/<int:pos>/",
        _redirect,
        name="dynforms-add-field",
    ),
    path(
        "<int:pk>/<int:page>/del/<int:pos>/",
        _redirect,
        name="dynforms-del-field",
    ),
    path(
        "<int:pk>/<int:page>/clone/<int:pos>/",
        _redirect,
        name="dynforms-clone-field",
    ),
    path("<int:pk>/<int:page>/del/", _redirect, name="dynforms-del-page"),
    path(
        "<int:pk>/<int:page>/put/<int:pos>/",
        _redirect,
        name="dynforms-put-field",
    ),
    path(
        "<int:pk>/<int:page>/get/<int:pos>/",
        _redirect,
        name="dynforms-get-field",
    ),
    path("<int:pk>/move/", _redirect, name="dynforms-move-field"),
    path(
        "<int:pk>/<int:page>/rules/<int:pos>/",
        _redirect,
        name="dynforms-field-rules",
    ),
]
