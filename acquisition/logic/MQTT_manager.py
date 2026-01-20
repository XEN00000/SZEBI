import paho.mqtt.client as mqtt
import queue
import os

class MQTTManager:

    def __init__(self, broker_url: str, topics: list):
        self.broker_url = os.getenv('MQTT_BROKER_HOST', broker_url)
        self.topics = topics
        self.client = mqtt.Client()
        self.message_queue = queue.Queue()
        self.connection_status = False

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

    def _on_connect(self, _client, _userdata, _flags, rc):
        if rc == 0:
            self.connection_status = True
            for topic in self.topics:
                self.subscribe(topic)
        else:
            self.connection_status = False

    def _on_message(self, _client, _userdata, msg):
        self.message_queue.put((msg.topic, msg.payload.decode()))

    def _on_disconnect(self, _client, _userdata, _rc):
        self.connection_status = False

    def connect(self) -> bool:
        """
        Nawiązuje połączenie z brokerem MQTT.
        """
        try:
            self.client.connect(self.broker_url, 1883, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"MQTT connection failed: {e}")
            return False

    def reconnect(self) -> bool:
        """
        Automatycznie ponawia próbę połączenia.
        Wymagane, aby moduł automatycznie odzyskiwał połączenie po awarii MQTT.
        """
        if not self.connection_status:
            try:
                self.client.reconnect()
                return True
            except Exception as e:
                print(f"MQTT connection failed: {e}")
                return False
        return True

        # return self.connection_status

    def get_connection_status(self) -> bool:
        """
        Zwraca bieżący stan połączenia.
        """
        return self.connection_status

    def subscribe(self, topic: str) -> None:
        """
        Subskrybuje określony temat.
        """
        self.client.subscribe(topic)
        # print(f"MQTT: Subskrybowano temat: {topic}")


    def receive(self) -> list:
        messages = []
        while not self.message_queue.empty():
            messages.append(self.message_queue.get())
        return messages
