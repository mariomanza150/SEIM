"""
Bulk action serializers for the exchange application.

Handles serialization for bulk operations and their logging.
"""

from rest_framework import serializers
from ...models import BulkAction, BulkActionItem, BulkActionLog
from .base import BaseSerializer, UserSerializer


class BulkActionSerializer(BaseSerializer):
    """
    Serializer for BulkAction model.
    """
    
    created_by = UserSerializer(read_only=True)
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = BulkAction
        fields = '__all__'
        read_only_fields = [
            'id', 'created_by', 'created_at', 'updated_at', 
            'started_at', 'completed_at'
        ]
    
    def create(self, validated_data):
        """Create bulk action with current user as creator."""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class BulkActionItemSerializer(BaseSerializer):
    """
    Serializer for BulkActionItem model.
    """
    
    bulk_action = BulkActionSerializer(read_only=True)
    exchange = serializers.PrimaryKeyRelatedField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = BulkActionItem
        fields = '__all__'
        read_only_fields = ['id', 'processed_at']


class BulkActionLogSerializer(BaseSerializer):
    """
    Serializer for BulkActionLog model.
    """
    
    bulk_action = BulkActionSerializer(read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    
    class Meta:
        model = BulkActionLog
        fields = '__all__'
        read_only_fields = ['id', 'timestamp']
