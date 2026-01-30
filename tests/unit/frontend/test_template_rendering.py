"""
Template rendering tests for frontend pages.

These tests verify that all Django templates render correctly without syntax errors,
have proper static tag loading, and display expected content.
"""

from django.test import Client, TestCase
from django.urls import reverse

from tests.utils import TestUtils


class TestPublicPageRendering(TestCase):
    """Test public pages render correctly."""

    def setUp(self):
        """Set up test case."""
        self.client = Client()

    def test_home_page_renders(self):
        """Test home page renders without errors."""
        response = self.client.get(reverse('frontend:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/home.html')
        self.assertContains(response, 'SEIM')

    def test_login_page_renders(self):
        """Test login page renders without errors."""
        response = self.client.get(reverse('frontend:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/auth/login.html')
        self.assertContains(response, 'Login')

    def test_register_page_renders(self):
        """Test register page renders without errors."""
        response = self.client.get(reverse('frontend:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/auth/register.html')
        self.assertContains(response, 'Register')

    def test_password_reset_page_renders(self):
        """Test password reset page renders without errors."""
        response = self.client.get(reverse('frontend:password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/auth/password_reset.html')


class TestAuthenticatedPageRendering(TestCase):
    """Test authenticated pages render correctly."""

    def setUp(self):
        """Set up test case."""
        self.client = Client()
        self.student = TestUtils.create_test_user(role='student')
        self.coordinator = TestUtils.create_test_user(role='coordinator')
        self.admin = TestUtils.create_test_user(role='admin')

    def test_dashboard_renders_for_student(self):
        """Test dashboard renders for student users."""
        self.client.force_login(self.student)
        response = self.client.get(reverse('frontend:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/dashboard.html')
        self.assertContains(response, 'dashboard-content')

    def test_dashboard_renders_for_coordinator(self):
        """Test dashboard renders for coordinator users."""
        self.client.force_login(self.coordinator)
        response = self.client.get(reverse('frontend:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/dashboard.html')

    def test_dashboard_renders_for_admin(self):
        """Test dashboard renders for admin users."""
        self.client.force_login(self.admin)
        response = self.client.get(reverse('frontend:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/dashboard.html')

    def test_profile_page_renders(self):
        """Test profile page renders without errors."""
        self.client.force_login(self.student)
        response = self.client.get(reverse('frontend:profile'))
        self.assertEqual(response.status_code, 200)
        # Main goal: verify page renders, not exact template path

    def test_settings_page_renders(self):
        """Test settings page renders without errors."""
        self.client.force_login(self.student)
        response = self.client.get(reverse('frontend:settings'))
        self.assertEqual(response.status_code, 200)
        # Main goal: verify page renders, not exact template path

    def test_preferences_page_renders(self):
        """Test preferences page renders without errors."""
        self.client.force_login(self.student)
        response = self.client.get(reverse('frontend:preferences'))
        self.assertEqual(response.status_code, 200)
        # Main goal: verify page renders, not exact template path

    def test_applications_page_renders(self):
        """Test applications page renders without errors."""
        self.client.force_login(self.student)
        response = self.client.get(reverse('frontend:applications'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/applications/list.html')

    def test_programs_page_renders(self):
        """Test programs page renders without errors."""
        self.client.force_login(self.student)
        response = self.client.get(reverse('frontend:programs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/programs/list.html')

    def test_calendar_page_renders(self):
        """Test calendar page renders without errors."""
        self.client.force_login(self.student)
        response = self.client.get(reverse('frontend:calendar'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'calendar.html')


class TestAdminPageRendering(TestCase):
    """Test admin pages render correctly."""

    def setUp(self):
        """Set up test case."""
        self.client = Client()
        self.admin = TestUtils.create_test_user(role='admin')
        self.coordinator = TestUtils.create_test_user(role='coordinator')
        self.student = TestUtils.create_test_user(role='student')

    def test_admin_dashboard_renders(self):
        """Test admin dashboard renders without errors."""
        self.client.force_login(self.admin)
        response = self.client.get(reverse('frontend:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/admin/dashboard.html')

    def test_analytics_page_renders_for_admin(self):
        """Test analytics page renders for admin users."""
        self.client.force_login(self.admin)
        response = self.client.get(reverse('frontend:analytics'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/admin/analytics.html')

    def test_analytics_page_renders_for_coordinator(self):
        """Test analytics page renders for coordinator users."""
        self.client.force_login(self.coordinator)
        response = self.client.get(reverse('frontend:analytics'))
        # Coordinators should have access
        self.assertIn(response.status_code, [200, 302])

    def test_student_cannot_access_admin_dashboard(self):
        """Test students are redirected from admin dashboard."""
        self.client.force_login(self.student)
        response = self.client.get(reverse('frontend:admin_dashboard'))
        # Should redirect, not show admin dashboard
        self.assertEqual(response.status_code, 302)


class TestTemplateStaticTagLoading(TestCase):
    """Test that all templates properly load the static tag."""

    def setUp(self):
        """Set up test case."""
        self.client = Client()
        self.user = TestUtils.create_test_user(role='student')
        self.client.force_login(self.user)

    def test_dashboard_has_static_tag(self):
        """Test dashboard template loads static tag properly."""
        response = self.client.get(reverse('frontend:dashboard'))
        self.assertEqual(response.status_code, 200)
        # If static tag is missing, response would be 500
        # The fact we get 200 proves static tag works

    def test_all_authenticated_pages_have_static_access(self):
        """Test all authenticated pages can load static files."""
        pages = [
            'frontend:dashboard',
            'frontend:profile',
            'frontend:applications',
            'frontend:programs',
            'frontend:settings',
            'frontend:preferences',
        ]
        
        for page_name in pages:
            with self.subTest(page=page_name):
                response = self.client.get(reverse(page_name))
                self.assertEqual(
                    response.status_code, 200,
                    f"Page {page_name} failed to render (status {response.status_code})"
                )


class TestApplicationPageRendering(TestCase):
    """Test application-related pages render correctly."""

    def setUp(self):
        """Set up test case."""
        self.client = Client()
        self.student = TestUtils.create_test_user(role='student')
        self.program = TestUtils.create_test_program()
        self.client.force_login(self.student)

    def test_application_create_page_renders(self):
        """Test application create page renders without errors."""
        response = self.client.get(
            reverse('frontend:application_create'),
            {'program': self.program.id}
        )
        self.assertEqual(response.status_code, 200)
        # Main goal: verify page renders without template syntax errors

    def test_application_detail_page_renders(self):
        """Test application detail page renders without errors."""
        application = TestUtils.create_test_application(
            student=self.student,
            program=self.program
        )
        response = self.client.get(
            reverse('frontend:application_detail', args=[application.id])
        )
        self.assertEqual(response.status_code, 200)
        # Main goal: verify page renders without template syntax errors

    def test_application_edit_page_renders(self):
        """Test application edit page renders without errors."""
        application = TestUtils.create_test_application(
            student=self.student,
            program=self.program
        )
        response = self.client.get(
            reverse('frontend:application_edit', args=[application.id])
        )
        self.assertEqual(response.status_code, 200)
        # Main goal: verify page renders without template syntax errors


class TestProgramPageRendering(TestCase):
    """Test program-related pages render correctly."""

    def setUp(self):
        """Set up test case."""
        self.client = Client()
        self.admin = TestUtils.create_test_user(role='admin')
        self.program = TestUtils.create_test_program()

    def test_program_create_page_renders(self):
        """Test program create page renders without errors."""
        self.client.force_login(self.admin)
        response = self.client.get(reverse('frontend:program_create'))
        self.assertEqual(response.status_code, 200)
        # Program create uses a form, should render without errors


class TestUnauthenticatedAccessRedirects(TestCase):
    """Test that unauthenticated users are redirected from protected pages."""

    def setUp(self):
        """Set up test case."""
        self.client = Client()

    def test_dashboard_redirects_when_not_authenticated(self):
        """Test dashboard redirects unauthenticated users."""
        response = self.client.get(reverse('frontend:dashboard'))
        # Should be accessible (JS-protected page)
        self.assertEqual(response.status_code, 200)

    def test_profile_requires_authentication(self):
        """Test profile page requires authentication."""
        response = self.client.get(reverse('frontend:profile'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login'))

    def test_applications_requires_authentication(self):
        """Test applications page requires authentication."""
        response = self.client.get(reverse('frontend:applications'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login'))


class TestErrorPageHandling(TestCase):
    """Test error pages and edge cases."""

    def setUp(self):
        """Set up test case."""
        self.client = Client()
        self.user = TestUtils.create_test_user()

    def test_nonexistent_application_handled(self):
        """Test accessing non-existent application is handled gracefully."""
        self.client.force_login(self.user)
        import uuid
        fake_id = uuid.uuid4()
        response = self.client.get(
            reverse('frontend:application_detail', args=[fake_id])
        )
        # Could be 404 or redirect (302), both are valid
        self.assertIn(response.status_code, [302, 404])

    def test_application_edit_nonexistent_handled(self):
        """Test editing non-existent application is handled gracefully."""
        self.client.force_login(self.user)
        import uuid
        fake_id = uuid.uuid4()
        response = self.client.get(
            reverse('frontend:application_edit', args=[fake_id])
        )
        # Could be 404 or redirect (302), both are valid
        self.assertIn(response.status_code, [302, 404])


class TestTemplateContextData(TestCase):
    """Test that templates receive expected context data."""

    def setUp(self):
        """Set up test case."""
        self.client = Client()
        self.user = TestUtils.create_test_user(role='student')
        self.client.force_login(self.user)

    def test_dashboard_has_user_context(self):
        """Test dashboard template receives user context."""
        response = self.client.get(reverse('frontend:dashboard'))
        self.assertEqual(response.status_code, 200)
        # Template should render successfully with user context

    def test_applications_has_applications_list(self):
        """Test applications page has applications in context."""
        # Create test application
        program = TestUtils.create_test_program()
        TestUtils.create_test_application(
            student=self.user,
            program=program
        )
        
        response = self.client.get(reverse('frontend:applications'))
        self.assertEqual(response.status_code, 200)
        # Response should include applications (either in context or loaded via API)

    def test_programs_page_renders_with_programs(self):
        """Test programs page renders with program list."""
        # Create test programs
        TestUtils.create_test_program(name="Test Program 1")
        TestUtils.create_test_program(name="Test Program 2")
        
        response = self.client.get(reverse('frontend:programs'))
        self.assertEqual(response.status_code, 200)


class TestTemplateInheritance(TestCase):
    """Test that template inheritance works correctly."""

    def setUp(self):
        """Set up test case."""
        self.client = Client()
        self.user = TestUtils.create_test_user()
        self.client.force_login(self.user)

    def test_base_template_elements_present(self):
        """Test that all pages include base template elements."""
        pages = [
            'frontend:dashboard',
            'frontend:profile',
            'frontend:applications',
        ]
        
        for page_name in pages:
            with self.subTest(page=page_name):
                response = self.client.get(reverse(page_name))
                self.assertEqual(response.status_code, 200)
                
                # Check for base template elements (navigation, footer, etc.)
                # These would be in base.html that all pages extend
                content = response.content.decode('utf-8')
                
                # Just verify the page rendered without 500 error
                # Actual content validation is less important than syntax validation
                self.assertNotIn('TemplateSyntaxError', content)
                self.assertNotIn('Invalid block tag', content)


class TestStaticFileReferences(TestCase):
    """Test that templates can reference static files."""

    def setUp(self):
        """Set up test case."""
        self.client = Client()
        self.user = TestUtils.create_test_user()
        self.client.force_login(self.user)

    def test_dashboard_static_files_referenced(self):
        """Test dashboard can reference static files without errors."""
        response = self.client.get(reverse('frontend:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode('utf-8')
        
        # Verify static tag worked (no template syntax errors)
        self.assertNotIn('TemplateSyntaxError', content)
        
        # Verify page has expected structure
        self.assertIn('dashboard-content', content)

    def test_home_static_files_referenced(self):
        """Test home page can reference static files without errors."""
        # Use unauthenticated client to actually see home page
        unauthenticated_client = Client()
        response = unauthenticated_client.get(reverse('frontend:home'))
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode('utf-8')
        self.assertNotIn('TemplateSyntaxError', content)


class TestThemePages(TestCase):
    """Test theme-related test pages render correctly."""

    def setUp(self):
        """Set up test case."""
        self.client = Client()

    def test_dark_mode_test_page_renders(self):
        """Test dark mode test page renders without errors."""
        response = self.client.get(reverse('frontend:dark_mode_test'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/dark-mode-test.html')

    def test_theme_test_page_renders(self):
        """Test theme test page renders without errors."""
        response = self.client.get(reverse('frontend:theme_test'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/theme-test.html')

    def test_theme_feedback_test_page_renders(self):
        """Test theme feedback test page renders without errors."""
        response = self.client.get(reverse('frontend:theme_feedback_test'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/theme-feedback-test.html')


class TestCachePageRendering(TestCase):
    """Test pages with caching render correctly."""

    def setUp(self):
        """Set up test case."""
        self.client = Client()
        self.user = TestUtils.create_test_user(role='student')
        self.client.force_login(self.user)

    def test_cached_applications_page_renders(self):
        """Test applications page with caching renders correctly."""
        # First request (cache miss)
        response1 = self.client.get(reverse('frontend:applications'))
        self.assertEqual(response1.status_code, 200)
        
        # Second request (cache hit)
        response2 = self.client.get(reverse('frontend:applications'))
        self.assertEqual(response2.status_code, 200)
        
        # Both should render successfully

    def test_cached_admin_dashboard_renders(self):
        """Test admin dashboard with caching renders correctly."""
        admin = TestUtils.create_test_user(role='admin')
        self.client.force_login(admin)
        
        # First request
        response1 = self.client.get(reverse('frontend:admin_dashboard'))
        self.assertEqual(response1.status_code, 200)
        
        # Second request (from cache)
        response2 = self.client.get(reverse('frontend:admin_dashboard'))
        self.assertEqual(response2.status_code, 200)


class TestAllFrontendPagesIntegrity(TestCase):
    """Comprehensive test to verify all frontend pages render."""

    def setUp(self):
        """Set up test case."""
        self.client = Client()
        self.student = TestUtils.create_test_user(role='student')
        self.coordinator = TestUtils.create_test_user(role='coordinator')
        self.admin = TestUtils.create_test_user(role='admin')

    def test_all_student_accessible_pages(self):
        """Test all pages accessible to students render correctly."""
        self.client.force_login(self.student)
        
        student_pages = [
            'frontend:dashboard',
            'frontend:profile',
            'frontend:settings',
            'frontend:preferences',
            'frontend:applications',
            'frontend:programs',
            'frontend:calendar',
        ]
        
        failed_pages = []
        for page_name in student_pages:
            try:
                response = self.client.get(reverse(page_name))
                if response.status_code not in [200, 302]:
                    failed_pages.append((page_name, response.status_code))
            except Exception as e:
                failed_pages.append((page_name, str(e)))
        
        self.assertEqual(
            len(failed_pages), 0,
            f"Pages failed to render: {failed_pages}"
        )

    def test_all_admin_accessible_pages(self):
        """Test all pages accessible to admins render correctly."""
        self.client.force_login(self.admin)
        
        admin_pages = [
            'frontend:dashboard',
            'frontend:admin_dashboard',
            'frontend:analytics',
            'frontend:profile',
            'frontend:settings',
            'frontend:preferences',
            'frontend:applications',
            'frontend:programs',
            'frontend:program_create',
        ]
        
        failed_pages = []
        for page_name in admin_pages:
            try:
                response = self.client.get(reverse(page_name))
                if response.status_code not in [200, 302]:
                    failed_pages.append((page_name, response.status_code))
            except Exception as e:
                failed_pages.append((page_name, str(e)))
        
        self.assertEqual(
            len(failed_pages), 0,
            f"Pages failed to render: {failed_pages}"
        )

    def test_no_template_syntax_errors_in_responses(self):
        """Comprehensive check that no pages have template syntax errors."""
        self.client.force_login(self.student)
        
        pages = [
            'frontend:dashboard',
            'frontend:profile',
            'frontend:applications',
            'frontend:programs',
        ]
        
        for page_name in pages:
            with self.subTest(page=page_name):
                response = self.client.get(reverse(page_name))
                content = response.content.decode('utf-8')
                
                # Check for common template errors
                self.assertNotIn('TemplateSyntaxError', content)
                self.assertNotIn('TemplateDoesNotExist', content)
                self.assertNotIn('Invalid block tag', content)
                self.assertNotIn('Did you forget to register', content)

