"""Exchange HTTP API routes.

ViewSets in ``exchange.views`` and ``exchange.partner_views`` are mounted
under ``/api/`` (Django namespace ``api``) via ``include()`` from ``api.urls``.
This app has no separate template/HTML urlconf; the Vue SPA consumes these
DRF endpoints.
"""

from django.urls import include, path
from rest_framework.routers import SimpleRouter

from exchange.partner_views import (
    PartnerAgreementViewSet,
    PartnerApplicationViewSet,
    PartnerContactViewSet,
)
from exchange.views import (
    ApplicationStatusViewSet,
    ApplicationSubjectSelectionViewSet,
    ApplicationViewSet,
    CalendarEventViewSet,
    CommentViewSet,
    EligibilityRuleSetViewSet,
    ExchangeAgreementViewSet,
    HostAcademicProgramViewSet,
    HostInstitutionViewSet,
    HostSchoolViewSet,
    HostSubjectViewSet,
    ProgramViewSet,
    SavedSearchViewSet,
    ScholarshipScoringRulesetViewSet,
    TimelineEventViewSet,
    calendar_subscribe_ics,
)

router = SimpleRouter()
router.register(r"programs", ProgramViewSet)
router.register(
    r"eligibility-rulesets", EligibilityRuleSetViewSet, basename="eligibility-ruleset"
)
router.register(
    r"scholarship-scoring-rulesets",
    ScholarshipScoringRulesetViewSet,
    basename="scholarship-scoring-ruleset",
)
router.register(
    r"exchange-agreements",
    ExchangeAgreementViewSet,
    basename="exchange-agreement",
)
router.register(
    r"host-institutions", HostInstitutionViewSet, basename="host-institution"
)
router.register(r"schools", HostSchoolViewSet, basename="host-school")
router.register(
    r"academic-programs",
    HostAcademicProgramViewSet,
    basename="host-academic-program",
)
router.register(r"host-subjects", HostSubjectViewSet, basename="host-subject")
router.register(r"applications", ApplicationViewSet, basename="application")
router.register(
    r"application-subject-selections",
    ApplicationSubjectSelectionViewSet,
    basename="application-subject-selection",
)
router.register(r"application-statuses", ApplicationStatusViewSet)
router.register(r"comments", CommentViewSet)
router.register(r"timeline-events", TimelineEventViewSet)
router.register(r"saved-searches", SavedSearchViewSet, basename="saved-search")
router.register(r"calendar/events", CalendarEventViewSet, basename="calendar-event")
router.register(
    r"partner/agreements", PartnerAgreementViewSet, basename="partner-agreement"
)
router.register(
    r"partner/applications",
    PartnerApplicationViewSet,
    basename="partner-application",
)
router.register(r"partner-contacts", PartnerContactViewSet, basename="partner-contact")

urlpatterns = [
    path(
        "calendar/subscribe.ics",
        calendar_subscribe_ics,
        name="calendar-subscribe-ics",
    ),
    path("", include(router.urls)),
]
