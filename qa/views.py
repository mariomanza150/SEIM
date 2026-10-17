import mimetypes
import os

from django.conf import settings
from django.db import transaction
from django.db.models import Count
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .gating import (
    CLAIM_IMPERSONATOR,
    deploy_tier,
    get_tester,
    is_impersonating,
    is_triager,
    tester_tools_enabled,
)
from .models import Issue, IssueAttachment, IssueComment
from .permissions import IsTester
from .serializers import (
    IssueAttachmentSerializer,
    IssueCommentSerializer,
    IssueCreateSerializer,
    IssueDetailSerializer,
    IssueListSerializer,
    IssueReporterUpdateSerializer,
    IssueTriageUpdateSerializer,
    validate_uploads,
)
from .services import notify_new_issue, notify_reopened, notify_status_change


class QAScopedThrottle(ScopedRateThrottle):
    """Scoped throttle keyed on the real tester (not the switched demo user)."""

    def get_cache_key(self, request, view):
        tester = get_tester(request)
        ident = tester.pk if tester else self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}


class QAContextView(APIView):
    """
    Tester-toolkit context for the SPA. 404 when the environment gate is closed,
    so real production does not reveal the toolkit exists.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not tester_tools_enabled():
            raise Http404
        tester = get_tester(request)
        acting = request.user if is_impersonating(request) else None
        data = {
            "enabled": True,
            "is_tester": tester is not None,
            "is_triager": is_triager(tester),
            "deploy_tier": deploy_tier(),
            "version": getattr(settings, "VERSION", ""),
            "commit": getattr(settings, "BUILD_COMMIT", ""),
            "limits": {
                "max_attachments": getattr(settings, "QA_MAX_ATTACHMENTS", 5),
                "max_image_mb": getattr(settings, "QA_MAX_IMAGE_MB", 10),
                "max_video_mb": getattr(settings, "QA_MAX_VIDEO_MB", 25),
            },
            "acting_as": None,
            "tester": None,
        }
        if tester is not None:
            data["tester"] = {"id": str(tester.pk), "email": tester.email}
        if acting is not None and tester is not None:
            data["acting_as"] = {
                "id": str(acting.pk),
                "email": acting.email,
                "role": getattr(acting, "primary_role", ""),
                "is_demo_account": bool(getattr(acting, "is_demo_account", False)),
                "mode": "impersonate"
                if request.auth is not None and request.auth.get(CLAIM_IMPERSONATOR)
                else "switch",
            }
        response = Response(data)
        response["Cache-Control"] = "private, no-store"
        return response


class IssueViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Testers see their own reports; triagers (admins) see all."""

    permission_classes = [IsAuthenticated, IsTester]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ("status", "severity", "kind")
    search_fields = ("title", "description", "route_name")
    ordering_fields = ("number", "created_at", "updated_at", "severity", "status")
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_throttles(self):
        if self.action == "create":
            self.throttle_scope = "qa_issue"
            return [QAScopedThrottle()]
        if self.action in ("attachments", "comments"):
            self.throttle_scope = "qa_upload"
            return [QAScopedThrottle()]
        return super().get_throttles()

    # helpers -------------------------------------------------------------
    @property
    def tester(self):
        if not hasattr(self, "_tester"):
            self._tester = get_tester(self.request)
        return self._tester

    @property
    def triager(self):
        return is_triager(self.tester)

    def get_queryset(self):
        qs = Issue.objects.select_related(
            "reporter", "acting_as", "assignee", "duplicate_of"
        )
        qs = qs.annotate(attachment_count=Count("attachments", distinct=True)).order_by(
            "-number"
        )
        if not self.triager:
            qs = qs.filter(reporter=self.tester)
        mine = self.request.query_params.get("mine")
        if mine in ("1", "true"):
            qs = qs.filter(reporter=self.tester)
        if self.request.query_params.get("assigned") == "me":
            qs = qs.filter(assignee=self.tester)
        elif self.request.query_params.get("assigned") == "none":
            qs = qs.filter(assignee__isnull=True)
        open_only = self.request.query_params.get("open")
        if open_only in ("1", "true"):
            qs = qs.filter(status__in=Issue.OPEN_STATUSES)
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return IssueListSerializer
        if self.action == "create":
            return IssueCreateSerializer
        if self.action in ("update", "partial_update"):
            return (
                IssueTriageUpdateSerializer
                if self.triager
                else IssueReporterUpdateSerializer
            )
        return IssueDetailSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["is_triager"] = self.triager
        return ctx

    def _detail(self, issue, status_code=status.HTTP_200_OK):
        issue = self.get_queryset().get(pk=issue.pk)
        return Response(
            IssueDetailSerializer(issue, context=self.get_serializer_context()).data,
            status=status_code,
        )

    # actions -------------------------------------------------------------
    def create(self, request, *args, **kwargs):
        serializer = IssueCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        files = request.FILES.getlist("files")
        cleaned = validate_uploads(files) if files else []
        tester = self.tester
        acting = request.user if request.user.pk != tester.pk else None
        role_source = acting or tester
        with transaction.atomic():
            issue = serializer.save(
                reporter=tester,
                acting_as=acting,
                reporter_role=getattr(role_source, "primary_role", "") or "",
                deploy_tier=deploy_tier(),
                user_agent=(
                    serializer.validated_data.get("user_agent")
                    or request.META.get("HTTP_USER_AGENT", "")
                )[:500],
            )
            for clean, ctype, kind, original in cleaned:
                IssueAttachment.objects.create(
                    issue=issue,
                    file=clean,
                    original_name=os.path.basename(original)[:255],
                    content_type=ctype,
                    size=clean.size or 0,
                    kind=kind,
                    uploaded_by=tester,
                )
        transaction.on_commit(lambda: notify_new_issue(issue))
        return self._detail(issue, status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        issue = self.get_object()
        if not self.triager:
            if issue.status != Issue.Status.NEW:
                return Response(
                    {"detail": _("Reports can only be edited while they are new.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        serializer_cls = self.get_serializer_class()
        serializer = serializer_cls(issue, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        old_status = issue.status
        issue = serializer.save()
        if issue.status != old_status:
            IssueComment.objects.create(
                issue=issue,
                author=self.tester,
                body=f"Status: {old_status} → {issue.status}",
                is_system=True,
            )
            notify_status_change(issue, old_status, self.tester)
        return self._detail(issue)

    def update(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        """Reporter (or triager) confirms a fix or reopens the report."""
        issue = self.get_object()
        if not (self.triager or issue.reporter_id == self.tester.pk):
            raise Http404
        if issue.status != Issue.Status.FIXED:
            return Response(
                {"detail": _("Only fixed reports can be verified or reopened.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        result = str(request.data.get("result") or "")
        note = str(request.data.get("comment") or "").strip()[:10000]
        if result not in ("verified", "reopen"):
            return Response({"result": [_("Choose verified or reopen.")]}, status=400)
        if result == "reopen" and not note:
            return Response(
                {"comment": [_("Explain what is still wrong.")]}, status=400
            )
        old_status = issue.status
        issue.status = (
            Issue.Status.VERIFIED if result == "verified" else Issue.Status.TRIAGED
        )
        issue.save(update_fields=["status", "updated_at"])
        IssueComment.objects.create(
            issue=issue,
            author=self.tester,
            body=f"Status: {old_status} → {issue.status}",
            is_system=True,
        )
        if note:
            IssueComment.objects.create(issue=issue, author=self.tester, body=note)
        if result == "reopen":
            transaction.on_commit(lambda: notify_reopened(issue, self.tester))
        return self._detail(issue)

    @action(detail=True, methods=["post"])
    def comments(self, request, pk=None):
        issue = self.get_object()
        serializer = IssueCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        body = (serializer.validated_data.get("body") or "").strip()[:10000]
        if not body:
            return Response({"body": [_("Comment cannot be empty.")]}, status=400)
        internal = bool(serializer.validated_data.get("is_internal")) and self.triager
        comment = IssueComment.objects.create(
            issue=issue, author=self.tester, body=body, is_internal=internal
        )
        return Response(IssueCommentSerializer(comment).data, status=201)

    @action(detail=True, methods=["post"])
    def attachments(self, request, pk=None):
        issue = self.get_object()
        files = request.FILES.getlist("files")
        if not files:
            return Response({"files": [_("Choose at least one file.")]}, status=400)
        existing = issue.attachments.count()
        limit = getattr(settings, "QA_MAX_ATTACHMENTS", 5)
        if existing + len(files) > limit:
            return Response(
                {"files": [_("You can attach up to %(n)d files.") % {"n": limit}]},
                status=400,
            )
        created = []
        for clean, ctype, kind, original in validate_uploads(files):
            created.append(
                IssueAttachment.objects.create(
                    issue=issue,
                    file=clean,
                    original_name=os.path.basename(original)[:255],
                    content_type=ctype,
                    size=clean.size or 0,
                    kind=kind,
                    uploaded_by=self.tester,
                )
            )
        return Response(IssueAttachmentSerializer(created, many=True).data, status=201)

    @action(
        detail=True,
        methods=["get"],
        url_path=r"attachments/(?P<attachment_id>[0-9a-f-]+)/download",
    )
    def download(self, request, pk=None, attachment_id=None):
        issue = self.get_object()
        att = get_object_or_404(IssueAttachment, pk=attachment_id, issue=issue)
        try:
            handle = att.file.open("rb")
        except FileNotFoundError as exc:
            raise Http404 from exc
        ctype = (
            att.content_type
            or mimetypes.guess_type(att.file.name)[0]
            or "application/octet-stream"
        )
        response = FileResponse(handle, content_type=ctype)
        inline = ctype.startswith(("image/", "video/"))
        safe_name = (att.original_name or os.path.basename(att.file.name)).replace(
            '"', ""
        )
        response["Content-Disposition"] = (
            f'{"inline" if inline else "attachment"}; filename="{safe_name}"'
        )
        response["X-Content-Type-Options"] = "nosniff"
        response["Cache-Control"] = "private, no-store"
        response["Content-Security-Policy"] = (
            "default-src 'none'; img-src 'self'; media-src 'self'; sandbox"
        )
        return response
