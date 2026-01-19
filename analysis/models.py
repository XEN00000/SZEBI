from django.db import models
from uuid import uuid4
from django.conf import settings

from .logic.enums import ReportType, Measurement
class Report(models.Model):
    title = models.CharField(max_length=200)
    generated_at = models.DateTimeField(auto_now_add=True)
    payload = models.JSONField(default=dict)

    def __str__(self):
        return self.title



class FileType(models.TextChoices):
    PDF = "PDF"
    PNG = "PNG"
class StatisticElement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    periodStart = models.DateTimeField()
    periodEnd = models.DateTimeField()

    createdAt = models.DateTimeField(auto_now_add=True)
    createdBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    reportType = models.CharField(
        max_length=20,
        choices=ReportType.choices,
        default=ReportType.DAILY,
        db_index=True,
    )

    metric = models.CharField(
        max_length=30,
        choices=Measurement.choices,
        null=True,
        blank=True,
        db_index=True,
    )

    roomId = models.CharField(max_length=100, null=True, blank=True, db_index=True)

    fileType = models.CharField(
        max_length=10,
        choices=FileType.choices,
        default=FileType.PDF,
        db_index=True,
    )

    fileContent = models.BinaryField()

    def __str__(self):
        return f"{self.reportType} {self.roomId} {self.metric} [{self.periodStart} - {self.periodEnd}]"