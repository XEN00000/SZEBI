import json
import logging
import threading
import time

import paho.mqtt.client as mqtt

from .device_cache import device_cache

logger = logging.getLogger(__name__)


class DeviceStateListener:
    """
    Subskrybuje stany urządzeń z symulacji i zapisuje je do DeviceCache.
    """

    def __init__(
        self,
        mqtt_host: str = "mqtt",
        mqtt_port: int = 1883,
        topic: str = "simulation-1/device/state/#",
        client_id: str = "optimization-device-listener",
    ) -> None:
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.topic = topic
        self.client_id = client_id

        self._thread: threading.Thread | None = None
        self._started = False

    def start(self) -> None:
        if self._started:
            return
        self._started = True

        t = threading.Thread(target=self._run, name="optimization-mqtt-listener", daemon=True)
        self._thread = t
        t.start()
        logger.info("[MQTT] DeviceStateListener started (topic=%s)", self.topic)

    def _run(self) -> None:
        client = mqtt.Client(client_id=self.client_id, clean_session=True)

        def on_connect(cli, userdata, flags, rc):
            if rc == 0:
                logger.info("[MQTT] Connected to %s:%s", self.mqtt_host, self.mqtt_port)
                cli.subscribe(self.topic)
                logger.info("[MQTT] Subscribed to %s", self.topic)
            else:
                logger.error("[MQTT] Connect failed rc=%s", rc)

        def on_message(cli, userdata, msg):
            try:
                payload = json.loads(msg.payload.decode("utf-8"))
                device_cache.upsert(payload)
                # do debug: logger.debug("[MQTT] %s -> %s", msg.topic, payload)
            except Exception as e:
                logger.warning("[MQTT] Invalid message on %s: %s", msg.topic, e)

        client.on_connect = on_connect
        client.on_message = on_message

        # pętla reconnect
        while True:
            try:
                client.connect(self.mqtt_host, self.mqtt_port, keepalive=30)
                client.loop_forever()
            except Exception as e:
                logger.error("[MQTT] Connection error: %s (retry in 3s)", e)
                time.sleep(3)