from io import StringIO

from django.core.management import call_command
from django.test import TestCase


class TestEnhanceDocstringsCommand(TestCase):
    def test_enhance_docstrings_command_success(self):
        """Test successful docstring enhancement"""
        out = StringIO()
        call_command('enhance_docstrings', stdout=out)
        self.assertIn('Docstring enhancement completed', out.getvalue())

    def test_enhance_docstrings_command_with_file(self):
        """Test docstring enhancement for specific file"""
        out = StringIO()
        call_command('enhance_docstrings', file='accounts/models.py', stdout=out)
        self.assertIn('Docstring enhancement completed', out.getvalue())

    def test_enhance_docstrings_command_with_directory(self):
        """Test docstring enhancement for specific directory"""
        out = StringIO()
        call_command('enhance_docstrings', directory='accounts', stdout=out)
        self.assertIn('Docstring enhancement completed', out.getvalue())

class TestGenerateDocsCommand(TestCase):
    def test_generate_docs_command_success(self):
        """Test successful documentation generation"""
        out = StringIO()
        call_command('generate_docs', stdout=out)
        self.assertIn('Documentation generation completed', out.getvalue())

    def test_generate_docs_command_with_format(self):
        """Test documentation generation with specific format"""
        out = StringIO()
        call_command('generate_docs', format='html', stdout=out)
        self.assertIn('Documentation generation completed', out.getvalue())

    def test_generate_docs_command_with_output_dir(self):
        """Test documentation generation with custom output directory"""
        out = StringIO()
        call_command('generate_docs', output_dir='test_docs', stdout=out)
        self.assertIn('Documentation generation completed', out.getvalue())

class TestResetThemeCommand(TestCase):
    def test_reset_theme_command_success(self):
        """Test successful theme reset"""
        out = StringIO()
        call_command('reset_theme', all=True, stdout=out)
        self.assertIn('Theme reset for', out.getvalue())

    def test_reset_theme_command_with_user(self):
        """Test theme reset for specific user"""
        out = StringIO()
        call_command('reset_theme', user='testuser', stdout=out)
        self.assertIn('User not found', out.getvalue())  # User doesn't exist in test

    def test_reset_theme_command_all_users(self):
        """Test theme reset for all users"""
        out = StringIO()
        call_command('reset_theme', all=True, stdout=out)
        self.assertIn('Theme reset for', out.getvalue())

class TestTestCacheCommand(TestCase):
    def test_test_cache_command_success(self):
        """Test successful cache testing"""
        out = StringIO()
        call_command('test_cache', test=True, stdout=out)
        self.assertIn('Running Cache Performance Tests', out.getvalue())

    def test_test_cache_command_status(self):
        """Test cache status command"""
        out = StringIO()
        call_command('test_cache', status=True, stdout=out)
        self.assertIn('Cache Configuration Status', out.getvalue())

    def test_test_cache_command_verbose(self):
        """Test cache testing with verbose output"""
        out = StringIO()
        call_command('test_cache', test=True, verbose=True, stdout=out)
        self.assertIn('Running Cache Performance Tests', out.getvalue())

    def test_test_cache_command_clear(self):
        """Test cache clear command"""
        out = StringIO()
        call_command('test_cache', clear=True, stdout=out)
        self.assertIn('All cache cleared successfully', out.getvalue())
