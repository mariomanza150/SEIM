"""Authenticated SPA help-center API (Wagtail FAQ pages, rendered HTML)."""

from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cms.help import (
    help_article_queryset_for_user,
    parse_contextual_keys,
    serialize_help_article,
)


def _filtered_help_pages(request):
    queryset = help_article_queryset_for_user(request.user)
    topic = (request.query_params.get("topic") or "").strip()
    if topic:
        queryset = queryset.filter(topic=topic)
    query = (request.query_params.get("q") or "").strip()
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) | Q(introduction__icontains=query)
        )
    pages = list(queryset.distinct().order_by("topic", "title"))
    key = (request.query_params.get("key") or "").strip()
    if key:
        pages = [page for page in pages if key in parse_contextual_keys(page.contextual_keys)]
    return pages


@extend_schema(
    summary="List SPA help articles",
    parameters=[
        OpenApiParameter(name="q", description="Search title and introduction", required=False, type=str),
        OpenApiParameter(
            name="key",
            description="Vue route name tagged on contextual_keys",
            required=False,
            type=str,
        ),
        OpenApiParameter(name="topic", description="Hub topic key", required=False, type=str),
    ],
)
class HelpArticleListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pages = _filtered_help_pages(request)
        results = [serialize_help_article(page) for page in pages]
        return Response({"count": len(results), "results": results})


@extend_schema(summary="Retrieve one SPA help article")
class HelpArticleDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        page = help_article_queryset_for_user(request.user).filter(slug=slug).first()
        if page is None:
            raise NotFound()
        return Response(serialize_help_article(page))
