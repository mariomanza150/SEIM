import hashlib
import logging
import mimetypes
import os

from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch, Q
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from core.cache import (
    CacheManager,
    application_api_cache_generation,
    cache_api_response,
    invalidate_application_api_responses,
)
from core.permissions import IsAdminOrReadOnly, IsCoordinatorOrAdmin, IsOwnerOrAdmin

from .audit import audit_info, audit_warning
from .filters import DocumentFilter, ExchangeAgreementDocumentFilter
from .mailmerge import (
    MERGE_FIELD_CATALOG,
    docx_has_fillable_fields,
    is_docx_filename,
    merge_docx,
    merge_values_for_application,
    merge_values_for_student,
)
from .models import (
    Document,
    DocumentComment,
    DocumentResubmissionRequest,
    DocumentType,
    DocumentValidation,
    ExchangeAgreementDocument,
)
from .prefill_filters import (
    bulk_add_prefill_students,
    clear_prefill_active_filters,
    forget_prefill_exclusion,
    normalize_email_domain,
    parse_prefill_filter_params,
    prefill_filter_queryset,
    remember_prefill_exclusion,
    serialize_active_filters,
    set_prefill_active_filters,
)
from .serializers import (
    DocumentCommentSerializer,
    DocumentResubmissionRequestSerializer,
    DocumentSerializer,
    DocumentTypeListSerializer,
    DocumentTypeSerializer,
    DocumentValidationSerializer,
    ExchangeAgreementDocumentSerializer,
)
from .services import DocumentService

logger = logging.getLogger(__name__)
User = get_user_model()

# Create your views here.


class ExchangeAgreementDocumentViewSet(viewsets.ModelViewSet):
    """Staff repository files linked to exchange agreements (not application uploads)."""

    queryset = ExchangeAgreementDocument.objects.select_related(
        "agreement", "uploaded_by", "supersedes"
    ).all()
    serializer_class = ExchangeAgreementDocumentSerializer
    permission_classes = [IsCoordinatorOrAdmin]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ExchangeAgreementDocumentFilter
    search_fields = [
        "title",
        "notes",
        "agreement__title",
        "agreement__partner_institution_name",
    ]
    ordering_fields = ["created_at", "category"]


