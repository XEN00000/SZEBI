from django.core.mail import send_mail
from django.conf import settings
import logging
import requests

from .models import (
    Alert,
    AlertRule,
    AlertStatus,
    AlertPriority,
    AlertComment,
    NotificationLog,
    NotificationStatus,
    ChannelType,
    ChannelTypes
)
from core.models import User, Role

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
            user = User.objects.get(id=user_id)

            # Sprawdź uprawnienia użytkownika
            if not (user.is_building_admin or user.is_maintenance_engineer):
                logger.error(
                    f"Użytkownik {user.username} nie ma uprawnień do potwierdzania alarmów")
                return False

            alert.acknowledge(user)

            if comment:
                alert_comment = AlertComment.objects.create(text=comment)
                alert.alert_comment = alert_comment
                alert.save()

            logger.info(f"Alarm {alert_id} potwierdzony przez {user.username}")
            return True
        except (Alert.DoesNotExist, User.DoesNotExist) as e:
            logger.error(f"Błąd potwierdzenia alarmu: {e}")
            return False

    @staticmethod
    def close_alert(alert_id, user_id, comment=None):
        """Zamknij alarm"""
        try:
            alert = Alert.objects.get(id=alert_id)
            user = User.objects.get(id=user_id)

            # Sprawdź uprawnienia użytkownika
            if not (user.is_building_admin or user.is_maintenance_engineer):
                logger.error(
                    f"Użytkownik {user.username} nie ma uprawnień do zamykania alarmów")
                return False

            alert.close(user)

            if comment:
                alert_comment = AlertComment.objects.create(text=comment)
                alert.alert_comment = alert_comment
                alert.save()

            logger.info(f"Alarm {alert_id} zamknięty przez {user.username}")
            return True
        except (Alert.DoesNotExist, User.DoesNotExist) as e:
            logger.error(f"Błąd zamknięcia alarmu: {e}")
            return False

    @staticmethod
    def create_rule(data):
        """Utwórz regułę alarmu"""
        try:
            # Filtruj tylko dozwolone pola modelu AlertRule
            allowed_fields = [
                'name', 'target_metric', 'operator',
                'threshold_min', 'threshold_max',
                'duration_seconds', 'priority'
            ]
            filtered_data = {k: v for k,
                             v in data.items() if k in allowed_fields}

            rule = AlertRule.objects.create(**filtered_data)
            logger.info(f"Utworzono regułę {rule.name}")
            return rule
        except Exception as e:
            logger.error(f"Błąd tworzenia reguły: {e}")
            return None


class MonitoringService:
    """Serwis monitorowania - wykrywa anomalie i tworzy alarmy"""

    @staticmethod
    def inspect_data(metric_name, value, timestamp, details=None):
        """Analizuj dane i sprawdź reguły"""
        rules = AlertRule.objects.filter(target_metric=metric_name)

        for rule in rules:
            if rule.check_condition(value):
                alert = MonitoringService.create_alert(
                    rule=rule,
                    metric_name=metric_name,
                    value=value,
                    timestamp=timestamp,
                    details=details,
                )

    # todo: czy timestamp dodac jako timestamp_generated?
    @staticmethod
    def create_alert(rule, metric_name, value, timestamp, details=None, user=None):
        """Utwórz alarm"""
        try:
            # Sprawdź uprawnienia użytkownika jeśli podano
            if user and not (user.is_building_admin or user.is_maintenance_engineer):
                logger.error(
                    f"Użytkownik {user.username} nie ma uprawnień do tworzenia alarmów")
                return None

            alert = Alert.objects.create(
                alert_rule=rule,
                metric_name=metric_name,
                triggering_value=value,
                measurement_timestamp=timestamp,
                timestamp_generated=timestamp,
                priority=rule.priority,
                status=AlertStatus.NEW,
                details=details,
            )
            logger.info(f"Utworzono alarm {alert.id} dla reguły {rule.name}")
            return alert
        except Exception as e:
            logger.error(f"Błąd tworzenia alarmu: {e}")
            return None


