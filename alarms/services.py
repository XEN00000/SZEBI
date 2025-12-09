from django.core.mail import send_mail
from django.conf import settings
import logging

from .models import (
    Alert,
    AlertRule,
    AlertStatus,
    AlertPriority,
    AlertComment,
    SZEBiUser,
    NotificationLog,
    NotificationStatus,
    ChannelType,
    ChannelTypes,
    NotificationPreference
)

logger = logging.getLogger(__name__)


class AlertManager:
    """Menedżer alarmów - odpowiada za zarządzanie cyklem życia alarmów"""
    
    @staticmethod
    def get_alert_details(alert_id):
        """Pobierz szczegóły alarmu"""
        try:
            return Alert.objects.select_related(
                'alert_rule', 
                'alert_comment',
                'acknowledged_by',
                'closed_by'
            ).get(id=alert_id)
        except Alert.DoesNotExist:
            logger.error(f"Alarm {alert_id} nie istnieje")
            return None
    
    @staticmethod
    def acknowledge_alert(alert_id, user_id, comment=None):
        """Potwierdź alarm"""
        try:
            alert = Alert.objects.get(id=alert_id)
            user = SZEBiUser.objects.get(id=user_id)
            
            alert.acknowledge(user)
            
            if comment:
                alert_comment = AlertComment.objects.create(text=comment)
                alert.alert_comment = alert_comment
                alert.save()
            
            logger.info(f"Alarm {alert_id} potwierdzony przez {user.username}")
            return True
        except (Alert.DoesNotExist, SZEBiUser.DoesNotExist) as e:
            logger.error(f"Błąd potwierdzenia alarmu: {e}")
            return False
    
    @staticmethod
    def close_alert(alert_id, user_id, comment=None):
        """Zamknij alarm"""
        try:
            alert = Alert.objects.get(id=alert_id)
            user = SZEBiUser.objects.get(id=user_id)
            
            alert.close(user)
            
            if comment:
                alert_comment = AlertComment.objects.create(text=comment)
                alert.alert_comment = alert_comment
                alert.save()
            
            logger.info(f"Alarm {alert_id} zamknięty przez {user.username}")
            return True
        except (Alert.DoesNotExist, SZEBiUser.DoesNotExist) as e:
            logger.error(f"Błąd zamknięcia alarmu: {e}")
            return False
    
    @staticmethod
    def create_rule(data):
        """Utwórz regułę alarmu"""
        try:
            rule = AlertRule.objects.create(**data)
            logger.info(f"Utworzono regułę {rule.name}")
            return rule
        except Exception as e:
            logger.error(f"Błąd tworzenia reguły: {e}")
            return None


class MonitoringService:
    """Serwis monitorowania - wykrywa anomalie i tworzy alarmy"""
    
    @staticmethod
    def inspect_data(metric_name, value, timestamp):
        """Analizuj dane i sprawdź reguły"""
        rules = AlertRule.objects.filter(target_metric=metric_name)
        
        for rule in rules:
            if rule.check_condition(value):
                alert = MonitoringService.create_alert(rule, value, timestamp)
                if alert:
                    NotificationService.send_alert_notification(alert)
    
    @staticmethod
    def evaluate_rules(metric_name, value):
        """Oceń reguły dla danej metryki"""
        rules = AlertRule.objects.filter(target_metric=metric_name)
        triggered_rules = []
        
        for rule in rules:
            if rule.check_condition(value):
                triggered_rules.append(rule)
        
        return triggered_rules
    
    @staticmethod
    def create_alert(rule, value, timestamp):
        """Utwórz alarm"""
        try:
            alert = Alert.objects.create(
                alert_rule=rule,
                triggering_value=value,
                priority=rule.priority,
                status=AlertStatus.NEW
            )
            logger.info(f"Utworzono alarm {alert.id} dla reguły {rule.name}")
            return alert
        except Exception as e:
            logger.error(f"Błąd tworzenia alarmu: {e}")
            return None
    
    @staticmethod
    def save_alert(alert_id, user_id):
        """Zapisz alarm (historyczny zapis)"""
        try:
            alert = Alert.objects.get(id=alert_id)
            logger.info(f"Zapisano alarm {alert_id}")
            return True
        except Alert.DoesNotExist:
            logger.error(f"Alarm {alert_id} nie istnieje")
            return False


