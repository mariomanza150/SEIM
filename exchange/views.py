import hashlib
import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone as dj_tz
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.cache import CacheManager, cache_api_response
from core.permissions import (
    IsAdminOrReadOnly,
    IsCoordinatorOrAdmin,
    IsStudentOrReadOnly,
)

from .agreement_renewal import AgreementRenewalService
from .calendar_events import build_calendar_event_dicts
from .calendar_ics import (
    build_subscribe_query,
    events_to_ics,
    sign_calendar_subscribe_token,
    unsign_calendar_subscribe_token,
)
from .eligibility_rules import checks_passed_labels, evaluate_eligibility
from .filters import ApplicationFilter, ExchangeAgreementFilter, ProgramFilter
from .models import (
    SEAT_HOLDING_APPLICATION_STATUS_NAMES,
    Application,
    ApplicationStatus,
    Comment,
    ExchangeAgreement,
    Program,
    SavedSearch,
    TimelineEvent,
)
from .scholarship_scoring import scholarship_scores_export_response
from .serializers import (
    ApplicationSerializer,
    ApplicationStatusSerializer,
    CalendarEventSerializer,
    CommentSerializer,
    ExchangeAgreementSerializer,
    ProgramSerializer,
    SavedSearchSerializer,
    TimelineEventSerializer,
)
from .services import ApplicationService

# Create your views here.


def calendar_subscribe_ics(request):
    """
    Public (token-authenticated) iCalendar feed for external calendar apps.

    Query: token — HMAC-signed user id (see GET .../calendar/events/subscribe-token/).
    Horizon: 90 days past through 730 days future, type=all (matches full staff/student rules).
    """
    token = request.GET.get("token", "")
    uid = unsign_calendar_subscribe_token(token)
    if uid is None:
        return HttpResponse(
            "Invalid subscription link.",
            status=403,
            content_type="text/plain; charset=utf-8",
        )
    User = get_user_model()
    try:
        user = User.objects.get(pk=uid)
    except User.DoesNotExist:
        return HttpResponse(
            "Unknown user.",
            status=404,
            content_type="text/plain; charset=utf-8",
        )
    if not user.is_active:
        return HttpResponse(
            "Inactive user.",
            status=403,
            content_type="text/plain; charset=utf-8",
        )

    start_dt = dj_tz.now() - timedelta(days=90)
    end_dt = dj_tz.now() + timedelta(days=730)
    events = build_calendar_event_dicts(
        user,
        start_param=start_dt.isoformat(),
        end_param=end_dt.isoformat(),
        event_type="all",
    )
    body = events_to_ics(events, cal_name="SEIM deadlines & milestones")
    resp = HttpResponse(body, content_type="text/calendar; charset=utf-8")
    resp["Content-Disposition"] = 'inline; filename="seim-calendar.ics"'
    return resp


