from django.contrib import admin
from .models import OptimizationRule, UserPreference, OptimizationLog

@admin.register(OptimizationRule)
class OptimizationRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority', 'is_active', 'action')
    list_filter = ('is_active', 'priority')

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('device', 'target_value')

@admin.register(OptimizationLog)
class OptimizationLogAdmin(admin.ModelAdmin):
    list_display = ('status', 'action', 'affected_devices_count', 'timestamp')
    list_filter = ('status', 'timestamp')
    readonly_fields = ('timestamp',)