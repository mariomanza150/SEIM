"""Phase 2 tester tools: demo role switcher, impersonation, outbox, flags, reset."""

from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .demo import DESCRIPTIONS, demo_queryset
from .gating import (
    CLAIM_IMPERSONATOR,
    CLAIM_SWITCHED_FROM,
    deploy_tier,
    get_tester,
    is_triager,
)
from .models import CapturedEmail, QAAuditEvent
from .permissions import IsTester, IsTriager
from .views import QAScopedThrottle

SWITCH_LIFETIME = timedelta(hours=8)
IMPERSONATION_LIFETIME = timedelta(minutes=30)


def _client_ip(request):
    return (request.META.get("REMOTE_ADDR") or "")[:45] or None


def _audit(request, actor, target, action, note=""):
    QAAuditEvent.objects.create(
        actor=actor,
        target=target,
        action=action,
        ip_address=_client_ip(request),
        user_agent=(request.META.get("HTTP_USER_AGENT") or "")[:500],
        note=note[:500],
    )


def _tokens_for(target, claim, actor, lifetime):
    refresh = RefreshToken.for_user(target)
    refresh[claim] = str(actor.pk)
    refresh.set_exp(lifetime=lifetime)
    access = refresh.access_token
    access.set_exp(lifetime=min(lifetime, settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]))
    return {"access": str(access), "refresh": str(refresh)}


def _user_summary(user):
    return {
        "id": str(user.pk),
        "email": user.email,
        "name": f"{user.first_name} {user.last_name}".strip() or user.email,
        "role": user.primary_role,
        "is_staff": user.is_staff,
        "description": DESCRIPTIONS.get(user.email.lower(), ""),
    }


class DemoAccountsView(APIView):
    """List demo accounts testers can switch into (never real users)."""

    permission_classes = [IsAuthenticated, IsTester]

    def get(self, request):
        accounts = [_user_summary(u) for u in demo_queryset()]
        order = {"admin": 0, "coordinator": 1, "partner": 2, "student": 3}
        accounts.sort(key=lambda a: (order.get(a["role"], 9), a["email"]))
        return Response(
            {
                "results": accounts,
                "password_hint": _("Ask the SEIM admin for the shared demo password."),
            }
        )


class DemoSwitchView(APIView):
    """Issue tokens for a demo account, tagged with the real tester's id."""

    permission_classes = [IsAuthenticated, IsTester]
    throttle_scope = "qa_demo_login"

    def get_throttles(self):
        return [QAScopedThrottle()]

    def post(self, request):
        tester = get_tester(request)
        target = get_object_or_404(demo_queryset(), pk=request.data.get("user_id"))
        if target.pk == tester.pk:
            return Response({"detail": _("Choose a demo account.")}, status=400)
        _audit(request, tester, target, QAAuditEvent.Action.DEMO_SWITCH)
        data = _tokens_for(target, CLAIM_SWITCHED_FROM, tester, SWITCH_LIFETIME)
        data["acting_as"] = _user_summary(target)
        return Response(data)


class DemoReturnView(APIView):
    """Audit the return to the tester's own account (tokens are restored client-side)."""

    permission_classes = [IsAuthenticated, IsTester]

    def post(self, request):
        tester = get_tester(request)
        if request.user.pk != tester.pk:
            action = (
                QAAuditEvent.Action.IMPERSONATE_STOP
                if request.auth and request.auth.get(CLAIM_IMPERSONATOR)
                else QAAuditEvent.Action.DEMO_RETURN
            )
            _audit(request, tester, request.user, action)
            refresh = request.data.get("refresh")
            if refresh:
                try:
                    RefreshToken(refresh).blacklist()
                except Exception:  # noqa: BLE001 - best effort
                    pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class ImpersonateSearchView(APIView):
    permission_classes = [IsAuthenticated, IsTriager]

    def get(self, request):
        q = (request.query_params.get("q") or "").strip()
        if len(q) < 2:
            return Response({"results": []})
        User = get_user_model()
        qs = (
            User.objects.filter(is_active=True)
            .filter(
                Q(email__icontains=q)
                | Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
                | Q(username__icontains=q)
            )
            .prefetch_related("roles")
            .order_by("email")[:20]
        )
        return Response({"results": [_user_summary(u) for u in qs]})


