
from django.contrib.auth import get_user_model
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_field
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from core.throttling import BurstRateThrottle

from .models import Permission, Profile, Role, UserSession, UserSettings
from .serializers import (
    AppearanceSettingsSerializer,
    ChangePasswordSerializer,
    DeleteAccountResponseSerializer,
    EmailVerificationSerializer,
    LoginSerializer,
    LogoutResponseSerializer,
    LogoutSerializer,
    NotificationSettingsSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    PermissionSerializer,
    PrivacySettingsSerializer,
    ProfileSerializer,
    ProfileUpdateRequestSerializer,
    ProfileUpdateResponseSerializer,
    RegistrationSerializer,
    RevokeSessionResponseSerializer,
    RoleSerializer,
    UserSerializer,
    UserSessionSerializer,
    UserSettingsSerializer,
)

# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model operations."""
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]  # Only admins can manage users


class ProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for Profile model operations."""
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter profiles based on user permissions."""
        if self.request.user.is_staff:
            return Profile.objects.all()
        return Profile.objects.filter(user=self.request.user)


class RegistrationView(generics.CreateAPIView):
    """User registration endpoint with burst rate limiting."""

    serializer_class = RegistrationSerializer
    permission_classes = []  # Allow any user to register
    throttle_classes = [BurstRateThrottle]  # Limit registration attempts

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "detail": "Registration successful. Please check your email to verify your account."
            },
            status=status.HTTP_201_CREATED,
        )


