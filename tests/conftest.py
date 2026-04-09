"""
Global pytest configuration and fixtures for SEIM tests.

This file contains shared fixtures, test data factories, and utilities
that are used across all test modules.
"""

import os
import tempfile
from datetime import timedelta

import factory
import pytest
from contextlib import contextmanager
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from faker import Faker
from rest_framework.test import APIClient

try:
    from freezegun import freeze_time
except ImportError:

    @contextmanager
    def freeze_time(_when=None):
        yield
from rest_framework_simplejwt.tokens import RefreshToken

# Selenium imports for E2E tests (optional in minimal images)
try:
    from selenium.webdriver.chrome.options import Options
except ImportError:
    Options = None

from accounts.models import Permission, Profile, Role, User
from documents.models import Document
from exchange.models import (
    Application,
    ApplicationStatus,
    Comment,
    Program,
    TimelineEvent,
)
from notifications.models import Notification

# Initialize Faker for test data generation
fake = Faker()

User = get_user_model()

# =============================================================================
# SELENIUM DRIVER CONFIGURATION
# =============================================================================

@pytest.fixture(scope="session")
def chrome_options():
    """Configure Chrome options for testing to disable unnecessary services."""
    if Options is None:

        class _MissingSeleniumOptions:
            def add_argument(self, *_args, **_kwargs):
                pass

        return _MissingSeleniumOptions()

    options = Options()

    # Disable Google API calls and background services
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=VizDisplayCompositor")

    # Disable Google services that cause slowdowns
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-breakpad")
    options.add_argument("--disable-client-side-phishing-detection")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-hang-monitor")
    options.add_argument("--disable-ipc-flooding-protection")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-prompt-on-repost")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-sync")
    options.add_argument("--disable-translate")
    options.add_argument("--metrics-recording-only")
    options.add_argument("--no-first-run")
    options.add_argument("--safebrowsing-disable-auto-update")
    options.add_argument("--disable-component-extensions-with-background-pages")
    options.add_argument("--disable-background-mode")
    options.add_argument("--disable-features=TranslateUI")
    options.add_argument("--disable-ipc-flooding-protection")

    # Disable logging to reduce noise
    options.add_argument("--log-level=3")
    options.add_argument("--silent")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # Disable images and CSS for faster loading
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        "profile.managed_default_content_settings.cookies": 1,
        "profile.managed_default_content_settings.javascript": 1,
        "profile.managed_default_content_settings.plugins": 1,
        "profile.managed_default_content_settings.popups": 2,
        "profile.managed_default_content_settings.geolocation": 2,
        "profile.managed_default_content_settings.media_stream": 2,
    }
    options.add_experimental_option("prefs", prefs)

    return options

# =============================================================================
# FACTORY BOY FACTORIES
# =============================================================================


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating test users."""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    is_active = True
    is_email_verified = True

    @factory.post_generation
    def roles(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for role in extracted:
                self.roles.add(role)


class ProfileFactory(factory.django.DjangoModelFactory):
    """Factory for creating user profiles."""

    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory)
    secondary_email = factory.Faker("email")
    gpa = factory.Faker(
        "pyfloat", left_digits=1, right_digits=2, min_value=2.0, max_value=4.0
    )
    language = factory.Iterator(["English", "Spanish", "French", "German"])

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override to handle automatic profile creation."""
        user = kwargs.get("user")
        if user and hasattr(user, "profile"):
            # Profile already exists, update it
            profile = user.profile
            for key, value in kwargs.items():
                if key != "user":
                    setattr(profile, key, value)
            profile.save()
            return profile
        return super()._create(model_class, *args, **kwargs)


class RoleFactory(factory.django.DjangoModelFactory):
    """Factory for creating user roles."""

    class Meta:
        model = Role

    name = factory.Iterator(["student", "coordinator", "admin"])


class PermissionFactory(factory.django.DjangoModelFactory):
    """Factory for creating permissions."""

    class Meta:
        model = Permission

    name = factory.Faker("word")


class ProgramFactory(factory.django.DjangoModelFactory):
    """Factory for creating exchange programs."""

    class Meta:
        model = Program

    name = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("paragraph")
    start_date = factory.Faker("future_date", end_date="+1y")
    end_date = factory.LazyAttribute(lambda obj: obj.start_date + timedelta(days=180))
    is_active = True
    min_gpa = factory.Faker(
        "pyfloat", left_digits=1, right_digits=2, min_value=2.0, max_value=4.0
    )
    required_language = factory.Iterator(["English", "Spanish", "French", "German"])
    recurring = factory.Faker("boolean")


