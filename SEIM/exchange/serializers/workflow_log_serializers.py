from rest_framework import serializers
from SEIM.exchange.models.applications.timeline import WorkflowLog

class WorkflowLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowLog
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
