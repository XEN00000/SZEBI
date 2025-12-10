from django.contrib import admin
from .models import SimulationState, EnergyTariff, Device, WeatherData

@admin.register(SimulationState)
class SimulationStateAdmin(admin.ModelAdmin):
    list_display = ('current_sim_time', 'is_running')

@admin.register(EnergyTariff)
class EnergyTariffAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_per_kwh', 'start_hour', 'end_hour')

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'device_type', 'nominal_power', 'is_active')
    list_filter = ('device_type', 'is_active')

@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'temperature', 'cloud_cover')
    list_filter = ('timestamp',)