from django.db import models
from django.utils import timezone
from .enumeration_models import (
    DataLogLevel,
    SensorStatus,
    MeasurementStatus
)


class DataLog(models.Model):
    id = models.AutoField(primary_key=True, db_column="log_id")
    measurement = models.ForeignKey(
        'Measurement',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    message = models.TextField()
    level = models.CharField(max_length=15, choices=DataLogLevel.choices, default=DataLogLevel.INFO)
    # nie ma w schemacie ale by się przydało
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['level']),
        ]

    def __str__(self):
        return f"[{self.level}] {self.message[:50]}..."

class Location(models.Model):
    id = models.AutoField(primary_key=True, db_column="location_id")

    # =======================================
    # TYMCZASOWO room TO UUID WYSYŁANE PRZEZ SYMULACJE
    # =======================================
    floor = models.IntegerField(null=True, blank=True)
    room = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["room"]),
        ]

    def __str__(self):
        if self.floor is not None:
            return f"{self.room} (floor {self.floor})"
        return self.room

class SensorType(models.Model):
    id = models.AutoField(primary_key=True, db_column="type_id")
    name = models.CharField(max_length=100)
    default_unit = models.CharField(max_length=20)
    min_value = models.FloatField(null=True)
    max_value = models.FloatField(null=True)

    def __str__(self):
        return f"{self.name} ({self.default_unit})"

class Sensor(models.Model):
    type = models.ForeignKey(SensorType, on_delete=models.PROTECT)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    id = models.AutoField(primary_key=True, db_column="sensor_id")
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=15, choices=SensorStatus.choices, default=SensorStatus.ACTIVE)
    installation_date = models.DateTimeField(default=timezone.now)
    last_communication = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["last_communication"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.type.name}, {self.location.room})"


class Measurement(models.Model):
    id = models.AutoField(primary_key=True, db_column="measurement_id")
    sensor = models.ForeignKey(Sensor, on_delete=models.PROTECT)
    timestamp = models.DateTimeField()
    value = models.FloatField()
    status = models.CharField(max_length=15, choices=MeasurementStatus.choices, default=MeasurementStatus.OK)

    class Meta:
        unique_together = ('sensor', 'timestamp')

    def __str__(self):
        return f"{self.sensor} at {self.timestamp} ({self.value} / {self.status})"