class EmailVerificationView(generics.GenericAPIView):
    """Email verification endpoint with burst rate limiting."""

    serializer_class = EmailVerificationSerializer
    permission_classes = []
    throttle_classes = [BurstRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Email verified successfully. You can now log in."},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    """Login endpoint with burst rate limiting to prevent brute force attacks."""

    serializer_class = LoginSerializer
    # Do not run Session/JWT auth before validating credentials. Otherwise a prior Django
    # session triggers SessionAuthentication CSRF enforcement and account-switch POSTs
    # return 403 while the SPA sends JSON without CSRF headers (MQ-007).
    authentication_classes = []
    permission_classes = []
    throttle_classes = [BurstRateThrottle]  # Strict limit to prevent brute force

    def get_authenticate_header(self, request):
        """Return a JWT challenge so ``AuthenticationFailed`` stays HTTP 401.

        With ``authentication_classes = []``, DRF's default has no challenge header and
        coerces ``AuthenticationFailed`` to 403; wrong password must be 401 for clients/tests.
        """
        return JWTAuthentication().authenticate_header(request)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        # Create Django session for server-side authentication
        from django.contrib.auth import login

        login(request, user)

        # Create or update user session record
        try:
            session = UserSession.objects.get(
                user=user,
                session_key=request.session.session_key,
                is_active=True
            )
            session.last_activity = timezone.now()
            session.save()
        except UserSession.DoesNotExist:
            # Create new session record
            UserSession.objects.create(
                user=user,
                session_key=request.session.session_key,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                ip_address=request.META.get('REMOTE_ADDR'),
                device=self._get_device_info(request.META.get('HTTP_USER_AGENT', '')),
                location=self._get_location_info(request.META.get('REMOTE_ADDR')),
                is_active=True
            )

        # Issue JWT token for API authentication
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

    def _get_device_info(self, user_agent):
        """Extract device information from user agent."""
        if not user_agent:
            return 'Unknown'

        user_agent_lower = user_agent.lower()
        if 'mobile' in user_agent_lower or 'android' in user_agent_lower or 'iphone' in user_agent_lower:
            return 'Mobile'
        elif 'tablet' in user_agent_lower or 'ipad' in user_agent_lower:
            return 'Tablet'
        else:
            return 'Desktop'

    def _get_location_info(self, ip_address):
        """Get location information from IP address (simplified)."""
        if not ip_address:
            return 'Unknown'

        # For now, just return a generic location
        # In production, you might use a geolocation service
        if ip_address in ['127.0.0.1', 'localhost']:
            return 'Local'
        else:
            return 'Remote'


class PasswordResetRequestView(generics.GenericAPIView):
    """Password reset request endpoint with burst rate limiting."""

    serializer_class = PasswordResetRequestSerializer
    permission_classes = []
    throttle_classes = [BurstRateThrottle]  # Limit password reset attempts

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {"message": "Password reset email sent"}, status=status.HTTP_200_OK
            )
        except Exception:
            # Always return 200 for security, even if email does not exist
            return Response(
                {"message": "Password reset email sent"}, status=status.HTTP_200_OK
            )


class PasswordResetConfirmView(generics.GenericAPIView):
    """Password reset confirmation endpoint with burst rate limiting."""

    serializer_class = PasswordResetConfirmSerializer
    permission_classes = []
    throttle_classes = [BurstRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Get or create profile for the user
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile


class ProfileUpdateView(generics.GenericAPIView):
    """View for updating user account information (email, first_name, last_name)."""
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileUpdateRequestSerializer

    @extend_schema(
        request=ProfileUpdateRequestSerializer,
        responses={200: ProfileUpdateResponseSerializer, 400: ProfileUpdateResponseSerializer}
    )
    def patch(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        # Update user fields
        if 'email' in data and data['email'] != user.email:
            # Check if email is already taken
            if get_user_model().objects.filter(email=data['email']).exclude(id=user.id).exists():
                return Response(
                    {"message": "Email address is already in use."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.email = data['email']

        if 'first_name' in data:
            user.first_name = data['first_name']

        if 'last_name' in data:
            user.last_name = data['last_name']

        try:
            user.save()
            return Response(
                {"detail": "Profile updated successfully."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"message": f"Failed to update profile: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(generics.GenericAPIView):
    """API view for logging out users."""

    # JWT only: default SessionAuthentication on this POST triggers CSRF when the client
    # also holds a Django session from login(), causing 403 and blocking the next JSON
    # login (same class as MQ-007 on LoginView) — MQ-008.
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    @extend_schema(
        request=LogoutSerializer,
        responses={200: LogoutResponseSerializer}
    )
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass  # Ignore errors for idempotency

        # Clear Django session
        from django.contrib.auth import logout

        logout(request)

        return Response(
            {"message": "Successfully logged out"}, status=status.HTTP_200_OK
        )


class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password changed successfully."}, status=status.HTTP_200_OK
        )


class AppearanceSettingsView(generics.RetrieveUpdateAPIView):
    """View for managing appearance settings."""
    serializer_class = AppearanceSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        settings, created = UserSettings.objects.get_or_create(user=user)
        return settings


class NotificationSettingsView(generics.RetrieveUpdateAPIView):
    """View for managing notification settings."""
    serializer_class = NotificationSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        settings, created = UserSettings.objects.get_or_create(user=user)
        return settings


class PrivacySettingsView(generics.RetrieveUpdateAPIView):
    """View for managing privacy settings."""
    serializer_class = PrivacySettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        settings, created = UserSettings.objects.get_or_create(user=user)
        return settings


class UserSettingsView(generics.RetrieveUpdateAPIView):
    """Generic view for user settings operations."""
    serializer_class = UserSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Get or create user settings for the authenticated user."""
        settings, created = UserSettings.objects.get_or_create(user=self.request.user)
        return settings


class UserSessionsView(generics.ListAPIView):
    """View for listing user sessions."""
    serializer_class = UserSessionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Disable pagination for sessions

    def get_queryset(self):
        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return UserSession.objects.none()
        return UserSession.objects.filter(user=self.request.user, is_active=True)


class RevokeSessionView(generics.GenericAPIView):
    """View for revoking a user session."""
    permission_classes = [IsAuthenticated]
    serializer_class = RevokeSessionResponseSerializer

    @extend_schema(
        responses={200: RevokeSessionResponseSerializer, 404: RevokeSessionResponseSerializer}
    )
    def post(self, request, session_id):
        try:
            session = UserSession.objects.get(
                id=session_id,
                user=request.user,
                is_active=True
            )
            session.is_active = False
            session.save()
            return Response(
                {"detail": "Session revoked successfully."},
                status=status.HTTP_200_OK
            )
        except UserSession.DoesNotExist:
            return Response(
                {"detail": "Session not found."},
                status=status.HTTP_404_NOT_FOUND
            )


class DeleteAccountView(generics.GenericAPIView):
    """View for deleting user account."""
    permission_classes = [IsAuthenticated]
    serializer_class = DeleteAccountResponseSerializer

    @extend_schema(
        responses={200: DeleteAccountResponseSerializer}
    )
    def delete(self, request):
        user = request.user
        # Soft delete by deactivating the user
        user.is_active = False
        user.save()

        # Logout the user
        from django.contrib.auth import logout
        logout(request)

        return Response(
            {"detail": "Account deleted successfully."},
            status=status.HTTP_200_OK
        )


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for listing and retrieving roles."""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for listing and retrieving permissions."""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]


class UserSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for listing and deleting user sessions."""
    serializer_class = UserSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return UserSession.objects.none()
        return UserSession.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserPermissionsView(APIView):
    """
    API endpoint to get current user's permissions.
    Used by frontend JavaScript to determine what UI elements to show.
    
    GET /api/accounts/permissions/
    
    Returns:
        {
            "roles": ["student", "coordinator"],
            "primary_role": "coordinator",
            "permissions": ["view_own_applications", "create_application", ...],
            "is_admin": false,
            "is_coordinator": true,
            "is_student": true
        }
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get user permissions",
        description="Returns current user's roles and permissions for frontend use",
        responses={200: {
            "type": "object",
            "properties": {
                "roles": {"type": "array", "items": {"type": "string"}},
                "primary_role": {"type": "string"},
                "permissions": {"type": "array", "items": {"type": "string"}},
                "is_admin": {"type": "boolean"},
                "is_coordinator": {"type": "boolean"},
                "is_student": {"type": "boolean"},
            }
        }}
    )
    def get(self, request):
        user = request.user
        return Response({
            'roles': user.get_all_roles(),
            'primary_role': user.primary_role,
            'permissions': user.get_all_permissions(),
            'is_admin': user.is_admin,
            'is_coordinator': user.is_coordinator,
            'is_student': user.is_student,
        })


class ResendVerificationEmailView(APIView):
    """
    API endpoint to resend verification email.
    
    POST /api/accounts/resend-verification/
    Body: {"email": "user@example.com"}
    
    Rate limited to prevent abuse (1 request per 5 minutes per email).
    """
    permission_classes = []  # Allow unauthenticated
    throttle_classes = [BurstRateThrottle]
    
    @extend_schema(
        summary="Resend verification email",
        description="Resend email verification link to user's email address",
        request={
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"}
            },
            "required": ["email"]
        },
        responses={
            200: {"description": "Verification email sent"},
            400: {"description": "Email already verified or not found"},
            429: {"description": "Too many requests"}
        }
    )
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response(
                {"error": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        User = get_user_model()
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if email exists (security)
            return Response(
                {"message": "If the email exists, a verification link has been sent."},
                status=status.HTTP_200_OK
            )
        
        # Check if already verified
        if user.is_email_verified:
            return Response(
                {"error": "Email is already verified"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate new token and send email
        from accounts.services import AccountService
        from notifications.services import NotificationService
        
        token = AccountService.generate_email_verification_token(user)
        
        NotificationService.send_notification(
            recipient=user,
            title="Email Verification Required",
            message=f"Please verify your email using this token: {token}",
            notification_type='email',
            transactional_route_key="account_security_email",
        )
        
        return Response(
            {"message": "Verification email sent successfully."},
            status=status.HTTP_200_OK
        )
