from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IssueViewSet, QAContextView
from .views_scenarios import (
    ScenarioListView,
    ScenarioMatrixView,
    ScenarioResultView,
    TriagerListView,
)
from .views_tools import (
    DemoAccountsView,
    DemoReturnView,
    DemoSwitchView,
    FlagsView,
    ImpersonateSearchView,
    ImpersonateView,
    OutboxDetailView,
    OutboxListView,
    ResetDemoView,
)

router = DefaultRouter()
router.register("issues", IssueViewSet, basename="qa-issue")

urlpatterns = [
    path("context/", QAContextView.as_view(), name="qa-context"),
    path("demo-accounts/", DemoAccountsView.as_view(), name="qa-demo-accounts"),
    path("demo-login/", DemoSwitchView.as_view(), name="qa-demo-login"),
    path("demo-login/return/", DemoReturnView.as_view(), name="qa-demo-return"),
    path("impersonate/", ImpersonateView.as_view(), name="qa-impersonate"),
    path(
        "impersonate/search/",
        ImpersonateSearchView.as_view(),
        name="qa-impersonate-search",
    ),
    path("outbox/", OutboxListView.as_view(), name="qa-outbox"),
    path("outbox/<uuid:pk>/", OutboxDetailView.as_view(), name="qa-outbox-detail"),
    path("flags/", FlagsView.as_view(), name="qa-flags"),
    path("reset-demo/", ResetDemoView.as_view(), name="qa-reset-demo"),
    path("scenarios/", ScenarioListView.as_view(), name="qa-scenarios"),
    path("scenarios/matrix/", ScenarioMatrixView.as_view(), name="qa-scenario-matrix"),
    path(
        "scenarios/<uuid:pk>/result/",
        ScenarioResultView.as_view(),
        name="qa-scenario-result",
    ),
    path("triagers/", TriagerListView.as_view(), name="qa-triagers"),
    path("", include(router.urls)),
]
