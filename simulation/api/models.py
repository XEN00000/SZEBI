from uuid import uuid4

from django.db import models
from django.utils import timezone


class SimulationRun(models.Model):
    
    name = models.CharField(max_length=80, default="default-simulation")
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    start_datetime = models.DateTimeField(default=timezone.now)
    base_millis_per_tick = models.PositiveIntegerField(default=15 * 60 * 1000)
    simulated_millis_per_tick = models.PositiveIntegerField(default=15 * 60 * 1000)
    current_tick = models.PositiveBigIntegerField(default=0)
    is_running = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Simulation {self.name} @ tick {self.current_tick}"


class Environment(models.Model):
    ENV_TYPE_CHOICES = (
        ("inside", "Inside"),
        ("outside", "Outside"),
    )

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    simulation = models.ForeignKey(
        SimulationRun, related_name="environments", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=80)
    env_type = models.CharField(max_length=10, choices=ENV_TYPE_CHOICES, default="outside")
    declared_usage = models.FloatField(default=0.0, help_text="kWh declared in current tick")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["simulation", "name"],
                name="unique_environment_name_per_simulation",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.env_type})"


class Device(models.Model):

    DEVICE_CLASS_CHOICES = (
        ("energy_source", "Energy source"),
        ("smart_device", "Smart device"),
        ("grid", "Grid"),
        ("storage", "Storage"),
    )

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    environment = models.ForeignKey(
        Environment, related_name="devices", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=80)
    device_class = models.CharField(max_length=20, choices=DEVICE_CLASS_CHOICES)
    subtype = models.CharField(max_length=40, help_text="Concrete logic class name")
    is_active = models.BooleanField(default=False)
    config = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["environment", "name"],
                name="unique_device_name_per_environment",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} [{self.subtype}]"


class SmartDevice(Device):

    power_usage_watt = models.FloatField(default=0.0)
    level = models.FloatField(default=0.0)

    class Meta:
        verbose_name = "Smart device"
        verbose_name_plural = "Smart devices"


class AirConditioning(SmartDevice):
    is_cooling = models.BooleanField(default=False)


class Heating(SmartDevice):
    is_heating = models.BooleanField(default=False)


class Lighting(SmartDevice):
    is_on = models.BooleanField(default=False)


class EnergySource(Device):

    class Meta:
        verbose_name = "Energy source"
        verbose_name_plural = "Energy sources"


class ElectricGrid(EnergySource):
    price_per_kwh = models.DecimalField(max_digits=8, decimal_places=4, default=0.0)


class EnergyStorage(EnergySource):
    capacity_kwh = models.FloatField(default=0.0)
    charge_kwh = models.FloatField(default=0.0)
    max_charge_kw = models.FloatField(default=0.0)
    max_discharge_kw = models.FloatField(default=0.0)


class PhotoVoltaic(EnergySource):
    peak_power_watt = models.FloatField(default=0.0)


class WindTurbine(EnergySource):
    rated_power_watt = models.FloatField(default=0.0)
    rated_speed = models.FloatField(default=12.0)


class WeatherSnapshot(models.Model):

    WEATHER_TYPE_CHOICES = (
        ("inside", "Inside"),
        ("outside", "Outside"),
    )

    environment = models.ForeignKey(
        Environment, related_name="weather_history", on_delete=models.CASCADE
    )
    recorded_at = models.DateTimeField(default=timezone.now)
    weather_type = models.CharField(max_length=10, choices=WEATHER_TYPE_CHOICES)

    sunlight = models.FloatField(default=0.0)
    brightness = models.FloatField(default=0.0)
    cloudiness = models.FloatField(default=0.0)
    rainfall = models.FloatField(default=0.0)
    wind = models.FloatField(default=0.0)
    temperature = models.FloatField(default=0.0)
    isolation = models.FloatField(default=0.0)
    curr_heating_power = models.FloatField(default=0.0)
    curr_lighting_power = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self) -> str:
        return f"{self.environment.name} @ {self.recorded_at.isoformat()}"


class SimulationState(models.Model):
    current_sim_time = models.DateTimeField(default=timezone.now)
    is_running = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_state(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return f"Simulation: {self.current_sim_time.strftime('%Y-%m-%d %H:%M')}"


class EnergyTariff(models.Model):

    name = models.CharField(max_length=50)
    price_per_kwh = models.DecimalField(max_digits=6, decimal_places=4)
    start_hour = models.IntegerField(default=0)
    end_hour = models.IntegerField(default=23)

    def __str__(self):
        return f"{self.name} ({self.price_per_kwh} PLN)"