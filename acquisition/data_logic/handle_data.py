import datetime
import json

from typing import Dict, Optional
from ..logic.database_manager import DatabaseManager
from ..models import Measurement, DataLog, MeasurementStatus, DataLogLevel, Location, SensorType, Sensor
from .validator import Validator
from .deduplicator import Deduplicator
from .transformer import Transformer
from django.utils import timezone

class HandleData:
    def __init__(self, db_manager: DatabaseManager, validator: Validator, deduplicator: Deduplicator, transformer: Transformer):
        self.validator = validator
        self.deduplicator = deduplicator
        self.transformer = transformer
        self.db_manager = db_manager

    def process(self, topic: str, raw_message: str) -> Optional[Measurement]:
        try:
            try:
                data = json.loads(raw_message)
            except json.JSONDecodeError:
                self._log_error("Błędny format JSON wiadomości MQTT", level=DataLogLevel.ERROR,
                                topic=topic, raw_message=raw_message)
                return None

            # --- obsługa różnych topiców ---
            if topic.startswith("szebi/status"):
                # dla statusu logujemy konsumpcję i ładowanie
                consumption_mode = data.get("consumption_mode")
                charging_mode = data.get("charging_mode")
                self._log_error(f"System status: consumption={consumption_mode}, charging={charging_mode}",
                                level=DataLogLevel.INFO, raw_message=raw_message)
                return None

            # Weather: szebi/weather/<uuid>/<metryka>
            elif topic.startswith("szebi/weather/") or topic.startswith("szebi/device/state/"):
                parts = topic.split("/")
                if len(parts) < 4:
                    return None
                env_uuid = parts[2]  # uuid pogody lub urządzenia
                metric_name = data.get("metric_name") or "is_active"
            else:
                self._log_error(f"Nieznany topic: {topic}", level=DataLogLevel.WARNING, raw_message=raw_message)
                return None

            # Konwersja surowych danych na obiekt modelu
            measurement = self._convert_raw_to_measurement(env_uuid, metric_name, data, topic)
            if not measurement:
                return None

            # Walidacja
            is_valid = self.validator.validate(measurement, topic=topic, raw_message=raw_message)
            if not is_valid:
                measurement.status = MeasurementStatus.ERROR
                self._log_error(f"Wartość {measurement.value} poza zakresem dla {metric_name}",
                                level=DataLogLevel.WARNING,
                                measurement=measurement,
                                topic=topic,
                                raw_message=raw_message)

            # Deduplikacja
            if self.deduplicator.merge_duplicates(measurement):
                measurement.status = MeasurementStatus.DUPLICATE

            # Transformacja
            measurement = self.transformer.convert_units(measurement)

            # Zapis do bazy i aktualizacja komunikacji sensora
            self.db_manager.insert_measurements(measurement)
            self.db_manager.update_sensor(measurement.sensor.id, measurement.timestamp)

            return measurement


        except Exception as e:
            self._log_error(f"Błąd krytyczny procesowania: {str(e)}",
                            level=DataLogLevel.CRITICAL,
                            topic=topic,
                            raw_message=raw_message)
            return None

    def _convert_raw_to_measurement(self, env_uuid: str, metric_name: str, data: Dict, topic: Optional[str] = None) -> Optional[Measurement]:
        try:
            unit = data.get("unit", "standard")

            sensor = self._find_or_create_sensor(env_uuid, metric_name, unit)
            raw_ts = data.get("ts")
            ts = datetime.datetime.fromtimestamp(raw_ts, tz=datetime.timezone.utc) if raw_ts else timezone.now()

            if "value" in data:
                val = data["value"]
            elif "is_active" in data:
                val = data.get("level", 1.0 if data["is_active"] else 0.0)
            else:
                val = 0.0

            measurement =  Measurement(
                sensor=sensor,
                timestamp=ts,
                value=float(val),
                status=MeasurementStatus.OK
            )

            measurement.unit = unit

            return measurement

        except Exception as e:
            self._log_error(f"Błąd konwersji danych: {e}",
                            level=DataLogLevel.ERROR,
                            topic=topic,
                            raw_message=str(data))
            return None

    def _find_or_create_sensor(self, env_name: str, param_name: str, unit) -> Sensor:

        # --- Parsowanie lokalizacji ---
        floor, room, description = self._parse_location_from_env(env_name)

        # --- Location ---
        location = Location.objects.filter(
            floor=floor,
            room__iexact=str(room)  # ignorujemy wielkość liter
        ).first()
        if not location:
            location = Location.objects.create(
                floor=floor,
                room=str(room),
                description=description
            )

        # --- Typ sensora (SensorType) ---
        sensor_type = SensorType.objects.filter(name__iexact=param_name).first()
        if not sensor_type:
            sensor_type = SensorType.objects.create(
                name=param_name,
                default_unit=unit
            )

        # --- Sensor ---
        sensor = Sensor.objects.filter(
            location=location,
            type=sensor_type
        ).first()
        if not sensor:
            sensor = Sensor.objects.create(
                location=location,
                type=sensor_type,
                name=f"{param_name} @ floor {floor} room {room}",
                status="ACTIVE"
            )

        return sensor

    # def _log_error(self, message: str, level: str):
    #     self.db_manager.insert_data_log(DataLog(level=level, message=message))

    def _log_error(self, message: str, level: str = DataLogLevel.ERROR, measurement: Optional[Measurement] = None,
                   topic: Optional[str] = None, raw_message: Optional[str] = None):
        """
        Zapisuje log do tabeli DataLog.
        Opcjonalnie można podać measurement, topic i raw_message, żeby mieć pełny kontekst.
        """
        full_message = message
        if topic:
            full_message += f" | topic: {topic}"
        if raw_message:
            full_message += f" | raw: {raw_message}"

        self.db_manager.insert_data_log(DataLog(
            measurement=measurement,
            level=level,
            message=full_message[:255]
        ))

    def _parse_location_from_env(self, env_name: str) -> tuple[int, int, str]:

        env_name = env_name.lower()

        if env_name.startswith(("in", "inside")):
            floor = 1
            room_number = ''.join(c for c in env_name if c.isdigit())
            room = int(room_number) if room_number else 0
            description = "inside"
        elif env_name.startswith(("out", "outside")):
            floor = None
            room = 0
            description = "outside"
        else:
            floor = None
            room = 0
            description = "unknown"

        return floor, room, description