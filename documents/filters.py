import django_filters
from django.db.models import Exists, OuterRef

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
