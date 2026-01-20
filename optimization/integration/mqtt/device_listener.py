import json
import logging
import threading
import time
from typing import Any, Dict

import paho.mqtt.client as mqtt

from .device_cache import device_cache

logger = logging.getLogger(__name__)


def normalize_device_payload(payload: Dict[str, Any], topic: str) -> Dict[str, Any]:
    """
    Normalizacja payloadu z symulacji do formatu wygodnego dla optimization.

    Symulacja publikuje na:
      szebi/device/set/<uuid>

    Payload (typowo):
      {
        "uuid": "...",
        "is_active": true,
        "type": "SMART_DEVICE",
        "name": "...",
        "model": "...",
        # dla SMART_DEVICE:
        "is_on": true/false,
        "level": 0..100   (UWAGA: procent)
      }
    """
    out = dict(payload) if isinstance(payload, dict) else {}

    # UUID: z payloadu albo z ostatniego segmentu topicu
    uuid = out.get("uuid")
    if not uuid:
        parts = (topic or "").split("/")
        if parts:
            uuid = parts[-1]
    if uuid:
        out["uuid"] = str(uuid)

    # Aktywność
    out["is_active"] = bool(out.get("is_active", False))

    # Typ urządzenia
    # (symulacja używa "type", Ty możesz chcieć też mieć alias "device_type")
    if "type" in out and "device_type" not in out:
        out["device_type"] = out["type"]

    # SMART_DEVICE: level w stanie bywa 0..100 -> zrób też level01 (0..1)
    level = out.get("level")
    if level is not None:
        try:
            lvl = float(level)
        except (TypeError, ValueError):
            lvl = 0.0

        # jeżeli wygląda jak procent, przelicz
        if lvl > 1.0:
            lvl01 = max(0.0, min(1.0, lvl / 100.0))
        else:
            lvl01 = max(0.0, min(1.0, lvl))

        out["level01"] = lvl01  # 0..1 (wygodne do optymalizacji)
        # out["level"] zostawiamy jak przyszło (debug / UI)

    # Dla wygody: id = uuid (jeśli gdzieś w kodzie oczekujesz "id")
    if "id" not in out and out.get("uuid"):
        out["id"] = out["uuid"]

    return out


class DeviceStateListener:
    """
    Subskrybuje stany urządzeń z symulacji i zapisuje je do DeviceCache.
    """

    def __init__(
        self,
        mqtt_host: str = "mqtt",
        mqtt_port: int = 1883,
        topic: str = "szebi/device/state/#",
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
                raw = json.loads(msg.payload.decode("utf-8"))
                normalized = normalize_device_payload(raw, msg.topic)
                device_cache.upsert(normalized)
                # logger.debug("[MQTT] %s -> %s", msg.topic, normalized)
            except Exception as e:
                logger.warning("[MQTT] Invalid message on %s: %s", msg.topic, e)

        client.on_connect = on_connect
        client.on_message = on_message

        while True:
            try:
                client.connect(self.mqtt_host, self.mqtt_port, keepalive=30)
                client.loop_forever()
            except Exception as e:
                logger.error("[MQTT] Connection error: %s (retry in 3s)", e)
                time.sleep(3)