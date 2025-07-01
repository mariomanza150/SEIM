"""
Document serializers for the exchange application.

Handles serialization for document uploads, validation, and verification workflows.
"""

from rest_framework import serializers
from ...models import Document, DocumentType
from ..base import TimestampedModelSerializer, UserSerializer


class DocumentTypeSerializer(TimestampedModelSerializer):
    """
    Serializer for DocumentType model.
    """
    
    class Meta:
        model = DocumentType
        fields = '__all__'


class DocumentSerializer(TimestampedModelSerializer):
    """
    Comprehensive serializer for Document model.
    """
    
    exchange = serializers.PrimaryKeyRelatedField(read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    verified_by = UserSerializer(read_only=True)
    supersedes = serializers.PrimaryKeyRelatedField(read_only=True)
    superseded_by = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    # File metadata
    filename = serializers.SerializerMethodField()
    file_extension = serializers.SerializerMethodField() 
    human_readable_size = serializers.SerializerMethodField()
    
    # Status checks
    is_pending = serializers.BooleanField(read_only=True)
    is_approved = serializers.BooleanField(read_only=True)
    is_rejected = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = [
            'id', 'exchange', 'file_size', 'file_hash', 'verified', 
            'verified_by', 'verified_at', 'uploaded_at', 'updated_at'
        ]
    
    def get_filename(self, obj):
        """Get filename from file field."""
        return obj.get_filename() if hasattr(obj, 'get_filename') else ''
    
    def get_file_extension(self, obj):
        """Get file extension."""
        return obj.get_file_extension() if hasattr(obj, 'get_file_extension') else ''
    
    def get_human_readable_size(self, obj):
        """Get human readable file size."""
        return obj.get_human_readable_size() if hasattr(obj, 'get_human_readable_size') else ''


class DocumentUploadSerializer(serializers.ModelSerializer):
    """
    Serializer for document upload operations.
    """
    
    class Meta:
        model = Document
        fields = [
            'title', 'description', 'category', 'file'
        ]
    
    def validate_file(self, value):
        """Validate uploaded file."""
        if not value:
            raise serializers.ValidationError("File is required")
        
        # File size validation (e.g., max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError("File size cannot exceed 10MB")
        
        # File type validation
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
        file_extension = value.name.split('.')[-1].lower()
        if f'.{file_extension}' not in allowed_extensions:
            raise serializers.ValidationError(
                f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        return value
    
    def create(self, validated_data):
        """Create document with metadata extraction."""
        file_obj = validated_data.get('file')
        if file_obj:
            validated_data['file_size'] = file_obj.size
            # File hash calculation would be done in model save method
        
        # Exchange should be set from context
        validated_data['exchange'] = self.context['exchange']
        
        return super().create(validated_data)


class DocumentVerificationSerializer(serializers.Serializer):
    """
    Serializer for document verification workflow.
    """
    
    action = serializers.ChoiceField(
        choices=['approve', 'reject'],
        required=True,
        help_text="Action to take on the document"
    )
    comments = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Verification comments"
    )
    
    def validate(self, attrs):
        """Validate verification data."""
        if attrs['action'] == 'reject' and not attrs.get('comments'):
            raise serializers.ValidationError({
                'comments': 'Comments are required when rejecting a document'
            })
        return attrs


class DocumentReplaceSerializer(serializers.Serializer):
    """
    Serializer for replacing an existing document.
    """
    
    new_file = serializers.FileField(required=True)
    reason = serializers.CharField(
        required=True,
        help_text="Reason for replacing the document"
    )
    
    def validate_new_file(self, value):
        """Validate the replacement file."""
        # Reuse validation from DocumentUploadSerializer
        upload_serializer = DocumentUploadSerializer()
        return upload_serializer.validate_file(value)


class DocumentListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing documents.
    """
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    filename = serializers.SerializerMethodField()
    human_readable_size = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'category', 'category_display', 'status', 
            'status_display', 'filename', 'file_size', 'human_readable_size',
            'uploaded_at', 'verified'
        ]
    
    def get_filename(self, obj):
        """Get filename from file field."""
        return obj.get_filename() if hasattr(obj, 'get_filename') else ''
    
    def get_human_readable_size(self, obj):
        """Get human readable file size."""
        return obj.get_human_readable_size() if hasattr(obj, 'get_human_readable_size') else ''
