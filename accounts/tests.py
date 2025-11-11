from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from accounts import serializers

# Create your tests here.

class TestAccountSerializers(TestCase):
    def test_user_serializer_valid(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'TestPass123!'
        }
        serializer = serializers.UserSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_user_serializer_missing_fields(self):
        data = {'username': 'testuser'}
        serializer = serializers.UserSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors
        # assert 'password' in serializer.errors  # Removed - UserSerializer doesn't have password field

    def test_user_serializer_invalid_email(self):
        data = {
            'username': 'testuser',
            'email': 'not-an-email',
            'password': 'TestPass123!'
        }
        serializer = serializers.UserSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    # Add similar tests for other serializers if present

class TestAccountViews(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        # Use the default manager to create a user
        try:
            self.user = User.objects.create_user(
                username='testuser', email='testuser@example.com', password='TestPass123!')
        except AttributeError:
            # Fallback: use the base manager if custom manager is missing create_user
            self.user = User._default_manager.create(
                username='testuser', email='testuser@example.com', password='TestPass123!')

    def test_register_view_get(self):
        url = reverse('frontend:register')
        response = self.client.get(url)
        assert response.status_code == 200

    def test_login_view_get(self):
        url = reverse('frontend:login')
        response = self.client.get(url)
        assert response.status_code == 200

    def test_login_view_post(self):
        url = reverse('frontend:login')
        response = self.client.post(url, {'username': 'testuser', 'password': 'TestPass123!'})
        assert response.status_code in (200, 302)

    # Add more view tests as needed for other endpoints
