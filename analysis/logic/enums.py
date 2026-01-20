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
    LUX = "lux"
    LUMEN = "lumen"
    PERCENT = "percent"
    MMH = "mmh"
    MPS = "mps"
    KILOWATT_HOUR = "kilowatt-hour"
    WATT = "watt"
    VOLT = "volt"
    NONE = "none"


class Measurement(models.TextChoices):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    ENERGY = "energy"
    POWER = "power"
    VOLTAGE = "voltage"
    SUNLIGHT = "sunlight"
    BRIGHTNESS = "brightness"
    CLOUDINESS = "cloudiness"
    RAINFALL = "rainfall"
    WIND = "wind"