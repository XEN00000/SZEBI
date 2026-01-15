from django.db import models

class OptimizationRule(models.Model):
    """
    Reguły optymalizacji definiowane przez administratora.
    Np. "Jeśli cena > 1.0 PLN, wyłącz urządzenia o priorytecie < 3".
    """
    name = models.CharField(max_length=128)
    priority = models.IntegerField(default=1, help_text="Wyższy numer = ważniejsza reguła")
    is_active = models.BooleanField(default=True)
    
    # Warunek w formie tekstowej (np. "cena > 1.0 PLN")
    condition = models.CharField(max_length=255) 
    
    # Akcja do wykonania
    action = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} (Prio: {self.priority})"

class UserPreference(models.Model):
    """
    Preferencje użytkownika przypisane do konkretnego urządzenia.
    """
    # Relacja do urządzenia z modułu symulacji
    device = models.OneToOneField('simulation.Device', on_delete=models.CASCADE, related_name='preference')
    # Oczekiwane parametry (np. temperatura w pokoju, jasność)
    target_value = models.FloatField(null=True, blank=True, help_text="Np. docelowa temperatura lub jasność")
    # Harmonogram pracy (JSON)
    schedule = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Preferencje dla {self.device.name}"
