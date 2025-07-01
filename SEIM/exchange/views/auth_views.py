"""
Authentication views for handling user registration and login.
"""
from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.cache import cache_control
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import CreateView
from django_ratelimit.decorators import ratelimit
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from ..forms import LoginForm, RegistrationForm
from ..services.email_service import EmailService
from ..models import StudentProfile, StaffProfile
from ..serializers import UserSerializer, StudentProfileSerializer, StaffProfileSerializer


@method_decorator(ratelimit(key='ip', rate='5/m', method=['POST']), name='post')
class CustomAuthToken(ObtainAuthToken):
    """
    Custom authentication token view that returns user data along with token
    Rate limited to 5 attempts per minute per IP address
    """

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "user": UserSerializer(user).data,
                "profile": (StudentProfileSerializer(user.profile).data if hasattr(user, "profile") else None),
            }
        )


@method_decorator(ratelimit(key='ip', rate='3/h', method=['GET', 'POST']), name='create')
@method_decorator(sensitive_post_parameters('password'), name='dispatch')
class RegisterView(generics.CreateAPIView):
    """
    User registration view
    Students can register themselves, staff accounts must be created by admins
    Rate limited to 3 attempts per hour per IP address
    """
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return render(request, "authentication/register.html", {"form": RegistrationForm()})

    def create(self, request, *args, **kwargs):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")

        # Validate required fields
        if not all([username, email, password]):
            return Response(
                {"error": "Username, email, and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username is already taken"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "Email is already registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create user with is_active=False
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=False  # User must verify email first
        )

        # Create user profile with default student role
        profile = StudentProfile.objects.create(
            user=user,
            institution=request.data.get("institution", "")
        )

        # Create token for email verification
        token = default_token_generator.make_token(user)

        # Create activation URL
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token_url = reverse('exchange:activate', kwargs={'uidb64': uid, 'token': token})
        activation_url = request.build_absolute_uri(token_url)

        # Send verification email
        email_service = EmailService()
        email_result = email_service.send_email(
            to_emails=[email],
            subject='Activate Your SEIM Account',
            template_name='account_activation_email',
            context={
                'user': user,
                'activation_url': activation_url,
            }
        )

        if not email_result:
            # If email fails, delete user and return error
            #user.delete()
            return Response(
                {"error": "User Created, but Failed to send verification email"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "message": "Registration successful. Please check your email to activate your account.",
                "email": email,
            },
            status=status.HTTP_201_CREATED,
        )


@ratelimit(key='ip', rate='5/m', method=['GET', 'POST'])
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def login_view(request):
    """
    View function for user login page
    Rate limited to 5 attempts per minute per IP address
    """
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirect to dashboard or next URL
            next_url = request.GET.get("next", "exchange:dashboard")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, "authentication/login.html", {"form": form})


@api_view(["POST", "GET"])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='10/m', method=['POST', 'GET'])
def logout_view(request):
    """
    Logout view - deletes the user's auth token
    Rate limited to 10 attempts per minute per user
    """
    if request.method == "POST":
        try:
            request.user.auth_token.delete()
            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception:
            pass  # Silent pass for token deletion errors

    logout(request)
    messages.success(request, "Account logged out successfully!")
    return redirect("exchange:login")


@login_required
@cache_control(private=True, must_revalidate=True)
def profile_view(request):
    """
    View function for user profile page - simplified version
    """
    from ..forms import StudentProfileForm, StaffProfileForm

    # Ensure user has a profile
    try:
        profile, created = StudentProfile.objects.get_or_create(user=request.user)
    except Exception:
        profile, created = StaffProfile.objects.get_or_create(user=request.user)
    # Initialize context with all expected values
    context = {
        "profile_completeness": profile.get_profile_completeness(),
        "total_exchanges": 0,
        "completed_exchanges": 0,
    }

    # Get exchange counts for students
    if isinstance(profile, StudentProfile) and hasattr(request.user, "exchange_applications"):
        exchanges = request.user.exchange_applications.all()
        context["total_exchanges"] = exchanges.count()
        context["completed_exchanges"] = exchanges.filter(status="COMPLETED").count()

    if request.method == "POST":
        form_type = request.POST.get("form_type", "personal")

        if form_type == "personal":
            if isinstance(profile, StudentProfile):
                form = StudentProfileForm(request.POST, instance=profile)
            elif isinstance(profile, StaffProfile):
                form = StaffProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect("exchange:profile")
            else:
                messages.error(request, f"Issue while saving profile!")
        else:
            # For other form types, just show a message for now
            messages.info(request, f"The {form_type} form is not yet implemented.")
            return redirect("exchange:profile")
    else:
        if isinstance(profile, StudentProfile):
            form = StudentProfileForm(instance=profile)
        elif isinstance(profile, StaffProfile):
            form = StaffProfileForm(instance=profile)

    # Pass the same form for all tabs to avoid template errors
    # In the future, different forms can be created for each tab
    context.update(
        {
            "personal_form": form,
            "academic_form": form,  # Placeholder - using same form
            "preferences_form": form,  # Placeholder - using same form
            "password_form": form,  # Placeholder - using same form
        }
    )

    return render(request, "authentication/profile.html", context)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='10/h', method='PUT')
def update_profile(request):
    """
    Update user profile information
    """
    user = request.user
    profile = user.profile if hasattr(user, "profile") else None

    if not profile:
        return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)

    # Update profile fields
    profile.institution = request.data.get("institution", profile.institution)
    profile.department = request.data.get("department", profile.department)
    profile.position = request.data.get("position", profile.position)
    profile.office_phone = request.data.get("office_phone", profile.office_phone)

    # Don't allow users to change their own role
    # Role changes should be done by admins only

    profile.save()

    return Response(
        {
            "user": UserSerializer(user).data,
            "profile": StudentProfileSerializer(profile).data if isinstance(profile, StudentProfile) else StaffProfileSerializer(profile).data,
        }
    )


@method_decorator(ratelimit(key='user', rate='3/h', method=['PUT']), name='update')
class ChangePasswordView(generics.UpdateAPIView):
    """
    Change password view with rate limiting
    Limited to 3 attempts per hour per user
    """
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not all([old_password, new_password]):
            return Response(
                {"error": "Old password and new password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify old password
        if not user.check_password(old_password):
            return Response({"error": "Invalid old password"}, status=status.HTTP_400_BAD_REQUEST)

        # Set new password
        user.set_password(new_password)
        user.save()

        # Delete old token and create new one
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)

        return Response(
            {"message": "Password changed successfully", "token": token.key},
            status=status.HTTP_200_OK
        )


@ratelimit(key='ip', rate='5/h', method=['GET'])
def activate_account(request, uidb64, token):
    """
    View for activating a user account through email verification
    Rate limited to 5 attempts per hour per IP address
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated! You can now login.")
        return redirect('exchange:login')
    else:
        messages.error(request, "The activation link is invalid or has expired.")
        return redirect('exchange:register')
