from rest_framework import serializers
from simulation.models import Device
from optimization.models import OptimizationRule, UserPreference

class ExternalAlarmSerializer(serializers.Serializer):
    """
    Serializer pasujący do formatu danych z modułu Alarmów.
    """
    id = serializers.IntegerField()
    status = serializers.CharField()
    priority = serializers.CharField()      
    triggering_value = serializers.FloatField()
    timestamp_generated = serializers.DateTimeField()
    rule_name = serializers.CharField(required=False, allow_null=True)
    rule_metric = serializers.CharField(required=False, allow_null=True)


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['id', 'name', 'device_type', 'is_active', 'nominal_power']

class OptimizationResultSerializer(serializers.Serializer):
    status = serializers.CharField()
    processed_devices = serializers.IntegerField()
    message = serializers.CharField()

class OptimizationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptimizationRule
        fields = '__all__'

class UserPreferenceSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    class Meta:
        model = UserPreference
        fields = ['id', 'device', 'device_name', 'target_value', 'schedule']