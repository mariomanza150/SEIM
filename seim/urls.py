"""
URL configuration for SEIM project - Vue.js SPA Version

This configuration separates:
- Admin interfaces (Django Admin, Wagtail CMS) - Server-side
- REST API endpoints - Used by Vue.js frontend
- User-facing routes - Handled by Vue.js SPA
"""
from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django_js_reverse.views import urls_js
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from core.views import health_check, health_live
from frontend import views as frontend_views

_WAGTAIL = apps.is_installed("wagtail")

if _WAGTAIL:
    from wagtail import urls as wagtail_urls
    from wagtail.admin import urls as wagtailadmin_urls
    from wagtail.api.v2.router import WagtailAPIRouter
    from wagtail.api.v2.views import PagesAPIViewSet
    from wagtail.documents import urls as wagtaildocs_urls
    from wagtail.documents.api.v2.views import DocumentsAPIViewSet
    from wagtail.images.api.v2.views import ImagesAPIViewSet

    wagtail_api_router = WagtailAPIRouter("wagtailapi")
    wagtail_api_router.register_endpoint("pages", PagesAPIViewSet)
    wagtail_api_router.register_endpoint("images", ImagesAPIViewSet)
    wagtail_api_router.register_endpoint("documents", DocumentsAPIViewSet)

urlpatterns = [
    # ============================================
    # HEALTH CHECK
    # ============================================
    path("health/live/", health_live, name="health_live"),
    path("health/", health_check, name="health_check"),

    # Redirect /admin/ to Django admin (moved to avoid SPA route collisions under /seim/admin/*)
    path("admin/", lambda request: redirect("/seim/django-admin/"), name="admin_redirect"),
    # Redirect legacy /django/admin/ to the new Django admin path
    path("django/admin/", lambda request: redirect("/seim/django-admin/"), name="django_admin_redirect"),
    # Redirect /cms/admin/ to proper CMS admin
    path("cms/admin/", lambda request: redirect("/cms/"), name="cms_admin_redirect"),
    # ============================================
    # ADMIN INTERFACES (Server-side Django/Wagtail)
    # ============================================
    path("seim/django-admin/", admin.site.urls),
    path("data-management/", include("data_management.urls")),  # Data Management
]

if _WAGTAIL:
    urlpatterns += [
        path("cms/", include(wagtailadmin_urls)),  # Wagtail CMS Admin
        path("cms-documents/", include(wagtaildocs_urls)),  # Wagtail Documents
    ]

urlpatterns += [
    # ============================================
    # REST API ENDPOINTS (Used by Vue.js Frontend)
    # ============================================
    path("api/", include(("api.urls", "api"), namespace="api")),
    path("api/accounts/", include("accounts.urls")),
    path("analytics/", include(("analytics.urls", "analytics"), namespace="analytics")),
    path("grades/", include(("grades.urls", "grades"), namespace="grades")),

    # Application Forms API
    path('api/application-forms/', include(('application_forms.urls', 'application_forms'), namespace='application_forms')),

    # django-dynforms builder (admin-only); see core/dynforms_urls.py
    *(
        [path("dynforms/", include("core.dynforms_urls"))]
        if apps.is_installed("dynforms")
        else []
    ),

    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

if _WAGTAIL:
    urlpatterns.append(
        path("api/cms/", wagtail_api_router.urls, name="wagtailapi"),
    )

urlpatterns += [
    # ============================================
    # SEIM APPLICATION (Vue.js SPA)
    # ============================================
    # Vue.js SPA lives exclusively under /seim/ namespace - catch all subpaths
    re_path(r"^seim(?:/.*)?/?$", TemplateView.as_view(template_name='index.html'), name='vue-app'),

    # ============================================
    # UTILITIES
    # ============================================
    path('i18n/', include('django.conf.urls.i18n')),  # Internationalization
    path("jsreverse/", urls_js, name="js_reverse"),  # JavaScript reverse URLs
    # Contact form (Django templates) — before Wagtail/frontend ``""`` includes so ``/contact/`` resolves
    path("", include(("core.urls", "core"))),
]

if _WAGTAIL:
    urlpatterns.append(
        path("admin-dashboard/", frontend_views.admin_dashboard_view),
    )

# Django template frontend routes (non-root) must be registered *before* Wagtail's ``""``
# catch-all so paths like ``/programs/`` and ``/dashboard/analytics/`` resolve here; ``/`` is
# served by Wagtail when a root page exists.
urlpatterns += [
    path("", include(("frontend.urls", "frontend"), namespace="frontend")),
]

if _WAGTAIL:
    urlpatterns.append(
        path(
            "",
            include(wagtail_urls),
        ),
    )
else:
    # Unit tests and minimal installs disable Wagtail; keep a template marketing root.
    urlpatterns.append(path("", frontend_views.home_view, name="marketing_home"))

# ============================================
# DEVELOPMENT: Serve media and static files
# ============================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Vite ``base`` is ``/static/`` (see ``frontend-vue/vite.config.js``); built HTML loads
    # ``/static/assets/*.js``. Django's staticfiles finder serves those from ``frontend-vue/dist``.
    # Legacy fallback: older builds used ``/assets/*`` without the ``static`` prefix.
    urlpatterns += static(
        "/assets/",
        document_root=settings.BASE_DIR / "frontend-vue" / "dist" / "assets",
    )
