import django_filters
from django.db.models import Exists, OuterRef, Q
from django.utils import timezone

from .models import Document, ExchangeAgreementDocument


class ExchangeAgreementDocumentFilter(django_filters.FilterSet):
    agreement = django_filters.UUIDFilter(field_name="agreement_id")
    category = django_filters.CharFilter(field_name="category")
    current_only = django_filters.BooleanFilter(method="filter_current_only")

    ordering = django_filters.OrderingFilter(
        fields=(
            ("created_at", "created_at"),
            ("category", "category"),
        ),
    )

    class Meta:
        model = ExchangeAgreementDocument
        fields = ["agreement", "category"]

    def filter_current_only(self, queryset, name, value):
        if not value:
            return queryset
        successor = ExchangeAgreementDocument.objects.filter(
            supersedes_id=OuterRef("pk")
        )
        return queryset.annotate(_has_newer=Exists(successor)).filter(_has_newer=False)


class DocumentFilter(django_filters.FilterSet):
    """Query filters for application-linked documents (student uploads)."""

    pending_review = django_filters.BooleanFilter(method="filter_pending_review")
    overdue = django_filters.BooleanFilter(method="filter_overdue")

    ordering = django_filters.OrderingFilter(
        fields=(
            ("created_at", "created_at"),
            ("validated_at", "validated_at"),
        ),
    )

    class Meta:
        model = Document
        fields = {
            "application": ["exact"],
            "type": ["exact"],
            "is_valid": ["exact"],
        }

    def filter_pending_review(self, queryset, name, value):
        if value is None:
            return queryset
        if value:
            return queryset.filter(is_valid=False)
        return queryset.filter(is_valid=True)

    def filter_overdue(self, queryset, name, value):
        """
        Filter documents whose program requirement deadline has passed
        and the upload is not yet approved.
        """
        if not value:
            return queryset

        from exchange.models import ProgramDocumentRequirement

        today = timezone.localdate()
        matching = Q(pk__in=[])  # empty
        for req in ProgramDocumentRequirement.objects.select_related("program"):
            deadline = req.resolve_deadline()
            if not deadline or today <= deadline:
                continue
            matching |= Q(
                is_valid=False,
                application__program_id=req.program_id,
                type_id=req.document_type_id,
            )
        return queryset.filter(matching).distinct()
