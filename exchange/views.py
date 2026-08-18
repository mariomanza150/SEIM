import hashlib
import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone as dj_tz
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from core.cache import (
    CacheManager,
    application_api_cache_generation,
    cache_api_response,
    invalidate_application_api_responses,
)
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
from .eligibility_rules import (
    ELIGIBILITY_SCHEMA_VERSION,
    checks_passed_labels,
    evaluate_eligibility,
)
from .eligibility_rulesets import ProgramEligibilityProxy, parse_ruleset_overrides
from .filters import ApplicationFilter, ExchangeAgreementFilter, ProgramFilter
from .models import (
    SEAT_HOLDING_APPLICATION_STATUS_NAMES,
    AgreementComment,
    Application,
    ApplicationStatus,
    ApplicationSubjectPlanVersion,
    ApplicationSubjectSelection,
    Comment,
    EligibilityRuleSet,
    ExchangeAgreement,
    HostAcademicProgram,
    HostInstitution,
    HostSchool,
    HostSubject,
    Program,
    SavedSearch,
    TimelineEvent,
    visible_host_subjects_queryset,
)
from .scholarship_scoring import scholarship_scores_export_response
from .subject_grades import (
    confirm_subject_grades,
    persist_carta_homologacion,
    propose_subject_grades,
    reject_subject_grades,
)
from .subject_plan_versions import (
    snapshot_subject_plan,
    subject_plan_mapping_changed,
)
from .serializers import (
    AgreementCommentSerializer,
    ApplicationSerializer,
    ApplicationStatusSerializer,
    ApplicationSubjectPlanVersionSerializer,
    ApplicationSubjectSelectionSerializer,
    CalendarEventSerializer,
    CommentSerializer,
    EligibilityRuleSetSerializer,
    ExchangeAgreementSerializer,
    HostAcademicProgramSerializer,
    HostInstitutionSerializer,
    HostSchoolSerializer,
    HostSubjectSerializer,
    ProgramCheckEligibilityResponseSerializer,
    ProgramSerializer,
    SavedSearchSerializer,
    TimelineEventSerializer,
)
from .services import ApplicationService

# Create your views here.


_PROGRAM_CACHE_GEN_KEY = "api_cache_gen:ProgramViewSet"


