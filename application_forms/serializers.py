"""
Application Forms Serializers

DRF serializers for FormType and FormSubmission models.
"""

from rest_framework import serializers

from .models import FormSubmission, FormType


class FormTypeSerializer(serializers.ModelSerializer):
    """Serializer for FormType model"""

    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True
    )
    field_count = serializers.IntegerField(
        source='get_field_count',
        read_only=True
    )
    required_fields = serializers.ListField(
        source='get_required_fields',
        read_only=True
    )

    class Meta:
        model = FormType
        fields = [
            'id', 'name', 'form_type', 'description', 'schema', 'ui_schema',
            'is_active', 'created_by', 'created_by_username', 'created_at',
            'updated_at', 'field_count', 'required_fields'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def validate_schema(self, value):
        """Validate that schema is a valid dict"""
        if value and not isinstance(value, dict):
            raise serializers.ValidationError('Schema must be a valid JSON object')
        return value

    def validate_ui_schema(self, value):
        """Validate that ui_schema is a valid dict"""
        if value and not isinstance(value, dict):
            raise serializers.ValidationError('UI Schema must be a valid JSON object')
        return value


class FormSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for FormSubmission model"""

    form_type_name = serializers.CharField(
        source='form_type.name',
        read_only=True
    )
    submitted_by_username = serializers.CharField(
        source='submitted_by.username',
        read_only=True
    )
    program_name = serializers.CharField(
        source='program.name',
        read_only=True,
        allow_null=True
    )
    response_count = serializers.IntegerField(
        source='get_response_count',
        read_only=True
    )

    class Meta:
        model = FormSubmission
        fields = [
            'id', 'form_type', 'form_type_name', 'submitted_by',
            'submitted_by_username', 'responses', 'submitted_at', 'updated_at',
            'program', 'program_name', 'application', 'response_count'
        ]
        read_only_fields = ['id', 'submitted_by', 'submitted_at', 'updated_at']

    def validate_responses(self, value):
        """Validate that responses is a valid dict"""
        if value and not isinstance(value, dict):
            raise serializers.ValidationError('Responses must be a valid JSON object')
        return value

    def validate(self, data):
        """Validate that required fields are present in responses"""
        form_type = data.get('form_type')
        responses = data.get('responses', {})

        if form_type and form_type.schema:
            required_fields = form_type.get_required_fields()
            missing_fields = [field for field in required_fields if field not in responses]
            if missing_fields:
                raise serializers.ValidationError({
                    'responses': f'Missing required fields: {", ".join(missing_fields)}'
                })

        return data

    def create(self, validated_data):
        """Auto-assign submitted_by from request user"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['submitted_by'] = request.user
        return super().create(validated_data)


class FormTypeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for FormType lists"""

    field_count = serializers.IntegerField(
        source='get_field_count',
        read_only=True
    )

    class Meta:
        model = FormType
        fields = ['id', 'name', 'form_type', 'description', 'is_active', 'field_count', 'created_at']
        read_only_fields = fields


class FormSubmissionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for FormSubmission lists"""

    form_type_name = serializers.CharField(
        source='form_type.name',
        read_only=True
    )
    submitted_by_username = serializers.CharField(
        source='submitted_by.username',
        read_only=True
    )

    class Meta:
        model = FormSubmission
        fields = ['id', 'form_type_name', 'submitted_by_username', 'submitted_at', 'program', 'application']
        read_only_fields = fields

