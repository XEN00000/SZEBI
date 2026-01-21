from django.contrib import admin
from django import forms
from .models import SimulationConfig, WeatherConfig, DeviceConfig

class WeatherConfigForm(forms.ModelForm):
    class Meta:
        model = WeatherConfig
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ogranicz outside_ref do pogod z tej samej symulacji i typu outside
        if self.instance and self.instance.simulation_id:
            qs = WeatherConfig.objects.filter(
                simulation_id=self.instance.simulation_id,
                type=WeatherConfig.TYPE_OUTSIDE
            )
            self.fields["outside_ref"].queryset = qs


class DeviceConfigForm(forms.ModelForm):
    class Meta:
        model = DeviceConfig
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ogranicz weather_ref do pogod z tej samej symulacji
        if self.instance and self.instance.simulation_id:
            self.fields["weather_ref"].queryset = WeatherConfig.objects.filter(
                simulation_id=self.instance.simulation_id
            )

@admin.register(SimulationConfig)
class SimulationConfigAdmin(admin.ModelAdmin):
    list_display = ("name", "base_millis_per_tick", "simulated_millis_per_tick", "created_at")
    search_fields = ("name",)

@admin.register(WeatherConfig)
class WeatherConfigAdmin(admin.ModelAdmin):
    form = WeatherConfigForm
    list_display = ("name", "type", "simulation", "outside_ref")
    list_filter = ("type", "simulation")
    search_fields = ("name",)

@admin.register(DeviceConfig)
class DeviceConfigAdmin(admin.ModelAdmin):
    form = DeviceConfigForm
    list_display = ("name", "type", "simulation", "weather_ref", "is_active")
    list_filter = ("type", "simulation", "is_active")
    search_fields = ("name",)