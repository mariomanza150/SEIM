from rest_framework import serializers

from core.models import InstitutionFeatureSettings


class InstitutionFeatureSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionFeatureSettings
        fields = (
            "scholarships_enabled",
            "document_version_history_enabled",
            "document_version_history_student",
            "document_version_history_coordinator",
            "document_version_history_admin",
            "updated_at",
        )
        read_only_fields = ("updated_at",)
