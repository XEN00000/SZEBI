from rest_framework import serializers
from .models import Alert, AlertRule, AlertComment
from core.models import User


class AlertRuleSerializer(serializers.ModelSerializer):
    """Serializer dla reguł alarmów"""

    class Meta:
        model = AlertRule
        fields = [
            'id',
            'name',
            'target_metric',
            'operator',
            'threshold_min',
            'threshold_max',
            'duration_seconds',
            'priority'
        ]
        read_only_fields = ['id']


class UserSerializer(serializers.ModelSerializer):
    """Serializer dla użytkowników"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class AlertCommentSerializer(serializers.ModelSerializer):
    """Serializer dla komentarzy alarmów"""

    class Meta:
        model = AlertComment
        fields = ['text', 'timestamp']


class AlertSerializer(serializers.ModelSerializer):
    """Serializer dla alarmów"""
    alert_rule = AlertRuleSerializer(read_only=True)
    alert_comment = AlertCommentSerializer(read_only=True)
    acknowledged_by = UserSerializer(read_only=True)
    closed_by = UserSerializer(read_only=True)

    status_display = serializers.CharField(
        source='get_status_display', read_only=True)
    priority_display = serializers.CharField(
        source='get_priority_display', read_only=True)

    class Meta:
        model = Alert
        fields = [
            'id',
            'alert_rule',
            'alert_comment',
            'metric_name',
            'details',
            'triggering_value',
            'measurement_timestamp',
            'timestamp_generated',
            'timestamp_acknowledged',
            'timestamp_closed',
            'status',
            'status_display',
            'priority',
            'priority_display',
            'acknowledged_by',
            'closed_by'
        ]
        read_only_fields = [
            'id',
            'timestamp_generated',
            'timestamp_acknowledged',
            'timestamp_closed',
            'acknowledged_by',
            'closed_by'
        ]
