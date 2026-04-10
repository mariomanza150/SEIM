"""
URLConf for django-dynforms under /dynforms/, admin-only.

Mirrors ``dynforms.urls`` but wraps each view with login + admin role checks,
and uses ``builder/<pk>/`` for the form builder to match SEIM paths and tests.
"""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import path

from dynforms import views


class _DynformsAdminRequired(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        return user.is_superuser or user.has_role("admin")


def _wrap(view_cls):
    return type(
        f"AuthDynforms{view_cls.__name__}",
        (LoginRequiredMixin, _DynformsAdminRequired, view_cls),
        {},
    )


urlpatterns = [
    path("", _wrap(views.FormList).as_view(), name="dynforms-list"),
    path("new/", _wrap(views.CreateFormType).as_view(), name="dynforms-create-type"),
    path(
        "builder/<int:pk>/",
        _wrap(views.FormBuilder).as_view(),
        name="dynforms-builder",
    ),
    path("<int:pk>/run/", _wrap(views.TestFormView).as_view(), name="dynforms-run"),
    path("<int:pk>/check/", _wrap(views.CheckFormAPI).as_view(), name="dynforms-check"),
    path(
        "<int:pk>/edit/",
        _wrap(views.EditTemplate).as_view(),
        name="dynforms-edit-template",
    ),
    path(
        "<int:pk>/delete/",
        _wrap(views.DeleteFormType).as_view(),
        name="dynforms-delete-type",
    ),
    path(
        "<int:pk>/<int:page>/add/<slug:type>/<int:pos>/",
        _wrap(views.AddFieldView).as_view(),
        name="dynforms-add-field",
    ),
    path(
        "<int:pk>/<int:page>/del/<int:pos>/",
        _wrap(views.DeleteFieldView).as_view(),
        name="dynforms-del-field",
    ),
    path(
        "<int:pk>/<int:page>/clone/<int:pos>/",
        _wrap(views.CloneFieldView).as_view(),
        name="dynforms-clone-field",
    ),
    path(
        "<int:pk>/<int:page>/del/",
        _wrap(views.DeletePageView).as_view(),
        name="dynforms-del-page",
    ),
    path(
        "<int:pk>/<int:page>/put/<int:pos>/",
        _wrap(views.EditFieldView).as_view(),
        name="dynforms-put-field",
    ),
    path(
        "<int:pk>/<int:page>/get/<int:pos>/",
        _wrap(views.GetFieldView).as_view(),
        name="dynforms-get-field",
    ),
    path(
        "<int:pk>/move/",
        _wrap(views.MoveFieldView).as_view(),
        name="dynforms-move-field",
    ),
    path(
        "<int:pk>/<int:page>/rules/<int:pos>/",
        _wrap(views.FieldRulesView).as_view(),
        name="dynforms-field-rules",
    ),
]
