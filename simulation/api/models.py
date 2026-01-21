from django.db import models
import uuid

class SimulationConfig(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    # Default: 1 minute simulated time per tick, processed every 100ms real-time
    # This gives 600x speedup: 1 minute in 100ms, 1 hour in 6 seconds
    base_millis_per_tick = models.PositiveIntegerField(default=60 * 100)  # 1 minute
    simulated_millis_per_tick = models.PositiveIntegerField(default=100)  # 100ms real-time
    consumption_mode = models.CharField(max_length=50, default="normal")
    charging_mode = models.CharField(max_length=50, default="balanced")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class WeatherConfig(models.Model):
    TYPE_OUTSIDE = "outside"
    TYPE_INSIDE = "inside"
    TYPE_CHOICES = [
        (TYPE_OUTSIDE, "Outside"),
        (TYPE_INSIDE, "Inside"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    simulation = models.ForeignKey(SimulationConfig, on_delete=models.CASCADE, related_name="weathers")
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    outside_ref = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="inside_weathers")

    # Bazowe parametry (mogą być nadpisane przez logikę symulacji)
    temperature_c = models.FloatField(default=20.0)
    sunlight = models.FloatField(default=0.5)
    brightness = models.FloatField(default=0.5)
    cloudiness = models.FloatField(default=0.3)
    wind_speed = models.FloatField(default=2.0)

    extra = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class DeviceConfig(models.Model):
    TYPE_LIGHTING = "lighting"
    TYPE_AC = "airconditioning"
    TYPE_PV = "photovoltaic"
    TYPE_STORAGE = "energystorage"
    TYPE_GRID = "electricgrid"
    TYPE_HEATING = "heating"
    TYPE_WINDTURBINE = "windturbine"
    TYPE_CHOICES = [
        (TYPE_LIGHTING, "Lighting"),
        (TYPE_AC, "Air Conditioning"),
        (TYPE_PV, "Photovoltaic"),
        (TYPE_STORAGE, "Energy Storage"),
        (TYPE_GRID, "Electric Grid"),
        (TYPE_HEATING, "Heating System"),
        (TYPE_WINDTURBINE, "Wind Turbine"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    simulation = models.ForeignKey(SimulationConfig, on_delete=models.CASCADE, related_name="devices")
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    weather_ref = models.ForeignKey(WeatherConfig, on_delete=models.CASCADE, related_name="devices")

    is_active = models.BooleanField(default=True)
    initial_level = models.FloatField(null=True, blank=True)  # np. 0..1 dla dimmera/AC
    initial_is_on = models.BooleanField(default=True)

    # Uniwersalne parametry mocy/energii (używane zależnie od typu)
    power_watts = models.FloatField(null=True, blank=True)          # lighting/AC
    light_output = models.FloatField(null=True, blank=True)         # lighting
    cooling_power = models.FloatField(null=True, blank=True)        # AC
    peak_power = models.FloatField(null=True, blank=True)           # PV
    capacity_wh = models.FloatField(null=True, blank=True)          # storage
    max_charge_w = models.FloatField(null=True, blank=True)         # storage
    max_discharge_w = models.FloatField(null=True, blank=True)      # storage

    extra = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"