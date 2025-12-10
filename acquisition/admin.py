from django.contrib import admin
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import path


from .models import (
    DataLog, Location, Sensor, SensorType, Measurement, 
    AcquisitionControl 
)
from . import mqtt_runner

@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ('id', 'sensor', 'value', 'status', 'timestamp')
    list_filter = (
        'status',
        'sensor__location__room',
        'sensor__type__name'
    )
    date_hierarchy = 'timestamp'
    search_fields = ('sensor__name', 'sensor__location__room')


@admin.register(DataLog)
class DataLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'level', 'message', 'measurement')
    list_filter = ('level', 'timestamp')
    date_hierarchy = 'timestamp'
    search_fields = ('message',)


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'type', 'location', 'last_communication')
    list_filter = ('status', 'type__name', 'location__room')
    search_fields = ('name', 'location__room')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'floor')
    list_filter = ('floor',)
    search_fields = ('room',)

@admin.register(SensorType)
class SensorTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_unit', 'min_value', 'max_value')
    search_fields = ('name', 'default_unit')

@admin.register(AcquisitionControl)
class AcquisitionControlAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False 
        
    def has_delete_permission(self, request, obj=None):
        return False 

    def has_change_permission(self, request, obj=None):
        return False 

    def changelist_view(self, request, extra_context=None):
        if request.method == "POST":
            action = request.POST.get("action")
            
            if action == "start":
                msg = mqtt_runner.start_mqtt_worker()
                self.message_user(request, msg, level=messages.SUCCESS)
            elif action == "stop":
                msg = mqtt_runner.stop_mqtt_worker()
                self.message_user(request, msg, level=messages.WARNING)
                
            return redirect(request.path)

        status = "Działa (ON)" if mqtt_runner.is_running() else "Zatrzymany (OFF)"
        status_color = "green" if mqtt_runner.is_running() else "red"

        context = {
            'title': 'Panel Sterowania Akwizycją',
            'status': status,
            'status_color': status_color,
            **self.admin_site.each_context(request),
        }
        
        return render(request, 'admin/acquisition/control_panel.html', context)