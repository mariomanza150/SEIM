"""
Django settings configuration for internationalization and localization.
Enable multi-language support for the Student Exchange Information Manager.
"""

from django.utils.translation import gettext_lazy as _

# Internationalization settings to be added to settings.py
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Available languages
LANGUAGES = [
    ('en', _('English')),
    ('es', _('Spanish')),
    ('fr', _('French')),
    ('de', _('German')),
    ('zh-hans', _('Simplified Chinese')),
    ('ja', _('Japanese')),
    ('pt', _('Portuguese')),
    ('it', _('Italian')),
    ('ru', _('Russian')),
    ('ar', _('Arabic')),
]

# Paths where Django should look for translation files
LOCALE_PATHS = [
    'locale/',
]

# Middleware required for internationalization
# Make sure these are included in your MIDDLEWARE settings
INTERNATIONALIZATION_MIDDLEWARE = [
    'django.middleware.locale.LocaleMiddleware',
]

# Context processors required for internationalization
# Make sure these are included in your TEMPLATES settings
INTERNATIONALIZATION_CONTEXT_PROCESSORS = [
    'django.template.context_processors.i18n',
]

# Use gettext_lazy for translatable strings in models and forms
# Example usage in models:
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

class Exchange(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', _('Draft')),
        ('SUBMITTED', _('Submitted')),
        ('UNDER_REVIEW', _('Under Review')),
        ('APPROVED', _('Approved')),
        ('REJECTED', _('Rejected')),
        ('COMPLETED', _('Completed')),
    )
"""

# Use gettext for translatable strings in views
# Example usage in views:
"""
from django.utils.translation import gettext as _
from django.contrib import messages

messages.success(request, _("Exchange application submitted successfully."))
"""

# Use Trans and BlockTrans template tags for translatable strings in templates
# Example usage in templates:
"""
{% load i18n %}

<h1>{% trans "Exchange Application" %}</h1>

{% blocktrans with name=user.first_name %}
Welcome, {{ name }}! Please complete your application.
{% endblocktrans %}
"""

# Language switcher template example:
"""
{% load i18n %}

<form action="{% url 'set_language' %}" method="post">
    {% csrf_token %}
    <input name="next" type="hidden" value="{{ redirect_to }}">
    <select name="language" onchange="this.form.submit()">
        {% get_current_language as LANGUAGE_CODE %}
        {% get_available_languages as LANGUAGES %}
        {% for lang_code, lang_name in LANGUAGES %}
            <option value="{{ lang_code }}" {% if lang_code == LANGUAGE_CODE %}selected{% endif %}>
                {{ lang_name }}
            </option>
        {% endfor %}
    </select>
</form>
"""

# URL configuration to include Django's i18n patterns and set_language view
# Example to include in urls.py:
"""
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

# Wrap your main URLs with i18n_patterns to make them localizable
urlpatterns += i18n_patterns(
    path(_('admin/'), admin.site.urls),
    path(_('exchanges/'), include('exchange.urls')),
    prefix_default_language=False,
)
"""

# Date formatting based on locale
# Make sure USE_L10N is set to True for this to work
# Example usage in templates:
"""
{% load l10n i18n %}

<p>{% trans "Created on" %}: {{ exchange.created_at|date:"SHORT_DATE_FORMAT" }}</p>
<p>{% trans "Time" %}: {{ exchange.created_at|time:"TIME_FORMAT" }}</p>
<p>{% trans "Price" %}: {{ exchange.price|localize }}</p>
"""

# Number and currency formatting based on locale
# Example usage in templates:
"""
{% load l10n %}

<p>{{ number|localize }}</p>
<p>{{ decimal_value|localize }}</p>
"""

# For localized form fields, use localized=True
# Example usage in forms:
"""
from django import forms

class ExchangeForm(forms.ModelForm):
    gpa = forms.DecimalField(localize=True)
    
    class Meta:
        model = Exchange
        fields = ['gpa']
"""

# Create a language selector middleware to set language based on user preferences
"""
from django.utils import translation
from django.utils.deprecation import MiddlewareMixin

class LanguagePreferenceMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.language:
            translation.activate(request.user.profile.language)
            request.LANGUAGE_CODE = translation.get_language()
"""