class ImpersonateView(APIView):
    """Admins (triagers) may act as any non-superuser account; audit-logged, 30 min."""

    permission_classes = [IsAuthenticated, IsTriager]
    throttle_scope = "qa_demo_login"

    def get_throttles(self):
        return [QAScopedThrottle()]

    def post(self, request):
        actor = get_tester(request)
        User = get_user_model()
        target = get_object_or_404(User, pk=request.data.get("user_id"), is_active=True)
        if target.pk == actor.pk:
            return Response({"detail": _("You are already this user.")}, status=400)
        if target.is_superuser and not actor.is_superuser:
            return Response(
                {"detail": _("Only superusers can act as a superuser.")}, status=403
            )
        reason = str(request.data.get("reason") or "")[:500]
        _audit(
            request, actor, target, QAAuditEvent.Action.IMPERSONATE_START, note=reason
        )
        data = _tokens_for(target, CLAIM_IMPERSONATOR, actor, IMPERSONATION_LIFETIME)
        data["acting_as"] = _user_summary(target)
        data["expires_in"] = int(IMPERSONATION_LIFETIME.total_seconds())
        return Response(data)


def _visible_emails(request, tester):
    """Testers see mail to demo accounts and to themselves; triagers see all."""
    qs = CapturedEmail.objects.all()
    if is_triager(tester):
        return qs
    addresses = [tester.email.lower()] + [
        e.lower() for e in demo_queryset().values_list("email", flat=True)
    ]
    cond = Q()
    for addr in addresses:
        cond |= Q(recipients_index__icontains=addr)
    return qs.filter(cond) if addresses else qs.none()


class OutboxListView(APIView):
    permission_classes = [IsAuthenticated, IsTester]

    def get(self, request):
        tester = get_tester(request)
        qs = _visible_emails(request, tester)
        q = (request.query_params.get("q") or "").strip()
        if q:
            qs = qs.filter(
                Q(subject__icontains=q) | Q(recipients_index__icontains=q.lower())
            )
        rows = qs.only("id", "subject", "from_email", "to", "created_at")[:100]
        return Response(
            {
                "capturing": settings.EMAIL_BACKEND == "qa.mail.CaptureEmailBackend",
                "results": [
                    {
                        "id": str(m.pk),
                        "subject": m.subject,
                        "from_email": m.from_email,
                        "to": m.to,
                        "created_at": m.created_at,
                    }
                    for m in rows
                ],
            }
        )


class OutboxDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTester]

    def get(self, request, pk):
        tester = get_tester(request)
        msg = _visible_emails(request, tester).filter(pk=pk).first()
        if msg is None:
            raise Http404
        response = Response(
            {
                "id": str(msg.pk),
                "subject": msg.subject,
                "from_email": msg.from_email,
                "to": msg.to,
                "cc": msg.cc,
                "body_text": msg.body_text,
                "body_html": msg.body_html,
                "created_at": msg.created_at,
            }
        )
        response["Cache-Control"] = "private, no-store"
        return response


class FlagsView(APIView):
    """Read-only feature flags + tester-relevant environment summary."""

    permission_classes = [IsAuthenticated, IsTester]

    def get(self, request):
        from core.models import InstitutionFeatureSettings

        inst = InstitutionFeatureSettings.get_solo()
        institution = {
            f.name: getattr(inst, f.name)
            for f in inst._meta.fields
            if f.get_internal_type() == "BooleanField"
        }
        throttles = settings.REST_FRAMEWORK.get("DEFAULT_THROTTLE_CLASSES") or []
        return Response(
            {
                "feature_flags": dict(getattr(settings, "FEATURE_FLAGS", {})),
                "institution": institution,
                "environment": {
                    "deploy_tier": deploy_tier(),
                    "version": getattr(settings, "VERSION", ""),
                    "commit": getattr(settings, "BUILD_COMMIT", ""),
                    "email_capture": settings.EMAIL_BACKEND
                    == "qa.mail.CaptureEmailBackend",
                    "virus_scanner": getattr(settings, "VIRUS_SCANNER_TYPE", ""),
                    "global_throttles": bool(throttles),
                    "demo_password_configured": bool(
                        (getattr(settings, "TESTER_DEMO_PASSWORD", "") or "").strip()
                    ),
                },
            }
        )


class ResetDemoView(APIView):
    """Admins only: queue a demo-data reset (Celery)."""

    permission_classes = [IsAuthenticated, IsTriager]
    throttle_scope = "qa_reset"

    def get_throttles(self):
        return [QAScopedThrottle()]

    def post(self, request):
        from .tasks import RESET_LOCK_KEY, reset_demo_data_task

        if str(request.data.get("confirm") or "").strip().upper() != "RESET":
            return Response({"detail": _("Type RESET to confirm.")}, status=400)
        if not cache.add(RESET_LOCK_KEY, "1", timeout=900):
            return Response({"detail": _("A reset is already running.")}, status=409)
        actor = get_tester(request)
        _audit(request, actor, None, QAAuditEvent.Action.RESET_DEMO)
        try:
            reset_demo_data_task.delay()
        except Exception:
            cache.delete(RESET_LOCK_KEY)
            return Response({"detail": _("Could not queue the reset.")}, status=503)
        return Response({"queued": True}, status=202)
