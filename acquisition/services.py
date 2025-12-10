import datetime
from typing import List, Optional, Dict, Any

from .logic.database_manager import DatabaseManager
from .models import Measurement, DataLog

class AcquisitionDataService:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_measurements_by_time_range(
        self,
        sensor_id: int,
        start_time: datetime.datetime,
        end_time: datetime.datetime
    ) -> List[Measurement]:
        """
        [API Read Method 1] Pobiera wszystkie pomiary dla danego czujnika
        w określonym zakresie czasu.
        """
        return self.db_manager.get_measurements(sensor_id, start_time, end_time)

def get_latest_measurement(self, sensor_id: int) -> Optional[Measurement]:
        """
        Pobiera najnowszy, pojedynczy pomiar dla czujnika, niezależnie od tego, kiedy wpłynął.
        """
        return self.db_manager.get_last_measurement(sensor_id)


    def get_sensor_statistics(self) -> List[Dict[str, Any]]:
        """
        [API Read Method 3] Pobiera agregowane statystyki czujników (np. status,
        liczba aktywnych/nieaktywnych, czas ostatniej komunikacji).
        """
        return self.db_manager.get_sensor_statistics()

    def get_logs_by_level(self, level: str) -> List[DataLog]:
        """
        [API Read Method 4] Pobiera logi błędów wg poziomu.
        """
        return self.db_manager.get_logs(level)

    def get_filtered_analysis_data(
            self,
            room: Optional[str] = None,
            metric: Optional[str] = None,
            start_time: Optional[datetime.datetime] = None,
            end_time: Optional[datetime.datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        [API Read Method 5] Udostępnia dane z zaawansowanym filtrowaniem. Umożliwia filtrowanie po lokalizacji (room)
        i typie sensora.
        """

        return self.db_manager.get_filtered_measurements(
            room=room,
            metric=metric,
            start_time=start_time,
            end_time=end_time
        )