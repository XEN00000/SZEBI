from django.db import models

class SensorStatus(models.TextChoices):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    MAINTENANCE = "MAINTENANCE"
    FAILED = "FAILED"

class DataLogLevel(models.TextChoices):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class MeasurementStatus(models.TextChoices):
    OK = "OK"
    ERROR = "ERROR"
    DUPLICATE = "DUPLICATE"
    NULL = "NULL"