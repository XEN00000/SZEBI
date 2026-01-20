import json
import os
import time
import logging
from typing import Any, Dict, Optional

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class MqttClient:
    """
    Prosty wrapper na paho-mqtt do publikowania (i opcjonalnie subskrypcji).
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        client_id: str = "optimization-service",
    ):
        self.host = host or os.getenv("MQTT_HOST", "mqtt")
        self.port = int(port or os.getenv("MQTT_PORT", "1883"))
        self.username = username or os.getenv("MQTT_USERNAME")
        self.password = password or os.getenv("MQTT_PASSWORD")

        self.client = mqtt.Client(client_id=client_id, clean_session=True)

        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

        self._connected = False

    def _on_connect(self, client, userdata, flags, rc):
        self._connected = (rc == 0)
        if rc == 0:
            logger.info("[MQTT] Connected to %s:%s", self.host, self.port)
        else:
            logger.error("[MQTT] Connection failed rc=%s", rc)

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False
        logger.warning("[MQTT] Disconnected rc=%s", rc)

    def connect(self, timeout_s: float = 3.0) -> bool:
        try:
            self.client.connect(self.host, self.port, keepalive=60)
            self.client.loop_start()

            # poczekaj chwilę na callback on_connect
            t0 = time.time()
            while time.time() - t0 < timeout_s and not self._connected:
                time.sleep(0.05)

            return self._connected
        except Exception as e:
            logger.exception("[MQTT] Connect error: %s", e)
            return False

    def publish_json(self, topic: str, payload: Dict[str, Any], qos: int = 1, retain: bool = False) -> bool:
        if not self._connected:
            if not self.connect():
                logger.error("[MQTT] Cannot publish, not connected.")
                return False

        try:
            msg = json.dumps(payload, ensure_ascii=False)
            res = self.client.publish(topic, msg, qos=qos, retain=retain)
            res.wait_for_publish()
            ok = (res.rc == mqtt.MQTT_ERR_SUCCESS)
            if ok:
                logger.info("[MQTT] Published topic=%s", topic)
            else:
                logger.error("[MQTT] Publish failed topic=%s rc=%s", topic, res.rc)
            return ok
        except Exception as e:
            logger.exception("[MQTT] Publish error: %s", e)
            return False

    def disconnect(self):
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except Exception:
            pass