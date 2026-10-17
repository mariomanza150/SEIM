"""Phase 3: test scenario checklist + triage helpers."""

from collections import defaultdict

from django.conf import settings
from django.db.models import Max
from django.shortcuts import get_object_or_404
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .gating import get_tester
from .models import Issue, ScenarioResult, TestScenario
from .permissions import IsTester, IsTriager
from .services import triager_queryset


def current_build():
    return (getattr(settings, "BUILD_COMMIT", "") or "")[:40]


def _localized(scenario, field, lang):
    if lang.startswith("es"):
        return getattr(scenario, f"{field}_es") or getattr(scenario, field)
    return getattr(scenario, field)


def _scenario_payload(s, lang):
    return {
        "id": str(s.pk),
        "code": s.code,
        "area": s.area,
        "role": s.role,
        "route_name": s.route_name,
        "title": _localized(s, "title", lang),
        "steps": _localized(s, "steps", lang),
        "expected": _localized(s, "expected", lang),
    }


def _result_payload(r):
    if r is None:
        return None
    return {
        "outcome": r.outcome,
        "note": r.note,
        "issue_number": r.issue.number if r.issue_id else None,
        "issue_id": str(r.issue_id) if r.issue_id else None,
        "updated_at": r.updated_at,
    }


def _lang(request):
    return (request.query_params.get("lang") or get_language() or "en").lower()


class ScenarioListView(APIView):
    """Checklist for the current build with the tester's own results."""

    permission_classes = [IsAuthenticated, IsTester]

    def get(self, request):
        tester = get_tester(request)
        build = current_build()
        lang = _lang(request)
        scenarios = list(TestScenario.objects.filter(is_active=True))
        mine = {
            r.scenario_id: r
            for r in ScenarioResult.objects.filter(
                tester=tester, build_commit=build
            ).select_related("issue")
        }
        rows = []
        summary = defaultdict(int)
        for s in scenarios:
            r = mine.get(s.pk)
            summary[r.outcome if r else "todo"] += 1
            rows.append({**_scenario_payload(s, lang), "result": _result_payload(r)})
        return Response({"build": build, "summary": dict(summary), "results": rows})


class ScenarioResultView(APIView):
    permission_classes = [IsAuthenticated, IsTester]

    def post(self, request, pk):
        tester = get_tester(request)
        scenario = get_object_or_404(TestScenario, pk=pk, is_active=True)
        outcome = str(request.data.get("outcome") or "")
        if outcome not in ScenarioResult.Outcome.values:
            return Response({"outcome": [_("Choose a valid result.")]}, status=400)
        note = str(request.data.get("note") or "").strip()[:5000]
        issue = None
        number = request.data.get("issue_number")
        if number not in (None, ""):
            try:
                issue = Issue.objects.filter(number=int(number)).first()
            except (TypeError, ValueError):
                issue = None
            if issue is None:
                return Response(
                    {"issue_number": [_("Unknown report number.")]}, status=400
                )
        result, _created = ScenarioResult.objects.update_or_create(
            scenario=scenario,
            tester=tester,
            build_commit=current_build(),
            defaults={"outcome": outcome, "note": note, "issue": issue},
        )
        return Response(_result_payload(result))

    def delete(self, request, pk):
        tester = get_tester(request)
        ScenarioResult.objects.filter(
            scenario_id=pk, tester=tester, build_commit=current_build()
        ).delete()
        return Response(status=204)


OUTCOME_RANK = {"fail": 0, "blocked": 1, "pass": 2, "skipped": 3}


class ScenarioMatrixView(APIView):
    """Triagers: worst outcome per scenario for the latest builds."""

    permission_classes = [IsAuthenticated, IsTriager]

    def get(self, request):
        lang = _lang(request)
        builds = list(
            ScenarioResult.objects.values("build_commit")
            .annotate(last=Max("updated_at"))
            .order_by("-last")
            .values_list("build_commit", flat=True)[:6]
        )
        current = current_build()
        if current not in builds:
            builds = [current] + builds[:5]
        cells = defaultdict(dict)
        for r in ScenarioResult.objects.filter(build_commit__in=builds).select_related(
            "tester", "issue"
        ):
            cell = cells[str(r.scenario_id)].setdefault(
                r.build_commit,
                {"outcome": None, "counts": defaultdict(int), "issues": []},
            )
            cell["counts"][r.outcome] += 1
            if (
                cell["outcome"] is None
                or OUTCOME_RANK[r.outcome] < OUTCOME_RANK[cell["outcome"]]
            ):
                cell["outcome"] = r.outcome
            if r.issue_id:
                cell["issues"].append(r.issue.number)
        rows = []
        for s in TestScenario.objects.filter(is_active=True):
            per_build = {}
            for b in builds:
                c = cells.get(str(s.pk), {}).get(b)
                per_build[b] = (
                    {
                        "outcome": c["outcome"],
                        "counts": dict(c["counts"]),
                        "issues": c["issues"],
                    }
                    if c
                    else None
                )
            rows.append({**_scenario_payload(s, lang), "builds": per_build})
        return Response({"builds": builds, "current": current, "results": rows})


class TriagerListView(APIView):
    """Assignee choices for the triage page."""

    permission_classes = [IsAuthenticated, IsTriager]

    def get(self, request):
        return Response(
            {
                "results": [
                    {"id": str(u.pk), "email": u.email}
                    for u in triager_queryset().order_by("email")
                ]
            }
        )
