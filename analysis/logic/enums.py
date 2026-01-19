from django.db import models


class ReportType(models.TextChoices):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    SEASONAL = "SEASONAL"
    SEMIANNUAL = "SEMIANNUAL"
    ANNUAL = "ANNUAL"


class MeasurementUnit(models.TextChoices):
    CELSIUS = "celsius"
    FAHRENHEIT = "fahrenheit"
    PERCENT = "percent"
    KILOWATT_HOUR = "kilowatt-hour"
    WATT = "watt"
    NONE = "none"


class Measurement(models.TextChoices):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    ENERGY = "energy"
    POWER = "power"
    VOLTAGE = "voltage"