class NotificationService:
    """Serwis powiadomień - obsługuje wysyłanie powiadomień"""

    @staticmethod
    def send_alert_notification(alert):
        """Wyślij powiadomienie o alarmie"""
        # Wyślij do emergency-mode tylko jeśli alert jest CRITICAL
        if alert.priority == AlertPriority.CRITICAL:
            NotificationService.send_to_emergency_mode(alert)

        # Pobierz użytkowników, którzy powinni otrzymać powiadomienie
        users = NotificationService.get_recipients(alert)

        for user in users:
            # Sprawdź czy użytkownik powinien otrzymać powiadomienie dla danego priorytetu
            if NotificationService._should_notify_user(user, alert):
                # todo: może wydajniej by było zbierać adresy email i potem wysłać jednego maila do wszystkich
                NotificationService._send_email(user, alert)

    @staticmethod
    def get_recipients(alert):
        """Pobierz odbiorców powiadomienia dla alarmu na podstawie priorytetu i roli"""
        # Dla krytycznych alarmów - wszyscy aktywni użytkownicy
        if alert.priority == AlertPriority.CRITICAL:
            return User.objects.filter(is_active=True)

        # Dla wysokiego priorytetu - Admin i Maintenance
        if alert.priority == AlertPriority.HIGH:
            return User.objects.filter(
                is_active=True,
                role__name__in=[Role.ADMIN, Role.MAINTENANCE]
            )

        # Dla średniego priorytetu - Admin, Maintenance i Energy Provider
        if alert.priority == AlertPriority.MEDIUM:
            return User.objects.filter(
                is_active=True,
                role__name__in=[Role.ADMIN,
                                Role.MAINTENANCE, Role.ENERGY_PROVIDER]
            )

        # Dla niskiego priorytetu - tylko Admin
        return User.objects.filter(
            is_active=True,
            role__name=Role.ADMIN
        )

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
    def _should_notify_user(user, alert):
        """Sprawdź czy użytkownik powinien otrzymać powiadomienie na podstawie roli i priorytetu alarmu"""
        if not user.role:
            return False

        # Krytyczne alarmy - wszyscy
        if alert.priority == AlertPriority.CRITICAL:
            return True

        # Wysokie alarmy - Admin i Maintenance
        if alert.priority == AlertPriority.HIGH:
            return user.role.name in [Role.ADMIN, Role.MAINTENANCE]

        # Średnie alarmy - Admin, Maintenance i Energy Provider
        if alert.priority == AlertPriority.MEDIUM:
            return user.role.name in [Role.ADMIN, Role.MAINTENANCE, Role.ENERGY_PROVIDER]

        # Niskie alarmy - tylko Admin
        if alert.priority == AlertPriority.LOW:
            return user.role.name == Role.ADMIN

        return False

    @staticmethod
    def send_to_emergency_mode(alert):
        """Wyślij alert na endpoint /api/optimization/alarm/ metodą GET (parametry w URL)."""
        try:
            alert_data = {
                'id': alert.id,
                'status': alert.status,
                'priority': alert.priority,
                'triggering_value': alert.triggering_value,
                'timestamp_generated': alert.timestamp_generated.isoformat(),
                'rule_name': alert.alert_rule.name if alert.alert_rule else None,
                'rule_metric': alert.alert_rule.target_metric if alert.alert_rule else None,
            }
            response = requests.get(
                f"{settings.BASE_URL}/api/optimization/alarm/",
                params=alert_data,
                timeout=5
            )
            if response.status_code == 200:
                logger.info(
                    f"Alert {alert.id} wysłany do /api/optimization/alarm/")
                return True
            logger.error(
                f"Błąd wysyłania do /api/optimization/alarm/ {response.status_code} - {response.text}"
            )
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Błąd połączenia z /api/optimization/alarm/: {e}")
            return False
