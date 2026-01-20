from typing import Dict

from ..logic.database_manager import DatabaseManager
from ..models import Measurement, DataLog, DataLogLevel


class Deduplicator:
    def __init__(self, db_manager: DatabaseManager):
        self.recent_records: Dict[int, str] = {}
        self.db_manager = db_manager

    def merge_duplicates(self, data: Measurement) -> bool:
        """
        Identyfikuje rekordy o identycznym sensor_id i timestamp, scala je.
        """
        # data.status = MeasurementStatus.DUPLICATE
        sensor_id = data.sensor.id
        current_ts = data.timestamp.isoformat()

        if sensor_id in self.recent_records:
            if self.recent_records[sensor_id] == current_ts:
                if self.db_manager:
                    self.db_manager.insert_data_log(DataLog(
                        level=DataLogLevel.INFO,
                        message=f"Zduplikowana wiadomość dla sensor_id={sensor_id}, timestamp={current_ts}"
                    ))
                return True

        self.recent_records[sensor_id] = current_ts
        return False