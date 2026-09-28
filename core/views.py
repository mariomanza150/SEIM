import logging
import time

import redis
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.core.cache import cache
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from application_forms.models import FormType
from core.branding import brand_from_settings
from core.models import InstitutionFeatureSettings
from core.permissions import IsAdminRole
from core.serializers import InstitutionFeatureSettingsSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


def _render_contact_message(request, *, page_title, message, alert_variant="warning"):
    """Full HTML page for contact-related status (unconfigured form, errors, thanks)."""
    return render(
        request,
        "core/contact_message.html",
        {
            "page_title": page_title,
            "message": message,
            "alert_variant": alert_variant,
        },
    )


class DynamicFormFromSchema(forms.Form):
    """
    Dynamic form class that creates form fields based on a FormType schema.
    """

    def __init__(self, form_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_type = form_type
        self._build_fields_from_schema()

    def _build_fields_from_schema(self):
        """Build form fields from the FormType schema."""
        if not self.form_type or not self.form_type.schema:
            return

        schema = self.form_type.schema
        properties = schema.get("properties", {})
        required_fields = schema.get("required", [])

        for field_name, field_config in properties.items():
            field_type = field_config.get("type", "string")
            title = field_config.get("title", field_name.replace("_", " ").title())

            # Create field based on type
            if field_type == "string":
                if field_config.get("format") == "email":
                    field = forms.EmailField(
                        label=title,
                        required=field_name in required_fields,
                        help_text=field_config.get("description", ""),
                    )
                elif "maxLength" in field_config and field_config["maxLength"] > 100:
                    field = forms.CharField(
                        label=title,
                        required=field_name in required_fields,
                        widget=forms.Textarea,
                        help_text=field_config.get("description", ""),
                    )
                else:
                    field = forms.CharField(
                        label=title,
                        required=field_name in required_fields,
                        max_length=field_config.get("maxLength", 255),
                        help_text=field_config.get("description", ""),
                    )
            elif field_type == "number" or field_type == "integer":
                field = forms.DecimalField(
                    label=title,
                    required=field_name in required_fields,
                    help_text=field_config.get("description", ""),
                )
            elif field_type == "boolean":
                field = forms.BooleanField(
                    label=title,
                    required=field_name in required_fields,
                    help_text=field_config.get("description", ""),
                )
            elif (
                field_type == "array"
                and field_config.get("items", {}).get("type") == "string"
            ):
                # Handle select/choice fields
                choices = field_config.get("items", {}).get("enum", [])
                if choices:
                    field = forms.ChoiceField(
                        label=title,
                        required=field_name in required_fields,
                        choices=[(choice, choice) for choice in choices],
                        help_text=field_config.get("description", ""),
                    )
                else:
                    field = forms.CharField(
                        label=title,
                        required=field_name in required_fields,
                        help_text=field_config.get("description", ""),
                    )
            else:
                # Default to text field
                field = forms.CharField(
                    label=title,
                    required=field_name in required_fields,
                    help_text=field_config.get("description", ""),
                )

            self.fields[field_name] = field


@csrf_exempt
@require_http_methods(["GET"])
def branding_api(request):
    """Public institution branding for SPA shell (logo, nav label)."""
    brand = brand_from_settings(settings)
    theme = brand.get("theme") or {}
    return JsonResponse(
        {
            "logo_url": brand.get("logo_url") or "",
            "nav_brand": brand.get("nav_brand") or "",
            "short_name": brand.get("short_name") or "",
            "name": brand.get("name") or "",
            "theme_css": brand.get("theme_css") or "uadec/theme.css",
            "theme": theme,
        }
    )


class InstitutionFeaturesAPIView(APIView):
    """GET authenticated feature flags; PATCH admin-only."""

    def get_permissions(self):
        if self.request.method in ("PATCH", "PUT"):
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated()]

    def get(self, request):
        settings_obj = InstitutionFeatureSettings.get_solo()
        return Response(InstitutionFeatureSettingsSerializer(settings_obj).data)

    def patch(self, request):
        settings_obj = InstitutionFeatureSettings.get_solo()
        serializer = InstitutionFeatureSettingsSerializer(
            settings_obj, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@csrf_exempt
@require_http_methods(["GET"])
def health_live(request):
    """
    Liveness probe: process is up; does not query Postgres/Redis.
    Use for Docker HEALTHCHECK so transient dependency failures do not fail the probe (curl -f exits 22 on HTTP error).
    """
    return JsonResponse(
        {
            "status": "live",
            "version": getattr(settings, "VERSION", "unknown"),
            "environment": getattr(settings, "DJANGO_ENV", "unknown"),
        },
        status=200,
    )


HEALTH_CHECK_TIMEOUT_SECONDS = 2
HEALTH_CRITICAL_CHECKS = frozenset({"db"})


class _SkipCheck(Exception):
    pass


def _check_db():
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")


def _check_cache():
    backend = settings.CACHES.get("default", {}).get("BACKEND", "")
    if backend.endswith("DummyCache"):
        raise _SkipCheck
    cache.set("health_check", "ok", 10)
    if cache.get("health_check") != "ok":
        raise RuntimeError("cache round-trip failed")


def _check_redis():
    redis_url = getattr(settings, "REDIS_URL", None)
    if not redis_url:
        raise _SkipCheck
    client = redis.from_url(
        redis_url,
        socket_connect_timeout=HEALTH_CHECK_TIMEOUT_SECONDS,
        socket_timeout=HEALTH_CHECK_TIMEOUT_SECONDS,
    )
    try:
        client.ping()
    finally:
        client.close()


HEALTH_CHECKS = {"db": _check_db, "cache": _check_cache, "redis": _check_redis}


def _run_health_check(name, check):
    started = time.perf_counter()
    try:
        check()
    except _SkipCheck:
        return {"status": "skipped"}
    except Exception as exc:
        logger.warning("health check failed", extra={"check": name, "error": repr(exc)})
        return {
            "status": "error",
            "latency_ms": round((time.perf_counter() - started) * 1000, 1),
            "error": type(exc).__name__,
        }
    return {
        "status": "ok",
        "latency_ms": round((time.perf_counter() - started) * 1000, 1),
    }


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Readiness probe for monitoring (ops standard health contract).

    ``status`` is ``ok``, ``degraded`` (a non-critical check failed; HTTP 200) or
    ``down`` (the database failed; HTTP 503).
    """
    checks = {name: _run_health_check(name, fn) for name, fn in HEALTH_CHECKS.items()}
    failed = {name for name, result in checks.items() if result["status"] == "error"}
    if failed & HEALTH_CRITICAL_CHECKS:
        overall, http_status = "down", 503
    elif failed:
        overall, http_status = "degraded", 200
    else:
        overall, http_status = "ok", 200
    return JsonResponse(
        {
            "status": overall,
            "version": getattr(settings, "VERSION", "unknown"),
            "environment": getattr(settings, "DJANGO_ENV", "unknown"),
            "checks": checks,
        },
        status=http_status,
        json_dumps_params={"separators": (",", ":")},
    )


def marketing_home(request):
    """Public home when Wagtail is not installed (e.g. default unit test settings)."""
    if request.user.is_authenticated:
        return redirect("/seim/dashboard/")
    return HttpResponse(
        "<!DOCTYPE html><html><head><title>SEIM</title></head><body>"
        "<h1>Student Exchange Information Manager</h1>"
        "</body></html>"
    )


def spa_logout(request):
    """Clear the Django session and send the user to the Vue login shell."""
    logout(request)
    response = redirect("/seim/login/")
    response.set_cookie("clear_jwt_tokens", "true", max_age=1)
    messages.success(request, "You have been logged out successfully.")
    return response


class ContactFormView(View):
    """
    View to display the dynamic contact form.
    Renders the template core/contact_form.html with the dynamic form.
    """

    def get(self, request):
        # Get the first contact form (filter by form_type='custom' or 'feedback')
        # For this example, we'll get the first available form
        try:
            form_type = FormType.objects.filter(
                form_type__in=["custom", "feedback"], is_active=True
            ).first()

            if not form_type:
                return _render_contact_message(
                    request,
                    page_title="Contact",
                    message="No contact form configured. Please create a dynamic form in the admin.",
                    alert_variant="warning",
                )

            # Create the dynamic form instance
            form = DynamicFormFromSchema(form_type)

            context = {
                "form_type": form_type,
                "form": form,
            }
            return render(request, "core/contact_form.html", context)

        except Exception as e:
            logger.error(f"Error loading contact form: {e}")
            return _render_contact_message(
                request,
                page_title="Contact",
                message="Error loading contact form. Please try again later.",
                alert_variant="danger",
            )


class ContactFormSubmitView(View):
    """
    View to handle form submission from the dynamic contact form.
    If valid, prints cleaned data to console and returns thank you message.
    If invalid, re-renders the form with errors.
    """

    def post(self, request):
        # Get the dynamic form
        try:
            form_type = FormType.objects.filter(
                form_type__in=["custom", "feedback"], is_active=True
            ).first()

            if not form_type:
                return _render_contact_message(
                    request,
                    page_title="Contact",
                    message="No contact form configured.",
                    alert_variant="warning",
                )

            # Create the dynamic form instance with POST data
            form = DynamicFormFromSchema(form_type, request.POST)

            if form.is_valid():
                # Print cleaned data to console
                cleaned_data = form.cleaned_data
                print("=== CONTACT FORM SUBMISSION ===")
                for field, value in cleaned_data.items():
                    print(f"{field}: {value}")
                print("===============================")

                # Save form submission using our custom FormSubmission model
                try:
                    from application_forms.models import FormSubmission

                    FormSubmission.objects.create(
                        form_type=form_type,
                        submitted_by=request.user
                        if request.user.is_authenticated
                        else None,
                        responses=cleaned_data,
                    )
                    logger.info(f"Contact form submission saved: {cleaned_data}")
                except Exception as e:
                    logger.error(f"Error saving contact form submission: {e}")
                    # Still log the submission even if save fails
                    logger.info(f"Contact form submission: {cleaned_data}")

                return _render_contact_message(
                    request,
                    page_title="Thank you",
                    message="Thank you for your submission! We'll get back to you soon.",
                    alert_variant="success",
                )
            else:
                # Form is invalid, re-render with errors
                context = {
                    "form_type": form_type,
                    "form": form,
                }
                return render(request, "core/contact_form.html", context)

        except Exception as e:
            logger.error(f"Error processing contact form submission: {e}")
            return _render_contact_message(
                request,
                page_title="Contact",
                message="Error processing your submission. Please try again later.",
                alert_variant="danger",
            )
