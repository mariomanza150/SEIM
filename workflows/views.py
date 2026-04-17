import datetime
import xml.etree.ElementTree as ET

from django.db.models import Max
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import HasPermission

from .models import WorkflowDefinition, WorkflowVersion
from .serializers import WorkflowDefinitionSerializer, WorkflowVersionSerializer


class CanManageWorkflows(HasPermission):
    permission_name = "manage_workflows"


class WorkflowDefinitionViewSet(viewsets.ModelViewSet):
    queryset = WorkflowDefinition.objects.all()
    serializer_class = WorkflowDefinitionSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageWorkflows]

    @action(detail=True, methods=["get", "post"], url_path="versions")
    def versions(self, request, pk=None):
        definition = self.get_object()
        if request.method == "GET":
            qs = definition.versions.order_by("-version")
            return Response(WorkflowVersionSerializer(qs, many=True).data)

        # POST: create new draft version
        bpmn_xml = request.data.get("bpmn_xml")
        if not isinstance(bpmn_xml, str) or not bpmn_xml.strip():
            return Response({"bpmn_xml": "This field is required."}, status=400)
        next_version = (
            definition.versions.aggregate(m=Max("version")).get("m") or 0
        ) + 1
        v = WorkflowVersion.objects.create(
            definition=definition,
            version=next_version,
            status=WorkflowVersion.Status.DRAFT,
            bpmn_xml=bpmn_xml,
            created_by=request.user,
        )
        return Response(WorkflowVersionSerializer(v).data, status=status.HTTP_201_CREATED)


class WorkflowVersionViewSet(viewsets.ModelViewSet):
    queryset = WorkflowVersion.objects.select_related("definition").all()
    serializer_class = WorkflowVersionSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageWorkflows]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="validate")
    def validate_bpmn(self, request, pk=None):
        """
        Minimal BPMN validation: require parseable XML and a BPMN definitions root.
        Runtime engine validation is added later.
        """
        obj = self.get_object()
        raw = obj.bpmn_xml or ""
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as exc:
            return Response({"valid": False, "error": str(exc)}, status=400)
        tag = root.tag.lower()
        if "definitions" not in tag:
            return Response(
                {"valid": False, "error": "Root element must be <definitions>."},
                status=400,
            )
        return Response({"valid": True})

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        obj = self.get_object()
        if obj.status == WorkflowVersion.Status.PUBLISHED:
            return Response(WorkflowVersionSerializer(obj).data)
        obj.status = WorkflowVersion.Status.PUBLISHED
        obj.published_at = timezone.now()
        obj.save(update_fields=["status", "published_at", "updated_at"])
        return Response(WorkflowVersionSerializer(obj).data)

