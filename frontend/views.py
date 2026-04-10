from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.response import Response

from analytics.services import AnalyticsService

# Add application_forms import
from core.cache import cache_page_with_auth
from exchange.forms import ProgramForm
from exchange.models import Application, Program

# Create your views here.


def home_view(request):
    """Marketing home when Wagtail is not installed (e.g. default unit test settings)."""
    if request.user.is_authenticated:
        return redirect("/seim/dashboard/")

    try:
        total_programs = Program.objects.filter(is_active=True).count()
        total_applications = Application.objects.count()
    except Exception:
        total_programs = 0
        total_applications = 0

    return render(
        request,
        "frontend/home.html",
        {"total_programs": total_programs, "total_applications": total_applications},
    )


def register_view(request):
    """Registration page."""
    if request.user.is_authenticated:
        return redirect("/seim/dashboard/")

    return render(request, "frontend/auth/register.html")


def logout_view(request):
    """Logout view that handles both Django session and JWT tokens."""
    # Clear Django session
    logout(request)

    # Return a response that will clear JWT tokens via JavaScript
    response = redirect("/seim/login/")
    response.set_cookie('clear_jwt_tokens', 'true', max_age=1)  # Short-lived cookie to signal JS
    messages.success(request, "You have been logged out successfully.")
    return response


# Pure JS-protected dashboard: always render the shell, JS handles authentication and user state
def dashboard_view(request):
    """Dashboard shell; user-specific content is loaded via JS using JWT."""
    return render(request, "frontend/dashboard.html")


# cache_page_with_auth handles authentication and caching for authenticated users
@login_required
@cache_page_with_auth(timeout=600, key_prefix="programs")  # Cache for 10 minutes
def programs_view(request):
    """Programs listing page with caching."""
    programs = Program.objects.filter(is_active=True)
    return render(
        request,
        "frontend/programs/list.html",
        {"programs": programs, "user": request.user},
    )


# cache_page_with_auth handles authentication and caching for authenticated users
@login_required
@cache_page_with_auth(timeout=300, key_prefix="applications")  # Cache for 5 minutes
def applications_view(request):
    """Applications listing page with caching."""
    user = request.user

    if user.has_any_role(['coordinator', 'admin']):
        applications = Application.objects.all()
    else:
        applications = Application.objects.filter(student=user)

    return render(
        request,
        "frontend/applications/list.html",
        {"applications": applications, "user": user},
    )





