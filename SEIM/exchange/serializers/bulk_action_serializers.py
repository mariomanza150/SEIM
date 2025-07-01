from rest_framework import serializers
from SEIM.exchange.models.tracking.bulk_action import BulkAction

class BulkActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulkAction
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
