from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from .models import AlertRule, Alert, RuleOperator, AlertPriority, SZEBiUser, AlertStatus
from .services import MonitoringService, NotificationService, AlertManager

User = get_user_model()

class AlarmSystemTest(TestCase):

    def setUp(self):
        # Przygotowanie danych testowych
        self.user = User.objects.create_user(username='testuser', password='password')
        self.szebi_user = SZEBiUser.objects.create(user=self.user, username='testuser', email='test@example.com', role='admin')
        
        self.rule = AlertRule.objects.create(
            name="Test Temp High",
            target_metric="temp_sensor_1",
            operator=RuleOperator.GREATER_THAN,
            threshold_max=50.0,
            priority=AlertPriority.CRITICAL # CRITICAL wymusza wysyłkę do Optymalizacji
        )

    # --- TEST 1: Logika Reguł ---
    def test_rule_logic(self):
        """Sprawdza, czy reguła poprawnie wykrywa przekroczenie progu"""
        self.assertTrue(self.rule.check_condition(51.0))
        self.assertFalse(self.rule.check_condition(49.0))

    # --- TEST 2: Tworzenie Alarmu przez Serwis ---
    def test_alert_creation(self):
        """Sprawdza czy MonitoringService tworzy alarm w bazie"""
        MonitoringService.inspect_data("temp_sensor_1", 55.0, "2024-01-01T12:00:00Z")
        
        self.assertEqual(Alert.objects.count(), 1)
        alert = Alert.objects.first()
        self.assertEqual(alert.triggering_value, 55.0)
        self.assertEqual(alert.priority, AlertPriority.CRITICAL)

    # --- TEST 3: Mockowanie Komunikacji z Modułem Optymalizacji ---
    @patch('alarms.services.requests.get')
    def test_communication_with_optimization(self, mock_get):
        """
        Symulujemy wysłanie alarmu do modułu optymalizacji.
        Używamy @patch, aby podmienić 'requests.get' na fałszywy obiekt (mock).
        """
        # Konfigurujemy mocka, żeby udawał sukces (status 200)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Wywołujemy logikę, która powinna wysłać request
        MonitoringService.inspect_data("temp_sensor_1", 60.0, "2024-01-01T12:00:00Z")
        
        # Sprawdzamy czy alarm powstał
        alert = Alert.objects.first()
        
        # ASERCJA: Czy requests.get został wywołany co najmniej raz?
        self.assertGreaterEqual(mock_get.call_count, 1)
        
        # Możemy sprawdzić argumenty wywołania (czy URL był dobry)
        args, kwargs = mock_get.call_args
        self.assertIn('/api/optimalization/alarm/', args[0])
        self.assertEqual(kwargs['params']['id'], alert.id)
        self.assertEqual(kwargs['params']['triggering_value'], 60.0)

    # --- TEST 4: Potwierdzanie Alarmu ---
    def test_acknowledge_alert(self):
        alert = Alert.objects.create(
            alert_rule=self.rule, triggering_value=100, priority=AlertPriority.HIGH
        )
        AlertManager.acknowledge_alert(alert.id, self.szebi_user.id, "Widzę to")
        
        alert.refresh_from_db()
        self.assertEqual(alert.status, AlertStatus.ACKNOWLEDGED)
        self.assertEqual(alert.alert_comment.text, "Widzę to")