def _program_cache_generation() -> str:
    value = cache.get(_PROGRAM_CACHE_GEN_KEY)
    return str(value if value is not None else 0)


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
        "custom_tags",
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
            "partner_contacts",
            "partner_contacts__user",
            Prefetch(
                "renewal_successors",
                queryset=draft_successors,
                to_attr="_draft_renewal_successors",
            ),
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

    @action(detail=True, methods=["get", "post"], url_path="comments")
    def comments(self, request, pk=None):
        """Staff thread on an exchange agreement, including private notes."""
        agreement = self.get_object()
        if request.method == "GET":
            qs = (
                AgreementComment.objects.filter(agreement=agreement)
                .select_related("author")
                .order_by("created_at", "id")
            )
            return Response(AgreementCommentSerializer(qs, many=True).data)
        text = (request.data.get("text") or "").strip()
        if not text:
            return Response(
                {"text": ["This field may not be blank."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        raw_private = request.data.get("is_private", False)
        if isinstance(raw_private, str):
            is_private = raw_private.strip().lower() in ("1", "true", "yes", "on")
        else:
            is_private = bool(raw_private)
        comment = AgreementComment.objects.create(
            agreement=agreement,
            author=request.user,
            text=text,
            is_private=is_private,
        )
        return Response(
            AgreementCommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )


class EligibilityRuleSetViewSet(viewsets.ModelViewSet):
    """Staff CRUD API for persisted eligibility rule sets."""

    queryset = EligibilityRuleSet.objects.all()
    serializer_class = EligibilityRuleSetSerializer
    permission_classes = [IsCoordinatorOrAdmin]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_fields = ["is_active", "schema_version"]
    ordering_fields = [
        "name",
        "schema_version",
        "created_at",
        "updated_at",
        "is_active",
    ]


def _program_list_cache_key(*args, **kwargs):
    """Stable list cache key (path + user + generation) so mutations bust entries."""
    request = args[1]
    user_key = str(request.user.pk) if request.user.is_authenticated else "anon"
    digest = hashlib.sha256(request.get_full_path().encode()).hexdigest()[:32]
    gen = _program_cache_generation()
    return CacheManager.get_cache_key(
        "api_response", f"ProgramViewSet.list:{gen}:{user_key}:{digest}"
    )


def _program_retrieve_cache_key(*args, **kwargs):
    request = args[1]
    user_key = str(request.user.pk) if request.user.is_authenticated else "anon"
    pk = kwargs.get("pk", "")
    gen = _program_cache_generation()
    return CacheManager.get_cache_key(
        "api_response", f"ProgramViewSet.retrieve:{gen}:{user_key}:{pk}"
    )


def _program_active_cache_key(*args, **kwargs):
    request = args[1]
    user_key = str(request.user.pk) if request.user.is_authenticated else "anon"
    digest = hashlib.sha256(request.get_full_path().encode()).hexdigest()[:32]
    gen = _program_cache_generation()
    return CacheManager.get_cache_key(
        "api_response", f"ProgramViewSet.active:{gen}:{user_key}:{digest}"
    )


def _invalidate_program_api_caches() -> None:
    """Bust view-level generation and glob-delete leftover middleware keys."""
    try:
        cache.incr(_PROGRAM_CACHE_GEN_KEY)
    except ValueError:
        cache.set(_PROGRAM_CACHE_GEN_KEY, 1, timeout=None)
    CacheManager.clear_pattern("api_resp:v1:api_middleware:/api/programs*")
    CacheManager.clear_pattern("api_resp:v1:ProgramViewSet*")


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
        return Program.objects.prefetch_related("coordinators").annotate(
            _seat_holding_count=Count("application", filter=seat_filter)
        )

    def perform_create(self, serializer):
        serializer.save()
        _invalidate_program_api_caches()

    def perform_update(self, serializer):
        serializer.save()
        _invalidate_program_api_caches()

    def perform_destroy(self, instance):
        instance.delete()
        _invalidate_program_api_caches()

    @cache_api_response(timeout=600, key_func=_program_list_cache_key)
    def list(self, request, *args, **kwargs):
        """List all programs with caching."""
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=600, key_func=_program_retrieve_cache_key)
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific program with caching."""
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    @cache_api_response(timeout=600, key_func=_program_active_cache_key)
    def active(self, request):
        """Get only active programs with caching."""
        active_programs = self.filter_queryset(
            self.get_queryset().filter(is_active=True)
        )
        serializer = self.get_serializer(active_programs, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="List or create host institutions for a mobility scheme",
        responses={200: HostInstitutionSerializer(many=True)},
    )
    @action(detail=True, methods=["get", "post"], url_path="host-institutions")
    def host_institutions(self, request, pk=None):
        """Host universities under this program (mobility scheme)."""
        program = self.get_object()
        if request.method == "POST":
            payload = request.data.copy()
            payload["program"] = str(program.id)
            serializer = HostInstitutionSerializer(
                data=payload, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(program=program)
            _invalidate_program_api_caches()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        qs = HostInstitution.objects.filter(program=program).select_related(
            "grade_scale"
        )
        if not (
            request.user.is_staff
            or (hasattr(request.user, "is_admin") and request.user.is_admin)
        ):
            qs = qs.filter(is_active=True)
        qs = qs.order_by("name")
        return Response(HostInstitutionSerializer(qs, many=True).data)

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
            min_semester=original_program.min_semester,
            min_credits_approved_percent=original_program.min_credits_approved_percent,
            required_language=original_program.required_language,
            min_language_level=original_program.min_language_level,
            min_age=original_program.min_age,
            max_age=original_program.max_age,
            auto_reject_ineligible=original_program.auto_reject_ineligible,
            recurring=original_program.recurring,
            application_form=original_program.application_form,
            workflow_version=original_program.workflow_version,
            eligibility_ruleset=original_program.eligibility_ruleset,
            enrollment_capacity=original_program.enrollment_capacity,
            waitlist_when_full=original_program.waitlist_when_full,
        )
        cloned_program.coordinators.set(original_program.coordinators.all())

        _invalidate_program_api_caches()

        serializer = self.get_serializer(cloned_program)
        return Response(
            {"status": "Program cloned successfully", "program": serializer.data},
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Check eligibility for this program",
        description=(
            "Evaluates code-defined rules for the **authenticated user** (profile, window, etc.). "
            "Optional query ``application`` (UUID): must be owned by the caller and belong to this "
            "program; when set, **required_documents** and **dynamic_form** rules run when configured. "
            "Optional ``use_ruleset=true`` when the program has a linked **EligibilityRuleSet**: applies "
            "``rules_json.program_overrides`` on top of program fields for this check only. "
            "Successful rule outcome uses HTTP 200 with ``eligible: true|false``; "
            "``schema_version`` increments when rule set or shape changes."
        ),
        parameters=[
            OpenApiParameter(
                name="application",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "Application id for per-application rules (documents, dynamic form). "
                    "Must match this program and the current user."
                ),
            ),
            OpenApiParameter(
                name="use_ruleset",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "When true and the program has an active linked eligibility ruleset, evaluate using "
                    "ruleset scalar overrides (``rules_json.program_overrides``)."
                ),
            ),
        ],
        responses={
            200: ProgramCheckEligibilityResponseSerializer,
            400: OpenApiResponse(
                description="Invalid `application` id or application not for this program (`detail`).",
            ),
            403: OpenApiResponse(
                description="`application` belongs to another user (`detail`).",
            ),
            404: OpenApiResponse(
                description="`application` not found (`detail`).",
            ),
        },
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

        Optional query: ``application=<uuid>`` — when the row belongs to the current
        student and matches this program, evaluates **required_documents** and
        **dynamic_form** (when configured) against that application.
        """
        program = self.get_object()
        ruleset_snapshot = None
        rs = getattr(program, "eligibility_ruleset", None)
        if rs is not None and getattr(rs, "is_active", True):
            ruleset_snapshot = {
                "id": rs.id,
                "name": rs.name,
                "schema_version": rs.schema_version,
            }
        use_ruleset_raw = request.query_params.get("use_ruleset")
        use_ruleset = (
            bool(ruleset_snapshot)
            and use_ruleset_raw is not None
            and str(use_ruleset_raw).strip().lower() in ("1", "true", "yes", "on")
        )
        eval_program = (
            ProgramEligibilityProxy(program, parse_ruleset_overrides(rs))
            if use_ruleset and rs is not None
            else program
        )

        application_obj = None
        application_context = None
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

            # When an application is provided, return step-level context to support
            # multi-step document gates and UX parity with the application detail layout.
            try:
                from documents.services import DocumentService

                full_app = (
                    Application.objects.select_related("program", "student")
                    .only("id", "program_id", "student_id", "dynamic_form_current_step")
                    .get(pk=application_obj.pk)
                )
                checklist = DocumentService.build_application_document_checklist(
                    full_app
                )
                current_step_documents = None
                ft = getattr(program, "application_form", None)
                if ft and ft.is_multi_step():
                    current_key = full_app.dynamic_form_current_step
                    eff_ids = []
                    if current_key:
                        for s in ft.get_multi_step_layout():
                            if str(s.get("key")) == str(current_key):
                                eff_ids = DocumentService.intersect_program_required_document_type_ids(
                                    program, s.get("required_document_type_ids") or []
                                )
                                break
                    if eff_ids:
                        sub_items = [
                            it
                            for it in (checklist.get("items") or [])
                            if it.get("document_type_id") in eff_ids
                        ]
                        current_step_documents = {
                            "complete": all(
                                it.get("status") == "approved" for it in sub_items
                            ),
                            "items": sub_items,
                        }
                    else:
                        current_step_documents = {"complete": True, "items": []}
                application_context = {
                    "application_id": str(full_app.id),
                    "dynamic_form_current_step": full_app.dynamic_form_current_step,
                    "document_checklist": checklist,
                    "current_step_documents": current_step_documents,
                }
            except Exception:
                application_context = None

        ev = evaluate_eligibility(
            request.user, eval_program, application=application_obj
        )
        program_snapshot = {
            "name": program.name,
            "min_gpa": program.min_gpa,
            "min_semester": program.min_semester,
            "min_credits_approved_percent": (
                float(program.min_credits_approved_percent)
                if program.min_credits_approved_percent is not None
                else None
            ),
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
                    "schema_version": ELIGIBILITY_SCHEMA_VERSION,
                    **({"ruleset": ruleset_snapshot} if ruleset_snapshot else {}),
                    **({"using_ruleset": True} if use_ruleset else {}),
                    **(
                        {"application_context": application_context}
                        if application_context
                        else {}
                    ),
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
                "schema_version": ELIGIBILITY_SCHEMA_VERSION,
                **({"ruleset": ruleset_snapshot} if ruleset_snapshot else {}),
                **({"using_ruleset": True} if use_ruleset else {}),
                **(
                    {"application_context": application_context}
                    if application_context
                    else {}
                ),
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["get", "put"],
        url_path="nominations",
        permission_classes=[IsCoordinatorOrAdmin],
    )
    def nominations(self, request, pk=None):
        from exchange.nomination_matching import (
            program_nomination_payload,
            set_nomination_ranks,
        )

        program = self.get_object()
        if request.method == "GET":
            return Response(program_nomination_payload(program))
        items = request.data.get("ranks") or request.data.get("items") or []
        if not isinstance(items, list):
            return Response(
                {"ranks": ["Expected a list of {id, rank} objects."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            payload = set_nomination_ranks(program, items)
        except (TypeError, ValueError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(payload)

    @action(
        detail=True,
        methods=["post"],
        url_path="nominations/match",
        permission_classes=[IsCoordinatorOrAdmin],
    )
    def nominations_match(self, request, pk=None):
        from exchange.nomination_matching import match_nominations

        program = self.get_object()
        return Response(match_nominations(program, request.user))


def _application_list_cache_key(*args, **kwargs):
    """Scope cached list per user, path, and generation (mutations bump gen)."""
    request = args[1]
    user_key = str(request.user.pk) if request.user.is_authenticated else "anon"
    digest = hashlib.sha256(request.get_full_path().encode()).hexdigest()[:32]
    gen = application_api_cache_generation()
    return CacheManager.get_cache_key(
        "api_response", f"ApplicationViewSet.list:{gen}:{user_key}:{digest}"
    )


def _application_retrieve_cache_key(*args, **kwargs):
    """Scope cached detail per user, application id, and generation."""
    request = args[1]
    user_key = str(request.user.pk) if request.user.is_authenticated else "anon"
    pk = kwargs.get("pk", "")
    gen = application_api_cache_generation()
    return CacheManager.get_cache_key(
        "api_response", f"ApplicationViewSet.retrieve:{gen}:{user_key}:{pk}"
    )


def _comment_list_cache_key(*args, **kwargs):
    """Scope cached comment lists per user, path, and application generation."""
    request = args[1]
    user_key = str(request.user.pk) if request.user.is_authenticated else "anon"
    digest = hashlib.sha256(request.get_full_path().encode()).hexdigest()[:32]
    gen = application_api_cache_generation()
    return CacheManager.get_cache_key(
        "api_response", f"CommentViewSet.list:{gen}:{user_key}:{digest}"
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
    filterset_class = ApplicationFilter  # Use advanced filter
    search_fields = [
        "program__name",
        "student__username",
        "student__email",
        "student__first_name",
        "student__last_name",
        "student__middle_name",
        "student__mothers_last_name",
        "status__name",
    ]
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
            "program",  # ForeignKey - use select_related
            "student",  # ForeignKey
            "assigned_coordinator",
            "status",  # ForeignKey
            "host_institution",
            "host_institution__grade_scale",
            "host_school",
            "host_academic_program",
        ).prefetch_related(
            "program__coordinators",
            "program__required_document_types",
            "student__roles",  # ManyToMany through student
            "comments",
            "comments__author",
            "comments__author__roles",
            "timeline_events",  # Reverse FK: events for this application
            "timeline_events__created_by",
            "document_set",  # Reverse ForeignKey (documents)
            "document_set__type",  # Document types
            "document_set__uploaded_by",  # Who uploaded them
            "scholarship_award",
            "scholarship_award__disbursements",
            "scholarship_award__decided_by",
        )

        # Filter based on role
        if user.has_role("coordinator") or user.has_role("admin"):
            return base_qs
        else:
            return base_qs.filter(student=user)

    def perform_create(self, serializer):
        """Set the student after enforcing apply-readiness (catalogs + eligibility)."""
        from accounts.models import Profile

        try:
            profile = self.request.user.profile
        except Profile.DoesNotExist:
            profile = None
        if not profile or not profile.is_ready_to_apply:
            raise ValidationError(
                {
                    "detail": (
                        "Complete your personal, academic, and eligibility profile "
                        "(GPA, grade scale, language, credits, and semester) before "
                        "starting an application."
                    ),
                    "code": "profile_incomplete",
                }
            )
        serializer.save(student=self.request.user)
        invalidate_application_api_responses(serializer.instance)

    def perform_update(self, serializer):
        serializer.save()
        invalidate_application_api_responses(serializer.instance)

    def perform_destroy(self, instance):
        invalidate_application_api_responses(instance)
        instance.delete()

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
            return Response(
                {"error": "Program not found."}, status=status.HTTP_404_NOT_FOUND
            )

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

    @action(detail=False, methods=["get"], url_path="scholarship-awards-export")
    def scholarship_awards_export(self, request):
        """Export scholarship awards for a program cohort (CSV, staff)."""
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
            return Response(
                {"error": "Program not found."}, status=status.HTTP_404_NOT_FOUND
            )
        qs = (
            Application.objects.filter(program_id=program_id)
            .select_related(
                "program",
                "student",
                "scholarship_award",
                "scholarship_award__decided_by",
            )
            .order_by("created_at")
        )
        from exchange.scholarship_awards import awards_export_response

        return awards_export_response(program_id, qs, program_name=program.name)

    @action(
        detail=True,
        methods=["get", "put", "patch"],
        url_path="scholarship-award",
    )
    def scholarship_award(self, request, pk=None):
        """Read or upsert the scholarship award on this application."""
        application = self.get_object()
        from exchange.scholarship_awards import serialize_award, upsert_award

        if request.method == "GET":
            award = getattr(application, "scholarship_award", None)
            if not award:
                return Response({"scholarship_award": None})
            return Response(serialize_award(award))
        user = request.user
        if not user.has_any_role(["coordinator", "admin"]):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        try:
            award = upsert_award(
                application,
                user,
                status_value=request.data.get("status"),
                amount=request.data.get("amount", None)
                if "amount" in request.data
                else None,
                currency=request.data.get("currency"),
                notes=request.data.get("notes"),
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serialize_award(award))

    @action(
        detail=True,
        methods=["post"],
        url_path="scholarship-award/transition",
    )
    def scholarship_award_transition(self, request, pk=None):
        application = self.get_object()
        user = request.user
        if not user.has_any_role(["coordinator", "admin"]):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        award = getattr(application, "scholarship_award", None)
        if not award:
            return Response(
                {"error": "No scholarship award on this application."},
                status=status.HTTP_404_NOT_FOUND,
            )
        new_status = request.data.get("status")
        if not new_status:
            return Response(
                {"error": "status is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        from exchange.scholarship_awards import serialize_award, transition_award

        try:
            award = transition_award(award, user, new_status)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serialize_award(award))

    @action(
        detail=True,
        methods=["post"],
        url_path="scholarship-award/disbursements",
    )
    def scholarship_award_disbursement(self, request, pk=None):
        application = self.get_object()
        user = request.user
        if not user.has_any_role(["coordinator", "admin"]):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        award = getattr(application, "scholarship_award", None)
        if not award:
            return Response(
                {"error": "No scholarship award on this application."},
                status=status.HTTP_404_NOT_FOUND,
            )
        from exchange.scholarship_awards import serialize_award, upsert_disbursement

        try:
            upsert_disbursement(award, request.data, actor=user)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        award.refresh_from_db()
        return Response(serialize_award(award), status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        """Submit an application."""
        application = self.get_object()
        try:
            ApplicationService.submit_application(application, request.user)
            self._invalidate_application_cache(application)
            return Response({"status": "Application submitted successfully"})
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["get"],
        url_path="solicitud-participacion",
    )
    def solicitud_participacion(self, request, pk=None):
        """
        Download system-generated Solicitud de Participación PDF
        (profile + application + destination when host FKs exist).
        """
        from django.http import HttpResponse

        from documents.pdf_generation import render_solicitud_participacion_pdf

        application = self.get_object()
        pdf_bytes = render_solicitud_participacion_pdf(application)
        filename = f"solicitud_participacion_{application.id}.pdf"
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    @action(detail=True, methods=["get"], url_path="workflow")
    def workflow_snapshot(self, request, pk=None):
        """Return workflow instance snapshot and available actions (admin-configurable workflow)."""
        application = self.get_object()
        if not getattr(application.program, "workflow_version_id", None):
            return Response(
                {"detail": "No workflow configured for this program."},
                status=status.HTTP_404_NOT_FOUND,
            )
        from workflows.runtime import WorkflowRuntimeService
        from workflows.serializers import WorkflowInstanceSerializer

        snap = WorkflowRuntimeService.get_snapshot(application, user=request.user)
        return Response(
            {
                "instance": WorkflowInstanceSerializer(snap.instance).data,
                "available_actions": snap.available_actions,
            }
        )

    @action(detail=True, methods=["post"], url_path="workflow/action")
    def workflow_action(self, request, pk=None):
        """Trigger a workflow action (completes a ready manual task by id/spec_id/name)."""
        application = self.get_object()
        if not getattr(application.program, "workflow_version_id", None):
            return Response(
                {"detail": "No workflow configured for this program."},
                status=status.HTTP_404_NOT_FOUND,
            )
        action_name = request.data.get("action")
        payload = (
            request.data.get("payload") if isinstance(request.data, dict) else None
        )
        user = request.user

        # Minimal role guard in MVP: students can only submit/cancel-like actions.
        if hasattr(user, "has_role") and user.has_role("student"):
            allowed = {"submitted", "cancelled", "withdrawn"}
            if str(action_name or "") not in allowed:
                return Response(
                    {"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN
                )

        from workflows.runtime import WorkflowRuntimeService
        from workflows.serializers import WorkflowInstanceSerializer

        try:
            snap = WorkflowRuntimeService.trigger_action(
                application, action=str(action_name or ""), user=user, payload=payload
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        self._invalidate_application_cache(application)
        return Response(
            {
                "instance": WorkflowInstanceSerializer(snap.instance).data,
                "available_actions": snap.available_actions,
            }
        )

    @action(detail=True, methods=["post"])
    def withdraw(self, request, pk=None):
        """Withdraw an application."""
        application = self.get_object()
        try:
            ApplicationService.withdraw_application(application, request.user)
            self._invalidate_application_cache(application)
            return Response({"status": "Application withdrawn successfully"})
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Download Carta de Homologación PDF",
        responses={200: OpenApiResponse(description="PDF file")},
    )
    @action(detail=True, methods=["get"], url_path="carta-homologacion")
    def carta_homologacion(self, request, pk=None):
        """
        Generate and download Carta de Homologación from subject selections.

        Empty selections still return a PDF with an explanatory notice.
        When DocumentType slug ``carta_homologacion`` exists, attach a draft
        Document for the student's checklist (download → sign → re-upload).
        """
        application = self.get_object()
        user = request.user
        is_staff = hasattr(user, "has_any_role") and user.has_any_role(
            ["coordinator", "admin"]
        )
        if not is_staff and application.student_id != user.pk:
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        pdf_bytes = persist_carta_homologacion(application, user)
        filename = f"carta_homologacion_{application.id}.pdf"
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        selection_count = application.subject_selections.count()
        response["X-Subject-Selection-Count"] = str(selection_count)
        if selection_count == 0:
            response["X-Homologacion-Empty"] = "1"
        return response

    @extend_schema(
        summary="List catalog subjects visible for this application's destination",
        responses={200: HostSubjectSerializer(many=True)},
    )
    @action(detail=True, methods=["get"], url_path="available-subjects")
    def available_subjects(self, request, pk=None):
        application = self.get_object()
        user = request.user
        is_staff = hasattr(user, "has_any_role") and user.has_any_role(
            ["coordinator", "admin"]
        )
        if not is_staff and application.student_id != user.pk:
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        qs = visible_host_subjects_queryset(
            institution_id=application.host_institution_id,
            school_id=application.host_school_id,
            academic_program_id=application.host_academic_program_id,
            include_inactive=False,
        )
        return Response(HostSubjectSerializer(qs, many=True).data)

    @extend_schema(summary="Student proposes host subject grades for confirmation")
    @action(detail=True, methods=["post"], url_path="propose-subject-grades")
    def propose_subject_grades_action(self, request, pk=None):
        application = self.get_object()
        user = request.user
        is_staff = hasattr(user, "has_any_role") and user.has_any_role(
            ["coordinator", "admin"]
        )
        if not is_staff and application.student_id != user.pk:
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        try:
            updated = propose_subject_grades(application, user)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        self._invalidate_application_cache(application)
        return Response({"updated": updated, "status": "proposed"})

    @extend_schema(summary="Coordinator confirms host grades and locks translations")
    @action(detail=True, methods=["post"], url_path="confirm-subject-grades")
    def confirm_subject_grades_action(self, request, pk=None):
        application = self.get_object()
        user = request.user
        if not (
            hasattr(user, "has_any_role")
            and user.has_any_role(["coordinator", "admin"])
        ):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        notes = ""
        if isinstance(request.data, dict):
            notes = (
                request.data.get("notes")
                or request.data.get("confirmation_notes")
                or ""
            )
        try:
            updated = confirm_subject_grades(application, user, notes=notes)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        self._invalidate_application_cache(application)
        return Response({"updated": updated, "status": "confirmed"})

    @extend_schema(summary="Coordinator rejects host grades and reopens student edits")
    @action(detail=True, methods=["post"], url_path="reject-subject-grades")
    def reject_subject_grades_action(self, request, pk=None):
        application = self.get_object()
        user = request.user
        if not (
            hasattr(user, "has_any_role")
            and user.has_any_role(["coordinator", "admin"])
        ):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        notes = ""
        if isinstance(request.data, dict):
            notes = (
                request.data.get("notes")
                or request.data.get("confirmation_notes")
                or ""
            )
        try:
            updated = reject_subject_grades(application, user, notes=notes)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        self._invalidate_application_cache(application)
        return Response({"updated": updated, "status": "rejected"})

    @extend_schema(
        summary="List historic subject-plan snapshots (max 3)",
        responses={200: ApplicationSubjectPlanVersionSerializer(many=True)},
    )
    @action(detail=True, methods=["get"], url_path="subject-plan-versions")
    def subject_plan_versions(self, request, pk=None):
        """Read-only historic study plans for the owning student or staff."""
        user = request.user
        is_staff = hasattr(user, "has_any_role") and user.has_any_role(
            ["coordinator", "admin"]
        )
        try:
            application = Application.objects.get(pk=pk)
        except (Application.DoesNotExist, ValueError, TypeError):
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        if not is_staff and application.student_id != user.pk:
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        versions = application.subject_plan_versions.select_related(
            "created_by"
        ).order_by("-version_number")
        return Response(
            ApplicationSubjectPlanVersionSerializer(versions, many=True).data
        )

    def _invalidate_application_cache(self, application):
        """Drop retrieve/list/comment API caches after an application mutation."""
        invalidate_application_api_responses(application)


def _user_is_catalog_admin(user) -> bool:
    return bool(
        user
        and (
            user.is_staff
            or (hasattr(user, "is_admin") and user.is_admin)
        )
    )


def _active_or_all(qs, request, *, admin_all=True):
    if admin_all and _user_is_catalog_admin(request.user):
        return qs
    return qs.filter(is_active=True)


class HostInstitutionViewSet(viewsets.ModelViewSet):
    """Host institutions; nested schools/subjects. Admin write, authenticated read."""

    serializer_class = HostInstitutionSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["program", "is_active"]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_queryset(self):
        qs = HostInstitution.objects.select_related("program", "grade_scale")
        if _user_is_catalog_admin(self.request.user):
            return qs
        return qs.filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save()
        _invalidate_program_api_caches()

    def perform_update(self, serializer):
        serializer.save()
        _invalidate_program_api_caches()

    def perform_destroy(self, instance):
        instance.delete()
        _invalidate_program_api_caches()

    @extend_schema(
        summary="List or create schools for a host institution",
        responses={200: HostSchoolSerializer(many=True)},
    )
    @action(detail=True, methods=["get", "post"], url_path="schools")
    def schools(self, request, pk=None):
        institution = self.get_object()
        if request.method == "POST":
            payload = request.data.copy()
            payload["institution"] = str(institution.id)
            serializer = HostSchoolSerializer(
                data=payload, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(institution=institution)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        qs = _active_or_all(
            HostSchool.objects.filter(institution=institution), request
        ).order_by("name")
        return Response(HostSchoolSerializer(qs, many=True).data)

    @extend_schema(
        summary="List or create subjects for a host institution",
        responses={200: HostSubjectSerializer(many=True)},
    )
    @action(detail=True, methods=["get", "post"], url_path="subjects")
    def subjects(self, request, pk=None):
        institution = self.get_object()
        if request.method == "POST":
            payload = request.data.copy()
            payload["institution"] = str(institution.id)
            serializer = HostSubjectSerializer(
                data=payload, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(institution=institution)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        school_id = request.query_params.get("school") or None
        academic_id = request.query_params.get("academic_program") or None
        scope = request.query_params.get("scope") or ""
        include_inactive = _user_is_catalog_admin(request.user)
        if scope == "all" or (
            include_inactive and not school_id and not academic_id
        ):
            qs = HostSubject.objects.filter(institution=institution)
            if not include_inactive:
                qs = qs.filter(is_active=True)
            qs = qs.order_by("name", "code")
        else:
            qs = visible_host_subjects_queryset(
                institution_id=institution.id,
                school_id=school_id,
                academic_program_id=academic_id,
                include_inactive=include_inactive,
            )
        return Response(HostSubjectSerializer(qs, many=True).data)


class HostSchoolViewSet(viewsets.ModelViewSet):
    """Host schools; nested academic programs and school-level subjects."""

    serializer_class = HostSchoolSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["institution", "is_active"]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_queryset(self):
        qs = HostSchool.objects.select_related("institution")
        if _user_is_catalog_admin(self.request.user):
            return qs
        return qs.filter(is_active=True)

    @extend_schema(
        summary="List or create academic programs for a host school",
        responses={200: HostAcademicProgramSerializer(many=True)},
    )
    @action(detail=True, methods=["get", "post"], url_path="academic-programs")
    def academic_programs(self, request, pk=None):
        school = self.get_object()
        if request.method == "POST":
            payload = request.data.copy()
            payload["school"] = str(school.id)
            serializer = HostAcademicProgramSerializer(
                data=payload, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(school=school)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        qs = _active_or_all(
            HostAcademicProgram.objects.filter(school=school), request
        ).order_by("name")
        return Response(HostAcademicProgramSerializer(qs, many=True).data)

    @extend_schema(
        summary="List or create subjects for a host school",
        responses={200: HostSubjectSerializer(many=True)},
    )
    @action(detail=True, methods=["get", "post"], url_path="subjects")
    def subjects(self, request, pk=None):
        school = self.get_object()
        if request.method == "POST":
            payload = request.data.copy()
            payload["institution"] = str(school.institution_id)
            payload["school"] = str(school.id)
            serializer = HostSubjectSerializer(
                data=payload, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(institution=school.institution, school=school)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        qs = HostSubject.objects.filter(school=school, academic_program__isnull=True)
        if not _user_is_catalog_admin(request.user):
            qs = qs.filter(is_active=True)
        return Response(
            HostSubjectSerializer(qs.order_by("name", "code"), many=True).data
        )


class HostAcademicProgramViewSet(viewsets.ModelViewSet):
    """Host academic programs; nested subjects for optional selection."""

    serializer_class = HostAcademicProgramSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["school", "is_active"]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_queryset(self):
        qs = HostAcademicProgram.objects.select_related(
            "school", "school__institution"
        )
        if _user_is_catalog_admin(self.request.user):
            return qs
        return qs.filter(is_active=True)

    @extend_schema(
        summary="List or create subjects for a host academic program",
        responses={200: HostSubjectSerializer(many=True)},
    )
    @action(detail=True, methods=["get", "post"], url_path="subjects")
    def subjects(self, request, pk=None):
        academic_program = self.get_object()
        if request.method == "POST":
            payload = request.data.copy()
            payload["institution"] = str(academic_program.school.institution_id)
            payload["school"] = str(academic_program.school_id)
            payload["academic_program"] = str(academic_program.id)
            serializer = HostSubjectSerializer(
                data=payload, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(
                institution=academic_program.school.institution,
                school=academic_program.school,
                academic_program=academic_program,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        qs = HostSubject.objects.filter(academic_program=academic_program)
        if not _user_is_catalog_admin(request.user):
            qs = qs.filter(is_active=True)
        return Response(
            HostSubjectSerializer(qs.order_by("name", "code"), many=True).data
        )


class HostSubjectViewSet(viewsets.ModelViewSet):
    """Staff CRUD for host subjects; authenticated users may list/retrieve active rows."""

    serializer_class = HostSubjectSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["institution", "school", "academic_program", "is_active"]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_queryset(self):
        qs = HostSubject.objects.select_related(
            "institution", "school", "academic_program"
        )
        if _user_is_catalog_admin(self.request.user):
            return qs
        return qs.filter(is_active=True)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.application_selections.exists():
            instance.is_active = False
            instance.save(update_fields=["is_active", "updated_at"])
            return Response(
                HostSubjectSerializer(instance).data, status=status.HTTP_200_OK
            )
        return super().destroy(request, *args, **kwargs)


class ApplicationSubjectSelectionViewSet(viewsets.ModelViewSet):
    """CRUD for optional subject selections on a student's own application."""

    serializer_class = ApplicationSubjectSelectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["application"]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        qs = ApplicationSubjectSelection.objects.select_related(
            "application",
            "application__status",
            "host_subject",
            "host_subject__academic_program",
            "host_subject__institution",
            "proposed_host_grade",
            "confirmed_host_grade",
            "home_grade",
        )
        if user.has_any_role(["coordinator", "admin"]):
            return qs
        return qs.filter(application__student=user)

    def perform_create(self, serializer):
        application = serializer.validated_data["application"]
        user = self.request.user
        if not user.has_any_role(["coordinator", "admin"]):
            if application.student_id != user.pk:
                raise ValidationError(
                    {
                        "application": "You can only add subjects to your own application."
                    }
                )
        with transaction.atomic():
            snapshot_subject_plan(
                application,
                user,
                trigger=ApplicationSubjectPlanVersion.Trigger.MAPPING_CHANGED,
            )
            serializer.save()

    def perform_update(self, serializer):
        instance = serializer.instance
        mapping_changed = subject_plan_mapping_changed(
            instance, serializer.validated_data
        )
        with transaction.atomic():
            if mapping_changed:
                snapshot_subject_plan(
                    instance.application,
                    self.request.user,
                    trigger=ApplicationSubjectPlanVersion.Trigger.MAPPING_CHANGED,
                )
            serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        is_staff = user.has_any_role(["coordinator", "admin"])
        locked = instance.grade_status in (
            ApplicationSubjectSelection.GradeStatus.PROPOSED,
            ApplicationSubjectSelection.GradeStatus.CONFIRMED,
        )
        if not is_staff and locked:
            raise ValidationError(
                {
                    "detail": (
                        "This subject mapping is locked until a coordinator "
                        "rejects the proposed grades."
                    )
                }
            )
        if not is_staff:
            from exchange.serializers import _application_subject_grades_locked

            if _application_subject_grades_locked(instance.application):
                raise ValidationError(
                    {
                        "detail": (
                            "Subject mappings cannot be changed after grades "
                            "have been proposed or confirmed."
                        )
                    }
                )
        with transaction.atomic():
            snapshot_subject_plan(
                instance.application,
                user,
                trigger=ApplicationSubjectPlanVersion.Trigger.MAPPING_CHANGED,
            )
            instance.delete()


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
            "application",  # ForeignKey
            "application__program",  # Through application
            "application__student",  # Through application
            "application__status",  # Through application
            "author",  # ForeignKey
        ).prefetch_related(
            "author__roles"  # Author's roles
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
        invalidate_application_api_responses(serializer.instance.application)

    def perform_update(self, serializer):
        serializer.save()
        invalidate_application_api_responses(serializer.instance.application)

    def perform_destroy(self, instance):
        application = instance.application
        instance.delete()
        invalidate_application_api_responses(application)

    @cache_api_response(timeout=300, key_func=_comment_list_cache_key)
    def list(self, request, *args, **kwargs):
        """List comments with caching."""
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Create a comment and notify subscribers."""
        response = super().create(request, *args, **kwargs)
        if response.status_code == 201:
            application_id = request.data.get("application") or response.data.get(
                "application"
            )
            if application_id:
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
            "application",  # ForeignKey
            "application__program",  # Through application
            "application__student",  # Through application
            "application__status",  # Through application
            "created_by",  # ForeignKey (nullable)
        ).prefetch_related(
            "created_by__roles"  # Creator's roles (if exists)
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
    filterset_fields = ["search_type", "is_default"]
    ordering_fields = ["created_at", "name"]

    def get_queryset(self):
        """Users can only see their own saved searches."""
        return SavedSearch.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Set user from request."""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def apply(self, request, pk=None):
        """
        Apply a saved search and return the filters.

        Returns the filter parameters that can be used to filter
        programs or applications.
        """
        saved_search = self.get_object()
        return Response(
            {
                "search_type": saved_search.search_type,
                "filters": saved_search.filters,
                "name": saved_search.name,
            }
        )

    @action(detail=True, methods=["post"])
    def set_default(self, request, pk=None):
        """Set this search as the default for its type."""
        saved_search = self.get_object()
        saved_search.is_default = True
        saved_search.save()
        return Response({"status": "default set"})


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
        event_type = request.query_params.get("type")
        start_param = request.query_params.get("start")
        end_param = request.query_params.get("end")
        events = build_calendar_event_dicts(
            request.user,
            start_param=start_param,
            end_param=end_param,
            event_type=event_type,
        )
        if event_type in (None, "", "all", "google"):
            from exchange.google_calendar import imported_event_dicts

            overlay = imported_event_dicts(
                request.user, start_param=start_param, end_param=end_param
            )
            if event_type == "google":
                events = overlay
            else:
                events = list(events) + overlay
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

    @action(detail=False, methods=["get"], url_path="google-status")
    def google_status(self, request):
        from exchange.google_calendar import connection_status

        return Response(connection_status(request.user))

    @action(detail=False, methods=["get"], url_path="google-authorize")
    def google_authorize(self, request):
        from exchange.google_calendar import build_authorization_url, is_configured

        if not is_configured():
            return Response(
                {
                    "configured": False,
                    "detail": "Google Calendar OAuth is not configured.",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        try:
            url = build_authorization_url(request, request.user)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"configured": True, "authorization_url": url})

    @action(
        detail=False,
        methods=["get"],
        url_path="google-callback",
        permission_classes=[permissions.AllowAny],
        authentication_classes=[],
    )
    def google_callback(self, request):
        from django.shortcuts import redirect

        from exchange.google_calendar import exchange_code, spa_settings_url

        error = request.query_params.get("error")
        if error:
            return redirect(spa_settings_url("google_calendar=error"))
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        if not code or not state:
            return redirect(spa_settings_url("google_calendar=error"))
        try:
            exchange_code(request, code, state)
        except Exception:
            return redirect(spa_settings_url("google_calendar=error"))
        return redirect(spa_settings_url("google_calendar=connected"))

    @action(detail=False, methods=["post"], url_path="google-disconnect")
    def google_disconnect(self, request):
        from exchange.google_calendar import connection_status, disconnect

        disconnect(request.user)
        return Response(connection_status(request.user))

    @action(detail=False, methods=["post"], url_path="google-sync")
    def google_sync(self, request):
        from exchange.google_calendar import connection_status, sync_user_events

        try:
            result = sync_user_events(request.user)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
        payload = connection_status(request.user)
        payload["sync"] = result
        return Response(payload)