class NotificationService:
    """Serwis powiadomień - obsługuje wysyłanie powiadomień"""
    
    @staticmethod
    def send_alert_notification(alert):
        """Wyślij powiadomienie o alarmie"""
        # Pobierz użytkowników, którzy powinni otrzymać powiadomienie
        users = NotificationService.get_recipients(alert)
        
        for user in users:
            preferences = user.get_notification_preferences()
            
            for pref in preferences:
                # Sprawdź poziom priorytetu
                if NotificationService._check_priority(alert.priority, pref.min_priority_level):
                    if pref.enable_email:
                        NotificationService._send_email(user, alert)
                    if pref.enable_webpush:
                        NotificationService._send_webpush(user, alert)
    
    @staticmethod
    def get_recipients(alert):
        """Pobierz odbiorców powiadomienia dla alarmu"""
        # Logika określania odbiorców (np. wszyscy aktywni użytkownicy)
        return SZEBiUser.objects.filter(is_active=True)
    
    @staticmethod
    def log_notification(user, alert, channel, status, error_message=''):
        """Zarejestruj powiadomienie w logu"""
        try:
            channel_obj, _ = ChannelType.objects.get_or_create(channel=channel)
            NotificationLog.objects.create(
                alert=alert,
                recipient=user,
                channel=channel_obj,
                status=status,
                error_message=error_message
            )
        except Exception as e:
            logger.error(f"Błąd logowania powiadomienia: {e}")
    
    @staticmethod
    def _send_email(user, alert):
        """Wyślij powiadomienie email"""
        try:
            subject = f"[{alert.priority}] Nowy alarm w systemie"
            message = f"""
            Wykryto nowy alarm:
            
            Priorytet: {alert.get_priority_display()}
            Status: {alert.get_status_display()}
            Wartość wyzwalająca: {alert.triggering_value}
            Czas wygenerowania: {alert.timestamp_generated}
            
            Zaloguj się do systemu aby zobaczyć szczegóły.
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            NotificationService.log_notification(
                user, alert, ChannelTypes.EMAIL, NotificationStatus.SENT
            )
            logger.info(f"Wysłano email do {user.email}")
        except Exception as e:
            error_msg = str(e)
            NotificationService.log_notification(
                user, alert, ChannelTypes.EMAIL, NotificationStatus.FAILED, error_msg
            )
            logger.error(f"Błąd wysyłania emaila: {error_msg}")
    
    @staticmethod
    def _send_webpush(user, alert):
        """Wyślij powiadomienie WebPush"""
        try:
            # Implementacja WebPush (wymaga dodatkowej biblioteki)
            # Na potrzeby przykładu tylko logowanie
            logger.info(f"Wysłano WebPush do {user.username}")
            
            NotificationService.log_notification(
                user, alert, ChannelTypes.WEBPUSH, NotificationStatus.SENT
            )
        except Exception as e:
            error_msg = str(e)
            NotificationService.log_notification(
                user, alert, ChannelTypes.WEBPUSH, NotificationStatus.FAILED, error_msg
            )
            logger.error(f"Błąd wysyłania WebPush: {error_msg}")
    
    @staticmethod
    def _check_priority(alert_priority, min_priority):
        """Sprawdź czy priorytet alarmu spełnia minimum"""
        priority_levels = {
            AlertPriority.LOW: 1,
            AlertPriority.MEDIUM: 2,
            AlertPriority.HIGH: 3,
            AlertPriority.CRITICAL: 4
        }
        return priority_levels.get(alert_priority, 0) >= priority_levels.get(min_priority, 0)

