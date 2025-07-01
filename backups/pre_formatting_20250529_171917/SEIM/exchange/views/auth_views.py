"""
Authentication views for the exchange app.
"""

from django.contrib.auth import authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from ..models import UserProfile
from ..serializers import UserProfileSerializer, UserSerializer


class CustomAuthToken(ObtainAuthToken):
    """
    Custom authentication token view that returns user data along with token
    """

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)

        # Return token with user data
        return Response(
            {
                "token": token.key,
                "user": UserSerializer(user).data,
                "profile": (
                    UserProfileSerializer(user.profile).data
                    if hasattr(user, "profile")
                    else None
                ),
            }
        )


class RegisterView(generics.CreateAPIView):
    """
    User registration view
    Students can register themselves, staff accounts must be created by admins
    """

    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        # Extract user data
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
                {"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "Email already registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Create user profile with default student role
        profile = UserProfile.objects.create(
            user=user, role="STUDENT", institution=request.data.get("institution", "")
        )

        # Create auth token
        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "user": UserSerializer(user).data,
                "profile": UserProfileSerializer(profile).data,
            },
            status=status.HTTP_201_CREATED,
        )


from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from ..forms import LoginForm  # This is the custom login form


def login_view(request):
    """
    View function for user login page
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
def logout_view(request):
    """
    Logout view - deletes the user's auth token
    """
    if request.method == "POST":
        try:
            # Delete the user's token
            request.user.auth_token.delete()
            return Response(
                {"message": "Successfully logged out"}, status=status.HTTP_200_OK
            )
        except:
            pass  # return Response({'error': 'Error logging out'}, status=status.HTTP_400_BAD_REQUEST)

    logout(request)
    messages.success(request, "Account logged out successfully!")
    return redirect("exchange:login")


@login_required
def profile_view(request):
    """
    View function for user profile page - simplified version
    """
    from ..forms import UserProfileForm

    # Ensure user has a profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Initialize context with all expected values
    context = {
        "profile_completeness": profile.get_profile_completeness(),
        "total_exchanges": 0,
        "completed_exchanges": 0,
    }

    # Get exchange counts for students
    if profile.is_student and hasattr(request.user, "exchange_applications"):
        exchanges = request.user.exchange_applications.all()
        context["total_exchanges"] = exchanges.count()
        context["completed_exchanges"] = exchanges.filter(status="COMPLETED").count()

    if request.method == "POST":
        form_type = request.POST.get("form_type", "personal")

        if form_type == "personal":
            form = UserProfileForm(request.POST, instance=profile)
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
        form = UserProfileForm(instance=profile)

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
def update_profile(request):
    """
    Update user profile information
    """
    user = request.user
    profile = user.profile if hasattr(user, "profile") else None

    if not profile:
        return Response(
            {"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND
        )

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
            "profile": UserProfileSerializer(profile).data,
        }
    )


class ChangePasswordView(generics.UpdateAPIView):
    """
    Change password view
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
            return Response(
                {"error": "Invalid old password"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Set new password
        user.set_password(new_password)
        user.save()

        # Delete old token and create new one
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)

        return Response(
            {"message": "Password changed successfully", "token": token.key}
        )
