from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Alert, AlertStatus, AlertPriority
from .services import NotificationService
import logging

logger = logging.getLogger(__name__)

# send a notification for each alarm created


@receiver(post_save, sender=Alert)
def alert_created_signal(sender, instance, created, **kwargs):
    """Signal that sends notifications when an alert is created"""
    if created and instance.status == AlertStatus.NEW:
        logger.info(f"Alert {instance.id} was created, sending notifications")

        NotificationService.send_alert_notification(instance)