class ApplicationStatusFactory(factory.django.DjangoModelFactory):
    """Factory for creating application statuses."""

    class Meta:
        model = ApplicationStatus

    name = factory.Iterator(
        ["draft", "submitted", "under_review", "approved", "rejected", "completed"]
    )
    order = factory.Sequence(lambda n: n)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override to use get_or_create to avoid unique constraint violations."""
        name = kwargs.get('name')
        if name:
            obj, created = model_class.objects.get_or_create(
                name=name,
                defaults=kwargs
            )
            return obj
        return super()._create(model_class, *args, **kwargs)


class ApplicationFactory(factory.django.DjangoModelFactory):
    """Factory for creating applications."""

    class Meta:
        model = Application

    program = factory.SubFactory(ProgramFactory)
    student = factory.SubFactory(UserFactory)
    status = factory.SubFactory(ApplicationStatusFactory)
    submitted_at = None
    withdrawn = False

    @factory.post_generation
    def submitted(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.submitted_at = fake.date_time_this_year()
            self.save()


class CommentFactory(factory.django.DjangoModelFactory):
    """Factory for creating application comments."""

    class Meta:
        model = Comment

    application = factory.SubFactory(ApplicationFactory)
    author = factory.SubFactory(UserFactory)
    text = factory.Faker("paragraph")
    is_private = factory.Faker("boolean")


class TimelineEventFactory(factory.django.DjangoModelFactory):
    """Factory for creating timeline events."""

    class Meta:
        model = TimelineEvent

    application = factory.SubFactory(ApplicationFactory)
    event_type = factory.Iterator(
        ["status_change", "comment_added", "document_uploaded"]
    )
    description = factory.Faker("sentence")
    created_by = factory.SubFactory(UserFactory)


class DocumentFactory(factory.django.DjangoModelFactory):
    """Factory for creating documents."""

    class Meta:
        model = Document

    application = factory.SubFactory(ApplicationFactory)
    uploaded_by = factory.SubFactory(UserFactory)
    file_name = factory.Faker("file_name", extension="pdf")
    file_type = "application/pdf"
    file_size = factory.Faker("random_int", min=1000, max=10000000)
    is_required = factory.Faker("boolean")
    is_validated = False

    @factory.post_generation
    def file(self, create, extracted, **kwargs):
        if not create:
            return

        # Create a temporary file for testing
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_file.write(b"Test PDF content")
        temp_file.close()

        self.file = SimpleUploadedFile(
            name=self.file_name,
            content=open(temp_file.name, "rb").read(),
            content_type=self.file_type,
        )

        # Clean up temporary file
        os.unlink(temp_file.name)


class NotificationFactory(factory.django.DjangoModelFactory):
    """Factory for creating notifications."""

    class Meta:
        model = Notification

    recipient = factory.SubFactory(UserFactory)
    title = factory.Faker("sentence")
    message = factory.Faker("paragraph")
    notification_type = factory.Iterator(["email", "in_app", "both"])
    is_read = False


class DocumentTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "documents.DocumentType"

    name = factory.Faker("word")


# =============================================================================
# PYTEST FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Set up the test database."""
    with django_db_blocker.unblock():
        # Create default roles
        roles = {}
        for role_name in ["student", "coordinator", "admin"]:
            roles[role_name] = Role.objects.get_or_create(name=role_name)[0]

        # Create default application statuses
        statuses = {}
        for i, status_name in enumerate(
            ["draft", "submitted", "under_review", "approved", "rejected", "completed"]
        ):
            statuses[status_name] = ApplicationStatus.objects.get_or_create(
                name=status_name, defaults={"order": i}
            )[0]


@pytest.fixture
def db_with_roles(django_db_setup, django_db_blocker):
    """Database with default roles and statuses."""
    with django_db_blocker.unblock():
        # Create default roles
        roles = {}
        for role_name in ["student", "coordinator", "admin"]:
            roles[role_name] = Role.objects.get_or_create(name=role_name)[0]

        # Create default application statuses
        statuses = {}
        for i, status_name in enumerate(
            ["draft", "submitted", "under_review", "approved", "rejected", "completed"]
        ):
            statuses[status_name] = ApplicationStatus.objects.get_or_create(
                name=status_name, defaults={"order": i}
            )[0]

        return {"roles": roles, "statuses": statuses}


