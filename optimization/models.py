from django.db import models
from django.utils import timezone

class OptimizationRule(models.Model):
    """
    Reguły optymalizacji definiowane przez administratora.
    Np. "Jeśli cena > 1.0 PLN, wyłącz urządzenia o priorytecie < 3".
    Każda reguła może mieć wiele warunków (JSON).
    Tylko jedna reguła może być aktywna na raz.
    """
    name = models.CharField(max_length=128)
    priority = models.IntegerField(default=1, help_text="Wyższy numer = ważniejsza reguła")
    is_active = models.BooleanField(default=True)
    
    # Warunki w formie JSON - lista warunków do spełnienia
    # Przykład: [{"field": "price", "operator": ">", "value": 0.8}]
    conditions = models.JSONField(default=list, blank=True, help_text="Lista warunków jako JSON")
    
    # Akcja do wykonania
    action = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        # Jeśli ta reguła jest aktywowana, deaktywuj wszystkie inne
        if self.is_active:
            OptimizationRule.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (Prio: {self.priority})"

class UserPreference(models.Model):
    """
    Preferencje użytkownika przypisane do konkretnego urządzenia.
    """
    # Relacja do urządzenia z modułu symulacji
    device = models.OneToOneField('simulation.DeviceConfig', on_delete=models.CASCADE, related_name='preference')
    # Oczekiwane parametry (np. temperatura w pokoju, jasność)
    target_value = models.FloatField(null=True, blank=True, help_text="Np. docelowa temperatura lub jasność")
    # Harmonogram pracy (JSON)
    schedule = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Preferencje dla {self.device.name}"

class OptimizationLog(models.Model):
    """
    Historia wykonywanych operacji optymalizacji.
    """
    STATUS_CHOICES = [
        ('running', 'W trakcie'),
        ('success', 'Sukces'),
        ('failed', 'Błąd'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    rule = models.ForeignKey(OptimizationRule, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=255, blank=True, help_text="Wykonana akcja")
    affected_devices_count = models.IntegerField(default=0, help_text="Liczba urządzeń, na które wpłynęła operacja")
    message = models.TextField(blank=True, help_text="Opis operacji lub błąd")
    details = models.JSONField(default=dict, blank=True, help_text="Dodatkowe szczegóły operacji")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.get_status_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
