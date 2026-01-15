import datetime
from typing import List, Dict, Any

class MQTTManager:

    def __init__(self, broker_url: str, topics: List[str]):
        self.broker_url = broker_url
        self.topics = topics
        self.connection_status = False

    def connect(self) -> bool:
        """
        Nawiązuje połączenie z brokerem MQTT.
        """
        self.connection_status = True
        print(f"MQTT: Połączono z brokerem na {self.broker_url}")

        for topic in self.topics:
            self.subscribe(topic)

        return self.connection_status

    def reconnect(self) -> bool:
        """
        Automatycznie ponawia próbę połączenia.
        Wymagane, aby moduł automatycznie odzyskiwał połączenie po awarii MQTT.
        """
        if not self.connection_status:
            print("MQTT: Trwa ponawianie połączenia...")
            self.connection_status = self.connect()

        return self.connection_status

    def get_connection_status(self) -> bool:
        """
        Zwraca bieżący stan połączenia.
        """
        return self.connection_status

    def subscribe(self, topic: str) -> None:
        """
        Subskrybuje określony temat.
        """

        print(f"MQTT: Subskrybowano temat: {topic}")


    def receive(self) -> List[Dict[str, Any]]:        
        import random
        val = 20.0 + random.uniform(-2.0, 2.0)
        
        processed_message = {
            'location_uuid': 'SALON-01', 
            'param_name': 'temperature',
            'value': round(val, 2),
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        return [processed_message]