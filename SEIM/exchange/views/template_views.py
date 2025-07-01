from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, TemplateView
from django.views.decorators.cache import cache_control
from django_ratelimit.decorators import ratelimit

from ..forms import LoginForm, RegistrationForm, UserProfileForm
from ..models import Exchange, UserProfile


@method_decorator(ratelimit(key="ip", rate="5/m", method=["GET", "POST"]), name="dispatch")
@method_decorator(cache_control(no_cache=True, no_store=True, must_revalidate=True), name="dispatch")
class CustomLoginView(LoginView):
    """
    Custom login view using Django templates with rate limiting and session management.
    - Rate limited to 5 attempts per minute per IP address
    - Implements Remember Me functionality
    - Includes security headers to prevent caching
    """

    template_name = "authentication/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True
    success_url = reverse_lazy("exchange:dashboard")

    def form_valid(self, form):
        """Process valid form data."""
        remember_me = form.cleaned_data.get("remember_me", False)
        if not remember_me:
            # Session expires when browser closes
            self.request.session.set_expiry(0)
        else:
            # Session expires in 30 days
            self.request.session.set_expiry(timedelta(days=30))

        messages.success(self.request, f"Welcome back, {form.get_user().username}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        """Handle invalid login attempts."""
        messages.error(
            self.request,
            "Invalid username or password. Please try again."
        )
        return super().form_invalid(form)

    def get_success_url(self):
        """Return the success URL."""
        next_url = self.request.GET.get('next')
        if next_url and next_url.startswith('/'):
            return next_url
        return self.success_url


@method_decorator(cache_control(no_cache=True, no_store=True, must_revalidate=True), name="dispatch")
class CustomLogoutView(LogoutView):
    """Custom logout view with security headers"""

    next_page = reverse_lazy("exchange:login")

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "You have been successfully logged out.")
        response = super().dispatch(request, *args, **kwargs)
        # Clear session data
        request.session.flush()
        return response


@method_decorator(ratelimit(key='ip', rate='3/h', method=['GET', 'POST']), name='dispatch')
@method_decorator(cache_control(no_cache=True, no_store=True, must_revalidate=True), name="dispatch")
class RegistrationView(CreateView):
    """
    User registration view with rate limiting and validation
    - Rate limited to 3 registration attempts per hour per IP
    - Auto-creates user profile
    - Implements email uniqueness check
    """

    template_name = "authentication/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("exchange:dashboard")

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()

        # Auto-login after registration
        login(self.request, user)
        messages.success(
            self.request,
            f"Welcome {user.get_full_name() or user.username}! Your account has been created successfully."
        )
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


@login_required
def dashboard_view(request):
    """
    Dashboard view for authenticated users
    """
    user = request.user
    context = {
        "user": user,
    }

    # Get exchange statistics based on user role
    if hasattr(user, "profile"):
        profile = user.profile

        if profile.role == "STUDENT":
            exchanges = Exchange.objects.filter(student=user)
        elif profile.role in ["COORDINATOR", "ADMINISTRATOR"]:
            exchanges = Exchange.objects.all()
        else:
            exchanges = Exchange.objects.none()

        # Calculate statistics
        context.update(
            {
                "total_exchanges": exchanges.count(),
                "active_exchanges": exchanges.filter(status__in=["submitted", "under_review", "approved"]).count(),
                "pending_exchanges": exchanges.filter(status="submitted").count(),
                "completed_exchanges": exchanges.filter(status="completed").count(),
                "recent_exchanges": exchanges.order_by("-created_at")[:5],
            }
        )
    else:
        # If no profile exists, create one
        UserProfile.objects.get_or_create(user=user, defaults={"role": "STUDENT"})
        context.update(
            {
                "total_exchanges": 0,
                "active_exchanges": 0,
                "pending_exchanges": 0,
                "completed_exchanges": 0,
                "recent_exchanges": [],
            }
        )

    return render(request, "exchange/dashboard.html", context)


@login_required
def profile_view(request):
    """
    User profile view and update
    """
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("exchange:profile")
    else:
        form = UserProfileForm(instance=profile)

    return render(request, "authentication/profile.html", {"form": form})


@login_required
def exchange_list_view(request):
    """
    List all exchanges accessible to the user
    """
    user = request.user

    if hasattr(user, "profile"):
        if user.profile.role == "STUDENT":
            exchanges = Exchange.objects.filter(student=user)
        else:
            exchanges = Exchange.objects.all()
    else:
        exchanges = Exchange.objects.filter(student=user)

    # Apply filters if provided
    status = request.GET.get("status")
    if status:
        exchanges = exchanges.filter(status=status)

    exchanges = exchanges.order_by("-created_at")

    return render(
        request,
        "exchange/exchange_list.html",
        {
            "exchanges": exchanges,
            "status_choices": Exchange.STATUS_CHOICES,
        },
    )


@login_required
def exchange_detail_view(request, pk):
    """
    Detail view for a specific exchange
    """
    # Function body for exchange_detail_view would go here
    pass


@login_required
def create_exchange_view(request):
    """
    Create a new exchange application
    """
    # This is a placeholder function body
    if request.method == "POST":
        # Process form submission
        pass
    else:
        # Display form
        pass
    return redirect("exchange:exchange-list")


@login_required
def exchange_edit_view(request, pk):
    """
    Edit an existing exchange application
    """
    # This is a placeholder function body - adding the missing function
    if request.method == "POST":
        # Process form submission for editing
        pass
    else:
        # Display edit form
        pass
    return redirect("exchange:exchange-list")


@login_required
def pending_approvals_view(request):
    """
    View pending approvals (for coordinators/administrators)
    """
    if not hasattr(request.user, "profile") or request.user.profile.role not in [
        "COORDINATOR",
        "ADMINISTRATOR",
    ]:
        messages.error(request, "You do not have permission to view this page.")
        return redirect("exchange:dashboard")

    # For now, redirect to exchange list with filter
    return redirect("exchange:exchange-list")


class HomeView(TemplateView):
    """
    Home page view (redirects to dashboard if authenticated)
    """

    template_name = "home/home.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("exchange:dashboard")
        return super().get(request, *args, **kwargs)
