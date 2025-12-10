# from django.db import models


# class Alarm(models.Model):
#     level = models.CharField(max_length=50)
#     message = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     acknowledged = models.BooleanField(default=False)

#     def __str__(self):
#         return f"[{self.level}] {self.message[:60]}"


from django.db import models
from django.conf import settings
from django.utils import timezone
from enum import Enum


class AlertPriority(models.TextChoices):
    CRITICAL = 'CRITICAL', 'Krytyczny'
    HIGH = 'HIGH', 'Wysoki'
    MEDIUM = 'MEDIUM', 'Średni'
    LOW = 'LOW', 'Niski'


class AlertStatus(models.TextChoices):
    NEW = 'NEW', 'Nowy'
    ACKNOWLEDGED = 'ACKNOWLEDGED', 'Potwierdzony'
    CLOSED = 'CLOSED', 'Zamknięty'


class NotificationStatus(models.TextChoices):
    SENT = 'SENT', 'Wysłane'
    FAILED = 'FAILED', 'Nieudane'


class ChannelTypes(models.TextChoices):
    EMAIL = 'EMAIL', 'Email'
    WEBPUSH = 'WEBPUSH', 'WebPush'


class RuleOperator(models.TextChoices):
    GREATER_THAN = 'GREATER_THAN', 'Większe niż'
    LESS_THAN = 'LESS_THAN', 'Mniejsze niż'
    EQUALS = 'EQUALS', 'Równe'


class NotificationGroup(models.Model):
    """Grupa użytkowników do powiadomień"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='notification_groups')
    
    class Meta:
        db_table = 'notification_group'
        verbose_name = 'Grupa powiadomień'
        verbose_name_plural = 'Grupy powiadomień'
    
    def __str__(self):
        return self.name
    
    def add_user(self, user):
        """Dodaj użytkownika do grupy"""
        self.users.add(user)
    
    def remove_user(self, user):
        """Usuń użytkownika z grupy"""
        self.users.remove(user)
    
    def get_users(self):
        """Pobierz listę użytkowników"""
        return self.users.all()


class SZEBiUser(models.Model):
    """Rozszerzony profil użytkownika"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='szebi_profile')
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    groups = models.ManyToManyField(NotificationGroup, related_name='szebi_users')
    
    class Meta:
        db_table = 'szebi_user'
        verbose_name = 'Użytkownik SZEBi'
        verbose_name_plural = 'Użytkownicy SZEBi'
    
    def __str__(self):
        return self.username
    
    def get_notification_preferences(self):
        """Pobierz preferencje powiadomień użytkownika"""
        return self.notification_preferences.all()


class NotificationPreference(models.Model):
    """Preferencje powiadomień użytkownika"""
    user = models.ForeignKey(
        SZEBiUser, 
        on_delete=models.CASCADE, 
        related_name='notification_preferences'
    )
    enable_email = models.BooleanField(default=True)
    enable_webpush = models.BooleanField(default=True)
    min_priority_level = models.CharField(
        max_length=20,
        choices=AlertPriority.choices,
        default=AlertPriority.LOW
    )
    
    class Meta:
        db_table = 'notification_preference'
        verbose_name = 'Preferencja powiadomień'
        verbose_name_plural = 'Preferencje powiadomień'
    
    def __str__(self):
        return f"Preferencje {self.user.username}"


class AlertRule(models.Model):
    """Reguła tworzenia alarmów"""
    operator = models.CharField(max_length=20, choices=RuleOperator.choices)
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    target_metric = models.CharField(max_length=255)
    threshold_min = models.FloatField(null=True, blank=True)
    threshold_max = models.FloatField(null=True, blank=True)
    duration_seconds = models.IntegerField(default=0)
    priority = models.CharField(
        max_length=20,
        choices=AlertPriority.choices,
        default=AlertPriority.MEDIUM
    )
    
    class Meta:
        db_table = 'alert_rule'
        verbose_name = 'Reguła alarmu'
        verbose_name_plural = 'Reguły alarmów'
    
    def __str__(self):
        return self.name
    
    def check_condition(self, value):
        """Sprawdź warunek reguły"""
        if self.operator == RuleOperator.GREATER_THAN:
            return value > self.threshold_max if self.threshold_max else False
        elif self.operator == RuleOperator.LESS_THAN:
            return value < self.threshold_min if self.threshold_min else False
        elif self.operator == RuleOperator.EQUALS:
            return value == self.threshold_min if self.threshold_min else False
        return False


class AlertComment(models.Model):
    """Komentarz do alarmu"""
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'alert_comment'
        verbose_name = 'Komentarz alarmu'
        verbose_name_plural = 'Komentarze alarmów'
    
    def __str__(self):
        return f"Komentarz z {self.timestamp}"


class Alert(models.Model):
    """Alarm w systemie"""
    alert_rule = models.ForeignKey(
        AlertRule, 
        on_delete=models.CASCADE, 
        related_name='alerts',
        null=True
    )
    alert_comment = models.ForeignKey(
        AlertComment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts'
    )
    triggering_value = models.FloatField()
    timestamp_generated = models.DateTimeField(auto_now_add=True)
    timestamp_acknowledged = models.DateTimeField(null=True, blank=True)
    timestamp_closed = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=AlertStatus.choices,
        default=AlertStatus.NEW
    )
    priority = models.CharField(
        max_length=20,
        choices=AlertPriority.choices,
        default=AlertPriority.MEDIUM
    )
    acknowledged_by = models.ForeignKey(
        SZEBiUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts'
    )
    closed_by = models.ForeignKey(
        SZEBiUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='closed_alerts'
    )
    
    class Meta:
        db_table = 'alert'
        verbose_name = 'Alarm'
        verbose_name_plural = 'Alarmy'
        ordering = ['-timestamp_generated']
    
    def __str__(self):
        return f"Alarm {self.id} - {self.status}"
    
    def acknowledge(self, user):
        """Potwierdź alarm"""
        self.status = AlertStatus.ACKNOWLEDGED
        self.timestamp_acknowledged = timezone.now()
        self.acknowledged_by = user
        self.save()
    
    def close(self, user):
        """Zamknij alarm"""
        self.status = AlertStatus.CLOSED
        self.timestamp_closed = timezone.now()
        self.closed_by = user
        self.save()


class ChannelType(models.Model):
    """Typ kanału powiadomień"""
    channel = models.CharField(
        max_length=20,
        choices=ChannelTypes.choices,
        unique=True
    )
    
    class Meta:
        db_table = 'channel_type'
        verbose_name = 'Typ kanału'
        verbose_name_plural = 'Typy kanałów'
    
    def __str__(self):
        return self.channel


class NotificationLog(models.Model):
    """Log powiadomień"""
    alert = models.ForeignKey(
        Alert,
        on_delete=models.CASCADE,
        related_name='notification_logs'
    )
    recipient = models.ForeignKey(
        SZEBiUser,
        on_delete=models.CASCADE,
        related_name='received_notifications'
    )
    channel = models.ForeignKey(
        ChannelType,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.SENT
    )
    timestamp_sent = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'notification_log'
        verbose_name = 'Log powiadomień'
        verbose_name_plural = 'Logi powiadomień'
        ordering = ['-timestamp_sent']
    
    def __str__(self):
        return f"Powiadomienie dla {self.recipient.username} - {self.status}"

