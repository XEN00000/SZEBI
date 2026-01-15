from django.test import TestCase
from simulation.models import Device
from optimization.models import OptimizationRule, UserPreference
from optimization.logic.algorithm import calculate_optimal_settings

class AlgorithmTestCase(TestCase):
    """
    Testy czystej logiki obliczeniowej (algorithms.py).
    Sprawdzamy, czy funkcja calculate_optimal_settings poprawnie podejmuje decyzje.
    """

    def setUp(self):
        # Tworzymy urządzenie, na którym będziemy testować
        self.device = Device.objects.create(
            name="Test Heater",
            device_type="CONSUMER",
            nominal_power=2.0,
            is_active=True
        )

    def test_default_behavior_safe_state(self):
        """
        Scenariusz A: Brak reguł, brak preferencji.
        Oczekujemy: Działania na 100% mocy (Safe State).
        """
        forecast = {"energy_price": 0.50} # Cena neutralna
        active_rules = [] # Pusta lista reguł
        preference = None

        result = calculate_optimal_settings(self.device, forecast, active_rules, preference)

        self.assertEqual(result['status'], "ON")
        self.assertEqual(result['power_limit'], 100)
        self.assertEqual(result['target_value'], 21.0) # Domyślna temperatura

    def test_high_price_rule_triggered(self):
        """
        Scenariusz B: Cena wysoka -> Uruchomienie reguły oszczędzania.
        """
        # Tworzymy regułę: Jeśli cena > 1.0, zredukuj moc
        rule = OptimizationRule.objects.create(
            name="Drogi Prąd",
            condition="price > 1.0",
            action="reduce_power",
            is_active=True,
            priority=10
        )
        
        forecast = {"energy_price": 1.50} # Cena wyższa niż w warunku (1.5 > 1.0)
        active_rules = [rule]
        
        result = calculate_optimal_settings(self.device, forecast, active_rules, None)

        # Sprawdzamy, czy algorytm zareagował
        self.assertEqual(result['power_limit'], 50) # Oczekujemy redukcji
        self.assertEqual(result['status'], "ECONOMY") # Oczekujemy zmiany statusu

    def test_user_preference_override(self):
        """
        Scenariusz C: Użytkownik ustawił własną temperaturę.
        """
        # Tworzymy preferencję dla urządzenia (np. chce 24 stopnie)
        preference = UserPreference.objects.create(
            device=self.device,
            target_value=24.0
        )
        
        forecast = {"energy_price": 0.50}
        
        result = calculate_optimal_settings(self.device, forecast, [], preference)

        # Algorytm powinien uwzględnić wolę użytkownika
        self.assertEqual(result['target_value'], 24.0)

    def test_critical_shutdown_rule(self):
        """
        Scenariusz D: Reguła krytyczna (wyłączenie).
        """
        rule = OptimizationRule.objects.create(
            name="Awaryjne Wyłączenie",
            condition="price > 5.0",
            action="shutdown",
            is_active=True
        )
        
        forecast = {"energy_price": 6.00} # Bardzo drogo
        
        result = calculate_optimal_settings(self.device, forecast, [rule], None)

        self.assertEqual(result['status'], "OFF")
        self.assertEqual(result['power_limit'], 0)