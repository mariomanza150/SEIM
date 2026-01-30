"""
URL configuration for SEIM project - Vue.js SPA Version

This configuration separates:
- Admin interfaces (Django Admin, Wagtail CMS) - Server-side
- REST API endpoints - Used by Vue.js frontend
- User-facing routes - Handled by Vue.js SPA
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django_js_reverse.views import urls_js
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Wagtail imports
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from core.views import health_check

urlpatterns = [
    # ============================================
    # HEALTH CHECK
    # ============================================
    path("health/", health_check, name="health_check"),
    
    # ============================================
    # ADMIN INTERFACES (Server-side Django/Wagtail)
    # ============================================
    path("seim/admin/", admin.site.urls),  # Django Admin
    path("cms/", include(wagtailadmin_urls)),  # Wagtail CMS Admin
    path("cms-documents/", include(wagtaildocs_urls)),  # Wagtail Documents
    
    # ============================================
    # REST API ENDPOINTS (Used by Vue.js Frontend)
    # ============================================
    path("api/", include(("api.urls", "api"), namespace="api")),
    path("api/accounts/", include("accounts.urls")),
    
    # JWT Authentication Endpoints
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    # Application Forms API
    path('api/application-forms/', include(('application_forms.urls', 'application_forms'), namespace='application_forms')),
    
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    
    # ============================================
    # UTILITIES
    # ============================================
    path('i18n/', include('django.conf.urls.i18n')),  # Internationalization
    path("jsreverse/", urls_js, name="js_reverse"),  # JavaScript reverse URLs
]

# ============================================
# DEVELOPMENT: Serve media and static files
# ============================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ============================================
# VUE.JS SPA - CATCH ALL USER-FACING ROUTES
# ============================================
# This must be LAST - catches all routes not matched above
# Vue Router will handle the actual client-side routing
# Excludes admin, cms, api, media, and static paths
urlpatterns += [
    re_path(r'^(?!seim/admin|cms|api|media|static).*$', 
            TemplateView.as_view(template_name='index.html'), 
            name='vue-app'),
]