@pytest.fixture
def api_client():
    """API client for testing REST endpoints."""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client):
    """API client with authentication."""
    user = UserFactory()
    # Ensure user has a profile
    if not hasattr(user, "profile"):
        ProfileFactory(user=user)
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    # Attach user and refresh_token attributes for test access
    api_client.user = user
    api_client.refresh_token = str(refresh)
    return api_client


@pytest.fixture
def admin_user(db_with_roles):
    """Create an admin user."""
    admin_role = db_with_roles["roles"]["admin"]
    user = UserFactory()
    user.roles.add(admin_role)
    return user


@pytest.fixture
def coordinator_user(db_with_roles):
    """Create a coordinator user."""
    coordinator_role = db_with_roles["roles"]["coordinator"]
    user = UserFactory()
    user.roles.add(coordinator_role)
    return user


@pytest.fixture
def student_user(db_with_roles):
    """Create a student user."""
    student_role = db_with_roles["roles"]["student"]
    user = UserFactory()
    user.roles.add(student_role)
    return user


@pytest.fixture
def user_student(student_user):
    """Alias for unit tests that parametrize on ``user_student``."""
    return student_user


@pytest.fixture
def user_coordinator(coordinator_user):
    """Alias for unit tests that parametrize on ``user_coordinator``."""
    return coordinator_user


@pytest.fixture
def another_user(db_with_roles):
    """Second distinct user for distinct-count / multi-user tests."""
    student_role = db_with_roles["roles"]["student"]
    user = UserFactory()
    user.roles.add(student_role)
    return user


@pytest.fixture
def admin_client(api_client, admin_user):
    """API client authenticated as admin."""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def coordinator_client(api_client, coordinator_user):
    """API client authenticated as coordinator."""
    refresh = RefreshToken.for_user(coordinator_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def student_client(api_client, student_user):
    """API client authenticated as student."""
    refresh = RefreshToken.for_user(student_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def sample_program():
    """Create a sample exchange program."""
    return ProgramFactory()


@pytest.fixture
def sample_application(student_user, sample_program, db_with_roles):
    """Create a sample application."""
    draft_status = db_with_roles["statuses"]["draft"]
    return ApplicationFactory(
        student=student_user, program=sample_program, status=draft_status
    )


@pytest.fixture
def submitted_application(student_user, sample_program, db_with_roles):
    """Create a submitted application."""
    submitted_status = db_with_roles["statuses"]["submitted"]
    return ApplicationFactory(
        student=student_user,
        program=sample_program,
        status=submitted_status,
        submitted_at=fake.date_time_this_year(),
    )


@pytest.fixture
def sample_document(student_user, sample_application):
    """Create a sample document."""
    return DocumentFactory(application=sample_application, uploaded_by=student_user)


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_file.write(b"Test file content")
    temp_file.close()

    yield temp_file.name

    # Clean up
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)


@pytest.fixture
def mock_email_backend(settings):
    """Mock email backend for testing."""
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


@pytest.fixture
def mock_celery(settings):
    """Mock Celery for testing."""
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True


@pytest.fixture
def mock_cache(settings):
    """Mock cache for testing."""
    settings.CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }


@pytest.fixture
def frozen_time():
    """Freeze time for testing time-dependent functionality."""
    with freeze_time("2025-01-15 12:00:00"):
        yield


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before and after each test to ensure isolation."""
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests automatically."""
    pass


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_test_file(filename, content=b"Test content", content_type="text/plain"):
    """Create a test file for upload testing."""
    return SimpleUploadedFile(name=filename, content=content, content_type=content_type)


def assert_response_success(response, status_code=200):
    """Assert that a response is successful."""
    assert response.status_code == status_code
    if hasattr(response, "data"):
        assert "error" not in response.data


def assert_response_error(response, status_code=400):
    """Assert that a response contains an error."""
    assert response.status_code == status_code
    if hasattr(response, "data"):
        assert "error" in response.data or "detail" in response.data


def create_user_with_role(role_name, **kwargs):
    """Create a user with a specific role."""
    user = UserFactory(**kwargs)
    role = Role.objects.get_or_create(name=role_name)[0]
    user.roles.add(role)
    return user


def create_application_workflow(student, program, status_name):
    """Create an application with a specific status."""
    status = ApplicationStatus.objects.get_or_create(name=status_name)[0]
    application = ApplicationFactory(student=student, program=program, status=status)

    if status_name != "draft":
        application.submitted_at = fake.date_time_this_year()
        application.save()

    return application
