import logging

import redis
from django import forms
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from application_forms.models import FormType

logger = logging.getLogger(__name__)


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
        properties = schema.get('properties', {})
        required_fields = schema.get('required', [])

        for field_name, field_config in properties.items():
            field_type = field_config.get('type', 'string')
            title = field_config.get('title', field_name.replace('_', ' ').title())

            # Create field based on type
            if field_type == 'string':
                if field_config.get('format') == 'email':
                    field = forms.EmailField(
                        label=title,
                        required=field_name in required_fields,
                        help_text=field_config.get('description', '')
                    )
                elif 'maxLength' in field_config and field_config['maxLength'] > 100:
                    field = forms.CharField(
                        label=title,
                        required=field_name in required_fields,
                        widget=forms.Textarea,
                        help_text=field_config.get('description', '')
                    )
                else:
                    field = forms.CharField(
                        label=title,
                        required=field_name in required_fields,
                        max_length=field_config.get('maxLength', 255),
                        help_text=field_config.get('description', '')
                    )
            elif field_type == 'number' or field_type == 'integer':
                field = forms.DecimalField(
                    label=title,
                    required=field_name in required_fields,
                    help_text=field_config.get('description', '')
                )
            elif field_type == 'boolean':
                field = forms.BooleanField(
                    label=title,
                    required=field_name in required_fields,
                    help_text=field_config.get('description', '')
                )
            elif field_type == 'array' and field_config.get('items', {}).get('type') == 'string':
                # Handle select/choice fields
                choices = field_config.get('items', {}).get('enum', [])
                if choices:
                    field = forms.ChoiceField(
                        label=title,
                        required=field_name in required_fields,
                        choices=[(choice, choice) for choice in choices],
                        help_text=field_config.get('description', '')
                    )
                else:
                    field = forms.CharField(
                        label=title,
                        required=field_name in required_fields,
                        help_text=field_config.get('description', '')
                    )
            else:
                # Default to text field
                field = forms.CharField(
                    label=title,
                    required=field_name in required_fields,
                    help_text=field_config.get('description', '')
                )

            self.fields[field_name] = field


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for monitoring and load balancer health checks.
    Returns 200 if all services are healthy, 503 if any service is unhealthy.
    """
    health_status = {
        'status': 'healthy',
        'services': {},
        'version': getattr(settings, 'VERSION', 'unknown'),
        'environment': getattr(settings, 'DJANGO_ENV', 'unknown')
    }

    overall_healthy = True

    # Check database connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['services']['database'] = 'healthy'
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status['services']['database'] = f'unhealthy: {str(e)}'
        overall_healthy = False

    # Check cache connectivity
    try:
        cache.set('health_check', 'ok', 10)
        cache_result = cache.get('health_check')
        if cache_result == 'ok':
            health_status['services']['cache'] = 'healthy'
        else:
            health_status['services']['cache'] = 'unhealthy: cache test failed'
            overall_healthy = False
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        health_status['services']['cache'] = f'unhealthy: {str(e)}'
        overall_healthy = False

    # Check Redis connectivity (if using Redis directly)
    try:
        redis_url = getattr(settings, 'REDIS_URL', None)
        if redis_url:
            r = redis.from_url(redis_url)
            r.ping()
            health_status['services']['redis'] = 'healthy'
        else:
            health_status['services']['redis'] = 'not configured'
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status['services']['redis'] = f'unhealthy: {str(e)}'
        overall_healthy = False

    # Set overall status
    if not overall_healthy:
        health_status['status'] = 'unhealthy'
        return JsonResponse(health_status, status=503)

    return JsonResponse(health_status, status=200)


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
                form_type__in=['custom', 'feedback'],
                is_active=True
            ).first()

            if not form_type:
                return HttpResponse("No contact form configured. Please create a dynamic form in the admin.")

            # Create the dynamic form instance
            form = DynamicFormFromSchema(form_type)

            context = {
                'form_type': form_type,
                'form': form,
            }
            return render(request, 'core/contact_form.html', context)

        except Exception as e:
            logger.error(f"Error loading contact form: {e}")
            return HttpResponse("Error loading contact form. Please try again later.")


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
                form_type__in=['custom', 'feedback'],
                is_active=True
            ).first()

            if not form_type:
                return HttpResponse("No contact form configured.")

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
                        submitted_by=request.user if request.user.is_authenticated else None,
                        responses=cleaned_data
                    )
                    logger.info(f"Contact form submission saved: {cleaned_data}")
                except Exception as e:
                    logger.error(f"Error saving contact form submission: {e}")
                    # Still log the submission even if save fails
                    logger.info(f"Contact form submission: {cleaned_data}")

                # Return thank you message
                return HttpResponse("Thank you for your submission! We'll get back to you soon.")
            else:
                # Form is invalid, re-render with errors
                context = {
                    'form_type': form_type,
                    'form': form,
                }
                return render(request, 'core/contact_form.html', context)

        except Exception as e:
            logger.error(f"Error processing contact form submission: {e}")
            return HttpResponse("Error processing your submission. Please try again later.")
