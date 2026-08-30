from __future__ import annotations

import logging
from datetime import datetime, timezone

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_datetime
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from toefl.models import PracticeAttempt
from toefl.partner import ToeflPartnerError, create_launch_token
from toefl.security import verify_signature
from toefl.serializers import (
    LaunchRequestSerializer,
    LaunchResponseSerializer,
    PracticeAttemptListSerializer,
    PracticeAttemptSerializer,
)

logger = logging.getLogger(__name__)
User = get_user_model()


def _is_staff_user(user) -> bool:
    return bool(
        user
        and user.is_authenticated
        and (user.is_staff or getattr(user, "is_admin", False))
    )


class PracticeAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    """List/retrieve practice attempts for the current student (staff: all)."""

    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_serializer_class(self):
        if self.action == "list":
            return PracticeAttemptListSerializer
        return PracticeAttemptSerializer

    def get_queryset(self):
        qs = PracticeAttempt.objects.select_related("user")
        user = self.request.user
        if _is_staff_user(user):
            user_id = self.request.query_params.get("user")
            if user_id:
                return qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=user)


class LaunchView(APIView):
    """Create a signed TOEFL Practice launch URL for the authenticated student."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = LaunchRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        exam_code = (
            data.get("exam_code")
            or getattr(settings, "TOEFL_DEFAULT_EXAM_CODE", "")
            or "director_extracted"
        )
        callback_url = getattr(settings, "TOEFL_CALLBACK_URL", "") or ""
        return_url = getattr(settings, "TOEFL_RETURN_URL", "") or ""
        if not callback_url or not return_url:
            return Response(
                {"detail": "TOEFL callback/return URLs are not configured"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            result = create_launch_token(
                exam_code=exam_code,
                client_ref=str(request.user.pk),
                callback_url=callback_url,
                return_url=return_url,
                macro_id=data.get("macro_id") or "all",
                categories=list(data.get("categories") or []),
                n=int(data.get("n") or 20),
            )
        except ToeflPartnerError as exc:
            return Response(
                {"detail": str(exc)},
                status=exc.status_code or status.HTTP_502_BAD_GATEWAY,
            )

        out = LaunchResponseSerializer(
            {
                "launch_url": result["launch_url"],
                "token": result.get("token") or "",
            }
        )
        return Response(out.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def webhook_view(request):
    """Receive signed score payloads from TOEFL Practice. Does not touch Profile.toefl_score."""
    secret = getattr(settings, "TOEFL_SIGNING_SECRET", "") or ""
    if not secret:
        return Response(
            {"detail": "TOEFL signing secret is not configured"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    signature = request.headers.get("X-Webhook-Signature") or ""
    raw = request.body or b""
    if not verify_signature(raw, signature, secret):
        return Response({"detail": "invalid signature"}, status=status.HTTP_401_UNAUTHORIZED)

    payload = request.data
    if not isinstance(payload, dict):
        return Response({"detail": "invalid payload"}, status=status.HTTP_400_BAD_REQUEST)

    session_id = str(payload.get("session_id") or "").strip()
    client_ref = str(payload.get("client_ref") or "").strip()
    if not session_id:
        return Response({"detail": "session_id required"}, status=status.HTTP_400_BAD_REQUEST)
    if not client_ref:
        return Response({"detail": "client_ref required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(pk=client_ref)
    except (User.DoesNotExist, ValueError, TypeError):
        logger.warning("TOEFL webhook unknown client_ref=%s", client_ref)
        return Response({"detail": "unknown client_ref"}, status=status.HTTP_400_BAD_REQUEST)

    score = payload.get("score") or {}
    if not isinstance(score, dict):
        score = {}

    completed_raw = payload.get("completed_at")
    completed_at = None
    if completed_raw:
        completed_at = parse_datetime(str(completed_raw))
        if completed_at is None:
            try:
                completed_at = datetime.fromisoformat(str(completed_raw).replace("Z", "+00:00"))
            except ValueError:
                completed_at = None
        if completed_at and completed_at.tzinfo is None:
            completed_at = completed_at.replace(tzinfo=timezone.utc)

    defaults = {
        "user": user,
        "exam_code": str(payload.get("exam_code") or ""),
        "macro_id": str(payload.get("macro_id") or ""),
        "client_ref": client_ref,
        "earned": int(score.get("earned") or 0),
        "total": int(score.get("total") or 0),
        "percent": float(score.get("percent") or 0),
        "categories": list(payload.get("categories") or []),
        "weakest": list(payload.get("weakest") or []),
        "items": list(payload.get("items") or []),
        "completed_at": completed_at,
        "raw_payload": payload,
    }
    attempt, created = PracticeAttempt.objects.update_or_create(
        external_session_id=session_id,
        defaults=defaults,
    )
    return Response(
        {
            "ok": True,
            "created": created,
            "id": str(attempt.id),
        },
        status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED,
    )
