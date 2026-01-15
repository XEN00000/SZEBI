from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Alert, AlertStatus, AlertPriority
from .services import NotificationService
import logging

logger = logging.getLogger(__name__)

# na potrzeby tworzenia w panelu admina
@receiver(post_save, sender=Alert)
def alert_created_signal(sender, instance, created, **kwargs):
    """Signal wysyłający powiadomienia gdy alert zostanie utworzony"""
    if created and instance.status == AlertStatus.NEW:
        logger.info(f"Alert {instance.id} został utworzony, wysyłam powiadomienia")
        
        # Wyślij powiadomienia
        NotificationService.send_alert_notification(instance)
