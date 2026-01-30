"""
URL configuration for seim project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.urls import include, path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django_js_reverse.views import urls_js
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# Import official dynforms views and add authentication
from dynforms.views import FormBuilder, FormList
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Wagtail imports
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from core.views import health_check


# Custom mixin to restrict to admin users only
def is_admin(user):
    """Check if user is admin - either has admin role OR is superuser"""
    if not user.is_authenticated:
        return False
    # Allow superusers even if they don't have admin role
    if user.is_superuser:
        return True
    # Check for admin role
    return user.has_role('admin')

class AdminOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return is_admin(self.request.user)

# Create authenticated versions of dynforms views, admin only
class AuthenticatedFormBuilder(LoginRequiredMixin, AdminOnlyMixin, FormBuilder):
    pass

class AuthenticatedFormList(LoginRequiredMixin, AdminOnlyMixin, FormList):
    pass

urlpatterns = [
    # Health check endpoint
    path("health/", health_check, name="health_check"),
    
    # Wagtail CMS Admin
    path("cms/", include(wagtailadmin_urls)),
    
    # Wagtail Documents
    path("documents/", include(wagtaildocs_urls)),
    
    # SEIM Application - All application routes under /seim/
    path("seim/admin/", admin.site.urls),  # Django Admin under SEIM
    path("seim/", include("frontend.urls")),  # SEIM Dashboard, auth, etc.
    path("seim/exchange/", include("exchange.urls")),  # Exchange management
    path("seim/analytics/", include(("analytics.urls", "analytics"), namespace="analytics")),
    path("seim/grades/", include(("grades.urls", "grades"), namespace="grades")),
    
    # Core URLs under SEIM
    path("seim/", include(("core.urls", "core"), namespace="core")),
    
    # Internationalization
    path('i18n/', include('django.conf.urls.i18n')),
    
    # API routes (keeping at root for consistency)
    path("api/", include(("api.urls", "api"), namespace="api")),
    path("api/accounts/", include("accounts.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("jsreverse/", urls_js, name="js_reverse"),
    
    # Django-dynforms URLs with authentication (admin only) - under SEIM
    # TODO: These will be deprecated once migration to Wagtail forms is complete
    path('seim/dynforms/', AuthenticatedFormList.as_view(), name='dynforms-list'),
    path('seim/dynforms/builder/', AuthenticatedFormBuilder.as_view(), name='dynforms-builder'),
    path('seim/dynforms/builder/<int:pk>/', AuthenticatedFormBuilder.as_view(), name='dynforms-builder-edit'),
    path('seim/dynforms/api/', include('dynforms.urls')),
    
    # Application forms API
    path('api/application-forms/', include(('application_forms.urls', 'application_forms'), namespace='application_forms')),
    
    # Internacional - Redirects for old CGRI and Movilidad URLs
    path('', include(('internacional.urls', 'internacional'), namespace='internacional')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Wagtail pages catch-all (must be last)
# This allows Wagtail to serve any URL not matched by the patterns above
urlpatterns += [
    re_path(r'', include(wagtail_urls)),
]
