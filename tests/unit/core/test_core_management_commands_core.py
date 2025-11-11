"""
Tests for core management commands.
"""
import os
import tempfile
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

User = get_user_model()


class TestEnhanceDocstringsCommand(TestCase):
    """Test the enhance_docstrings management command."""

    def setUp(self):
        """Set up test data."""
        self.temp_dir = tempfile.mkdtemp()

    def test_enhance_docstrings_invalid_path(self):
        """Test enhance_docstrings with invalid path."""
        out = StringIO()
        with self.assertRaises(CommandError):
            call_command('enhance_docstrings', '--file', '/nonexistent/path.py', stdout=out)

    def test_enhance_docstrings_success(self):
        """Test successful docstring enhancement."""
        # Create a test Python file
        test_file = os.path.join(self.temp_dir, 'test_file.py')
        with open(test_file, 'w') as f:
            f.write('def test_function():\n    pass\n')

        out = StringIO()
        call_command('enhance_docstrings', '--file', test_file, stdout=out)
        self.assertIn("Docstring enhancement completed", out.getvalue())

    def test_enhance_docstrings_directory(self):
        """Test enhance_docstrings with directory."""
        out = StringIO()
        call_command('enhance_docstrings', '--directory', self.temp_dir, stdout=out)
        self.assertIn("Docstring enhancement completed", out.getvalue())

    def test_enhance_docstrings_recursive(self):
        """Test enhance_docstrings with recursive option."""
        out = StringIO()
        call_command('enhance_docstrings', '--directory', self.temp_dir, '--recursive', stdout=out)
        self.assertIn("Docstring enhancement completed", out.getvalue())

    def test_enhance_docstrings_backup(self):
        """Test enhance_docstrings with backup option."""
        test_file = os.path.join(self.temp_dir, 'test_file.py')
        with open(test_file, 'w') as f:
            f.write('def test_function():\n    pass\n')

        out = StringIO()
        call_command('enhance_docstrings', '--file', test_file, '--backup', stdout=out)
        self.assertIn("Docstring enhancement completed", out.getvalue())

    def test_enhance_docstrings_dry_run(self):
        """Test enhance_docstrings with dry run option."""
        test_file = os.path.join(self.temp_dir, 'test_file.py')
        with open(test_file, 'w') as f:
            f.write('def test_function():\n    pass\n')

        out = StringIO()
        call_command('enhance_docstrings', '--file', test_file, '--dry-run', stdout=out)
        self.assertIn("DRY RUN", out.getvalue())


class TestGenerateDocsCommand(TestCase):
    """Test the generate_docs management command."""

    def test_generate_docs_success(self):
        """Test successful documentation generation."""
        out = StringIO()
        call_command('generate_docs', stdout=out)
        self.assertIn("Documentation generation completed", out.getvalue())

    def test_generate_docs_output_directory(self):
        """Test documentation generation with custom output directory."""
        temp_dir = tempfile.mkdtemp()
        out = StringIO()
        call_command('generate_docs', '--output-dir', temp_dir, stdout=out)
        self.assertIn("Documentation generation completed", out.getvalue())

    def test_generate_docs_include_apis(self):
        """Test documentation generation with API inclusion."""
        out = StringIO()
        call_command('generate_docs', '--include-apis', stdout=out)
        self.assertIn("Documentation generation completed", out.getvalue())

    def test_generate_docs_include_models(self):
        """Test documentation generation with model inclusion."""
        out = StringIO()
        call_command('generate_docs', '--include-models', stdout=out)
        self.assertIn("Documentation generation completed", out.getvalue())

    def test_generate_docs_verbose(self):
        """Test documentation generation with verbose output."""
        out = StringIO()
        call_command('generate_docs', '--verbose', stdout=out)
        self.assertIn("Documentation generation completed", out.getvalue())


class TestResetThemeCommand(TestCase):
    """Test the reset_theme management command."""

    def test_reset_theme_success(self):
        """Test successful theme reset."""
        out = StringIO()
        call_command('reset_theme', '--all', stdout=out)
        self.assertIn("Theme reset", out.getvalue())

    def test_reset_theme_user_specific(self):
        """Test theme reset for specific user."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        out = StringIO()
        call_command('reset_theme', '--user', user.username, stdout=out)
        self.assertIn("Theme reset", out.getvalue())

    def test_reset_theme_invalid_user(self):
        """Test theme reset with invalid user."""
        out = StringIO()
        call_command('reset_theme', '--user', 'nonexistent', stdout=out)
        self.assertIn("User not found", out.getvalue())


class TestTestCacheCommand(TestCase):
    """Test the test_cache management command."""

    def test_test_cache_success(self):
        """Test successful cache testing."""
        out = StringIO()
        call_command('test_cache', stdout=out)
        self.assertIn("Use --help to see available options", out.getvalue())

    def test_test_cache_set_get(self):
        """Test cache set/get operations."""
        out = StringIO()
        call_command('test_cache', '--test-set-get', stdout=out)
        self.assertIn("Cache test", out.getvalue())

    def test_test_cache_clear(self):
        """Test cache clear operation."""
        out = StringIO()
        call_command('test_cache', '--test-clear', stdout=out)
        self.assertIn("Cache test", out.getvalue())

    def test_test_cache_performance(self):
        """Test cache performance."""
        out = StringIO()
        call_command('test_cache', '--test-performance', stdout=out)
        self.assertIn("Cache test", out.getvalue())

    def test_test_cache_verbose(self):
        """Test cache testing with verbose output."""
        out = StringIO()
        call_command('test_cache', '--verbose', stdout=out)
        self.assertIn("Use --help to see available options", out.getvalue())
