"""Partner-institution portal APIs (limited agreement / applicant / document access)."""

from __future__ import annotations

from django.db.models import Prefetch
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from core.cache import invalidate_application_api_responses
from documents.models import ExchangeAgreementDocument
from documents.serializers import ExchangeAgreementDocumentSerializer
from exchange.models import (
    AgreementComment,
    Application,
    Comment,
    ExchangeAgreement,
    PartnerContact,
    TimelineEvent,
)
from exchange.serializers import (
    ExchangeAgreementSerializer,
    PartnerAgreementCommentSerializer,
    PartnerApplicationSerializer,
    PartnerCommentSerializer,
    PartnerContactSerializer,
)

# Partner-facing upload surface (staff keep full catalog via /api/agreement-documents/).
PARTNER_UPLOAD_CATEGORIES = frozenset(
    {
        ExchangeAgreementDocument.Category.SIGNED_COPY,
        ExchangeAgreementDocument.Category.CORRESPONDENCE,
        ExchangeAgreementDocument.Category.AMENDMENT,
        ExchangeAgreementDocument.Category.OTHER,
    }
)


def _is_staff(user) -> bool:
    return bool(
        getattr(user, "is_staff", False)
        or getattr(user, "is_superuser", False)
        or (
            hasattr(user, "has_any_role")
            and user.has_any_role(["coordinator", "admin"])
        )
    )


def _is_partner(user) -> bool:
    return bool(hasattr(user, "has_role") and user.has_role("partner"))


def partner_agreement_ids(user):
    return PartnerContact.objects.filter(user=user, is_active=True).values_list(
        "agreement_id", flat=True
    )


class IsPartnerOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return _is_staff(user) or _is_partner(user)


class PartnerContactViewSet(viewsets.ModelViewSet):
    """Staff CRUD for linking partner users to agreements."""

    serializer_class = PartnerContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = PartnerContact.objects.select_related("user", "agreement")
        if _is_staff(user):
            return qs.all()
        return qs.filter(user=user, is_active=True)

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            from core.permissions import IsCoordinatorOrAdmin

            return [IsCoordinatorOrAdmin()]
        return [permissions.IsAuthenticated()]


