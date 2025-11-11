from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.cache import cache_api_response
from core.permissions import IsAdminOrReadOnly, IsStudentOrReadOnly

from .models import (
    Application,
    ApplicationStatus,
    Comment,
    Program,
    TimelineEvent,
)
from .serializers import (
    ApplicationSerializer,
    ApplicationStatusSerializer,
    CommentSerializer,
    ProgramSerializer,
    TimelineEventSerializer,
)
from .services import ApplicationService

# Create your views here.


class ProgramViewSet(viewsets.ModelViewSet):
    """ViewSet for exchange programs with admin-only write permissions."""

    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [IsAdminOrReadOnly]  # Use custom permission class
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "start_date", "end_date", "created_at"]

    @cache_api_response(timeout=600)  # Cache for 10 minutes
    def list(self, request, *args, **kwargs):
        """List all programs with caching."""
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=600)  # Cache for 10 minutes
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific program with caching."""
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    @cache_api_response(timeout=600)  # Cache for 10 minutes
    def active(self, request):
        """Get only active programs with caching."""
        active_programs = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(active_programs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def clone(self, request, pk=None):
        """
        Clone an existing program to speed up creation of similar programs.

        Creates a copy of the program with:
        - Same configuration (min_gpa, required_language, recurring)
        - Same application form
        - New name (appended with " (Copy)")
        - New dates (to be set by admin)
        - Marked as inactive by default

        Admins can then modify the cloned program before activating it.
        """
        original_program = self.get_object()

        # Create a clone with modified name
        cloned_program = Program.objects.create(
            name=f"{original_program.name} (Copy)",
            description=original_program.description,
            start_date=original_program.start_date,
            end_date=original_program.end_date,
            is_active=False,  # Start as inactive, admin must activate
            min_gpa=original_program.min_gpa,
            required_language=original_program.required_language,
            min_language_level=original_program.min_language_level,
            min_age=original_program.min_age,
            max_age=original_program.max_age,
            auto_reject_ineligible=original_program.auto_reject_ineligible,
            recurring=original_program.recurring,
            application_form=original_program.application_form,
        )

        # Invalidate program cache
        from core.cache import invalidate_cache_pattern
        invalidate_cache_pattern("api:ProgramViewSet:*")

        serializer = self.get_serializer(cloned_program)
        return Response(
            {
                "status": "Program cloned successfully",
                "program": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["get"])
    def check_eligibility(self, request, pk=None):
        """
        Check if the current user is eligible for this program.

        Returns detailed eligibility status including:
        - Whether student meets all requirements
        - List of requirements checked
        - Detailed error messages if ineligible

        Useful for showing eligibility warnings before students start applications.
        """
        program = self.get_object()

        try:
            result = ApplicationService.check_eligibility(request.user, program)
            return Response(result)
        except ValueError as e:
            return Response(
                {
                    "eligible": False,
                    "message": str(e),
                    "program": {
                        "name": program.name,
                        "min_gpa": program.min_gpa,
                        "required_language": program.required_language,
                        "min_language_level": program.min_language_level,
                        "min_age": program.min_age,
                        "max_age": program.max_age,
                    }
                },
                status=status.HTTP_200_OK  # Not an error, just ineligible
            )


class ApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for applications with student-only write permissions."""

    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsStudentOrReadOnly]  # Use custom permission class
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "program", "student"]
    search_fields = ["program__name"]
    ordering_fields = ["created_at", "submitted_at"]

    def get_queryset(self):
        """
        Filter queryset based on user role with optimized queries.

        Uses select_related for foreign keys and prefetch_related for
        reverse foreign keys to prevent N+1 queries.
        """
        user = self.request.user

        # Base queryset with all optimizations
        base_qs = Application.objects.select_related(
            'program',           # ForeignKey - use select_related
            'student',           # ForeignKey
            'status'             # ForeignKey
        ).prefetch_related(
            'student__roles',    # ManyToMany through student
            'comment_set',       # Reverse ForeignKey (comments for this application)
            'comment_set__author',  # And the authors of those comments
            'comment_set__author__roles',  # And their roles
            'timelineevent_set',    # Reverse ForeignKey (events for this application)
            'timelineevent_set__created_by',  # And who created those events
            'document_set',         # Reverse ForeignKey (documents)
            'document_set__type',   # Document types
            'document_set__uploaded_by'  # Who uploaded them
        )

        # Filter based on role
        if user.has_role("coordinator") or user.has_role("admin"):
            return base_qs
        else:
            return base_qs.filter(student=user)

    def perform_create(self, serializer):
        """Set student to current user on creation."""
        serializer.save(student=self.request.user)

    @cache_api_response(timeout=300)  # Cache for 5 minutes
    def list(self, request, *args, **kwargs):
        """List applications with caching."""
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=300)  # Cache for 5 minutes
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific application with caching."""
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        """Submit an application."""
        application = self.get_object()
        try:
            ApplicationService.submit_application(application, request.user)
            # Invalidate cache after submission
            self._invalidate_application_cache(application)
            return Response({"status": "Application submitted successfully"})
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def withdraw(self, request, pk=None):
        """Withdraw an application."""
        application = self.get_object()
        try:
            ApplicationService.withdraw_application(application, request.user)
            # Invalidate cache after withdrawal
            self._invalidate_application_cache(application)
            return Response({"status": "Application withdrawn successfully"})
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def _invalidate_application_cache(self, application):
        """Invalidate cache for application-related data."""
        from core.cache import invalidate_cache_pattern

        # Invalidate application-specific cache
        invalidate_cache_pattern(f"api:ApplicationViewSet:*{application.id}*")
        # Invalidate list cache
        invalidate_cache_pattern("api:ApplicationViewSet:list*")


class ApplicationStatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ApplicationStatus.objects.all().order_by("order")
    serializer_class = ApplicationStatusSerializer
    permission_classes = [permissions.IsAuthenticated]

    @cache_api_response(timeout=1800)  # Cache for 30 minutes (statuses rarely change)
    def list(self, request, *args, **kwargs):
        """List all application statuses with caching."""
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=1800)  # Cache for 30 minutes
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific status with caching."""
        return super().retrieve(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["application", "author", "is_private"]

    def get_queryset(self):
        """
        Filter comments based on user role and permissions with optimizations.

        Uses select_related to prevent N+1 queries when accessing related objects.
        """
        user = self.request.user

        # Base queryset with optimizations
        base_qs = Comment.objects.select_related(
            'application',              # ForeignKey
            'application__program',     # Through application
            'application__student',     # Through application
            'application__status',      # Through application
            'author',                   # ForeignKey
        ).prefetch_related(
            'author__roles'            # Author's roles
        )

        if user.has_role("coordinator") or user.has_role("admin"):
            return base_qs
        else:
            # Students can only see their own comments and public comments on their applications
            return base_qs.filter(
                Q(author=user) | Q(application__student=user, is_private=False)
            )

    def perform_create(self, serializer):
        """Set author to current user on creation."""
        serializer.save(author=self.request.user)

    @cache_api_response(timeout=300)  # Cache for 5 minutes
    def list(self, request, *args, **kwargs):
        """List comments with caching."""
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Create a comment and invalidate cache."""
        response = super().create(request, *args, **kwargs)
        # Invalidate comment cache for the application
        if response.status_code == 201:
            application_id = request.data.get("application")
            if application_id:
                from core.cache import invalidate_cache_pattern

                invalidate_cache_pattern(f"api:CommentViewSet:*{application_id}*")
        return response


class TimelineEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TimelineEvent.objects.all()
    serializer_class = TimelineEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["application", "event_type", "created_by"]

    def get_queryset(self):
        """
        Filter timeline events based on user permissions with optimizations.

        Uses select_related to prevent N+1 queries.
        """
        user = self.request.user

        # Base queryset with optimizations
        base_qs = TimelineEvent.objects.select_related(
            'application',              # ForeignKey
            'application__program',     # Through application
            'application__student',     # Through application
            'application__status',      # Through application
            'created_by',               # ForeignKey (nullable)
        ).prefetch_related(
            'created_by__roles'        # Creator's roles (if exists)
        ).order_by('-created_at')      # Most recent first

        if user.has_role("coordinator") or user.has_role("admin"):
            return base_qs
        else:
            # Students can only see events for their own applications
            return base_qs.filter(application__student=user)

    @cache_api_response(timeout=300)  # Cache for 5 minutes
    def list(self, request, *args, **kwargs):
        """List timeline events with caching."""
        return super().list(request, *args, **kwargs)
