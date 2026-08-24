"""Shared DRF pagination for list endpoints."""

from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """Page-number pagination that honors a capped ``page_size`` query param."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