class PartnerAgreementViewSet(viewsets.ReadOnlyModelViewSet):
    """Partner-facing agreements they are linked to (staff can also list)."""

    serializer_class = ExchangeAgreementSerializer
    permission_classes = [IsPartnerOrStaff]

    def get_queryset(self):
        user = self.request.user
        draft_successors = ExchangeAgreement.objects.filter(
            status=ExchangeAgreement.Status.DRAFT
        )
        qs = ExchangeAgreement.objects.prefetch_related(
            "programs",
            Prefetch(
                "renewal_successors",
                queryset=draft_successors,
                to_attr="_draft_renewal_successors",
            ),
            "partner_contacts",
            "partner_contacts__user",
        )
        if _is_staff(user):
            return qs.all()
        return qs.filter(id__in=partner_agreement_ids(user))

    @action(
        detail=True,
        methods=["get", "post"],
        url_path="documents",
        parser_classes=[MultiPartParser, FormParser, JSONParser],
    )
    def documents(self, request, pk=None):
        """List or upload repository files for a linked agreement."""
        agreement = self.get_object()
        if request.method == "GET":
            docs = ExchangeAgreementDocument.objects.filter(
                agreement=agreement
            ).select_related("agreement", "uploaded_by", "supersedes")
            current_only = str(request.query_params.get("current_only") or "").lower() in (
                "1",
                "true",
                "yes",
            )
            if current_only:
                from django.db.models import Exists, OuterRef

                successor = ExchangeAgreementDocument.objects.filter(
                    supersedes_id=OuterRef("pk")
                )
                docs = docs.annotate(_has_newer=Exists(successor)).filter(
                    _has_newer=False
                )
            return Response(
                ExchangeAgreementDocumentSerializer(
                    docs, many=True, context={"request": request}
                ).data
            )

        upload = request.FILES.get("file") or request.data.get("file")
        if not upload:
            return Response(
                {"file": ["A file is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        category = (
            request.data.get("category")
            or ExchangeAgreementDocument.Category.SIGNED_COPY
        )
        if category not in PARTNER_UPLOAD_CATEGORIES:
            return Response(
                {
                    "category": [
                        "Partners may upload: "
                        + ", ".join(sorted(PARTNER_UPLOAD_CATEGORIES))
                        + "."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        payload = {
            "agreement": agreement.id,
            "category": category,
            "title": request.data.get("title") or "",
            "notes": request.data.get("notes") or "",
            "file": upload,
        }
        supersedes = request.data.get("supersedes")
        if supersedes:
            payload["supersedes"] = supersedes
        serializer = ExchangeAgreementDocumentSerializer(
            data=payload, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="partner-contacts")
    def add_partner_contact(self, request, pk=None):
        if not _is_staff(request.user):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        agreement = self.get_object()
        from django.contrib.auth import get_user_model

        from accounts.models import Role

        User = get_user_model()
        user = None
        user_id = request.data.get("user")
        email = (request.data.get("email") or "").strip()
        if user_id:
            user = User.objects.filter(pk=user_id).first()
        elif email:
            user = User.objects.filter(email__iexact=email).first()
        if not user:
            return Response(
                {"email": ["No user found for that email."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        partner_role, _ = Role.objects.get_or_create(name="partner")
        user.roles.add(partner_role)
        contact, created = PartnerContact.objects.get_or_create(
            user=user,
            agreement=agreement,
            defaults={
                "title": request.data.get("title") or "",
                "is_active": True,
            },
        )
        if not created:
            contact.is_active = True
            if request.data.get("title"):
                contact.title = request.data.get("title")
            contact.save()
        return Response(
            PartnerContactSerializer(contact).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get", "post"], url_path="comments")
    def comments(self, request, pk=None):
        """Public agreement thread for partner users (no private staff notes)."""
        agreement = self.get_object()
        if request.method == "GET":
            qs = (
                AgreementComment.objects.filter(agreement=agreement, is_private=False)
                .select_related("author")
                .order_by("created_at", "id")
            )
            return Response(PartnerAgreementCommentSerializer(qs, many=True).data)
        text = (request.data.get("text") or "").strip()
        if not text:
            return Response(
                {"text": ["This field may not be blank."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        comment = AgreementComment.objects.create(
            agreement=agreement,
            author=request.user,
            text=text,
            is_private=False,
        )
        return Response(
            PartnerAgreementCommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )


class PartnerApplicationViewSet(viewsets.ReadOnlyModelViewSet):
    """Limited applicant status for programs covered by the partner's agreements."""

    serializer_class = PartnerApplicationSerializer
    permission_classes = [IsPartnerOrStaff]

    def get_queryset(self):
        user = self.request.user
        qs = Application.objects.select_related(
            "program", "student", "status"
        ).prefetch_related("document_set", "document_set__type")
        if _is_staff(user):
            return qs.all()
        return qs.filter(
            program__exchange_agreements__id__in=partner_agreement_ids(user)
        ).distinct()

    @action(detail=True, methods=["get", "post"], url_path="comments")
    def comments(self, request, pk=None):
        """Public application thread for partner users (no private staff notes)."""
        application = self.get_object()
        if request.method == "GET":
            qs = (
                Comment.objects.filter(application=application, is_private=False)
                .select_related("author")
                .order_by("created_at", "id")
            )
            return Response(PartnerCommentSerializer(qs, many=True).data)
        text = (request.data.get("text") or "").strip()
        if not text:
            return Response(
                {"text": ["This field may not be blank."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        from exchange.services import ApplicationService

        comment = ApplicationService.add_comment(
            application, request.user, text, is_private=False
        )
        invalidate_application_api_responses(application)
        return Response(
            PartnerCommentSerializer(comment).data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["post"], url_path="acknowledge-nomination")
    def acknowledge_nomination(self, request, pk=None):
        """Partner acknowledges a nominated applicant for their linked programs."""
        from django.utils import timezone as dj_tz

        application = self.get_object()
        if application.status.name != "nominated":
            return Response(
                {"detail": "Only nominated applications can be acknowledged."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if application.partner_nomination_acknowledged_at:
            return Response(PartnerApplicationSerializer(application).data)
        application.partner_nomination_acknowledged_at = dj_tz.now()
        application.save(
            update_fields=["partner_nomination_acknowledged_at", "updated_at"]
        )
        TimelineEvent.objects.create(
            application=application,
            event_type="partner_nomination_acknowledged",
            description="Partner acknowledged nomination.",
            created_by=request.user,
        )
        return Response(PartnerApplicationSerializer(application).data)
