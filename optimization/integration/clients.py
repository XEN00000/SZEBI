from typing import Dict, Any
from django.utils import timezone

from optimization.integration.mqtt_client import MqttClient

class ForecastClient:
    """
    Klient do komunikacji z Modułem Prognozowania.
    Realizuje interfejs IEnergyForecast.
    """
    def get_energy_forecast(self):
        # MOCK: Symulujemy dane pogodowe i cenowe
        # requests.get('http://forecast-module/api/...')
        return {
            "energy_price": random.uniform(0.40, 1.50),  # Cena w PLN
            "temperature": random.uniform(-5.0, 30.0),   # Temp zewnętrzna
            "cloud_cover": random.randint(0, 100)        # Zachmurzenie %
        }

class SimulationClient:
    """
    Adapter do modułu symulacji – wysyłamy komendy przez MQTT.
    Realizuje interfejs IDeviceControl[cite: 265].
    """
    def __init__(self):
        self.mqtt = MqttClient(client_id="optimization-simulation-client")

    def publish_command(self, device_id: int, settings: Dict[str, Any]) -> bool:
        topic = f"simulation/commands/{device_id}"

        payload = {
            "device_id": device_id,
            "command": settings,
            "source": "optimization",
            "timestamp": timezone.now().isoformat(),
        }

        return self.mqtt.publish_json(topic, payload, qos=1, retain=False)