class ExchangeAgreementViewSet(viewsets.ModelViewSet):
    """Staff registry for exchange agreements (coordinators and admins)."""

    serializer_class = ExchangeAgreementSerializer
    permission_classes = [IsCoordinatorOrAdmin]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ExchangeAgreementFilter
    search_fields = [
        "title",
        "partner_institution_name",
        "partner_country",
        "internal_reference",
        "partner_reference_id",
        "notes",
    ]
    ordering_fields = [
        "start_date",
        "end_date",
        "created_at",
        "partner_institution_name",
        "status",
        "title",
    ]

    def get_queryset(self):
        draft_successors = ExchangeAgreement.objects.filter(
            status=ExchangeAgreement.Status.DRAFT
        )
        return ExchangeAgreement.objects.prefetch_related(
            "programs",
            Prefetch("renewal_successors", queryset=draft_successors, to_attr="_draft_renewal_successors"),
        ).all()

    @action(detail=True, methods=["post"], url_path="mark-renewal-pending")
    def mark_renewal_pending(self, request, pk=None):
        agreement = self.get_object()
        due_raw = request.data.get("renewal_follow_up_due")
        parsed = None
        if due_raw not in (None, ""):
            from datetime import date as date_cls

            try:
                parsed = date_cls.fromisoformat(str(due_raw))
            except ValueError:
                return Response(
                    {"error": "renewal_follow_up_due must be a YYYY-MM-DD date."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        try:
            AgreementRenewalService.mark_renewal_pending(
                agreement, renewal_follow_up_due=parsed
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        agreement.refresh_from_db()
        return Response(self.get_serializer(agreement).data)

    @action(detail=True, methods=["post"], url_path="create-renewal-successor")
    def create_renewal_successor(self, request, pk=None):
        agreement = self.get_object()
        raw = request.data.get("copy_documents", True)
        if isinstance(raw, str):
            copy_documents = raw.strip().lower() in ("1", "true", "yes", "on")
        else:
            copy_documents = bool(raw)
        try:
            successor = AgreementRenewalService.create_renewal_successor(
                agreement, request.user, copy_documents=copy_documents
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            self.get_serializer(successor).data,
            status=status.HTTP_201_CREATED,
        )


class ProgramViewSet(viewsets.ModelViewSet):
    """ViewSet for exchange programs with admin-only write permissions."""

    queryset = Program.objects.prefetch_related("coordinators")
    serializer_class = ProgramSerializer
    permission_classes = [IsAdminOrReadOnly]  # Use custom permission class
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ProgramFilter  # Use advanced filter
    search_fields = ["name", "description"]
    ordering_fields = ["name", "start_date", "end_date", "created_at"]

    def get_queryset(self):
        seat_filter = Q(
            application__withdrawn=False,
            application__status__name__in=SEAT_HOLDING_APPLICATION_STATUS_NAMES,
        )
        return (
            Program.objects.prefetch_related("coordinators")
            .annotate(_seat_holding_count=Count("application", filter=seat_filter))
        )

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
        active_programs = self.get_queryset().filter(is_active=True)
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
            application_open_date=original_program.application_open_date,
            application_deadline=original_program.application_deadline,
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
            enrollment_capacity=original_program.enrollment_capacity,
            waitlist_when_full=original_program.waitlist_when_full,
        )
        cloned_program.coordinators.set(original_program.coordinators.all())

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

        Optional query: ``application=<uuid>`` — when the draft belongs to the current
        student and matches this program, includes the **required_documents** rule
        (program required document types vs uploads).
        """
        program = self.get_object()

        application_obj = None
        raw_app = request.query_params.get("application")
        if raw_app:
            try:
                aid = uuid.UUID(str(raw_app))
            except (ValueError, TypeError, AttributeError):
                return Response(
                    {"detail": "Invalid application id."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            application_obj = (
                Application.objects.filter(pk=aid)
                .only("id", "student_id", "program_id")
                .first()
            )
            if not application_obj:
                return Response(
                    {"detail": "Application not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if application_obj.student_id != request.user.pk:
                return Response(
                    {"detail": "You do not have access to this application."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if application_obj.program_id != program.pk:
                return Response(
                    {"detail": "Application does not belong to this program."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        ev = evaluate_eligibility(request.user, program, application=application_obj)
        program_snapshot = {
            "name": program.name,
            "min_gpa": program.min_gpa,
            "required_language": program.required_language,
            "min_language_level": program.min_language_level,
            "min_age": program.min_age,
            "max_age": program.max_age,
        }
        if ev.eligible:
            return Response(
                {
                    "eligible": True,
                    "message": "All eligibility requirements met",
                    "checks_passed": checks_passed_labels(program),
                    "rules": ev.rules_as_dicts(),
                    "schema_version": 3,
                }
            )
        message = (
            ev.failures[0]
            if len(ev.failures) == 1 and ev.failures[0] == "Student profile is missing."
            else (
                "Eligibility requirements not met:\n- " + "\n- ".join(ev.failures)
                if ev.failures
                else "Not eligible."
            )
        )
        return Response(
            {
                "eligible": False,
                "message": message,
                "rules": ev.rules_as_dicts(),
                "program": program_snapshot,
                "schema_version": 3,
            },
            status=status.HTTP_200_OK,
        )


def _application_list_cache_key(*args, **kwargs):
    """Scope cached list per user and full path (default decorator key omitted request user)."""
    request = args[1]
    user_key = str(request.user.pk) if request.user.is_authenticated else "anon"
    identity = f"ApplicationViewSet.list:{user_key}:{request.get_full_path()}"
    digest = hashlib.sha256(identity.encode()).hexdigest()[:48]
    return CacheManager.get_cache_key("api_response", digest)


def _application_retrieve_cache_key(*args, **kwargs):
    """Scope cached detail per user and application id."""
    request = args[1]
    user_key = str(request.user.pk) if request.user.is_authenticated else "anon"
    pk = kwargs.get("pk", "")
    identity = f"ApplicationViewSet.retrieve:{user_key}:{pk}"
    digest = hashlib.sha256(identity.encode()).hexdigest()[:48]
    return CacheManager.get_cache_key("api_response", digest)


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
    filterset_class = ApplicationFilter  # Use advanced filter
    search_fields = ["program__name", "student__username", "student__email"]
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
            'assigned_coordinator',
            'status'             # ForeignKey
        ).prefetch_related(
            'program__coordinators',
            'program__required_document_types',
            'student__roles',    # ManyToMany through student
            "comments",
            "comments__author",
            "comments__author__roles",
            "timeline_events",  # Reverse FK: events for this application
            "timeline_events__created_by",
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

    @cache_api_response(timeout=300, key_func=_application_list_cache_key)
    def list(self, request, *args, **kwargs):
        """List applications with caching."""
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=300, key_func=_application_retrieve_cache_key)
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific application with caching."""
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=["get"], url_path="scholarship-scores-export")
    def scholarship_scores_export(self, request):
        """Export scholarship scores for a program cohort: CSV (default), XLSX, or PDF (staff)."""
        user = request.user
        if not user.is_authenticated or not user.has_any_role(["coordinator", "admin"]):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        program_id = request.query_params.get("program")
        if not program_id:
            return Response(
                {"error": "Query parameter 'program' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        from .models import Program

        program = Program.objects.filter(pk=program_id).first()
        if not program:
            return Response({"error": "Program not found."}, status=status.HTTP_404_NOT_FOUND)

        qs = (
            Application.objects.filter(program_id=program_id)
            .select_related("program", "student", "status", "student__profile")
            .prefetch_related(
                "program__required_document_types",
                "document_set",
                "document_set__type",
            )
            .order_by("created_at")
        )
        export_format = request.query_params.get("export_format", "csv")
        try:
            return scholarship_scores_export_response(
                program_id,
                qs,
                export_format=export_format,
                program_name=program.name,
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

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
                from notifications.services import NotificationService

                NotificationService.broadcast_application_sync(
                    str(application_id), "comment_added"
                )
        return response


class TimelineEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TimelineEvent.objects.all()
    serializer_class = TimelineEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["application", "event_type", "created_by"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["created_at"]

    def get_queryset(self):
        """
        Filter timeline events based on user permissions with optimizations.

        Uses select_related to prevent N+1 queries.
        """
        user = self.request.user

        # Base queryset with optimizations (default chronological for timelines)
        base_qs = TimelineEvent.objects.select_related(
            'application',              # ForeignKey
            'application__program',     # Through application
            'application__student',     # Through application
            'application__status',      # Through application
            'created_by',               # ForeignKey (nullable)
        ).prefetch_related(
            'created_by__roles'        # Creator's roles (if exists)
        )

        if user.has_role("coordinator") or user.has_role("admin"):
            return base_qs
        else:
            # Students can only see events for their own applications
            return base_qs.filter(application__student=user)


class SavedSearchViewSet(viewsets.ModelViewSet):
    """ViewSet for saved searches (coordinators/admins only)."""

    queryset = SavedSearch.objects.all()
    serializer_class = SavedSearchSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['search_type', 'is_default']
    ordering_fields = ['created_at', 'name']

    def get_queryset(self):
        """Users can only see their own saved searches."""
        return SavedSearch.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Set user from request."""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """
        Apply a saved search and return the filters.

        Returns the filter parameters that can be used to filter
        programs or applications.
        """
        saved_search = self.get_object()
        return Response({
            'search_type': saved_search.search_type,
            'filters': saved_search.filters,
            'name': saved_search.name
        })

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set this search as the default for its type."""
        saved_search = self.get_object()
        saved_search.is_default = True
        saved_search.save()
        return Response({'status': 'default set'})


class CalendarEventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for calendar events (FullCalendar-friendly JSON).

    Query parameters:
    - start, end: ISO datetimes bounding visible range (default ~30d past to 365d future)
    - type: `program` | `deadline` | `application` | `agreement` | `all`
      When omitted, returns program + deadline + application, and agreement ends for staff only.
    """

    serializer_class = CalendarEventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Program.objects.none()

    def list(self, request, *args, **kwargs):
        events = build_calendar_event_dicts(
            request.user,
            start_param=request.query_params.get("start"),
            end_param=request.query_params.get("end"),
            event_type=request.query_params.get("type"),
        )
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="subscribe-token")
    def subscribe_token(self, request):
        """Return signed HTTPS and webcal URLs for the personal ICS feed (no JWT in calendar clients)."""
        token = sign_calendar_subscribe_token(request.user.pk)
        q = build_subscribe_query(token)
        path = reverse("api:calendar-subscribe-ics")
        ics_url = request.build_absolute_uri(f"{path}?{q}")
        webcal_url = ics_url.replace("https://", "webcal://", 1).replace(
            "http://", "webcal://", 1
        )
        return Response({"ics_url": ics_url, "webcal_url": webcal_url})
