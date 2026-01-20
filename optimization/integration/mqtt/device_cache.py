import threading
from typing import Dict, Any, List


class DeviceCache:
    """
    Prosty cache ostatniego stanu urządzeń widzianych na MQTT.
    key = uuid (str), value = payload (dict)
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._by_uuid: Dict[str, Dict[str, Any]] = {}

    def upsert(self, payload: Dict[str, Any]) -> None:
        uuid = payload.get("uuid") or payload.get("id")
        if not uuid:
            return
        with self._lock:
            self._by_uuid[str(uuid)] = payload

    def all(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._by_uuid.values())

    def active(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [p for p in self._by_uuid.values() if p.get("is_active") is True]


# singleton na cały proces Django
device_cache = DeviceCache()