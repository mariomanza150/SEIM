"""Wagtail API v2 viewset that does not leak SPA-only FAQ pages."""

from wagtail.api.v2.views import PagesAPIViewSet

from cms.help import spa_help_index_page_ids, spa_only_faq_page_ids


class PublicPagesAPIViewSet(PagesAPIViewSet):
    """Same as stock pages API, minus spa-only FAQ pages and the SPA help index."""

    def get_queryset(self):
        queryset = super().get_queryset()
        hidden_ids = spa_only_faq_page_ids() + spa_help_index_page_ids()
        if hidden_ids:
            queryset = queryset.exclude(pk__in=hidden_ids)
        return queryset
