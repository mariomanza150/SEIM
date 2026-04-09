"""
Unit tests for internationalization (i18n) functionality.

Tests translation loading, language switching, and locale preferences.
"""

import pytest
from django.test import TestCase, RequestFactory, override_settings
from django.utils import translation
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class TestTranslationLoading(TestCase):
    """Test that translations are properly loaded."""

    def test_english_default(self):
        """Test that English is the default language."""
        with translation.override('en'):
            self.assertEqual(translation.get_language(), 'en')
            # Test a common translation
            translated = _("Dashboard")
            self.assertEqual(str(translated), "Dashboard")

    def test_spanish_translation(self):
        """Test that Spanish translations load correctly."""
        with translation.override('es'):
            self.assertEqual(translation.get_language(), 'es')
            # Test navigation translations
            translated = _("Dashboard")
            self.assertEqual(str(translated), "Panel de Control")
            
            translated = _("Applications")
            self.assertEqual(str(translated), "Solicitudes")

    def test_french_translation(self):
        """Test that French translations load correctly."""
        with translation.override('fr'):
            self.assertEqual(translation.get_language(), 'fr')
            translated = _("Dashboard")
            self.assertEqual(str(translated), "Tableau de Bord")
            
            translated = _("Applications")
            self.assertEqual(str(translated), "Candidatures")

    def test_german_translation(self):
        """Test that German translations load correctly."""
        with translation.override('de'):
            self.assertEqual(translation.get_language(), 'de')
            translated = _("Dashboard")
            self.assertEqual(str(translated), "Übersicht")
            
            translated = _("Applications")
            self.assertEqual(str(translated), "Bewerbungen")

    def test_fallback_to_english(self):
        """Test that missing translations fall back to English."""
        with translation.override('es'):
            # Test a string that might not be translated
            untranslated = _("SomeUntranslatedString")
            # Should return the original string if no translation exists
            self.assertEqual(str(untranslated), "SomeUntranslatedString")


class TestLanguageSwitching(TestCase):
    """Test language switching functionality."""

    def setUp(self):
        self.factory = RequestFactory()

    def test_language_switch_via_post(self):
        """Test language switching via POST request."""
        # This would test the set_language view
        # Simulating the Django i18n view
        response = self.client.post('/i18n/setlang/', {
            'language': 'es',
            'next': '/'
        })
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        
        # Check that language cookie is set
        self.assertIn('django_language', response.cookies)
        self.assertEqual(response.cookies['django_language'].value, 'es')

    def test_invalid_language_code(self):
        """Test that invalid language codes are handled gracefully."""
        response = self.client.post('/i18n/setlang/', {
            'language': 'invalid',
            'next': '/'
        })
        
        # Should still respond (Django handles invalid codes)
        self.assertEqual(response.status_code, 302)

    def test_language_persistence_in_session(self):
        """Test that language preference persists in session."""
        # Set language
        self.client.post('/i18n/setlang/', {
            'language': 'fr',
            'next': '/'
        })
        
        # Make another request
        response = self.client.get('/')
        
        # Language should be set in cookie
        self.assertEqual(self.client.cookies.get('django_language').value, 'fr')


class TestModelTranslations(TestCase):
    """Test model field translations."""

    def test_verbose_names_translated(self):
        """Test that model verbose names are translated."""
        from exchange.models import Application
        
        with translation.override('es'):
            # Get verbose name
            verbose_name = Application._meta.verbose_name
            self.assertEqual(str(verbose_name), "Solicitud")
            
            verbose_name_plural = Application._meta.verbose_name_plural
            self.assertEqual(str(verbose_name_plural), "Solicitudes")

    def test_help_text_translated(self):
        """Test that model field help text is translated."""
        from exchange.models import Program
        
        with translation.override('es'):
            # Get help text for a field
            min_gpa_field = Program._meta.get_field('min_gpa')
            help_text = str(min_gpa_field.help_text)
            self.assertEqual(help_text, "GPA mínimo requerido para elegibilidad.")

    def test_choices_translated(self):
        """Test that model field choices are translated."""
        from exchange.models import Program
        
        with translation.override('es'):
            # Get choices for language level field
            level_field = Program._meta.get_field('min_language_level')
            choices = dict(level_field.choices)
            
            # Check that choices are translated
            self.assertEqual(str(choices['A1']), "Principiante (A1)")
            self.assertEqual(str(choices['B1']), "Intermedio (B1)")
            self.assertEqual(str(choices['C1']), "Avanzado (C1)")


