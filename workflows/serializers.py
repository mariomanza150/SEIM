from rest_framework import serializers

from .models import WorkflowDefinition, WorkflowInstance, WorkflowVersion


class WorkflowVersionSerializer(serializers.ModelSerializer):
    definition_slug = serializers.CharField(source="definition.slug", read_only=True)
    definition_name = serializers.CharField(source="definition.name", read_only=True)

    class Meta:
        model = WorkflowVersion
        fields = [
            "id",
            "definition",
            "definition_slug",
            "definition_name",
            "version",
            "status",
            "bpmn_xml",
            "created_by",
            "published_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "published_at", "created_at", "updated_at"]


class WorkflowDefinitionSerializer(serializers.ModelSerializer):
    latest_published_version = serializers.SerializerMethodField()

    class Meta:
        model = WorkflowDefinition
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "is_active",
            "latest_published_version",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

    def get_latest_published_version(self, obj):
        v = obj.versions.filter(status=WorkflowVersion.Status.PUBLISHED).order_by("-version").first()
        if not v:
            return None
        return {"id": str(v.id), "version": v.version, "published_at": v.published_at}


class WorkflowInstanceSerializer(serializers.ModelSerializer):
    workflow_definition = serializers.CharField(source="workflow_version.definition.slug", read_only=True)
    workflow_version_number = serializers.IntegerField(source="workflow_version.version", read_only=True)

    class Meta:
        model = WorkflowInstance
        fields = [
            "id",
            "application",
            "workflow_version",
            "workflow_definition",
            "workflow_version_number",
            "engine_state",
            "current_tasks",
            "status",
            "last_event_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

