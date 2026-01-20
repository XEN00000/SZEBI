from typing import Dict, Any
from django.utils import timezone

from optimization.integration.mqtt_client import MqttClient


class SimulationClient:
    """
    Adapter do modułu symulacji – wysyłamy komendy przez MQTT.
    Topic: szebi/device/set/<uuid>
    Payload: bez zbędnego opakowania, zgodny z wymaganiami symulacji.
    """
    def __init__(self):
        self.mqtt = MqttClient(client_id="optimization-simulation-client")

    def publish_command(self, device_uuid: str, settings: Dict[str, Any]) -> bool:
        # UUID musi być stringiem (np. "TEST-UUID" albo prawdziwy uuid z symulacji)
        topic = f"szebi/device/set/{device_uuid}"

        # Symulacja oczekuje JSON z polami typu is_active/is_on/level itd.
        # Nie opakowujemy tego w {"device_id":..., "command":...}
        payload = {
            **settings,
            "source": "optimization",
            "timestamp": timezone.now().isoformat(),
        }

        return self.mqtt.publish_json(topic, payload, qos=1, retain=False)