# from django.db import models

from .models_definitions.data_models import *
from .models_definitions.enumeration_models import *

class AcquisitionControl(models.Model):
    class Meta:
        managed = False
        verbose_name = "Panel Sterowania"
        verbose_name_plural = "Panel Sterowania"
        app_label = 'acquisition'