class DocumentTypeViewSet(viewsets.ModelViewSet):
    """Document type catalog: authenticated read; admin create/update/delete."""

    queryset = DocumentType.objects.all()
    serializer_class = DocumentTypeSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["submission_mode", "allows_multiple"]
    search_fields = ["name", "slug", "description"]
    ordering_fields = ["name", "id"]
    ordering = ["name"]
    lookup_field = "pk"

    def get_queryset(self):
        qs = (
            DocumentType.objects.all()
            .annotate(requirement_count=Count("program_requirements"))
            .prefetch_related("file_type_families")
        )
        if self.action == "retrieve":
            return qs.prefetch_related("program_requirements__program")
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return DocumentTypeListSerializer
        return DocumentTypeSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        if self.action == "list":
            ctx["include_program_requirements"] = False
        return ctx

    def perform_create(self, serializer):
        serializer.save()
        instance = serializer.instance
        audit_info(
            "document_type_create",
            actor=self.request.user,
            object_id=instance.pk,
            object_slug=instance.slug or "",
            submission_mode=instance.submission_mode,
        )

    def perform_update(self, serializer):
        serializer.save()
        instance = serializer.instance
        audit_info(
            "document_type_update",
            actor=self.request.user,
            object_id=instance.pk,
            object_slug=instance.slug or "",
            submission_mode=instance.submission_mode,
        )

    def perform_destroy(self, instance):
        object_id = instance.pk
        object_slug = instance.slug or ""
        instance.delete()
        audit_info(
            "document_type_delete",
            actor=self.request.user,
            object_id=object_id,
            object_slug=object_slug,
        )

    @action(detail=False, methods=["get"], url_path="merge-fields")
    def merge_fields(self, request):
        """Word MERGEFIELD names available for template prefilling."""
        return Response({"fields": MERGE_FIELD_CATALOG})

    @action(detail=False, methods=["get"], url_path="file-type-families")
    def file_type_families(self, request):
        """Umbrella file-type groups (Image, Word, PDF) and their extensions."""
        from .file_type_families import seed_file_type_families
        from .models import FileTypeFamily
        from .serializers import FileTypeFamilySerializer

        if not FileTypeFamily.objects.exists():
            families = seed_file_type_families()
        else:
            families = FileTypeFamily.objects.filter(is_active=True).order_by(
                "sort_order", "name"
            )
        return Response({"results": FileTypeFamilySerializer(families, many=True).data})

    @action(
        detail=True,
        methods=["post"],
        url_path="upload-template",
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_template(self, request, pk=None):
        """Attach or replace the downloadable template file (admin)."""
        doc_type = self.get_object()
        replacing = bool(doc_type.template_file)
        upload = request.FILES.get("template_file") or request.FILES.get("file")
        if not upload:
            audit_warning(
                "document_type_template_upload_rejected",
                actor=request.user,
                object_id=doc_type.pk,
                reason="missing_file",
            )
            return Response(
                {"template_file": ["A template file is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        name = (upload.name or "").lower()
        if not (
            name.endswith(".docx")
            or name.endswith(".pdf")
            or name.endswith(".doc")
            or name.endswith(".odt")
        ):
            audit_warning(
                "document_type_template_upload_rejected",
                actor=request.user,
                object_id=doc_type.pk,
                reason="invalid_extension",
                size=getattr(upload, "size", None),
            )
            return Response(
                {
                    "template_file": [
                        "Template must be a Word (.docx), PDF, or similar document."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        doc_type.template_file = upload
        doc_type.save(update_fields=["template_file"])
        audit_info(
            "document_type_template_replace"
            if replacing
            else "document_type_template_upload",
            actor=request.user,
            object_id=doc_type.pk,
            object_slug=doc_type.slug or "",
            size=getattr(upload, "size", None),
        )
        serializer = DocumentTypeSerializer(doc_type, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["delete"], url_path="template")
    def delete_template(self, request, pk=None):
        """Remove the attached template file (admin)."""
        doc_type = self.get_object()
        if doc_type.template_file:
            doc_type.template_file.delete(save=True)
            audit_info(
                "document_type_template_delete",
                actor=request.user,
                object_id=doc_type.pk,
                object_slug=doc_type.slug or "",
            )
        serializer = DocumentTypeSerializer(doc_type, context={"request": request})
        return Response(serializer.data)

    @staticmethod
    def _user_is_coordinator_or_admin(user) -> bool:
        return bool(
            getattr(user, "has_role", None)
            and (user.has_role("coordinator") or user.has_role("admin"))
        )

    @staticmethod
    def _serialize_prefill_student(user) -> dict:
        profile = getattr(user, "profile", None)
        full_name = (
            " ".join(
                part
                for part in (
                    user.first_name,
                    getattr(user, "middle_name", "") or "",
                    user.last_name,
                    getattr(user, "mothers_last_name", "") or "",
                )
                if part
            ).strip()
            or user.get_full_name()
            or user.username
        )
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": full_name,
            "matricula": getattr(profile, "matricula", "") or "",
        }

    @staticmethod
    def _student_search_queryset(search: str = ""):
        qs = (
            User.objects.filter(roles__name="student", is_active=True)
            .select_related("profile")
            .distinct()
            .order_by("last_name", "first_name", "username")
        )
        term = (search or "").strip()
        if not term:
            return qs
        return qs.filter(
            Q(email__icontains=term)
            | Q(username__icontains=term)
            | Q(first_name__icontains=term)
            | Q(last_name__icontains=term)
            | Q(middle_name__icontains=term)
            | Q(mothers_last_name__icontains=term)
            | Q(profile__matricula__icontains=term)
        )

    @staticmethod
    def _parse_bulk_identifiers(request) -> list[str]:
        identifiers: list[str] = []
        text = request.data.get("text")
        if text is None and "text" not in getattr(request, "FILES", {}):
            text = request.data.get("identifiers") or ""
        if hasattr(text, "read"):
            text = text.read().decode("utf-8", errors="ignore")
        if text:
            identifiers.extend(str(text).replace("\r\n", "\n").split("\n"))
        upload = request.FILES.get("file") or request.FILES.get("csv")
        if upload is not None:
            raw = upload.read()
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8", errors="ignore")
            identifiers.extend(str(raw).replace("\r\n", "\n").split("\n"))
        cleaned: list[str] = []
        seen: set[str] = set()
        for line in identifiers:
            token = line.strip().strip(",").strip()
            if not token or token.lower() in seen:
                continue
            seen.add(token.lower())
            cleaned.append(token)
        return cleaned

    def _resolve_student_by_identifier(self, token: str):
        """Match an existing student by email or matrícula (case-insensitive)."""
        lowered = token.lower()
        user = (
            User.objects.filter(roles__name="student", is_active=True)
            .filter(Q(email__iexact=token) | Q(email__iexact=lowered))
            .select_related("profile")
            .first()
        )
        if user is not None:
            return user
        return (
            User.objects.filter(roles__name="student", is_active=True)
            .filter(profile__matricula__iexact=token)
            .select_related("profile")
            .first()
        )

    @staticmethod
    def _normalize_email_domain(raw: str | None) -> str:
        return normalize_email_domain(raw)

    @staticmethod
    def _parse_prefill_filter_params(data) -> dict:
        return parse_prefill_filter_params(data)

    def _prefill_filter_queryset(self, filters: dict):
        return prefill_filter_queryset(filters)

    def _prefill_filter_summary(
        self, doc_type, filters: dict, *, sample_limit: int = 5
    ):
        matched_qs = prefill_filter_queryset(filters)
        matched = matched_qs.count()
        listed_ids = set(doc_type.prefill_students.values_list("id", flat=True))
        excluded_ids = set(
            doc_type.prefill_filter_exclusions.values_list("id", flat=True)
        )
        skip = listed_ids | excluded_ids
        new_qs = matched_qs.exclude(pk__in=skip) if skip else matched_qs
        new_count = new_qs.count()
        already_listed = matched - new_count
        samples = [
            self._serialize_prefill_student(user) for user in new_qs[:sample_limit]
        ]
        return {
            "filter": filters,
            "matched": matched,
            "new_count": new_count,
            "already_listed": already_listed,
            "samples": samples,
        }

    @staticmethod
    def _bulk_add_prefill_students(doc_type, student_ids) -> int:
        return bulk_add_prefill_students(doc_type, student_ids)

    def _invalid_domain_response(self, request, filters: dict):
        if filters["domain"] == "" and (
            "domain" in request.data or "email_domain" in request.data
        ):
            raw = request.data.get("domain") or request.data.get("email_domain")
            if str(raw or "").strip():
                return Response(
                    {"domain": ["Enter a valid email domain (e.g. example.edu)."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return None

    @action(detail=False, methods=["get"], url_path="my-prefill-templates")
    def my_prefill_templates(self, request):
        """Document types the current user may download prefilled (no application).

        Types without an attached template file are excluded so the student UI
        never offers a download that would 404.
        """
        qs = (
            DocumentType.objects.filter(prefill_students=request.user)
            .exclude(Q(template_file="") | Q(template_file__isnull=True))
            .order_by("name")
            .distinct()
        )
        results = [
            {
                "id": dt.id,
                "name": dt.name,
                "slug": dt.slug,
                "has_template": True,
                "template_filename": (
                    dt.template_file.name.rsplit("/", 1)[-1] if dt.template_file else ""
                ),
            }
            for dt in qs
        ]
        return Response({"results": results})

    @action(
        detail=True,
        methods=["get", "post"],
        url_path="prefill-students",
        permission_classes=[permissions.IsAuthenticated, IsCoordinatorOrAdmin],
    )
    def prefill_students(self, request, pk=None):
        """List or add students allowed to download a prefilled template."""
        doc_type = self.get_object()
        if request.method == "GET":
            search = request.query_params.get("search") or ""
            qs = doc_type.prefill_students.select_related("profile").order_by(
                "last_name", "first_name", "username"
            )
            if search.strip():
                qs = qs.filter(
                    Q(email__icontains=search)
                    | Q(username__icontains=search)
                    | Q(first_name__icontains=search)
                    | Q(last_name__icontains=search)
                    | Q(profile__matricula__icontains=search)
                )
            return Response(
                {"results": [self._serialize_prefill_student(user) for user in qs]}
            )

        user_id = request.data.get("user_id") or request.data.get("user")
        if user_id is None:
            return Response(
                {"user_id": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        student = get_object_or_404(User.objects.select_related("profile"), pk=user_id)
        if doc_type.prefill_students.filter(pk=student.pk).exists():
            forget_prefill_exclusion(doc_type, student)
            return Response(
                {
                    "detail": "Student is already listed.",
                    "student": self._serialize_prefill_student(student),
                },
                status=status.HTTP_200_OK,
            )
        doc_type.prefill_students.add(student)
        forget_prefill_exclusion(doc_type, student)
        audit_info(
            "document_type_prefill_add",
            actor=request.user,
            object_id=doc_type.pk,
            student_id=student.pk,
        )
        return Response(
            {"student": self._serialize_prefill_student(student)},
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["delete"],
        url_path=(
            r"prefill-students/"
            r"(?P<user_id>[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12})"
        ),
        permission_classes=[permissions.IsAuthenticated, IsCoordinatorOrAdmin],
    )
    def prefill_students_remove(self, request, pk=None, user_id=None):
        """Remove a student from the prefill allow-list."""
        doc_type = self.get_object()
        student = get_object_or_404(User, pk=user_id)
        doc_type.prefill_students.remove(student)
        remember_prefill_exclusion(doc_type, student)
        audit_info(
            "document_type_prefill_remove",
            actor=request.user,
            object_id=doc_type.pk,
            student_id=student.pk,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["get"],
        url_path="prefill-students/candidates",
        permission_classes=[permissions.IsAuthenticated, IsCoordinatorOrAdmin],
    )
    def prefill_students_candidates(self, request, pk=None):
        """Search students (name, matrícula, email) to add to the allow-list."""
        doc_type = self.get_object()
        search = (
            request.query_params.get("search") or request.query_params.get("q") or ""
        )
        listed_ids = set(doc_type.prefill_students.values_list("id", flat=True))
        qs = self._student_search_queryset(search)[:25]
        results = []
        for user in qs:
            row = self._serialize_prefill_student(user)
            row["already_listed"] = user.id in listed_ids
            results.append(row)
        return Response({"results": results})

    @action(
        detail=True,
        methods=["post"],
        url_path="prefill-students/bulk",
        permission_classes=[permissions.IsAuthenticated, IsCoordinatorOrAdmin],
        parser_classes=[JSONParser, MultiPartParser, FormParser],
    )
    def prefill_students_bulk(self, request, pk=None):
        """Bulk-add students by matrícula or email (one per line). Never creates users."""
        doc_type = self.get_object()
        identifiers = self._parse_bulk_identifiers(request)
        added = 0
        already_listed = 0
        not_found: list[str] = []
        for token in identifiers:
            student = self._resolve_student_by_identifier(token)
            if student is None:
                not_found.append(token)
                continue
            if doc_type.prefill_students.filter(pk=student.pk).exists():
                already_listed += 1
                forget_prefill_exclusion(doc_type, student)
                continue
            doc_type.prefill_students.add(student)
            forget_prefill_exclusion(doc_type, student)
            added += 1
        audit_info(
            "document_type_prefill_bulk",
            actor=request.user,
            object_id=doc_type.pk,
            added=added,
            already_listed=already_listed,
            not_found_count=len(not_found),
        )
        return Response(
            {
                "added": added,
                "already_listed": already_listed,
                "not_found": not_found,
            }
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="prefill-students/filter-options",
        permission_classes=[permissions.IsAuthenticated, IsCoordinatorOrAdmin],
    )
    def prefill_students_filter_options(self, request, pk=None):
        """Dropdown values for filter bulk-add (unidad, school, known email domains)."""
        from accounts.models import SchoolFaculty, Unidad

        self.get_object()
        unidades = list(
            Unidad.objects.filter(is_active=True)
            .order_by("ordering", "name")
            .values("id", "name")
        )
        schools = list(
            SchoolFaculty.objects.filter(is_active=True)
            .order_by("ordering", "name")
            .values("id", "name", "unidad_id")
        )
        for row in unidades:
            row["id"] = str(row["id"])
        for row in schools:
            row["id"] = str(row["id"])
            row["unidad_id"] = str(row["unidad_id"]) if row.get("unidad_id") else None

        domains: set[str] = set()
        emails = (
            User.objects.filter(roles__name="student", is_active=True)
            .exclude(email="")
            .values_list("email", flat=True)
            .distinct()
        )
        for email in emails.iterator(chunk_size=500):
            if "@" not in str(email):
                continue
            domains.add(normalize_email_domain(email))
        return Response(
            {
                "unidades": unidades,
                "schools": schools,
                "domains": sorted(d for d in domains if d),
            }
        )

    @action(
        detail=True,
        methods=["get", "put", "patch", "delete"],
        url_path="prefill-students/active-filters",
        permission_classes=[permissions.IsAuthenticated, IsCoordinatorOrAdmin],
    )
    def prefill_students_active_filters(self, request, pk=None):
        """View, set, or clear persisted active filters for auto-inclusion."""
        doc_type = self.get_object()
        if request.method == "GET":
            return Response(serialize_active_filters(doc_type))

        if request.method == "DELETE":
            clear_prefill_active_filters(doc_type)
            audit_info(
                "document_type_prefill_active_filters_clear",
                actor=request.user,
                object_id=doc_type.pk,
            )
            return Response(serialize_active_filters(doc_type))

        filters = self._parse_prefill_filter_params(request.data)
        invalid = self._invalid_domain_response(request, filters)
        if invalid is not None:
            return invalid
        result = set_prefill_active_filters(doc_type, filters, sync=True)
        audit_info(
            "document_type_prefill_active_filters_set",
            actor=request.user,
            object_id=doc_type.pk,
            filter=result["filter"],
            added=result["added"],
            matched=result["matched"],
        )
        payload = serialize_active_filters(doc_type)
        payload.update(
            {
                "matched": result["matched"],
                "added": result["added"],
                "already_listed": result["already_listed"],
            }
        )
        return Response(payload)

    @action(
        detail=True,
        methods=["post"],
        url_path="prefill-students/filter-preview",
        permission_classes=[permissions.IsAuthenticated, IsCoordinatorOrAdmin],
    )
    def prefill_students_filter_preview(self, request, pk=None):
        """Preview how many students a filter would add (same query as confirm)."""
        doc_type = self.get_object()
        filters = self._parse_prefill_filter_params(request.data)
        invalid = self._invalid_domain_response(request, filters)
        if invalid is not None:
            return invalid
        return Response(self._prefill_filter_summary(doc_type, filters))

    @action(
        detail=True,
        methods=["post"],
        url_path="prefill-students/filter-confirm",
        permission_classes=[permissions.IsAuthenticated, IsCoordinatorOrAdmin],
    )
    def prefill_students_filter_confirm(self, request, pk=None):
        """Confirm filter bulk-add and persist the filters as active filters."""
        doc_type = self.get_object()
        filters = self._parse_prefill_filter_params(request.data)
        invalid = self._invalid_domain_response(request, filters)
        if invalid is not None:
            return invalid
        result = set_prefill_active_filters(doc_type, filters, sync=True)
        logger.info(
            "document_template_prefill_bulk_add",
            extra={
                "action": "prefill_bulk_filter_add",
                "actor_id": request.user.pk,
                "document_type_id": doc_type.pk,
                "document_type_slug": doc_type.slug or "",
                "filter": result["filter"],
                "matched": result["matched"],
                "added": result["added"],
                "already_listed": result["already_listed"],
                "active_filters": True,
            },
        )
        return Response(
            {
                "filter": result["filter"],
                "matched": result["matched"],
                "added": result["added"],
                "already_listed": result["already_listed"],
                "active_filters": serialize_active_filters(doc_type),
            }
        )

    @action(detail=True, methods=["get"], url_path="download-template")
    def download_template(self, request, pk=None):
        """Download template; .docx files are prefilled when ?application= is set.

        Without ?application=, listed students (``prefill_students``) receive a
        copy filled from their profile. Coordinators/admins may preview a listed
        student's copy with ``?student=<id>``.

        Official blank CGRI Word forms (no MERGEFIELD / ``{{…}}`` placeholders)
        are served as exact sample bytes — mail-merge is skipped so the file
        stays identical to ``SAMPLES/``.
        """
        from cms.cgri_samples import (
            official_sample_path,
            official_template_download_name,
        )

        doc_type = self.get_object()
        raw = None
        if doc_type.template_file:
            try:
                handle = doc_type.template_file.open("rb")
                raw = handle.read()
                handle.close()
            except FileNotFoundError:
                raw = None

        if raw is None:
            sample_path = official_sample_path(doc_type.slug)
            if sample_path is None:
                return Response(
                    {"detail": "No template file available for this document type."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            raw = sample_path.read_bytes()

        filename = official_template_download_name(doc_type.slug) or (
            os.path.basename(doc_type.template_file.name)
            if doc_type.template_file
            else "template.docx"
        )
        application_id = request.query_params.get("application")
        student_id = request.query_params.get("student")
        if application_id and is_docx_filename(filename):
            from exchange.models import Application

            application = get_object_or_404(
                Application.objects.select_related(
                    "student",
                    "student__profile",
                    "student__profile__school",
                    "student__profile__unidad",
                    "student__profile__academic_level",
                    "student__profile__home_academic_program",
                    "student__profile__bank_institution",
                    "program",
                    "host_institution",
                    "host_school",
                    "host_academic_program",
                ),
                pk=application_id,
            )
            user = request.user
            is_staff = self._user_is_coordinator_or_admin(user)
            if not is_staff and application.student_id != user.id:
                raise PermissionDenied(
                    "You cannot download a prefilled template for this application."
                )
            if not DocumentService.can_download_template(application, doc_type, user):
                raise PermissionDenied(
                    "Template download is not available after this document "
                    "has been approved. Contact staff if a resubmission is needed."
                )
            if docx_has_fillable_fields(raw):
                values = merge_values_for_application(application)
                raw = merge_docx(raw, values)
            stem, ext = os.path.splitext(filename)
            filename = f"{stem}_{application.student.username}{ext}"
        elif (
            not application_id
            and is_docx_filename(filename)
            and docx_has_fillable_fields(raw)
        ):
            user = request.user
            is_staff = self._user_is_coordinator_or_admin(user)
            target_student = None
            if student_id:
                if not is_staff:
                    raise PermissionDenied(
                        "You cannot download a prefilled template for another student."
                    )
                target_student = get_object_or_404(
                    User.objects.select_related(
                        "profile",
                        "profile__school",
                        "profile__unidad",
                        "profile__academic_level",
                        "profile__home_academic_program",
                        "profile__bank_institution",
                    ),
                    pk=student_id,
                )
                if not doc_type.prefill_students.filter(pk=target_student.pk).exists():
                    raise Http404("Student is not listed for this template.")
                logger.info(
                    "document_template_prefill_preview",
                    extra={
                        "action": "prefill_template_preview",
                        "actor_id": user.pk,
                        "student_id": target_student.pk,
                        "document_type_id": doc_type.pk,
                        "document_type_slug": doc_type.slug or "",
                    },
                )
            elif doc_type.prefill_students.filter(pk=user.pk).exists():
                target_student = User.objects.select_related(
                    "profile",
                    "profile__school",
                    "profile__unidad",
                    "profile__academic_level",
                    "profile__home_academic_program",
                    "profile__bank_institution",
                ).get(pk=user.pk)
            if target_student is not None:
                values = merge_values_for_student(target_student)
                raw = merge_docx(raw, values)
                stem, ext = os.path.splitext(filename)
                filename = f"{stem}_{target_student.username}{ext}"

        content_type, _ = mimetypes.guess_type(filename)
        response = HttpResponse(
            raw, content_type=content_type or "application/octet-stream"
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


def _document_user_path_cache_key(prefix, *args, **kwargs):
    request = args[1]
    user_key = str(request.user.pk) if request.user.is_authenticated else "anon"
    digest = hashlib.sha256(request.get_full_path().encode()).hexdigest()[:32]
    gen = application_api_cache_generation()
    return CacheManager.get_cache_key(
        "api_response", f"{prefix}:{gen}:{user_key}:{digest}"
    )


def _document_list_cache_key(*args, **kwargs):
    return _document_user_path_cache_key("DocumentViewSet.list", *args, **kwargs)


def _document_retrieve_cache_key(*args, **kwargs):
    request = args[1]
    user_key = str(request.user.pk) if request.user.is_authenticated else "anon"
    pk = kwargs.get("pk", "")
    gen = application_api_cache_generation()
    return CacheManager.get_cache_key(
        "api_response", f"DocumentViewSet.retrieve:{gen}:{user_key}:{pk}"
    )


def _document_validation_list_cache_key(*args, **kwargs):
    return _document_user_path_cache_key(
        "DocumentValidationViewSet.list", *args, **kwargs
    )


def _document_validation_retrieve_cache_key(*args, **kwargs):
    request = args[1]
    user_key = str(request.user.pk) if request.user.is_authenticated else "anon"
    pk = kwargs.get("pk", "")
    gen = application_api_cache_generation()
    return CacheManager.get_cache_key(
        "api_response", f"DocumentValidationViewSet.retrieve:{gen}:{user_key}:{pk}"
    )


def _document_resub_list_cache_key(*args, **kwargs):
    return _document_user_path_cache_key(
        "DocumentResubmissionRequestViewSet.list", *args, **kwargs
    )


def _document_resub_retrieve_cache_key(*args, **kwargs):
    request = args[1]
    user_key = str(request.user.pk) if request.user.is_authenticated else "anon"
    pk = kwargs.get("pk", "")
    gen = application_api_cache_generation()
    return CacheManager.get_cache_key(
        "api_response",
        f"DocumentResubmissionRequestViewSet.retrieve:{gen}:{user_key}:{pk}",
    )


def _document_comment_list_cache_key(*args, **kwargs):
    return _document_user_path_cache_key("DocumentCommentViewSet.list", *args, **kwargs)


def _document_comment_retrieve_cache_key(*args, **kwargs):
    request = args[1]
    user_key = str(request.user.pk) if request.user.is_authenticated else "anon"
    pk = kwargs.get("pk", "")
    gen = application_api_cache_generation()
    return CacheManager.get_cache_key(
        "api_response", f"DocumentCommentViewSet.retrieve:{gen}:{user_key}:{pk}"
    )


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for documents with role-based permissions and filtering."""

    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = DocumentFilter
    ordering_fields = ["created_at", "validated_at"]

    def get_permissions(self):
        # validate_document is a staff review write; IsOwnerOrAdmin only allows
        # applicant writes (upload/replace), which incorrectly blocked admins.
        if getattr(self, "action", None) == "validate_document":
            return [permissions.IsAuthenticated(), IsCoordinatorOrAdmin()]
        return super().get_permissions()

    def get_queryset(self):
        """
        Filter documents based on user permissions.

        - Students: Only their own documents
        - Coordinators/Admins: All documents
        """
        user = self.request.user

        val_qs = DocumentValidation.objects.select_related("validator").order_by(
            "validated_at", "created_at"
        )
        resub_qs = DocumentResubmissionRequest.objects.select_related(
            "requested_by"
        ).order_by("-requested_at")
        comment_qs = DocumentComment.objects.select_related("author").order_by(
            "created_at"
        )

        related = (
            "application",
            "application__student",
            "application__program",
            "application__status",
            "type",
            "uploaded_by",
            "supersedes",
        )
        prefetches = (
            "uploaded_by__roles",
            "type__file_type_families",
            "successors",
            Prefetch("documentvalidation_set", queryset=val_qs),
            Prefetch("documentresubmissionrequest_set", queryset=resub_qs),
            Prefetch("documentcomment_set", queryset=comment_qs),
        )

        # Students can only see their own documents
        qs = (
            Document.objects.filter(Q(uploaded_by=user) | Q(application__student=user))
            .select_related(*related)
            .prefetch_related(*prefetches)
        )

        # Coordinators and admins can see all documents
        if (
            user.is_staff
            or user.is_superuser
            or (
                hasattr(user, "has_role")
                and (user.has_role("coordinator") or user.has_role("admin"))
            )
        ):
            qs = Document.objects.select_related(*related).prefetch_related(*prefetches)

        include_superseded = str(
            self.request.query_params.get("include_superseded", "")
        ).lower() in {"1", "true", "yes"}
        # List defaults to current uploads only; retrieve by id still finds prior versions.
        if getattr(self, "action", None) == "list" and not include_superseded:
            qs = qs.filter(successors__isnull=True)
        return qs

    def get_serializer_context(self):
        """Attach per-request caches so list serialization stays O(1) queries/row."""
        ctx = super().get_serializer_context()
        user = self.request.user
        if getattr(user, "is_authenticated", False):
            # Populate roles prefetch cache so has_role()/has_any_role() do not
            # issue EXISTS queries once per document row.
            roles = list(user.roles.all())
            cache = getattr(user, "_prefetched_objects_cache", None)
            if cache is None:
                user._prefetched_objects_cache = {}
            user._prefetched_objects_cache["roles"] = roles
            ctx["viewer_is_document_staff"] = bool(
                user.is_staff
                or user.is_superuser
                or user.has_role("coordinator")
                or user.has_role("admin")
            )
        else:
            ctx["viewer_is_document_staff"] = False
        from core.models import InstitutionFeatureSettings

        ctx["institution_feature_settings"] = InstitutionFeatureSettings.get_solo()
        return ctx

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            upload = request.FILES.get("file")
            type_id = request.data.get("type")
            application_id = request.data.get("application")
            audit_warning(
                "document_upload_rejected",
                actor=request.user,
                document_type_id=type_id,
                application_id=application_id,
                size=getattr(upload, "size", None) if upload else None,
                outcome="rejected",
                status_code=400,
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        """Set uploaded_by to current user on creation."""
        serializer.save(uploaded_by=self.request.user)
        instance = serializer.instance
        size = None
        if instance.file:
            try:
                size = instance.file.size
            except Exception:
                size = None
        audit_info(
            "document_upload",
            actor=self.request.user,
            document_id=instance.pk,
            document_type_id=instance.type_id,
            application_id=instance.application_id,
            size=size,
            outcome="created",
        )
        invalidate_application_api_responses(instance.application)

    def perform_update(self, serializer):
        serializer.save()
        invalidate_application_api_responses(serializer.instance.application)

    def perform_destroy(self, instance):
        application = instance.application
        instance.delete()
        invalidate_application_api_responses(application)

    @cache_api_response(timeout=300, key_func=_document_list_cache_key)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=300, key_func=_document_retrieve_cache_key)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=["get"], url_path="preview")
    def preview(self, request, pk=None):
        """Stream the file for inline preview (JWT auth; same access as retrieve)."""
        document = self.get_object()
        file_field = document.file
        if not file_field:
            return Response(
                {"detail": "No file attached."},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            file_handle = file_field.open("rb")
        except FileNotFoundError:
            return Response(
                {"detail": "File missing on server."},
                status=status.HTTP_404_NOT_FOUND,
            )
        content_type, _ = mimetypes.guess_type(file_field.name)
        filename = os.path.basename(file_field.name)
        try:
            head = file_handle.read(5)
            file_handle.seek(0)
        except Exception:
            head = b""
        name_l = (file_field.name or filename or "").lower()
        if name_l.endswith(".pdf") or head.startswith(b"%PDF"):
            content_type = "application/pdf"
        elif not content_type:
            content_type = "application/octet-stream"
        response = FileResponse(file_handle, content_type=content_type)
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        return response

    @action(detail=True, methods=["post"])
    def validate_document(self, request, pk=None):
        """
        Mark document as valid or invalid (coordinator/admin only).
        POST with body: { "result": "valid"|"invalid", "details": "optional note" }
        """
        document = self.get_object()
        user = request.user
        result_val = (request.data.get("result") or "").lower()
        if result_val not in ("valid", "invalid"):
            return Response(
                {"result": ["Must be 'valid' or 'invalid'."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        details = request.data.get("details") or ""
        try:
            DocumentService.validate_document(document, user, result_val, details)
            document.refresh_from_db()
            invalidate_application_api_responses(document.application)
            serializer = self.get_serializer(document)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class DocumentValidationViewSet(viewsets.ModelViewSet):
    """ViewSet for document validations with role-based access."""

    queryset = DocumentValidation.objects.all()
    serializer_class = DocumentValidationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        # Validations are a staff review write; students may only read their own.
        if getattr(self, "action", None) in (
            "create",
            "update",
            "partial_update",
            "destroy",
        ):
            return [permissions.IsAuthenticated(), IsCoordinatorOrAdmin()]
        return super().get_permissions()

    def get_queryset(self):
        """Filter validations based on user permissions."""
        user = self.request.user

        if hasattr(user, "has_role") and (
            user.has_role("coordinator") or user.has_role("admin")
        ):
            return DocumentValidation.objects.select_related(
                "document", "document__application", "document__type", "validator"
            )

        # Students can only see validations for their documents
        return DocumentValidation.objects.filter(
            Q(document__uploaded_by=user) | Q(document__application__student=user)
        ).select_related(
            "document", "document__application", "document__type", "validator"
        )

    @cache_api_response(timeout=300, key_func=_document_validation_list_cache_key)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=300, key_func=_document_validation_retrieve_cache_key)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class DocumentResubmissionRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for document resubmission requests with role-based access."""

    queryset = DocumentResubmissionRequest.objects.all()
    serializer_class = DocumentResubmissionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        # Resubmission requests are staff-only writes; students may only read theirs.
        if getattr(self, "action", None) in (
            "create",
            "update",
            "partial_update",
            "destroy",
        ):
            return [permissions.IsAuthenticated(), IsCoordinatorOrAdmin()]
        return super().get_permissions()

    def get_queryset(self):
        """Filter resubmission requests based on user permissions."""
        user = self.request.user

        if hasattr(user, "has_role") and (
            user.has_role("coordinator") or user.has_role("admin")
        ):
            return DocumentResubmissionRequest.objects.select_related(
                "document", "document__application", "document__type", "requested_by"
            )

        # Students can only see requests for their documents
        return DocumentResubmissionRequest.objects.filter(
            Q(document__uploaded_by=user) | Q(document__application__student=user)
        ).select_related(
            "document", "document__application", "document__type", "requested_by"
        )

    def perform_create(self, serializer):
        serializer.save()
        document = serializer.instance.document
        invalidate_application_api_responses(document.application)

    def perform_update(self, serializer):
        serializer.save()
        document = serializer.instance.document
        invalidate_application_api_responses(document.application)

    @cache_api_response(timeout=300, key_func=_document_resub_list_cache_key)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=300, key_func=_document_resub_retrieve_cache_key)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class DocumentCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for document comments with role-based access."""

    queryset = DocumentComment.objects.all()
    serializer_class = DocumentCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter comments based on user permissions."""
        user = self.request.user

        if hasattr(user, "has_role") and (
            user.has_role("coordinator") or user.has_role("admin")
        ):
            return DocumentComment.objects.select_related(
                "document", "document__application", "author"
            )

        # Students can only see public comments on their documents
        return DocumentComment.objects.filter(
            Q(author=user) | Q(document__application__student=user, is_private=False)
        ).select_related("document", "document__application", "author")

    def perform_create(self, serializer):
        document = serializer.validated_data["document"]
        if not DocumentService.user_can_access_document(self.request.user, document):
            raise PermissionDenied("You cannot comment on this document.")
        serializer.save(author=self.request.user)
        invalidate_application_api_responses(document.application)

    @cache_api_response(timeout=300, key_func=_document_comment_list_cache_key)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=300, key_func=_document_comment_retrieve_cache_key)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
