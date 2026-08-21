from django.urls import path

from cms.views import HelpArticleDetailView, HelpArticleListView

urlpatterns = [
    path("articles/", HelpArticleListView.as_view(), name="help-article-list"),
    path(
        "articles/<slug:slug>/",
        HelpArticleDetailView.as_view(),
        name="help-article-detail",
    ),
]
