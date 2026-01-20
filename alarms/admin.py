# from django.contrib import admin
# from .models import Alarm


# @admin.register(Alarm)
# class AlarmAdmin(admin.ModelAdmin):
#     list_display = ('level', 'created_at', 'acknowledged')


from django.contrib import admin
from .models import (
    Alert,
    AlertRule,
    AlertComment,
    NotificationLog,
    NotificationGroup,
    ChannelType
)


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'priority',
                    'timestamp_generated', 'acknowledged_by']
    list_filter = ['status', 'priority', 'timestamp_generated']
    search_fields = ['id']
    readonly_fields = ['timestamp_generated']


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'target_metric', 'operator', 'priority']
    list_filter = ['priority', 'operator']
    search_fields = ['name', 'target_metric']


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'alert',
                    'channel', 'status', 'timestamp_sent']
    list_filter = ['status', 'channel', 'timestamp_sent']
    readonly_fields = ['timestamp_sent']


@admin.register(NotificationGroup)
class NotificationGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']