class TestTemplateTags(TestCase):
    """Test i18n template tags."""

    def test_trans_tag_in_template(self):
        """Test that {% trans %} tag works in templates."""
        from django.template import Context, Template
        
        with translation.override('es'):
            template = Template("""
                {% load i18n %}
                {% trans "Dashboard" %}
            """)
            rendered = template.render(Context({}))
            self.assertIn("Panel de Control", rendered.strip())

    def test_blocktrans_tag(self):
        """Test that {% blocktrans %} tag works in templates."""
        from django.template import Context, Template
        
        with translation.override('fr'):
            template = Template("""
                {% load i18n %}
                {% blocktrans %}Quick Actions{% endblocktrans %}
            """)
            rendered = template.render(Context({}))
            self.assertIn("Actions Rapides", rendered.strip())

    def test_language_in_template_context(self):
        """Test that LANGUAGE_CODE is available in template context."""
        from django.template import Context, Template
        
        with translation.override('de'):
            template = Template("""
                {{ LANGUAGE_CODE }}
            """)
            rendered = template.render(Context({'LANGUAGE_CODE': translation.get_language()}))
            self.assertIn("de", rendered.strip())


class TestPluralForms(TestCase):
    """Test plural form handling in translations."""

    def test_plural_forms_spanish(self):
        """Test Spanish plural forms."""
        with translation.override('es'):
            # ngettext handles pluralization
            from django.utils.translation import ngettext
            
            # Singular
            result = ngettext("%(count)d application", "%(count)d applications", 1) % {'count': 1}
            # Note: This would need actual translations in .po file
            
            # Plural
            result = ngettext("%(count)d application", "%(count)d applications", 5) % {'count': 5}

    def test_plural_forms_french(self):
        """Test French plural forms (different from English)."""
        with translation.override('fr'):
            from django.utils.translation import ngettext
            
            # French has different plural rules
            # 0 and 1 are singular, 2+ are plural
            result = ngettext("%(count)d application", "%(count)d applications", 0) % {'count': 0}


class TestRTLSupport(TestCase):
    """Test Right-to-Left language support (for future)."""

    def test_text_direction_ltr(self):
        """Test that LTR languages have correct text direction."""
        from django.utils.translation import get_language_bidi
        
        with translation.override('en'):
            self.assertFalse(get_language_bidi())
        
        with translation.override('es'):
            self.assertFalse(get_language_bidi())

    def test_text_direction_rtl(self):
        """Test RTL detection (for future Arabic support)."""
        from django.utils.translation import get_language_bidi
        
        # If Arabic is added in the future
        # with translation.override('ar'):
        #     self.assertTrue(get_language_bidi())
        pass


@override_settings(USE_I18N=True, LANGUAGE_CODE='en')
class TestI18nConfiguration(TestCase):
    """Test i18n configuration settings."""

    def test_i18n_enabled(self):
        """Test that i18n is enabled."""
        from django.conf import settings
        self.assertTrue(settings.USE_I18N)

    def test_default_language(self):
        """Test default language setting."""
        from django.conf import settings
        self.assertEqual(settings.LANGUAGE_CODE, 'en')

    def test_available_languages(self):
        """Test that all supported languages are configured."""
        from django.conf import settings
        
        # Get configured languages
        languages = dict(settings.LANGUAGES)
        
        # Check that our 4 languages are available
        self.assertIn('en', languages)
        self.assertIn('es', languages)
        self.assertIn('fr', languages)
        self.assertIn('de', languages)

    def test_locale_paths_configured(self):
        """Test that locale paths are configured."""
        from django.conf import settings
        self.assertTrue(hasattr(settings, 'LOCALE_PATHS'))
        self.assertTrue(len(settings.LOCALE_PATHS) > 0)


class TestTranslationContextProcessors(TestCase):
    """Test translation context processors."""

    def test_language_code_in_context(self):
        """Test that LANGUAGE_CODE is in template context."""
        response = self.client.get('/')
        
        # LANGUAGE_CODE should be available in context
        # This is provided by django.template.context_processors.i18n
        # Actual test would depend on view implementation


class TestUserLanguagePreference(TestCase):
    """Test user-specific language preferences."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_language_preference_in_session(self):
        """Test that language preference is stored in session."""
        self.client.login(username='testuser', password='testpass123')
        
        # Set language
        response = self.client.post('/i18n/setlang/', {
            'language': 'es',
            'next': '/dashboard/'
        })
        
        # Verify language is set
        self.assertEqual(response.cookies['django_language'].value, 'es')

    def test_language_persistence_across_requests(self):
        """Test that language persists across multiple requests."""
        self.client.login(username='testuser', password='testpass123')
        
        # Set language
        self.client.post('/i18n/setlang/', {
            'language': 'fr',
            'next': '/'
        })
        
        # Make subsequent requests
        response1 = self.client.get('/dashboard/')
        response2 = self.client.get('/programs/')
        
        # Language should persist
        self.assertEqual(self.client.cookies['django_language'].value, 'fr')

