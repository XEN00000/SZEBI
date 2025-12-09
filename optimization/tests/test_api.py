from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from simulation.models import Device

class ApiTestCase(TestCase):
    """
    Testy integracyjne API (views.py).
    Dostosowane do nowego formatu ExternalAlarmSerializer (Adapter).
    """
    
    def setUp(self):
        self.client = APIClient()
        # Tworzymy urządzenie o ID=1, ponieważ nasz kontroler (w logice adaptera)
        # hardcoduje sterowanie urządzeniem ID=1 w przypadku awarii.
        self.device = Device.objects.create(
            id=1, 
            name="Test Device", 
            device_type="CONSUMER", 
            nominal_power=1.0, 
            is_active=True
        )

    def test_alarm_endpoint_success(self):
        """
        Czy endpoint akceptuje nowy format JSON z modułu Alarmów?
        """
        # To jest format zgodny z ExternalAlarmSerializer
        data = {
            "id": 101,
            "status": "NEW",
            "priority": "CRITICAL",
            "triggering_value": 120.5,
            "timestamp_generated": timezone.now().isoformat(),
            "rule_name": "Test Ognia",
            "rule_metric": "temp_sensor_1"
        }
        
        response = self.client.post('/api/optimization/alarm/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'received')

    def test_alarm_endpoint_bad_request(self):
        """
        Czy brak kluczowych pól (np. priority, triggering_value) zwraca 400?
        """
        # Brakuje triggering_value i timestamp_generated
        data = {
            "id": 102,
            "status": "NEW",
            "priority": "HIGH"
        }
        
        response = self.client.post('/api/optimization/alarm/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_run_optimization_endpoint(self):
        """
        Czy ręczne uruchomienie cyklu działa? (Bez zmian)
        """
        response = self.client.post('/api/optimization/run/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')

    def test_device_list_endpoint(self):
        """
        Czy endpoint GET /devices/ zwraca listę urządzeń? (Bez zmian)
        """
        response = self.client.get('/api/optimization/devices/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Test Device")