@method_decorator(
    cache_page_with_auth(timeout=1800, key_prefix="analytics"), name="dispatch"
)  # Cache for 30 minutes
class AnalyticsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Analytics and reporting page with caching."""

    template_name = "frontend/admin/analytics.html"

    def test_func(self):
        return self.request.user.has_any_role(["admin", "coordinator"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get cached analytics data
        try:
            metrics = AnalyticsService.get_dashboard_metrics()
            context["metrics"] = metrics
        except Exception:
            context["metrics"] = {}

        return context


# cache_page_with_auth handles authentication and caching for authenticated users
@cache_page_with_auth(
    timeout=1800, key_prefix="admin_dashboard"
)  # Cache for 30 minutes
def admin_dashboard_view(request):
    """Admin dashboard with comprehensive analytics and caching."""
    if (
        not request.user.is_authenticated
        or not request.user.is_admin
    ):
        return redirect("/seim/dashboard/")

    # Get cached analytics data
    try:
        metrics = AnalyticsService.get_dashboard_metrics()
        program_metrics = AnalyticsService.get_program_metrics()
    except Exception:
        metrics = {}
        program_metrics = {}

    context = {
        "user": request.user,
        "metrics": metrics,
        "program_metrics": program_metrics,
        "role": "admin",
    }

    return render(request, "frontend/admin/dashboard.html", context)


@cache_page_with_auth(
    timeout=900, key_prefix="coordinator_dashboard"
)  # Cache for 15 minutes
def coordinator_dashboard_view(request):
    """
    Coordinator dashboard for reviewing applications and managing documents.
    Accessible to coordinators and admins.
    """
    if (
        not request.user.is_authenticated
        or not request.user.has_any_role(['coordinator', 'admin'])
    ):
        return redirect("/seim/dashboard/")

    # Get pending applications and documents
    try:
        from exchange.models import Application
        
        pending_applications = Application.objects.filter(
            status__name__in=['submitted', 'under_review']
        ).select_related(
            'student', 'program', 'status'
        ).order_by('-updated_at')[:20]
        
        # Get documents needing validation
        from documents.models import Document
        
        pending_documents = Document.objects.filter(
            documentvalidation__isnull=True
        ).select_related(
            'application', 'application__student', 'type'
        ).order_by('-uploaded_at')[:20]
        
        # Get recent activity
        recent_applications = Application.objects.all().select_related(
            'student', 'program', 'status'
        ).order_by('-updated_at')[:10]
        
    except Exception:
        pending_applications = []
        pending_documents = []
        recent_applications = []

    context = {
        "user": request.user,
        "pending_applications": pending_applications,
        "pending_documents": pending_documents,
        "recent_applications": recent_applications,
        "role": "coordinator",
    }

    return render(request, "frontend/coordinator/dashboard.html", context)


def invalidate_user_cache(request):
    """Invalidate cache for the current user."""
    if request.user.is_authenticated:
        user_id = request.user.id
        # Invalidate user-specific cache
        from core.cache import invalidate_cache_pattern

        invalidate_cache_pattern(f"*{user_id}*")
        return JsonResponse({"status": "Cache invalidated"})
    return JsonResponse({"status": "Not authenticated"}, status=401)


@require_http_methods(["POST"])
def clear_cache_view(request):
    """Clear all cache (admin only)."""
    if (
        not request.user.is_authenticated
        or not request.user.is_admin
    ):
        return JsonResponse({"error": "Unauthorized"}, status=403)

    try:
        # Clear all cache
        cache.clear()
        return JsonResponse({"status": "All cache cleared successfully"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def profile_view(request):
    """User profile page."""
    return render(request, "frontend/profile.html", {"user": request.user})


@login_required
def sessions_view(request):
    """User session management page - view and revoke active sessions."""
    from accounts.models import UserSession
    
    sessions = UserSession.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('-last_activity')
    
    context = {
        "user": request.user,
        "sessions": sessions,
    }
    
    return render(request, "frontend/sessions.html", context)


@login_required
def user_management_view(request):
    """
    User management page for coordinators and admins.
    Shows all users with their last login times and session information.
    """
    # Check permission
    if not request.user.has_any_role(['coordinator', 'admin']):
        messages.error(request, "You don't have permission to access this page.")
        return redirect("/seim/dashboard/")
    
    from django.contrib.auth import get_user_model
    from accounts.models import UserSession
    from django.db.models import Max, Count, Q
    
    User = get_user_model()
    
    # Get filter parameters
    role_filter = request.GET.get('role', '')
    search_query = request.GET.get('search', '')
    
    # Build query
    users = User.objects.annotate(
        last_login_time=Max('sessions__last_activity'),
        active_sessions_count=Count('sessions', filter=Q(sessions__is_active=True))
    ).select_related().prefetch_related('roles')
    
    # Apply filters
    if role_filter:
        users = users.filter(roles__name=role_filter)
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    users = users.order_by('-last_login_time')
    
    context = {
        "user": request.user,
        "users": users,
        "role_filter": role_filter,
        "search_query": search_query,
    }
    
    return render(request, "frontend/user-management.html", context)


@login_required
def settings_view(request):
    """User settings page."""
    return render(request, "frontend/settings.html", {"user": request.user})


@login_required
def preferences_view(request):
    """User preferences page for theme and accessibility settings."""
    return render(request, "preferences.html", {"user": request.user})


@login_required
def calendar_view(request):
    """Calendar page showing program dates and deadlines."""
    return render(request, "calendar.html", {"user": request.user})


def dark_mode_test_view(request):
    """Dark mode test page."""
    return render(request, "frontend/dark-mode-test.html")


def theme_test_view(request):
    """Theme test view for testing theme toggle functionality."""
    return render(request, "frontend/theme-test.html")


def application_create_view(request):
    """Create new application page."""
    # Get program ID from query params if provided
    program_id = request.GET.get('program')
    form_type = None

    if program_id:
        try:
            program = Program.objects.get(pk=program_id)
            form_type = program.application_form
        except Program.DoesNotExist:
            pass

    return render(
        request,
        "frontend/applications/form.html",
        {
            "user": request.user,
            "action": "create",
            "form_type": form_type,
            "form_data": {},
        },
    )


def application_detail_view(request, pk):
    """Application detail page."""
    try:
        application = Application.objects.get(pk=pk)
        # Check if user has permission to view this application
        if not request.user.is_staff and application.student != request.user:
            messages.error(
                request, "You do not have permission to view this application."
            )
            return redirect("frontend:applications")

        return render(
            request,
            "frontend/applications/detail.html",
            {"application": application, "user": request.user},
        )
    except Application.DoesNotExist:
        messages.error(request, "Application not found.")
        return redirect("frontend:applications")


def application_edit_view(request, pk):
    """Edit application page."""
    try:
        application = Application.objects.get(pk=pk)
        # Check if user has permission to edit this application
        if not request.user.is_staff and application.student != request.user:
            messages.error(
                request, "You do not have permission to edit this application."
            )
            return redirect("frontend:applications")

        # Get dynamic form data if exists
        form_type = application.program.application_form if application.program else None
        form_data = {}

        if form_type:
            try:
                from application_forms.models import FormSubmission
                submission = FormSubmission.objects.filter(
                    application=application,
                    form_type=form_type
                ).first()

                if submission:
                    form_data = submission.responses
            except ImportError:
                pass

        return render(
            request,
            "frontend/applications/form.html",
            {
                "application": application,
                "user": request.user,
                "action": "edit",
                "form_type": form_type,
                "form_data": form_data,
            },
        )
    except Application.DoesNotExist:
        messages.error(request, "Application not found.")
        return redirect("frontend:applications")


def password_reset_view(request):
    if (
        request.method == "POST"
        and request.headers.get("x-requested-with") == "XMLHttpRequest"
    ):
        email = request.POST.get("email")
        if not email:
            return Response(
                {"success": False, "message": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Simulate sending reset email
        # In production, trigger actual reset logic
        return Response(
            {"success": True, "message": "Password reset link sent."},
            status=status.HTTP_200_OK,
        )
    if request.user.is_authenticated:
        return redirect("/seim/dashboard/")

    return render(request, "frontend/auth/password_reset.html")


def theme_feedback_test_view(request):
    """Theme feedback positioning test page."""
    return render(request, "frontend/theme-feedback-test.html")


def documents_list_view(request):
    """Placeholder view for documents list."""
    return render(request, "frontend/documents/list.html", {"documents": []})


def is_admin(user):
    """Check if user is admin (for use with user_passes_test decorator)."""
    return user.is_admin

@login_required
@user_passes_test(is_admin)
def program_create_view(request):
    """Create new program (admin only)."""
    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Program created successfully!")
            return redirect('frontend:programs')
    else:
        form = ProgramForm()
    return render(request, 'frontend/programs/form.html', {'form': form})
