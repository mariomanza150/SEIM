"""
Document Type serializers for the exchange application.

Handles serialization for document type definitions and management.
"""

from rest_framework import serializers
from ...models import DocumentType
from ..base import TimestampedModelSerializer


class DocumentTypeSerializer(TimestampedModelSerializer):
    """
    Serializer for DocumentType model.
    """
    
    required_for_stage_display = serializers.CharField(
        source='get_required_for_stage_display', 
        read_only=True
    )
    
    class Meta:
        model = DocumentType
        fields = '__all__'
    
    def validate_name(self, value):
        """Validate document type name."""
        if not value or not value.strip():
            raise serializers.ValidationError("Document type name cannot be empty")
        
        # Check for duplicate names (excluding current instance if updating)
        qs = DocumentType.objects.filter(name__iexact=value.strip())
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise serializers.ValidationError("Document type name must be unique")
        
        return value.strip()


class DocumentTypeListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing document types.
    """
    
    required_for_stage_display = serializers.CharField(
        source='get_required_for_stage_display', 
        read_only=True
    )
    
    class Meta:
        model = DocumentType
        fields = [
            'id', 'name', 'description', 'required_for_stage', 
            'required_for_stage_display'
        ]


class DocumentTypeCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating document types.
    """
    
    class Meta:
        model = DocumentType
        fields = ['name', 'description', 'required_for_stage', 'upload_instructions']
    
    def validate_name(self, value):
        """Validate document type name."""
        if not value or not value.strip():
            raise serializers.ValidationError("Document type name cannot be empty")
        
        # Check for duplicate names
        if DocumentType.objects.filter(name__iexact=value.strip()).exists():
            raise serializers.ValidationError("Document type name must be unique")
        
        return value.strip()


class DocumentTypeUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating document types.
    """
    
    class Meta:
        model = DocumentType
        fields = ['name', 'description', 'required_for_stage', 'upload_instructions']
    
    def validate_name(self, value):
        """Validate document type name for uniqueness."""
        if not value or not value.strip():
            raise serializers.ValidationError("Document type name cannot be empty")
        
        # Check for duplicate names excluding current instance
        qs = DocumentType.objects.filter(name__iexact=value.strip())
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise serializers.ValidationError("Document type name must be unique")
        
        return value.strip()


class DocumentTypeByStageSerializer(serializers.Serializer):
    """
    Serializer for grouping document types by stage.
    """
    
    stage = serializers.CharField(read_only=True)
    stage_display = serializers.CharField(read_only=True)
    document_types = DocumentTypeListSerializer(many=True, read_only=True)
    total_count = serializers.IntegerField(read_only=True)


class DocumentTypeBulkSerializer(serializers.Serializer):
    """
    Serializer for bulk operations on document types.
    """
    
    document_types = serializers.ListField(
        child=DocumentTypeCreateSerializer(),
        min_length=1,
        help_text="List of document types to create"
    )
    
    def create(self, validated_data):
        """Create multiple document types."""
        document_types_data = validated_data['document_types']
        
        # Check for duplicate names in the batch
        names = [doc_type['name'] for doc_type in document_types_data]
        if len(names) != len(set(name.lower() for name in names)):
            raise serializers.ValidationError("Duplicate document type names in batch")
        
        # Check for existing names
        existing_names = DocumentType.objects.filter(
            name__iexact__in=names
        ).values_list('name', flat=True)
        
        if existing_names:
            raise serializers.ValidationError(
                f"Document type names already exist: {list(existing_names)}"
            )
        
        # Create document types
        document_types = []
        for doc_type_data in document_types_data:
            doc_type = DocumentType(**doc_type_data)
            document_types.append(doc_type)
        
        return DocumentType.objects.bulk_create(document_types)


class DocumentTypeUsageSerializer(serializers.Serializer):
    """
    Serializer for document type usage statistics.
    """
    
    document_type_id = serializers.IntegerField(read_only=True)
    document_type_name = serializers.CharField(read_only=True)
    required_for_stage = serializers.CharField(read_only=True)
    usage_count = serializers.IntegerField(read_only=True)
    percentage = serializers.FloatField(read_only=True)
    can_delete = serializers.BooleanField(read_only=True)


class DocumentTypeRequirementsSerializer(serializers.Serializer):
    """
    Serializer for document type requirements by exchange program.
    """
    
    exchange_program_id = serializers.IntegerField()
    required_document_types = DocumentTypeListSerializer(many=True, read_only=True)
    optional_document_types = DocumentTypeListSerializer(many=True, read_only=True)
    
    def validate_exchange_program_id(self, value):
        """Validate exchange program exists."""
        from ...models import ExchangeProgram
        try:
            ExchangeProgram.objects.get(id=value)
        except ExchangeProgram.DoesNotExist:
            raise serializers.ValidationError("Invalid exchange program ID")
        return value


class DocumentTypeValidationSerializer(serializers.Serializer):
    """
    Serializer for validating document type completeness for an exchange.
    """
    
    exchange_id = serializers.IntegerField()
    stage = serializers.ChoiceField(
        choices=DocumentType.DocumentStage.choices,
        required=False,
        help_text="Stage to validate for (defaults to current exchange stage)"
    )
    
    def validate_exchange_id(self, value):
        """Validate exchange exists and user has access."""
        from ...models import Exchange
        try:
            exchange = Exchange.objects.get(id=value)
        except Exchange.DoesNotExist:
            raise serializers.ValidationError("Invalid exchange ID")
        
        # Add access validation here if needed
        request = self.context.get('request')
        if request and request.user != exchange.student and not request.user.is_staff:
            raise serializers.ValidationError("Access denied to this exchange")
        
        return value
    
    def validate(self, attrs):
        """Check document type requirements compliance."""
        from ...models import Exchange, Document
        
        exchange_id = attrs['exchange_id']
        stage = attrs.get('stage')
        
        exchange = Exchange.objects.get(id=exchange_id)
        
        # Determine stage if not provided
        if not stage:
            stage = self.get_current_stage(exchange)
        
        # Get required document types for the stage
        required_doc_types = DocumentType.objects.filter(
            required_for_stage=stage
        )
        
        # Get uploaded documents for the exchange
        uploaded_docs = Document.objects.filter(
            exchange=exchange,
            status__in=['PENDING', 'APPROVED']  # Exclude rejected documents
        )
        
        # Check which document types are missing
        uploaded_categories = set(uploaded_docs.values_list('category', flat=True))
        required_categories = set(required_doc_types.values_list('name', flat=True))
        missing_categories = required_categories - uploaded_categories
        
        if missing_categories:
            missing_doc_types = DocumentType.objects.filter(name__in=missing_categories)
            missing_names = [dt.name for dt in missing_doc_types]
            raise serializers.ValidationError({
                'missing_documents': f"Missing required documents for {stage}: {', '.join(missing_names)}"
            })
        
        return attrs
    
    def get_current_stage(self, exchange):
        """Determine current stage based on exchange status."""
        # Map exchange status to document stages
        status_to_stage = {
            'DRAFT': 'APPLICATION',
            'SUBMITTED': 'APPLICATION',
            'UNDER_REVIEW': 'REVIEW',
            'APPROVED': 'ACCEPTANCE',
            'COMPLETED': 'FINALIZATION'
        }
        return status_to_stage.get(exchange.status, 'APPLICATION')


class DocumentTypeOrderingSerializer(serializers.Serializer):
    """
    Serializer for updating document type display order.
    """
    
    document_type_orders = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField()
        ),
        help_text="List of {id: order} mappings"
    )
    
    def validate_document_type_orders(self, value):
        """Validate document type IDs exist and orders are valid."""
        doc_type_ids = [item.get('id') for item in value if 'id' in item]
        
        # Check all document types exist
        existing_ids = set(
            DocumentType.objects.filter(id__in=doc_type_ids).values_list('id', flat=True)
        )
        invalid_ids = set(doc_type_ids) - existing_ids
        
        if invalid_ids:
            raise serializers.ValidationError(f"Invalid document type IDs: {list(invalid_ids)}")
        
        # Check orders are positive integers
        orders = [item.get('order') for item in value if 'order' in item]
        if any(order is None or order < 0 for order in orders):
            raise serializers.ValidationError("All orders must be non-negative integers")
        
        return value
