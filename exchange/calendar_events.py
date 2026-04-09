"""
Build calendar event dicts for JSON and ICS feeds (shared logic).
"""

from datetime import datetime, time as dt_time, timedelta

from django.db.models import Q
from django.utils import timezone as dj_tz

from .models import Application, ExchangeAgreement, Program


def _combine_day(d):
    return dj_tz.make_aware(
        datetime.combine(d, dt_time.min),
        dj_tz.get_current_timezone(),
    )


def build_calendar_event_dicts(user, start_param=None, end_param=None, event_type=None):
    """
    Return FullCalendar-style event dicts for *user* (same rules as CalendarEventViewSet).

    Query params mirror the REST API: optional ISO start/end, optional type filter.
    """
    events = []

    try:
        start_dt = (
            datetime.fromisoformat(start_param.replace("Z", "+00:00"))
            if start_param
            else dj_tz.now() - timedelta(days=30)
        )
        end_dt = (
            datetime.fromisoformat(end_param.replace("Z", "+00:00"))
            if end_param
            else dj_tz.now() + timedelta(days=365)
        )
    except (ValueError, AttributeError):
        start_dt = dj_tz.now() - timedelta(days=30)
        end_dt = dj_tz.now() + timedelta(days=365)

    start_d = start_dt.date()
    end_d = end_dt.date()

    staff = user.has_role("coordinator") or user.has_role("admin")

    if event_type == "all":
        wants = {"program", "deadline", "application", "agreement"}
    elif event_type in ("program", "deadline", "application", "agreement"):
        wants = {event_type}
    else:
        wants = {"program", "deadline", "application"}
        if staff:
            wants.add("agreement")

    if "program" in wants:
        programs = Program.objects.filter(
            is_active=True,
            start_date__lte=end_d,
            end_date__gte=start_d,
        )
        for program in programs:
            events.append(
                {
                    "id": f"program-start-{program.id}",
                    "title": f"{program.name} — Program starts",
                    "start": _combine_day(program.start_date),
                    "spa_path": f"/applications/new?program={program.id}",
                    "className": "event-program-start",
                    "backgroundColor": "#0d6efd",
                    "borderColor": "#0d6efd",
                    "allDay": True,
                }
            )
            events.append(
                {
                    "id": f"program-end-{program.id}",
                    "title": f"{program.name} — Program ends",
                    "start": _combine_day(program.end_date),
                    "spa_path": f"/programs/compare?ids={program.id}",
                    "className": "event-program-end",
                    "backgroundColor": "#6c757d",
                    "borderColor": "#6c757d",
                    "allDay": True,
                }
            )

    if "deadline" in wants:
        deadline_q = Q(
            application_open_date__isnull=False,
            application_open_date__gte=start_d,
            application_open_date__lte=end_d,
        ) | Q(
            application_deadline__isnull=False,
            application_deadline__gte=start_d,
            application_deadline__lte=end_d,
        )
        for program in Program.objects.filter(is_active=True).filter(deadline_q):
            if (
                program.application_open_date
                and start_d <= program.application_open_date <= end_d
            ):
                events.append(
                    {
                        "id": f"program-app-open-{program.id}",
                        "title": f"{program.name} — Applications open",
                        "start": _combine_day(program.application_open_date),
                        "spa_path": f"/applications/new?program={program.id}",
                        "className": "event-program-window",
                        "backgroundColor": "#6610f2",
                        "borderColor": "#6610f2",
                        "allDay": True,
                    }
                )
            if (
                program.application_deadline
                and start_d <= program.application_deadline <= end_d
            ):
                events.append(
                    {
                        "id": f"program-app-deadline-{program.id}",
                        "title": f"{program.name} — Apply by",
                        "start": _combine_day(program.application_deadline),
                        "spa_path": f"/applications/new?program={program.id}",
                        "className": "event-program-deadline",
                        "backgroundColor": "#dc3545",
                        "borderColor": "#dc3545",
                        "allDay": True,
                    }
                )

    if "application" in wants:
        app_in_range = Q(
            program__start_date__lte=end_d,
            program__end_date__gte=start_d,
        ) | Q(
            program__application_deadline__isnull=False,
            program__application_deadline__gte=start_d,
            program__application_deadline__lte=end_d,
        )
        app_base = Application.objects.filter(withdrawn=False).filter(app_in_range)
        if staff:
            applications = app_base.select_related("program", "status")
        else:
            applications = app_base.filter(student=user).select_related(
                "program", "status"
            )

        for application in applications:
            p = application.program
            sn = application.status.name
            if p.application_deadline and sn in (
                "draft",
                "submitted",
                "under_review",
            ):
                event_date = p.application_deadline
                label_suffix = " — apply by"
            else:
                event_date = p.start_date
                label_suffix = " — program start"
            if not (start_d <= event_date <= end_d):
                continue
            events.append(
                {
                    "id": f"application-{application.id}",
                    "title": f"Application: {p.name} ({sn}){label_suffix}",
                    "start": _combine_day(event_date),
                    "spa_path": f"/applications/{application.id}/",
                    "className": f"event-application event-status-{sn}",
                    "backgroundColor": "#198754" if sn == "approved" else "#ffc107",
                    "borderColor": "#198754" if sn == "approved" else "#ffc107",
                    "allDay": True,
                }
            )

    if "agreement" in wants and staff:
        ag_base = ExchangeAgreement.objects.filter(
            end_date__isnull=False,
            end_date__gte=start_d,
            end_date__lte=end_d,
        ).exclude(
            status__in=[
                ExchangeAgreement.Status.EXPIRED,
                ExchangeAgreement.Status.TERMINATED,
            ]
        )
        if user.has_role("admin"):
            agreements = ag_base.distinct()
        else:
            agreements = ag_base.filter(programs__coordinators=user).distinct()
        for ag in agreements:
            partner = ag.partner_institution_name or ag.title
            events.append(
                {
                    "id": f"agreement-end-{ag.id}",
                    "title": f"Agreement ends: {partner}",
                    "start": _combine_day(ag.end_date),
                    "spa_path": "/exchange-agreements",
                    "className": "event-agreement-end",
                    "backgroundColor": "#fd7e14",
                    "borderColor": "#fd7e14",
                    "allDay": True,
                }
            )

    return events
