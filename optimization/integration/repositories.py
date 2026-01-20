from optimization.models import OptimizationRule, UserPreference
from simulation.models import Device

class RuleRepository:
    """
    Zapewnia dostęp do reguł optymalizacji dla Kontrolera.
    Realizuje założenie: 'Pobierz reguły i preferencje'[cite: 216].
    """
    def get_active_rules(self):
        # Pobieramy tylko aktywne reguły, posortowane ważnością (priorytetem)
        return OptimizationRule.objects.filter(is_active=True).order_by('-priority')

class UserPreferenceRepository:
    """
    Zapewnia dostęp do preferencji użytkownika.
    """
    def get_all_preferences(self):
        # Pobranie wszystkich preferencji naraz (optymalizacja zapytań SQL - select_related)
        return UserPreference.objects.select_related('device').all()

    def get_preference_for_device(self, device_id):
        return UserPreference.objects.filter(device_id=device_id).first()

class DeviceRepository:
    """
    Dostęp do urządzeń (z modułu symulacji).
    """
    def get_all_active_devices(self):
        return Device.objects.filter(is_active=True)