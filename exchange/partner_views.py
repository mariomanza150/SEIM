"""Partner-institution portal APIs (limited agreement / applicant / document access)."""

from __future__ import annotations

from django.db.models import Prefetch
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from documents.models import ExchangeAgreementDocument
from documents.serializers import ExchangeAgreementDocumentSerializer
from exchange.models import Application, ExchangeAgreement, PartnerContact
from exchange.serializers import (
    ExchangeAgreementSerializer,
    PartnerApplicationSerializer,
    PartnerContactSerializer,
)


def _is_staff(user) -> bool:
    return bool(
        getattr(user, "is_staff", False)
        or getattr(user, "is_superuser", False)
        or (hasattr(user, "has_any_role") and user.has_any_role(["coordinator", "admin"]))
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

    @action(detail=True, methods=["get"], url_path="documents")
    def documents(self, request, pk=None):
        agreement = self.get_object()
        docs = ExchangeAgreementDocument.objects.filter(
            agreement=agreement
        ).select_related("agreement", "uploaded_by", "supersedes")
        return Response(ExchangeAgreementDocumentSerializer(docs, many=True).data)

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
