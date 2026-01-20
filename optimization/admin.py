from django.contrib import admin
from .models import OptimizationRule, UserPreference

@admin.register(OptimizationRule)
class OptimizationRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority', 'is_active', 'condition', 'action')
    list_filter = ('is_active', 'priority')

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('device', 'target_value')